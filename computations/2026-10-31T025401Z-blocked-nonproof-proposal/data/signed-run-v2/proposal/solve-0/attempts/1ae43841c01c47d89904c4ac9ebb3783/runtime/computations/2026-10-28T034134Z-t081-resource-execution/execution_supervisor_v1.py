"""One owned numerical stage at a time, with live state and an enforced budget."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import queue
import signal
import subprocess
import sys
import threading
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from scripts.run_observability import OutputDirectoryLock,RunStatusWriter,write_run_identity
from resource_limits_v1 import WindowsJob


def encode(value):return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()


def _posix_metrics(group):
    rss=0;pids=[]
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():continue
        try:
            text=(entry/'stat').read_text();fields=text[text.rfind(')')+2:].split()
            if int(fields[2])==group and fields[0]!='Z':
                pids.append(int(entry.name));rss+=int(fields[21])*os.sysconf('SC_PAGE_SIZE')
        except (OSError,ValueError,IndexError):continue
    return {'active_process_ids':pids,'active_process_count':len(pids),'aggregate_rss_bytes':rss}


class Execution:
    def __init__(self,output,budget,*,root=ROOT,worker=HERE/'stage_worker_v1.py'):
        self.output=Path(output).resolve();self.root=Path(root).resolve()
        self.budget=budget;self.worker=Path(worker).resolve();self.receipts=[]
        self.lock=None;self.writer=None;self.cancelled=threading.Event()
    def cancel(self):
        self.cancelled.set()
    def __enter__(self):
        self.lock=OutputDirectoryLock.acquire(self.output,command='t081-resource-execution-v1',support='81/100')
        try:
            commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
            write_run_identity(self.lock,driver_version='t081-resource-execution-v1',dimensions=[826],git_commit=commit,git_dirty=True)
            self.writer=RunStatusWriter.start(self.output,command='t081-resource-execution-v1',support='81/100',output_lock=self.lock)
            self.config=self.output/'execution-budget.json'
            with self.config.open('xb') as stream:stream.write(encode(self.budget))
            self.config_sha=sha(self.config.read_bytes())
            self.writer.event('RESOURCE_BUDGET',budget=self.budget)
            return self
        except BaseException:
            self.lock.release();raise
    def __exit__(self,kind,error,traceback):
        try:
            if error is not None:self.writer.record_failure('RUN_INTERRUPTED' if kind is KeyboardInterrupt else 'RUN_FAILED',error)
            else:self.writer.update(workflow_state='RUN_COMPLETED',current_operation=None,terminal=True)
        finally:self.lock.release()
    def run(self,name,program,arguments,*,kind,environment=None,expected_codes=(0,)):
        folder=self.output/name;folder.mkdir()
        program=Path(program).resolve()
        command=[sys.executable,'-B',str(self.worker),'--program',str(program),
            '--program-sha256',sha(program.read_bytes()),'--config',str(self.config),
            '--config-sha256',self.config_sha,'--profile',str(folder/'profile.json'),
            '--kind',kind,'--',*map(str,arguments)]
        env=os.environ.copy();env.pop('PYTHONPATH',None);env['PYTHONDONTWRITEBYTECODE']='1'
        for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','FLINT_NUM_THREADS'):
            env[key]='1'
        if environment:env.update(environment)
        messages=queue.Queue();readers=[];job=None;process=None
        started=time.monotonic();metrics={};peak=0;cleanup=False;error=None;history={}
        self.writer.event('STAGE_STARTED',stage=name,argv=command)
        self.writer.update(workflow_state='RUNNING',current_operation={'stage':name,'phase':'initializing','budget':self.budget})
        logs={channel:(folder/(channel+'.txt')).open('x',encoding='utf-8',newline='\n') for channel in ('stdout','stderr')}
        def read(channel,stream):
            try:
                for line in stream:messages.put((channel,line))
            finally:messages.put((channel,None))
        try:
            process=subprocess.Popen(command,cwd=self.root,env=env,stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',start_new_session=os.name=='posix')
            if os.name=='nt':
                job=WindowsJob(self.budget['memory_budget_bytes'],self.budget['cpu_budget']);job.attach(process)
            for channel in ('stdout','stderr'):
                reader=threading.Thread(target=read,args=(channel,getattr(process,channel)),daemon=True)
                reader.start();readers.append(reader)
            # The actual interpreter can differ from Popen.pid on Windows venvs.
            deadline=time.monotonic()+15;worker_pid=None
            while worker_pid is None:
                channel,line=messages.get(timeout=max(.01,deadline-time.monotonic()))
                if line is None:raise RuntimeError('worker exited before READY')
                logs[channel].write(line);logs[channel].flush()
                if channel=='stdout' and line.startswith('T081_READY '):
                    ready=json.loads(line[len('T081_READY '):])
                    if ready['config_sha256']!=self.config_sha:raise ValueError('worker READY identity mismatch')
                    worker_pid=ready['pid']
                if time.monotonic()>deadline:raise TimeoutError('worker READY deadline exceeded')
            if job:job.attach_worker_pid(worker_pid)
            process.stdin.write('GO\n');process.stdin.flush();process.stdin.close()
            completed_streams=set();operation={'stage':name,'phase':'program','budget':self.budget}
            next_sample=0.0
            while process.poll() is None or len(completed_streams)<2:
                if self.cancelled.is_set():raise KeyboardInterrupt('owned execution cancelled')
                # Reap descendants before waiting on inherited stdout/stderr EOF.
                if process.poll() is not None:
                    if job and job.usage()['active_process_count']:
                        job.terminate()
                    elif os.name=='posix' and _posix_metrics(process.pid)['active_process_ids']:
                        os.killpg(process.pid,signal.SIGKILL)
                try:channel,line=messages.get(timeout=.5)
                except queue.Empty:channel=line=None
                if channel is not None:
                    if line is None:completed_streams.add(channel)
                    else:
                        logs[channel].write(line);logs[channel].flush()
                        if line.startswith('T081_EVENT '):
                            event=json.loads(line[len('T081_EVENT '):]);self.writer.event('STAGE_PROGRESS',stage=name,detail=event)
                            operation={'stage':name,**event,'budget':self.budget,'remaining_estimate_seconds':None}
                            if event['event']=='work' and 'completed' in event and 'total' in event:
                                key=tuple(event.get(k) for k in ('phase','parity','kind','unit'))
                                old=history.get(key);now=time.monotonic();done=event['completed']
                                if old and done>old[0]:
                                    operation['remaining_estimate_seconds']=(now-old[1])/(done-old[0])*(event['total']-done)
                                    operation['estimate_basis']='last comparable observed work-unit interval, not wall-time percentage'
                                history[key]=(done,now)
                            print(name+': '+json.dumps(event,sort_keys=True),flush=True)
                        else:print(name+': '+line,end='',flush=True)
                now=time.monotonic()
                if now>=next_sample:
                    next_sample=now+1
                    if job:
                        metrics=job.usage();peak=max(peak,metrics['peak_committed_bytes'])
                    else:
                        # RLIMIT_AS is inherited; the aggregate is monitored separately.
                        metrics=_posix_metrics(process.pid);rss=metrics['aggregate_rss_bytes']
                        peak=max(peak,rss)
                        if rss>self.budget['memory_budget_bytes']:raise MemoryError('owned stage aggregate RSS exceeded memory budget')
                    operation.update({'stage_elapsed_seconds':now-started,'resources':metrics})
                    self.writer.update(current_operation=operation)
            process.wait()
            if job:
                metrics=job.usage();peak=max(peak,metrics['peak_committed_bytes'])
                if metrics['active_process_count']:
                    job.terminate()
                    deadline=time.monotonic()+10
                    while job.usage()['active_process_count'] and time.monotonic()<deadline:time.sleep(.05)
                cleanup=job.usage()['active_process_count']==0
            else:
                metrics=_posix_metrics(process.pid)
                if metrics['active_process_ids']:
                    os.killpg(process.pid,signal.SIGKILL)
                    deadline=time.monotonic()+10
                    while _posix_metrics(process.pid)['active_process_ids'] and time.monotonic()<deadline:time.sleep(.05)
                cleanup=not _posix_metrics(process.pid)['active_process_ids']
            if not cleanup:raise RuntimeError('owned numerical descendants remain after stage exit')
            if process.returncode not in expected_codes:raise RuntimeError(name+' exited '+str(process.returncode)+'; inspect retained stderr and profile')
        except BaseException as exception:
            error=exception
            if process is not None:
                if process.stdin is not None and not process.stdin.closed:process.stdin.close()
                if job:job.terminate()
                elif os.name=='posix' and _posix_metrics(process.pid)['active_process_ids']:
                    os.killpg(process.pid,signal.SIGKILL)
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:process.kill();process.wait()
                if job:
                    deadline=time.monotonic()+10
                    while job.usage()['active_process_count'] and time.monotonic()<deadline:time.sleep(.05)
                    cleanup=job.usage()['active_process_count']==0
                elif os.name=='posix':cleanup=not _posix_metrics(process.pid)['active_process_ids']
                else:cleanup=process.poll() is not None
            raise
        finally:
            if job:job.close()
            if process is not None and process.poll() is None:process.kill();process.wait()
            for reader in readers:reader.join()
            for stream in logs.values():stream.close()
            receipt={'format':'t081-owned-stage-receipt-v1','stage':name,'argv':command,
                'exit_code':None if process is None else process.returncode,'elapsed_seconds':time.monotonic()-started,
                'budget':self.budget,'last_metrics':metrics,'peak_budgeted_memory_bytes':peak,
                'memory_metric':'job committed memory' if os.name=='nt' else 'monitored aggregate RSS plus per-process RLIMIT_AS',
                'worker_cleanup_verified':cleanup,'error':None if error is None else f'{type(error).__name__}: {error}',
                'program_sha256':sha(program.read_bytes()),'config_sha256':self.config_sha,
                'logs':{channel:{'path':str((folder/(channel+'.txt')).relative_to(self.output)),
                    'sha256':sha((folder/(channel+'.txt')).read_bytes())} for channel in logs}}
            with (folder/'receipt.json').open('xb') as stream:stream.write(encode(receipt))
            self.receipts.append(receipt)
            self.writer.event('STAGE_FINISHED',stage=name,exit_code=receipt['exit_code'],cleanup_verified=cleanup)
        return receipt
