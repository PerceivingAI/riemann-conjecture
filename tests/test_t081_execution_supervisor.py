"""Actual owned-process progress, failure, cancellation and launcher containment."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import threading
import time

import pytest

ROOT=Path(__file__).resolve().parents[1]
BUNDLE=ROOT/'computations/2026-10-28T034134Z-t081-resource-execution'


@pytest.fixture
def supervisor(monkeypatch):
    monkeypatch.syspath_prepend(str(BUNDLE))
    spec=importlib.util.spec_from_file_location('t081_execution_supervisor_tests',BUNDLE/'execution_supervisor_v1.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def budget():
    return {'cpu_budget':1,'native_threads':1,'workers':1,'memory_budget_bytes':256*1024**2,
            'reserve_bytes':64*1024**2,'required_bytes':0,'diagnostics':[]}


def wait_for(predicate,seconds=15):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        value=predicate()
        if value:return value
        time.sleep(.02)
    raise AssertionError('bounded lifecycle condition was not observed')


def start_blocked(supervisor,tmp_path):
    release=tmp_path/'release';ready=tmp_path/'ready'
    program=tmp_path/'program.py'
    program.write_text("from pathlib import Path\nimport time\nfrom execution_events_v1 import emit\n"
        "def main():\n    emit('phase_started',phase='waiting_for_release',depth=1)\n"
        +f"    Path({str(ready)!r}).write_text('ready')\n"
        +f"    while not Path({str(release)!r}).exists(): time.sleep(.03)\n"
        +"    emit('work',phase='waiting_for_release',completed=1,total=1,unit='release')\n    return 0\n",encoding='utf-8')
    result={};execution=supervisor.Execution(tmp_path/'run',budget())
    def target():
        try:
            with execution:result['receipt']=execution.run('fixture',program,[],kind='fixture')
        except BaseException as error:result['error']=error
    thread=threading.Thread(target=target);thread.start()
    wait_for(lambda:ready.exists() or result.get('error'))
    assert 'error' not in result,str(result.get('error'))
    return execution,thread,result,release


def test_live_status_observes_real_worker_and_terminal_cleanup(supervisor,tmp_path):
    execution,thread,result,release=start_blocked(supervisor,tmp_path)
    try:
        status_path=tmp_path/'run/.live/run-status.json'
        def observed():
            if not status_path.exists():return None
            value=json.loads(status_path.read_bytes());operation=value.get('current_operation') or {}
            return value if operation.get('phase')=='waiting_for_release' and operation.get('resources') else None
        live=wait_for(observed)
        assert live['terminal'] is False
        assert live['current_operation']['resources']['active_process_count']>=1
        first=live['last_heartbeat_utc']
        wait_for(lambda:json.loads(status_path.read_bytes())['last_heartbeat_utc']!=first)
        release.touch();thread.join(15)
        assert not thread.is_alive()
        assert 'error' not in result,str(result.get('error'))
        assert result['receipt']['worker_cleanup_verified']
        assert result['receipt']['peak_budgeted_memory_bytes']<=budget()['memory_budget_bytes']
        final=json.loads(status_path.read_bytes())
        assert final['terminal'] and final['workflow_state']=='RUN_COMPLETED'
        events=[json.loads(line) for line in (tmp_path/'run/.live/events.jsonl').read_text().splitlines()]
        assert [x['seq'] for x in events]==list(range(1,len(events)+1))
        assert any(x['event']=='STAGE_PROGRESS' and x['detail'].get('completed')==1 for x in events)
    finally:
        release.touch();thread.join(15)


def test_cancellation_reaps_owned_worker_and_leaves_unrelated_process(supervisor,tmp_path):
    unrelated=subprocess.Popen([getattr(sys,'_base_executable',sys.executable),'-B','-c','import time;time.sleep(60)'])
    execution,thread,result,release=start_blocked(supervisor,tmp_path)
    try:
        execution.cancel();thread.join(15)
        assert not thread.is_alive()
        assert isinstance(result.get('error'),KeyboardInterrupt)
        receipt=json.loads((tmp_path/'run/fixture/receipt.json').read_bytes())
        assert receipt['worker_cleanup_verified']
        assert unrelated.poll() is None
        status=json.loads((tmp_path/'run/.live/run-status.json').read_bytes())
        assert status['terminal'] and status['workflow_state']=='RUN_INTERRUPTED'
    finally:
        release.touch();thread.join(15);unrelated.kill();unrelated.wait()


def test_real_failure_retains_error_logs_and_does_not_publish_success(supervisor,tmp_path):
    program=tmp_path/'bad.py';program.write_text("def main():\n    raise RuntimeError('deliberate stage failure')\n",encoding='utf-8')
    with pytest.raises(RuntimeError,match='fixture exited'):
        with supervisor.Execution(tmp_path/'run',budget()) as execution:
            execution.run('fixture',program,[],kind='fixture')
    receipt=json.loads((tmp_path/'run/fixture/receipt.json').read_bytes())
    assert receipt['exit_code']!=0 and receipt['worker_cleanup_verified']
    assert 'deliberate stage failure' in (tmp_path/'run/fixture/stderr.txt').read_text()
    status=json.loads((tmp_path/'run/.live/run-status.json').read_bytes())
    assert status['terminal'] and status['workflow_state']=='RUN_FAILED'
    assert not (tmp_path/'run/qualification.json').exists()


@pytest.mark.skipif(sys.platform!='win32',reason='owned Windows attachment failure')
def test_attachment_failure_never_releases_math_or_leaves_worker(supervisor,tmp_path,monkeypatch):
    marker=tmp_path/'math-executed'
    program=tmp_path/'never.py'
    program.write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('bad')\ndef main(): return 0\n",encoding='utf-8')
    def denied(self,pid):
        raise RuntimeError('deliberate attachment failure')
    monkeypatch.setattr(supervisor.WindowsJob,'attach_worker_pid',denied)
    with pytest.raises(RuntimeError,match='deliberate attachment failure'):
        with supervisor.Execution(tmp_path/'run',budget()) as execution:
            execution.run('fixture',program,[],kind='fixture')
    receipt=json.loads((tmp_path/'run/fixture/receipt.json').read_bytes())
    assert receipt['worker_cleanup_verified']
    assert not marker.exists()


def test_real_cli_rejects_insufficient_memory_before_creating_outputs(tmp_path):
    output=tmp_path/'not-started'
    command=[sys.executable,'-B',str(BUNDLE/'run-execution-v1.py'),'--output-dir',str(output),
             '--memory-mib','1','--reserve-mib','0']
    result=subprocess.run(command,capture_output=True,text=True)
    assert result.returncode!=0
    assert 'N and precision will not be reduced' in result.stderr
    assert not output.exists()


@pytest.mark.parametrize('fails',[False,True])
def test_worker_exit_reaps_descendant_holding_log_pipe(supervisor,tmp_path,fails):
    program=tmp_path/'orphan.py'
    program.write_text("import subprocess,sys\n"
        "def main():\n"
        "    subprocess.Popen([sys.executable,'-B','-c','import time;time.sleep(60)'])\n"
        +("    raise RuntimeError('worker failed with live descendant')\n" if fails else "    return 0\n"),
        encoding='utf-8')
    result={}
    def run():
        try:
            with supervisor.Execution(tmp_path/'run',budget()) as execution:
                result['receipt']=execution.run('fixture',program,[],kind='fixture')
        except BaseException as error:result['error']=error
    thread=threading.Thread(target=run);thread.start();thread.join(15)
    assert not thread.is_alive(),'worker exit must reap descendants before waiting for pipe EOF'
    receipt=json.loads((tmp_path/'run/fixture/receipt.json').read_bytes())
    assert receipt['worker_cleanup_verified']
    if fails:assert isinstance(result.get('error'),RuntimeError)
    else:assert 'error' not in result


def test_worker_applies_selected_threads_after_legacy_module_initialization(supervisor,tmp_path):
    program=tmp_path/'legacy_init.py'
    program.write_text("from flint import ctx\nctx.threads=2\n"
        "def main():\n    assert ctx.threads==1,'module initialization overrode selected thread budget'\n    return 0\n",
        encoding='utf-8')
    with supervisor.Execution(tmp_path/'run',budget()) as execution:
        receipt=execution.run('fixture',program,[],kind='fixture')
    assert receipt['worker_cleanup_verified']
    profile=json.loads((tmp_path/'run/fixture/profile.json').read_bytes())
    assert profile['native_threads']==1
