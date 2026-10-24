"""Replay unchanged research bytes from an isolated restored source version."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = Path(__file__).resolve().parent
DATA = BUNDLE/'data'
output = DATA/'archived-source-replay-v2.json'
if output.exists():
    raise SystemExit('refusing previous archived replay output')
start = time.perf_counter()
with tempfile.TemporaryDirectory(prefix='weighted-v2-replay-') as directory:
    isolated = Path(directory)
    shutil.copytree(BUNDLE/'source-v2', isolated, dirs_exist_ok=True)
    baseline_relative = Path('computations/2026-10-24T153012Z-weighted-reference-continuation/data')
    baseline = isolated/baseline_relative
    baseline.mkdir(parents=True)
    for name in ('source-m626-v1.json.gz', 'assessment-m626-v1.json'):
        shutil.copyfile(ROOT/baseline_relative/name, baseline/name)
    produced = isolated/'replay.json'
    command = [sys.executable, '-m', 'scripts.weil_weighted_support_extension', 'replay',
               '--packet', str(DATA/'extension-source-v1.json.gz'),
               '--audit', str(DATA/'extension-audit-v1.json.gz'),
               '--result', str(DATA/'extension-assessment-v1.json'), '--output', str(produced)]
    env = os.environ.copy()
    env['PYTHONPATH'] = str(isolated)
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env.setdefault(key, '1')
    completed = subprocess.run(command, cwd=isolated, env=env, capture_output=True, text=True)
    for name, text in (('archived-replay-v2.stdout.txt', completed.stdout),
                       ('archived-replay-v2.stderr.txt', completed.stderr)):
        with (DATA/name).open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(text)
    if completed.returncode == 0:
        with output.open('xb') as stream:
            stream.write(produced.read_bytes())
    receipt = {'status': 'ARCHIVED_SOURCE_REPLAY_PASS' if completed.returncode == 0 else 'ARCHIVED_SOURCE_REPLAY_FAILED',
               'exit_code': completed.returncode, 'command': command,
               'elapsed_seconds': time.perf_counter()-start,
               'created': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
               'isolated_source_version': 'source-v2',
               'restored_generator_sha256': hashlib.sha256((isolated/'scripts/weil_weighted_support_extension.py').read_bytes()).hexdigest(),
               'live_generator_sha256': hashlib.sha256((ROOT/'scripts/weil_weighted_support_extension.py').read_bytes()).hexdigest(),
               'scope': 'Exact retained input/witness replay after live-source cutover; no regenerated analytical audit'}
    with (DATA/'archived-replay-v2-run.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print(json.dumps(receipt), flush=True)
raise SystemExit(completed.returncode)
