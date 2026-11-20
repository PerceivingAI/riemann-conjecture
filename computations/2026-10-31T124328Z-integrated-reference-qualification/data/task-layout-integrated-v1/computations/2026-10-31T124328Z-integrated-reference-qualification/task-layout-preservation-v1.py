"""Preserve executable, scalar, test and environment inputs in a fresh tree."""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    from scripts.whole_source.contract import bind_problem, canonical_bytes
    from scripts.whole_source.retention import capture_inputs
    target = args.output_dir.resolve()
    result = capture_inputs(bind_problem('retained-t081'), target)
    rows = []
    paths = sorted(set([*ROOT.glob('tests/test_whole_source*.py'),
                       *ROOT.glob('computations/2026-10-31T124328Z-integrated-reference-qualification/*-v*.py'),
                       ROOT/'pyproject.toml', ROOT/'uv.lock']))
    captured = {row['artifact']['path'] for row in result['files']}
    for path in paths:
        name = path.relative_to(ROOT).as_posix()
        if name in captured:
            continue
        raw = path.read_bytes()
        destination = target/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as stream:
            stream.write(raw)
        rows.append({'path': name, 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    environment = {'python': sys.version, 'platform': platform.platform(),
                   'packages': {name: importlib.metadata.version(name) for name in
                                ('python-flint', 'numpy', 'scipy', 'pytest')}}
    with (target/'preservation-environment.json').open('xb') as stream:
        stream.write(canonical_bytes(environment))
    raw = (target/'capture-manifest.json').read_bytes()
    report = {'format': 'task-layout-preservation-v1', 'capture_sha256': hashlib.sha256(raw).hexdigest(),
              'extra_files': rows, 'environment': environment, 'expected_new_outputs_installed': False}
    with (target/'preservation-manifest.json').open('xb') as stream:
        stream.write(canonical_bytes(report))
    print(json.dumps({'directory': str(target), 'captured': len(result['files']), 'extra': len(rows)}))


if __name__ == '__main__':
    main()
