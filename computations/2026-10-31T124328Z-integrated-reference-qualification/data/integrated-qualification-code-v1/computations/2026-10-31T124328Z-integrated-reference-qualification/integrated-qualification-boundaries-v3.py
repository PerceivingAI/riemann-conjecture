"""Real CLI/admission/guardian with explicitly synthetic coordinator role outputs.

The role adapter and phase validator below are TEST_ONLY_NONAPPROVAL. They cannot
qualify mathematical source, replay, implementation review or final assessment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
import threading
import time
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
ORIGIN='a06cb9a74da776b71aa0113a81ccff30dc8a81f0'
SCOPE='TEST_ONLY_SYNTHETIC_COORDINATOR_NONAPPROVAL'


def save(path,value):
    from scripts.whole_source.contract import canonical_bytes
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream: stream.write(canonical_bytes(value))


def child(action,base):
    from scripts.weil_whole_source_split import main as cli
    from scripts.whole_source import retention, selection
    from scripts.whole_source.contract import canonical_bytes
    from scripts.whole_source.coordinator import read_phase_records
    base=Path(base)
    run=base/'operation'
    calls=[]
    def dispatch(phase,directory,prior,*args,**kwargs):
        calls.append({'phase':phase,'directory':str(directory)})
        directory.mkdir(parents=True,exist_ok=True)
        if action=='interrupt-proposal' and phase=='proposal':
            save(base/'proposal-interruption-ready.json', {'scope':SCOPE})
            time.sleep(60)
            raise AssertionError('control interruption was not delivered')
        if action=='failed-audit' and phase=='audit':
            save(directory/'failed-control.json',{'scope':SCOPE,'phase':phase})
            raise RuntimeError('CONTROL nonresumable adapter failure')
        names={'prepare':('source-inputs/problem.json','source-inputs/execution.json','premises/premises-receipt.json'),
            'source':('producer/source-manifest.json','producer/source-execution.json'),
            'audit':('analytical-receipt.json','audit-execution.json'),
            'proposal':('work/proposal.json',)}
        for name in names[phase]:
            save(directory/name,{'scope':SCOPE,'phase':phase})
    def validate(phase,outputs,directory,**kwargs):
        assert outputs==retention._phase_outputs(phase,directory)
        assert all(retention._document(ref)=={'scope':SCOPE,'phase':phase} for ref in outputs.values())
    through='source' if action=='stop-source' else 'audit' if action in ('failed-audit','retry-audit') else 'proposal'
    argv=['run','--problem',str(base/'inputs/problem.json'),'--execution',str(base/'inputs/execution.json'),
        '--output-dir',str(run),'--through',through]
    if action!='stop-source': argv.append('--resume')
    with patch.object(retention,'_dispatch_phase',dispatch), patch.object(selection,'validate_phase',validate):
        result=cli(argv)
    selected=read_phase_records(run)
    save(base/(action+'-outcome.json'),{'scope':SCOPE,'returncode':result,'argv':argv,
        'calls':calls,'selected':selected,'scientific_acceptance':False})
    if action=='failed-audit': assert result==2
    else: assert result==0


def main():
    from scripts.whole_source import retention, supervision as s
    from scripts.whole_source.contract import bind_problem
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    base=args.output_dir.resolve()
    base.relative_to(ROOT)
    base.mkdir(parents=True,exist_ok=False)
    retention.prepare_inputs(bind_problem('retained-t081'),base/'inputs',origin_git_commit=ORIGIN,origin_git_dirty=True)
    settings={'format':s.POLICY,'wall_seconds':45,'active_seconds':300,'grace_seconds':2,
        'memory_mib':None,'sample_milliseconds':500,'stale_milliseconds':5000,'observation_bytes':16*s.MIB}
    save(base/'policy.json',settings)
    rows=[]
    script=Path(__file__).resolve()
    sha=hashlib.sha256(script.read_bytes()).hexdigest()
    for action in ('stop-source','failed-audit','retry-audit','interrupt-proposal','continue-proposal'):
        wrapper=base/(action+'-child.py')
        wrapper.write_text('from pathlib import Path\nimport hashlib,runpy\n'
            f'p=Path({str(script)!r})\nassert hashlib.sha256(p.read_bytes()).hexdigest()=={sha!r}\n'
            f'runpy.run_path(str(p))["child"]({action!r},{str(base)!r})\n',encoding='utf-8')
        cancel=threading.Event()
        if action=='interrupt-proposal':
            def request_cancel():
                until=time.monotonic()+30
                while not (base/'proposal-interruption-ready.json').exists() and time.monotonic()<until:
                    time.sleep(.05)
                cancel.set()
            thread=threading.Thread(target=request_cancel,daemon=True)
            thread.start()
        receipt=s.supervise([],observation_root=base/'operation.lifecycle',operation_root=base/'operation',
            policy_document=settings,script=wrapper,cancel_event=cancel)
        if action=='interrupt-proposal': thread.join(1)
        outcome_path=base/(action+'-outcome.json')
        outcome=json.loads(outcome_path.read_bytes()) if outcome_path.exists() else None
        row={'action':action,'receipt':receipt,'outcome':outcome}
        rows.append(row)
        save(base/(action+'-check.json'),row)
        if action=='interrupt-proposal':
            from scripts.whole_source.coordinator import read_phase_records
            assert receipt['status']=='INTERRUPTED' and receipt['reason']=='explicit_cancel',row
            assert receipt['cleanup_verified'] and receipt['final_job']['active_process_ids']==[]
            selected=read_phase_records(base/'operation')
            assert selected['source']==original and 'proposal' not in selected
            print(json.dumps({'action':action,'guardian_status':receipt['status'],'scope':SCOPE}),flush=True)
            continue
        assert receipt['status']=='COMPLETED' and receipt['cleanup_verified'] and outcome is not None,row
        assert not (base/'operation/pipeline-result.json').exists()
        assert not (base/'operation/exact-inputs').exists()
        if action=='stop-source':
            original=outcome['selected']['source']
            assert [r['phase'] for r in outcome['calls']]==['prepare','source']
        else:
            assert outcome['selected']['source']==original
        if action=='failed-audit':
            assert outcome['calls'] and outcome['calls'][0]['phase']=='audit', row
            failed=Path(outcome['calls'][0]['directory'])/'failed-control.json'
            failed_raw=failed.read_bytes()
        if action=='retry-audit':
            assert outcome['calls'][0]['directory']!=str(failed.parent)
            assert failed.read_bytes()==failed_raw
        print(json.dumps({'action':action,'cli_returncode':outcome['returncode'],
                          'guardian_status':receipt['status'],'scope':SCOPE}),flush=True)
    save(base/'qualification.json',{'format':'whole-source-coordinator-software-qualification-v3',
        'scope':SCOPE,'status':'PASS_SYNTHETIC_COORDINATOR_WITH_REAL_CONTAINMENT_ONLY',
        'cases':rows,'original_source_preserved':True,'failed_attempt_preserved':True,
        'full_qualification':False,'scientific_acceptance':False,'production_admission':False})


if __name__=='__main__': main()
