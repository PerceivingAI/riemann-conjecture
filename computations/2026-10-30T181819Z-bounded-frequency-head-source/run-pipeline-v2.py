"""Run the explicitly non-admissible reduced source/audit through the actual CLI."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source.contract import bind_problem
from scripts.whole_source.pipeline import prepare_source_inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--control', action='store_true', required=True)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if not args.resume:
        output.mkdir(parents=True, exist_ok=False)
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        prepare_source_inputs(bind_problem('retained-t081'), output/'inputs',
            origin_git_commit=revision, origin_git_dirty=True, control=True, tile_modes=2)
        config = json.loads((output/'inputs/execution.json').read_bytes())
        files = {r['path']: r for role in config['roles'].values() for r in role['collection']['code_refs']}
        for name, ref in files.items():
            target = output/'captured-code'/name
            target.parent.mkdir(parents=True, exist_ok=True)
            raw = (ROOT/name).read_bytes()
            if hashlib.sha256(raw).hexdigest() != ref['sha256']:
                raise ValueError('changed captured source')
            target.write_bytes(raw)
    prefix = [sys.executable, '-B', '-m', 'scripts.weil_whole_source_split']
    shared = ['--problem', str(output/'inputs/problem.json'), '--execution', str(output/'inputs/execution.json')]
    commands = [('source-resume' if args.resume else 'source', prefix+['source', *shared,
                 '--output-dir', str(output/'source')]+(['--resume'] if args.resume else [])),
                ('audit-resume' if args.resume else 'audit', prefix+['audit', *shared,
                 '--source', str(output/'source/producer/source-manifest.json'),
                 '--output-dir', str(output/('audit-resume' if args.resume else 'audit'))])]
    invocations = []
    for label, command in commands:
        if label.startswith('audit'):
            state = json.loads((output/'source/source-state.json').read_bytes())
            source_path = output/'source'/state['manifest']['path']
            raw = source_path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != state['manifest']['sha256'] or len(raw) != state['manifest']['size']:
                raise ValueError('incorrect source-state manifest binding')
            command[command.index('--source')+1] = str(source_path)
        start = time.perf_counter()
        with (output/(label+'-stdout.txt')).open('xb') as stdout, (output/(label+'-stderr.txt')).open('xb') as stderr:
            result = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr, check=False)
        row = {'argv': command, 'exit_code': result.returncode,
               'elapsed_seconds_hex': (time.perf_counter()-start).hex(),
               'created_utc': datetime.now(timezone.utc).isoformat(),
               'program_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'scope': 'CONTROL_ONLY_REDUCED_MODEL'}
        for channel in ('stdout','stderr'):
            raw = (output/(label+'-'+channel+'.txt')).read_bytes()
            row[channel] = {'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        (output/(label+'-invocation.json')).write_text(json.dumps(row, indent=2, sort_keys=True)+'\n', encoding='utf-8')
        invocations.append(row)
        if result.returncode == 0:
            role_root = output/'source/producer' if label.startswith('source') else output/('audit-resume' if args.resume else 'audit')/'analytic'
            if any((role_root/'attempts').glob('*/staging/*')):
                raise ValueError('committed source scratch was not released')
        if result.returncode:
            print(json.dumps(row))
            return result.returncode
    print(json.dumps({'status': 'PASS_REAL_SOURCE_AND_AUDIT_CONTROL', 'invocations': invocations}))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
