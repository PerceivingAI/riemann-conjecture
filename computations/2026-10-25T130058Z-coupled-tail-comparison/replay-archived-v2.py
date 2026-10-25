"""Replay coupled-tail consequences using captured code and exact retained inputs."""
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
                 for name in ('source-v2', 'inputs')}
    with tempfile.TemporaryDirectory(prefix='rh-coupled-tail-v2-') as temporary:
        isolated = Path(temporary)
        for name, manifest in manifests.items():
            for relative, expected in manifest.items():
                raw = (BUNDLE/name/relative).read_bytes()
                if hashlib.sha256(raw).hexdigest() != expected:
                    raise ValueError('captured bytes changed: '+relative)
                target = isolated/relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
        launch = '''import pathlib,runpy,sys
root=pathlib.Path(sys.argv[1]).resolve()
module=sys.argv[2]
sys.path.insert(0,str(root))
sys.argv=[module]+sys.argv[3:]
try:
    runpy.run_module(module,run_name='__main__')
except SystemExit as error:
    if error.code not in (None,0):
        raise
loaded=[pathlib.Path(m.__file__).resolve() for name,m in sys.modules.items()
        if name.startswith('scripts.') and getattr(m,'__file__',None)]
assert loaded and all(p.is_relative_to(root) for p in loaded),loaded
'''
        report = BUNDLE/'data/comparison-v1.json'
        commands = (
            ('exact-replay', 'scripts.weil_coupled_tail_comparison',
             ['replay', '--result', str(report), '--output', str(output/'exact-replay.json')]),
            ('independent-audit', 'scripts.verify_coupled_tail_comparison',
             [str(report), '--output', str(output/'independent-audit.json')]),
        )
        for label, module, arguments in commands:
            done = subprocess.run([sys.executable, '-I', '-c', launch, str(isolated), module, *arguments],
                                  cwd=isolated, capture_output=True)
            (output/f'{label}.stdout.txt').write_bytes(done.stdout)
            (output/f'{label}.stderr.txt').write_bytes(done.stderr)
            if done.returncode:
                raise RuntimeError(f'isolated {label} failed: exit {done.returncode}')
        old = json.loads((BUNDLE/'data/independent-audit-v1.json').read_bytes())
        new = json.loads((output/'independent-audit.json').read_bytes())
        old.pop('elapsed_seconds'); new.pop('elapsed_seconds')
        if old != new:
            raise ValueError('independent comparison differs')
        if (output/'exact-replay.json').read_bytes() != (BUNDLE/'data/exact-replay-v1.json').read_bytes():
            raise ValueError('exact replay receipt differs')
        receipt = {'status': 'ARCHIVED_COUPLED_TAIL_REPLAY_PASS',
                   'source_files': len(manifests['source-v2']), 'input_files': len(manifests['inputs']),
                   'live_script_imports': False, 'audit_all_fields_equal_except': ['elapsed_seconds'],
                   'exact_replay_receipt_byte_identical': True,
                   'report_sha256': hashlib.sha256(report.read_bytes()).hexdigest(),
                   'selected_status': new['selected_status'],
                   'scope': 'Inherited-source directional comparison, not fresh analytical generation or admission.'}
        with (output/'receipt.json').open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(receipt, indent=2)+'\n')
        print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
