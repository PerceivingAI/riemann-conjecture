"""Retained supervisor for this fixed continuation; not a research evaluator."""
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = Path(__file__).resolve().parent
DATA = BUNDLE/'data'
DATA.mkdir(exist_ok=True)
STAGE = sys.argv[1]
PACKET = DATA/'source-m626-v1.json.gz'
AUDIT = DATA/'audit-m626-v1.json.gz'
RESULT = DATA/'assessment-m626-v1.json'
COMMANDS = {
    'source': ['scripts.weil_weighted_low_space','--boundary','626','--base',str(ROOT/'computations/2026-10-24T124142Z-weighted-low-space/data/source-m316-v1.json.gz'),'--output',str(PACKET)],
    'audit': ['scripts.verify_weighted_low_space_inputs','--packet',str(PACKET),'--reuse-accepted-low','--output',str(AUDIT)],
    'assessment': ['scripts.verify_weighted_low_space','--packet',str(PACKET),'--audit',str(AUDIT),'--output',str(RESULT)],
    'replay': ['scripts.verify_weighted_low_space','--packet',str(PACKET),'--audit',str(AUDIT),'--result',str(RESULT),'--output',str(DATA/'replay-m626-v1.json')],
}
command = [sys.executable,'-m',*COMMANDS[STAGE]]
receipt_path = DATA/(STAGE+'-run.json')
if receipt_path.exists(): raise SystemExit('refusing existing stage receipt')
class Counters(ctypes.Structure):
    _fields_ = [('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD),*[(name,ctypes.c_size_t) for name in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]]
class FileTime(ctypes.Structure):
    _fields_ = [('low',wintypes.DWORD),('high',wintypes.DWORD)]
kernel = ctypes.WinDLL('kernel32',use_last_error=True)
psapi = ctypes.WinDLL('psapi',use_last_error=True)
kernel.GetProcessTimes.argtypes = [wintypes.HANDLE,*([ctypes.POINTER(FileTime)]*4)]
psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
def sample(child):
    times = [FileTime() for _ in range(4)]
    memory = Counters(); memory.cb = ctypes.sizeof(memory)
    if not kernel.GetProcessTimes(int(child._handle),*[ctypes.byref(x) for x in times]): raise ctypes.WinError(ctypes.get_last_error())
    if not psapi.GetProcessMemoryInfo(int(child._handle),ctypes.byref(memory),memory.cb): raise ctypes.WinError(ctypes.get_last_error())
    ticks = lambda x: (x.high << 32) + x.low
    return {'elapsed_seconds':time.perf_counter()-start,'cpu_seconds':sum(ticks(x) for x in times[2:])/1e7,'working_set_bytes':memory.WorkingSetSize,'peak_working_set_bytes':memory.PeakWorkingSetSize}
env = os.environ.copy()
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'): env[key] = '1'
start = time.perf_counter(); samples=[]; timed_out=False
with (DATA/(STAGE+'.stdout.txt')).open('xb') as stdout, (DATA/(STAGE+'.stderr.txt')).open('xb') as stderr:
    child = subprocess.Popen(command,cwd=ROOT,env=env,stdout=stdout,stderr=stderr)
    try:
        while True:
            try:
                child.wait(timeout=15)
                break
            except subprocess.TimeoutExpired:
                progress=sample(child); samples.append(progress); print(json.dumps({'stage':STAGE,**progress}),flush=True)
                if progress['elapsed_seconds']>=1800:
                    timed_out=True; child.kill(); child.wait(); break
    finally:
        if child.poll() is None: child.kill(); child.wait()
receipt = {'command':command,'finished_utc':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),'stage':STAGE,'safety_deadline_seconds':1800,'timed_out':timed_out,'elapsed_seconds':time.perf_counter()-start,'exit_code':child.returncode,'owned_exit_confirmed':child.poll() is not None,'samples':samples,'supervisor_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
with receipt_path.open('x',encoding='utf-8',newline='\n') as stream: json.dump(receipt,stream,indent=2); stream.write('\n')
print(json.dumps(receipt),flush=True)
raise SystemExit(124 if timed_out else child.returncode)
