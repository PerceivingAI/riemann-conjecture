"""Capture fixed research executions without an elapsed-time permission cutoff."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = Path(__file__).resolve().parent
DATA = BUNDLE/'data'
STAGE = sys.argv[1]
SELECTION = DATA/'selection-v1.json'
PACKET = DATA/'extension-source-v1.json.gz'
AUDIT = DATA/'extension-audit-v1.json.gz'
RESULT = DATA/'extension-assessment-v1.json'
COMMANDS = {
    'baseline-v2': ['scripts.weil_weighted_extension_diagnostics', 'baseline', '--output', str(DATA/'baseline-losses-v2.json')],
    'source': ['scripts.weil_weighted_support_extension', 'generate', '--selection', str(SELECTION), '--output', str(PACKET)],
    'audit': ['scripts.verify_weighted_support_extension_inputs', '--packet', str(PACKET), '--output', str(AUDIT)],
    'assessment': ['scripts.weil_weighted_support_extension', 'assess', '--packet', str(PACKET), '--audit', str(AUDIT), '--output', str(RESULT)],
    'replay': ['scripts.weil_weighted_support_extension', 'replay', '--packet', str(PACKET), '--audit', str(AUDIT), '--result', str(RESULT), '--output', str(DATA/'extension-replay-v1.json')],
}
command = [sys.executable, '-m', *COMMANDS[STAGE]]
receipt_path = DATA/(STAGE+'-run.json')
if receipt_path.exists():
    raise SystemExit('refusing existing stage receipt')
env = os.environ.copy()
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    env.setdefault(name, '1')
start = time.perf_counter()
with (DATA/(STAGE+'.stdout.txt')).open('xb') as out, (DATA/(STAGE+'.stderr.txt')).open('xb') as err:
    child = subprocess.Popen(command, cwd=ROOT, env=env, stdout=out, stderr=err)
    try:
        while True:
            try:
                child.wait(timeout=15)
                break
            except subprocess.TimeoutExpired:
                print(json.dumps({'stage': STAGE, 'pid': child.pid, 'elapsed_seconds': time.perf_counter()-start}), flush=True)
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()
receipt = {'command': command, 'stage': STAGE, 'exit_code': child.returncode,
           'elapsed_seconds': time.perf_counter()-start, 'owned_exit_confirmed': child.poll() is not None,
           'finished_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
           'supervisor_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
with receipt_path.open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
print(json.dumps(receipt), flush=True)
raise SystemExit(child.returncode)
