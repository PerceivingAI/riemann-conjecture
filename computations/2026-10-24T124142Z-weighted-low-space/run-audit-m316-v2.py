"""Retained one-run supervisor for complete independent analytical reconstruction."""
import time
START = time.perf_counter()
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).resolve().parent/'data'
command = [sys.executable,'-m','scripts.verify_weighted_low_space_inputs',
           '--packet',str(DATA/'source-m316-v1.json.gz'),
           '--output',str(DATA/'audit-m316-v2.json.gz')]
env = os.environ.copy()
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    env[key] = '1'
child = subprocess.Popen(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
timed_out = False
try:
    out,err = child.communicate(timeout=120)
except subprocess.TimeoutExpired:
    timed_out = True
    child.kill()
    out,err = child.communicate()
(DATA/'audit-m316-v2.stdout.txt').write_bytes(out)
(DATA/'audit-m316-v2.stderr.txt').write_bytes(err)
receipt = {'command':command,'timeout_seconds':120,'timed_out':timed_out,
           'exit_code':child.returncode,'owned_exit_confirmed':child.poll() is not None,
           'elapsed_seconds':time.perf_counter()-START,
           'auditor_sha256':hashlib.sha256((ROOT/'scripts/verify_weighted_low_space_inputs.py').read_bytes()).hexdigest()}
(DATA/'audit-m316-v2-run.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt),flush=True)
print(out.decode(),flush=True)
print(err.decode(),flush=True,file=sys.stderr)
raise SystemExit(124 if timed_out else child.returncode)
