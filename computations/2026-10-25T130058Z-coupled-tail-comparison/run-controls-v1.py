"""Reject unsafe coupled-tail consequences, preserving every original report."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--bundle', type=Path, required=True)
args = parser.parse_args()
data = args.bundle/'data'
original = json.loads((data/'comparison-v1.json').read_bytes())

def save(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, indent=2)+'\n')

cases = []
changed = deepcopy(original)
changed['rows'][0]['g_exact'] = '1'
cases.append(('uncertified-coercivity', changed))
changed = deepcopy(original)
changed['rows'][0]['outside_excess_upper'] = '0'
cases.append(('unpaid-outside-tail', changed))
changed = deepcopy(original)
changed['rows'][1]['true_inverse_upper'] = changed['rows'][1]['finite_inverse_upper']
cases.append(('finite-inverse-as-full', changed))
changed = deepcopy(original)
changed['rows'][0]['true_schur_lower'] = changed['rows'][0]['lower_quadratic']
cases.append(('unpaid-schur-residual', changed))
changed = deepcopy(original)
changed['rows'][1]['stiffness_offdiagonal_lower'] = '0'
changed['rows'][1]['stiffness_offdiagonal_upper'] = '0'
cases.append(('erased-signed-stiffness', changed))
receipts = []
for name, report in cases:
    path = data/f'attack-{name}.json'
    output = data/f'attack-{name}.accepted.json'
    save(path, report)
    command = [sys.executable, '-m', 'scripts.verify_coupled_tail_comparison', str(path), '--output', str(output)]
    tick = time.perf_counter()
    done = subprocess.run(command, capture_output=True)
    receipt = {'name': name, 'command': command, 'exit_code': done.returncode,
               'elapsed_seconds': time.perf_counter()-tick, 'success_output_exists': output.exists()}
    (data/f'attack-{name}.stdout.txt').write_bytes(done.stdout)
    (data/f'attack-{name}.stderr.txt').write_bytes(done.stderr)
    save(data/f'attack-{name}.run.json', receipt)
    print(json.dumps(receipt), done.stderr.decode('utf-8', errors='replace'))
    if done.returncode != 2 or output.exists():
        raise ValueError('unsafe report was not rejected: '+name)
    receipts.append(receipt)
save(data/'rejection-summary.json', {'status': 'ALL_FIVE_REJECTIONS_PASS', 'cases': receipts})
