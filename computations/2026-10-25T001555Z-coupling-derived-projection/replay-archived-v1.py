"""Replay the retained-data projection using captured code and exact inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

BUNDLE = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifests = {directory: json.loads((BUNDLE/directory/'manifest.json').read_bytes())
                 for directory in ('source-v1', 'inputs')}
    with tempfile.TemporaryDirectory(prefix='rh-coupling-projection-v1-') as temporary:
        isolated = Path(temporary)
        for directory, manifest in manifests.items():
            for relative, expected in manifest.items():
                raw = (BUNDLE/directory/relative).read_bytes()
                if hashlib.sha256(raw).hexdigest() != expected:
                    raise ValueError('captured bytes changed: '+relative)
                target = isolated/relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
        launch = (
            "import pathlib,runpy,sys; root=pathlib.Path(sys.argv[1]).resolve(); "
            "module=sys.argv[2]; sys.path.insert(0,str(root)); sys.argv=[module]+sys.argv[3:]; "
            "runpy.run_module(module,run_name='__main__'); "
            "loaded=[pathlib.Path(m.__file__).resolve() for name,m in sys.modules.items() "
            "if name.startswith('scripts.') and getattr(m,'__file__',None)]; "
            "assert loaded and all(p.is_relative_to(root) for p in loaded),loaded"
        )
        report = BUNDLE/'data/projection-v1.json'
        commands = (
            ('exact-replay', 'scripts.weil_coupling_projection',
             ['replay', '--result', str(report), '--output', str(output/'exact-replay.json')]),
            ('native-audit', 'scripts.verify_coupling_projection',
             [str(report), '--output', str(output/'native-audit.json')]),
        )
        for label, module, arguments in commands:
            completed = subprocess.run([sys.executable, '-I', '-c', launch, str(isolated), module, *arguments],
                                       cwd=isolated, capture_output=True, check=False)
            (output/f'{label}.stdout.txt').write_bytes(completed.stdout)
            (output/f'{label}.stderr.txt').write_bytes(completed.stderr)
            if completed.returncode:
                raise RuntimeError(f'isolated {label} failed: exit {completed.returncode}')
        original = json.loads((BUNDLE/'data/projection-audit-v1.json').read_bytes())
        replayed = json.loads((output/'native-audit.json').read_bytes())
        original.pop('elapsed_seconds'); replayed.pop('elapsed_seconds')
        if original != replayed:
            raise ValueError('independent archived consequence differs')
        if (output/'exact-replay.json').read_bytes() != (BUNDLE/'data/projection-replay-v1.json').read_bytes():
            raise ValueError('archived exact replay receipt differs')
        receipt = {'status': 'ARCHIVED_PROJECTION_REPLAY_PASS',
                   'source_files': len(manifests['source-v1']), 'input_files': len(manifests['inputs']),
                   'live_script_imports': False, 'audit_all_fields_equal_except': ['elapsed_seconds'],
                   'exact_replay_receipt_byte_identical': True,
                   'report_sha256': hashlib.sha256(report.read_bytes()).hexdigest(),
                   'selected_projection': replayed['selected_projection'],
                   'scope': 'Only the original P16 compression is certified, not all P_L.'}
        (output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
        print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
