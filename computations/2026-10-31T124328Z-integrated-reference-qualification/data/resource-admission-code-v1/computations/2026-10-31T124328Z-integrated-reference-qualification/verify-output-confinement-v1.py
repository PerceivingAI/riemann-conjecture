"""Disposable metadata publication probe, not scientific acceptance."""

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import hashlib
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.whole_source import retention as r, pipeline
from scripts.whole_source.contract import ROOT, canonical_bytes, ContractError
class StopAfterOrigin(Exception): pass
with TemporaryDirectory(prefix='output-confinement-', dir=ROOT/'.pytest_cache') as temp:
    root=Path(temp)
    run=root/'run'; other=root/'other-sealed'
    for directory in (run,other): directory.mkdir()
    def put(path, value):
        path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(canonical_bytes(value))
    ref={'directory':str(run),'artifact':{'path':'placeholder.json','size':2,'sha256':hashlib.sha256(b'{}').hexdigest()}}
    put(run/'pipeline-result.json',{'problem':ref,'source_execution':ref})
    for name in ('review-decision.json','controls/controls-receipt.json','replay/replay-receipt.json','implementation.json','origin.json'):
        put(run/name,{})
    put(other/'science.json',{'fixture':'metadata only'})
    review={'implementation':{'directory':str(run),'artifact':{'path':'implementation.json'}}}
    spec=SimpleNamespace(code_refs=(),bounds={},quantities=(),partition=None,backend_version="fixture",native_threads=1,collection_id="fixture")
    plan=SimpleNamespace(codec_mib=1,workers=1,resource_policy=None,reserve_mib=1,provenance=SimpleNamespace(path=(run/'origin.json').relative_to(ROOT).as_posix()))
    r._seal(run); r._seal(other)
    print('before:',r.verify_inventory(run)['status'],r.verify_inventory(other)['status'])
    before={p.relative_to(run).as_posix():p.read_bytes() for p in run.rglob('*') if p.is_file()}
    with patch.object(pipeline,'_bind',return_value=(None,None,{'analytic':(spec,plan)})), patch.object(r,'_validate_review',return_value=review), patch.object(r,'_implementation_code',return_value=([],{'path':'scripts/whole_source/retention.py'},{})), patch.object(r.CollectionSpec,'create',return_value=spec), patch.object(r,'replace',side_effect=StopAfterOrigin):
        for name,output in [('same-run',run/'another-assessment'),('normalized-same-run',run/'x'/'..'/'normalized'),('sibling',root/'assessment'),('other-sealed',other/'assessment')]:
            try: r.accept(run,output,code_root=ROOT)
            except ContractError as exc: verdict=str(exc)
            except StopAfterOrigin: verdict='reached real assessment-origin publication; stopped before plan/worker'
            if name != 'sibling':
                assert not output.resolve().exists()
            else:
                assert (output/'assessment-origin.json').is_file()
            print(name,':',verdict,'origin_exists=',(output/'assessment-origin.json').is_file())
    after={p.relative_to(run).as_posix():p.read_bytes() for p in run.rglob('*') if p.is_file() and p.name!='.slice.lock'}
    assert before == after
    print('assessed-run-original-bytes-unchanged:',before==after)
    print('assessed-run-after:',r.verify_inventory(run)['status'])
    try: print('other-sealed-after:',r.verify_inventory(other)['status'])
    except ContractError:
        raise AssertionError('sealed destination inventory changed')
print('temporary-fixtures-removed:',not root.exists())
