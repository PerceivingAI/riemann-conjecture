"""Exercise invalid complete-space reports without changing historical inputs."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import time

from scripts import weil_complete_reprojection as source

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--bundle', type=Path, required=True)
args = parser.parse_args()
data = args.bundle/'data'
origin_path = data/'original-v2-gate-v1.json'
report = json.loads((data/'complete-reference-v1.json').read_bytes())
packet, _, choice, _, _ = source.load_inputs(origin_path)
_, tail, heads = source.project_arrays(packet)
heads[:292] = [[[0, 0] for _ in range(20)] for _ in range(292)]
missing_prefix = deepcopy(report)
missing_prefix['U_triangle'] = source.positive_majorant(
    tail, heads, 20, 312, 1018, source.Q(report['mu_reference_exact']))
changed_low = deepcopy(report)
changed_low['A_K_triangle'][19][0] = [v+(1 << 352) for v in changed_low['A_K_triangle'][19][0]]
borrowed_witness = deepcopy(report)
old_proof = choice['projection_rows'][-1]['parity_proofs'][0]
# Reuse the genuine old-subspace certificate: it must not certify ten coordinates.
borrowed_witness['blocks'][0]['positive_lower_witness'] = old_proof['witness']
borrowed_witness['blocks'][0]['mass_normalized_gap_exact'] = old_proof['mass_normalized_gap_exact']
forged_upper = deepcopy(report)
forged_upper['blocks'][1]['directional_check']['reference_upper'] = '-1'
changed_origin = json.loads(origin_path.read_bytes())
changed_origin['source_version'] = 'source-v3'
bad_origin_path = data/'attack-rewritten-origin.json'
source.save(bad_origin_path, changed_origin)
cases = [('missing-restored-prefix', missing_prefix, origin_path),
         ('changed-new-low-degree19', changed_low, origin_path),
         ('borrowed-eight-dimensional-witness', borrowed_witness, origin_path),
         ('forged-negative-upper', forged_upper, origin_path),
         ('rewritten-original-source-version', report, bad_origin_path)]
summary = []
for name, changed, origin in cases:
    path = data/f'attack-{name}.json'
    output = data/f'attack-{name}.accepted.json'
    source.save(path, changed)
    command = [sys.executable, '-m', 'scripts.verify_complete_reprojection', str(path),
               '--origin', str(origin), '--output', str(output)]
    tick = time.perf_counter()
    done = subprocess.run(command, cwd=source.ROOT, capture_output=True)
    receipt = {'name': name, 'command': command, 'exit_code': done.returncode,
               'elapsed_seconds': time.perf_counter()-tick,
               'success_output_exists': output.exists()}
    (data/f'attack-{name}.stdout.txt').write_bytes(done.stdout)
    (data/f'attack-{name}.stderr.txt').write_bytes(done.stderr)
    source.save(data/f'attack-{name}.run.json', receipt)
    print(json.dumps(receipt), done.stderr.decode('utf-8', errors='replace'))
    if done.returncode != 2 or output.exists():
        raise ValueError('invalid report was not rejected cleanly: '+name)
    summary.append(receipt)
source.save(data/'rejection-summary.json', {'status': 'ALL_FIVE_REJECTIONS_PASS', 'cases': summary})
