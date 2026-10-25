"""Regenerate from captured scripts and replay the original fixed-reference proof."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

BUNDLE = Path(__file__).resolve().parent
BASELINE = 'computations/2026-10-24T191616Z-weighted-support-extension/data/selection-v1.json'
PRIOR_SCALARS = 'computations/2026-10-24T224948Z-tail-restricted-residual/data/scalars-v1.json'


def decode(path: Path) -> dict:
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = decode(BUNDLE/'source-v1/manifest.json')
    with tempfile.TemporaryDirectory(prefix='rh-tail-matrix-v1-') as temporary:
        isolated = Path(temporary)
        for relative, expected in manifest.items():
            raw = (BUNDLE/'source-v1'/relative).read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError('captured source changed: '+relative)
            target = isolated/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        for relative, source in ((BASELINE, 'baseline-selection-v1.json'), (PRIOR_SCALARS, 'prior-scalars-v1.json')):
            target = isolated/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(BUNDLE/'data'/source, target)
        diagnostic = isolated/'computations'/BUNDLE.name/'residual-only-limit-v1.py'
        diagnostic.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(BUNDLE/'residual-only-limit-v1.py', diagnostic)
        wrapper = (
            "import pathlib,runpy,sys; root=pathlib.Path(sys.argv[1]).resolve(); "
            "mode,target=sys.argv[2:4]; sys.path.insert(0,str(root)); sys.argv=[target]+sys.argv[4:]; "
            "runpy.run_path(target,run_name='__main__') if mode=='path' else runpy.run_module(target,run_name='__main__'); "
            "loaded=[pathlib.Path(m.__file__).resolve() for name,m in sys.modules.items() "
            "if name.startswith('scripts.') and getattr(m,'__file__',None)]; "
            "assert loaded and all(p.is_relative_to(root) for p in loaded),loaded"
        )
        packet, audit, result = [BUNDLE/'data'/name for name in (
            'source-m54-v1.json.gz', 'audit-m54-v1.json.gz', 'result-m54-v1.json')]
        operations = (
            ('source', 'module', 'scripts.weil_tail_complement_assessment',
             ['generate', '--boundary', '54', '--output', str(output/'source-regenerated.json.gz')]),
            ('audit', 'module', 'scripts.verify_tail_complement_inputs',
             [str(packet), '--output', str(output/'audit-regenerated.json.gz')]),
            ('exact-replay', 'module', 'scripts.weil_tail_complement_assessment',
             ['replay', '--packet', str(packet), '--audit', str(audit), '--result', str(result),
              '--output', str(output/'exact-replay.json')]),
            ('residual-only-limit', 'path', str(diagnostic),
             ['--packet', str(packet), '--audit', str(audit), '--result', str(result),
              '--output', str(output/'residual-only-limit.json')]),
        )
        for label, mode, target, arguments in operations:
            completed = subprocess.run([sys.executable, '-I', '-c', wrapper, str(isolated), mode, target, *arguments],
                                       cwd=isolated, capture_output=True, check=False)
            (output/f'{label}.stdout.txt').write_bytes(completed.stdout)
            (output/f'{label}.stderr.txt').write_bytes(completed.stderr)
            if completed.returncode:
                raise RuntimeError(f'isolated {label} failed: exit {completed.returncode}')
        for original, regenerated in ((packet, output/'source-regenerated.json.gz'), (audit, output/'audit-regenerated.json.gz')):
            left, right = decode(original), decode(regenerated)
            left.pop('elapsed_seconds'); right.pop('elapsed_seconds')
            if left != right:
                raise ValueError('regenerated mathematical/source data differ: '+original.name)
        if (output/'residual-only-limit.json').read_bytes() != (BUNDLE/'data/residual-only-limit-v1.json').read_bytes():
            raise ValueError('optimistic control bytes differ')
        receipt = {
            'status': 'ARCHIVED_REGENERATION_AND_EXACT_REPLAY_PASS',
            'captured_files': len(manifest), 'live_script_imports': False,
            'source_and_audit_all_fields_equal_except': ['elapsed_seconds'],
            'optimistic_control_byte_identical': True,
            'original_sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (packet, audit, result)},
        }
        (output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
        print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
