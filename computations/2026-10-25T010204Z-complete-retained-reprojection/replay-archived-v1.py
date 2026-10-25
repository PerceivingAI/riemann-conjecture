"""Restore captured complete-reference code and exact retained inputs in isolation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

BUNDLE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifests = {name: json.loads((BUNDLE/name/'manifest.json').read_bytes())
                 for name in ('source-v1', 'inputs')}
    with tempfile.TemporaryDirectory(prefix='rh-complete-reference-v1-') as temporary:
        isolated = Path(temporary)
        for name, manifest in manifests.items():
            for relative, expected in manifest.items():
                raw = (BUNDLE/name/relative).read_bytes()
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
        origin = BUNDLE/'data/original-v2-gate-v1.json'
        report = BUNDLE/'data/complete-reference-v1.json'
        commands = (
            ('original-version-gate', 'scripts.weil_complete_reprojection',
             ['origin', '--output', str(output/'original-version-gate.json')]),
            ('exact-replay', 'scripts.weil_complete_reprojection',
             ['replay', '--origin', str(origin), '--result', str(report), '--output', str(output/'exact-replay.json')]),
            ('native-audit', 'scripts.verify_complete_reprojection',
             [str(report), '--origin', str(origin), '--output', str(output/'native-audit.json')]),
        )
        for label, module, arguments in commands:
            completed = subprocess.run([sys.executable, '-I', '-c', launch, str(isolated), module, *arguments],
                                       cwd=isolated, capture_output=True)
            (output/f'{label}.stdout.txt').write_bytes(completed.stdout)
            (output/f'{label}.stderr.txt').write_bytes(completed.stderr)
            if completed.returncode:
                raise RuntimeError(f'isolated {label} failed: exit {completed.returncode}')
        gate_old = json.loads(origin.read_bytes())
        gate_new = json.loads((output/'original-version-gate.json').read_bytes())
        for field in ('steps', 'elapsed_seconds'):
            gate_old.pop(field); gate_new.pop(field)
        if gate_old != gate_new:
            raise ValueError('original-version acceptance fields differ')
        audit_old = json.loads((BUNDLE/'data/independent-audit-v1.json').read_bytes())
        audit_new = json.loads((output/'native-audit.json').read_bytes())
        audit_old.pop('elapsed_seconds'); audit_new.pop('elapsed_seconds')
        if audit_old != audit_new:
            raise ValueError('independent complete consequence differs')
        if (output/'exact-replay.json').read_bytes() != (BUNDLE/'data/exact-replay-v1.json').read_bytes():
            raise ValueError('exact replay receipt differs')
        receipt = {'status': 'ARCHIVED_COMPLETE_REFERENCE_REPLAY_PASS',
                   'source_files': len(manifests['source-v1']), 'input_files': len(manifests['inputs']),
                   'live_script_imports': False, 'original_gate_bindings_equal': True,
                   'audit_all_fields_equal_except': ['elapsed_seconds'],
                   'exact_replay_receipt_byte_identical': True,
                   'report_sha256': hashlib.sha256(report.read_bytes()).hexdigest(),
                   'selected_status': audit_new['selected_status'],
                   'scope': 'Retained-input complete P20 research consequence, not fresh analytical acceptance or admission.'}
        (output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
        print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
