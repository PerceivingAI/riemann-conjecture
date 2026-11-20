"""Preserve executed bounded qualification code and original historical byte identities."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
METHODS=Path(__file__).resolve().parent


def sha(raw): return hashlib.sha256(raw).hexdigest()


def put(root,name,raw):
    path=root/name
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_bytes()==raw,name
    else:
        with path.open('xb') as stream: stream.write(raw)
    return {'path':name,'sha256':sha(raw),'size':len(raw)}


def main():
    from scripts.whole_source.contract import bind_problem,canonical_bytes
    from scripts.whole_source.retention import capture_inputs
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    output=args.output_dir.resolve()
    output.relative_to(ROOT)
    assert not output.exists(),'preservation destination must be fresh'
    captured=capture_inputs(bind_problem('retained-t081'),output)
    previous=METHODS/'data/lifecycle-supervision-code-v2'
    old=json.loads((previous/'preservation-manifest.json').read_bytes())
    names=sorted(set(['.gitattributes','scripts/README.md','pyproject.toml','uv.lock',
        'conftest.py','scripts/test_report_privacy.py','tests/test_report_privacy.py',
        *(p.relative_to(ROOT).as_posix() for p in (ROOT/'tests').glob('test_whole_source*.py')),
        *(r['path'] for r in old['extra_files']),
        *(p.relative_to(ROOT).as_posix() for p in METHODS.glob('integrated-qualification-*.py'))]))
    extra=[put(output,name,(ROOT/name).read_bytes()) for name in names]
    historical=[]
    for folder in ('resource-admission-code-v1','lifecycle-supervision-code-v1','lifecycle-supervision-code-v2'):
        base=METHODS/'data'/folder
        manifest=json.loads((base/'capture-manifest.json').read_bytes())
        preservation=json.loads((base/'preservation-manifest.json').read_bytes())
        refs=[row['artifact'] for row in manifest['files']]+preservation['extra_files']
        for ref in refs:
            raw=(base/ref['path']).read_bytes()
            assert len(raw)==ref['size'] and sha(raw)==ref['sha256'],str(base/ref['path'])
        historical.append({'directory':base.relative_to(ROOT).as_posix(),'references':len(refs),'mismatches':0})
    # Raw failed invocation code remains reproducible even before any numerical
    # stage existed. Each overlay is checked against that invocation's digest.
    old_supervision=(previous/'scripts/whole_source/supervision.py').read_bytes()
    page_fixed=old_supervision.replace(b'    memory = available-reserve-guardian_growth\n',
        b'    # Windows rounds job memory to pages. Install an exact lower MiB ceiling.\n'
        b'    memory = ((available-reserve-guardian_growth)//MIB)*MIB\n')
    candidates={}
    def offer(name,raw): candidates[(name,sha(raw))]=raw
    for name in names:
        offer(name,(ROOT/name).read_bytes())
    for row in captured['files']:
        name=row['artifact']['path'];offer(name,(output/name).read_bytes())
    for path in previous.rglob('*.py'):
        offer(path.relative_to(previous).as_posix(),path.read_bytes())
    offer('scripts/whole_source/supervision.py',page_fixed)
    for runtime in (METHODS/'data/integrated-qualification-owned-v3/operation').glob('source/producer/attempts/*/runtime'):
        for path in runtime.rglob('*.py'): offer(path.relative_to(runtime).as_posix(),path.read_bytes())
    development=[]
    for folder in ('integrated-qualification-owned-v1','integrated-qualification-owned-v2',
                   'integrated-qualification-owned-v3','integrated-qualification-owned-v4'):
        root=METHODS/'data'/folder/'operation.lifecycle'
        refs=[]
        for receipt_path in sorted((root/'receipts').glob('*.json')):
            receipt=json.loads(receipt_path.read_bytes())
            for name,digest in receipt['code'].items():
                raw=candidates[(name,digest)]
                ref=put(output,'executed-development/'+digest+'/'+name,raw)
                refs.append({'invocation_id':receipt['invocation_id'],'source_path':name,'artifact':ref})
        development.append({'directory':folder,'files':refs})
    for ref in [row['artifact'] for row in captured['files']]+extra:
        raw=(output/ref['path']).read_bytes()
        assert len(raw)==ref['size'] and sha(raw)==ref['sha256'],ref['path']
    report={'format':'whole-source-integrated-local-qualification-preservation-v1',
        'created_utc':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'captured_files':len(captured['files']),'extra_files':extra,
        'historical_verified':historical,'executed_development_code':development,
        'scope':'CODE_AND_INPUT_PRESERVATION_ONLY','numerical_work':False,
        'scientific_acceptance':False,'production_admission':False}
    put(output,'preservation-manifest.json',canonical_bytes(report))
    print(json.dumps({'captured_files':report['captured_files'],'extra_files':len(extra),
                      'historical_verified':historical,'scope':report['scope']}))


if __name__=='__main__': main()
