"""Preserve executable/scalar/test/environment inputs for metadata corrections."""
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source.contract import bind_problem
from scripts.whole_source.retention import capture_inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--origin-commit', required=True)
    parser.add_argument('--extra', type=Path, action='append', default=[])
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.relative_to(ROOT)
    output.mkdir(parents=True, exist_ok=False)
    capture_inputs(bind_problem('retained-t081'), output/'runtime')
    names = {p.relative_to(ROOT).as_posix() for p in (ROOT/'tests').glob('test_whole_source_*.py')}
    names.update(('pyproject.toml', 'uv.lock', Path(__file__).relative_to(ROOT).as_posix()))
    for path in args.extra:
        names.add(path.resolve().relative_to(ROOT).as_posix())
    for name in sorted(names):
        target = output/'additional'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT/name).read_bytes())
    for name in ('pyproject.toml', 'uv.lock'):
        (output/'runtime'/name).write_bytes((ROOT/name).read_bytes())
    files = [{'path':p.relative_to(output).as_posix(), 'size':p.stat().st_size,
              'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
             for p in sorted(output.rglob('*')) if p.is_file()]
    document = {'format':'metadata-correction-preservation-v1',
        'created_utc':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'origin_git_commit':args.origin_commit, 'origin_git_dirty':True,
        'environment':{'python':sys.version, 'packages':{name:importlib.metadata.version(name)
            for name in ('python-flint','numpy','scipy','pytest')}},
        'files':files,
        'reproduction':'Use runtime/ with its recorded lockfiles and additional tests/procedures in a fresh directory. Original historical outputs and failed runs remain unchanged.'}
    (output/'preservation.json').write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(output), 'preserved_files':len(files)}))


if __name__ == '__main__':
    main()
