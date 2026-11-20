"""Relocate retained evidence and replay ONLY its stdlib qualifier, not arithmetic."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    expected = (HERE/'data/qualification-v2.json').read_bytes()
    bindings = json.loads((HERE/'probe-inputs-v1.json').read_bytes())['bindings']
    copied = 0
    with tempfile.TemporaryDirectory(prefix='t1-evidence-replay-',dir=ROOT) as owned:
        temporary = Path(owned)
        relocated = temporary/HERE.relative_to(ROOT)
        for source in HERE.rglob('*'):
            if not source.is_file() or '__pycache__' in source.parts:
                continue
            relative = source.relative_to(HERE)
            if relative in (Path('data/qualification-v1.json'),Path('data/qualification-v2.json')):
                continue
            destination = relocated/relative
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,destination)
            copied += 1
        for binding in bindings.values():
            source = ROOT/binding['path']
            raw = source.read_bytes()
            assert hashlib.sha256(raw).hexdigest() == binding['sha256']
            destination = temporary/binding['path']
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(raw)
            copied += 1
        result_path = relocated/'data/relocated-qualification.json'
        command = [sys.executable,'-B',str(relocated/'qualify-measurements-v2.py'),'--output',str(result_path)]
        run = subprocess.run(command,cwd=temporary,capture_output=True,text=True,encoding='utf-8')
        assert run.returncode == 0,(run.stdout,run.stderr)
        actual = result_path.read_bytes()
        assert actual == expected,'relocated evidence qualification differs'
    assert not temporary.exists()
    result = {'format':'t1-relocated-evidence-qualification-replay-v1',
        'status':'PASS_BYTE_IDENTICAL_EVIDENCE_QUALIFICATION',
        'scope':'Only retained evidence qualification is replayed. No matrix, scalar mathematical proof or native arithmetic is rerun.',
        'copied_files':copied,'withheld_expected_qualification_reports':2,
        'qualification_sha256':hashlib.sha256(actual).hexdigest(),
        'program_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr,
        'owned_temporary_tree_removed':True,'target_positivity_proved':False,'production_admission':False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'copied_files':copied,'owned_temporary_tree_removed':True}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
