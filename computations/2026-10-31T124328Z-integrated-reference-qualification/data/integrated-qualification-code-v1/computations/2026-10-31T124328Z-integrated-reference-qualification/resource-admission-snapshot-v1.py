"""Preserve current resource-admission code and inputs, without running science."""
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    from scripts.whole_source.contract import bind_problem, canonical_bytes
    from scripts.whole_source.retention import capture_inputs
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.relative_to(ROOT)
    if output.exists():
        raise FileExistsError('snapshot destination must be fresh')
    manifest = capture_inputs(bind_problem('retained-t081'), output)
    previous = ROOT/'computations/2026-10-31T124328Z-integrated-reference-qualification/data/phase-coordinator-code-v1/preservation-manifest.json'
    preserved = json.loads(previous.read_bytes())
    extras = [
        'pyproject.toml', 'uv.lock', 'scripts/README.md',
        previous.relative_to(ROOT).as_posix(),
        *(path.relative_to(ROOT).as_posix() for path in (ROOT/'tests').glob('test_whole_source*.py')),
        *(row['path'] for row in preserved['extra_files']),
        *('computations/2026-10-31T124328Z-integrated-reference-qualification/'+name for name in (
            'compare-execution-v1.py', 'compare-execution-v2.py', 'compare-execution-v3.py',
            'phase-coordinator-snapshot-v1.py', 'resource-admission-snapshot-v1.py',
            'resource-admission-inspect-v1.py')),
    ]
    records = []
    for name in sorted(set(extras)):
        raw = (ROOT/name).read_bytes()
        target = output/name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.read_bytes() != raw:
                raise ValueError('conflicting preserved input: '+name)
        else:
            with target.open('xb') as stream:
                stream.write(raw)
        records.append({'path': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'size': len(raw)})
    refs = [row['artifact'] for row in manifest['files']] + records
    for ref in refs:
        raw = (output/ref['path']).read_bytes()
        if len(raw) != ref['size'] or hashlib.sha256(raw).hexdigest() != ref['sha256']:
            raise ValueError('snapshot bytes differ: '+ref['path'])
    report = {'format': 'whole-source-resource-code-preservation-v1',
        'created_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'capture_manifest_sha256': hashlib.sha256((output/'capture-manifest.json').read_bytes()).hexdigest(),
        'captured_files': len(manifest['files']), 'extra_files': records,
        'python': sys.version, 'packages': {name: importlib.metadata.version(name)
            for name in ('python-flint', 'numpy', 'scipy', 'pytest')},
        'scope': 'CODE_AND_INPUT_PRESERVATION_ONLY', 'numerical_work': False,
        'scientific_acceptance': False, 'production_admission': False}
    with (output/'preservation-manifest.json').open('xb') as stream:
        stream.write(canonical_bytes(report))
    print(json.dumps({'captured_files': report['captured_files'], 'extra_files': len(records),
                      'scope': report['scope']}))


if __name__ == '__main__':
    main()
