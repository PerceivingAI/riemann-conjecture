"""Fixed exact comparison with the preserved trial and odd lower direction."""
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
from flint import fmpq, fmpq_mat
from scripts.verify_weighted_low_space import weighted_matrices

ROOT = Path.cwd()
DATA = Path(__file__).resolve().parent/'data'
packet = json.loads(gzip.decompress((DATA/'source-m316-v1.json.gz').read_bytes()))
result = json.loads((DATA/'assessment-m316-native.json').read_bytes())
oldpath = ROOT/'computations/2026-10-23T192821Z-weighted-source-tail/data/result-v2.json'
old = json.loads(oldpath.read_bytes())
assert old['input_sha256']['computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json'] == packet['original_mu_input_sha256']
newlo = Q(result['original_trial_reference_lower'])
newhi = Q(result['original_trial_directional_upper']['reference_upper'])
oldlo,oldhi = Q(old['exact']['reference_lower']),Q(old['exact']['reference_upper'])
assert newlo <= oldlo <= oldhi <= newhi
assert Q(result['original_trial_directional_upper']['a_full_upper']) >= Q(old['exact']['a_full_lower'])
matrices = weighted_matrices(packet)
z = [Q(x) for x in result['blocks'][1]['trial']]
column = fmpq_mat([[fmpq(v.numerator,v.denominator)] for v in z])
value = (column.transpose()*matrices['lower']*column)[0,0]
exact_lower_direction = Q(int(value.p),int(value.q))
assert exact_lower_direction < 0
assert Q(result['blocks'][1]['directional_check']['reference_upper']) > 0
print(json.dumps({'status':'PASS','preserved_directional_packet_sha256':hashlib.sha256(oldpath.read_bytes()).hexdigest(),
                  'new_uniform_interval_contains_old_bracket':True,
                  'old_reference_lower':str(oldlo),'old_reference_upper':str(oldhi),
                  'new_uniform_lower':str(newlo),'new_prefix_upper':str(newhi),
                  'extra_lower_allowance_display':float(oldlo-newlo),
                  'odd_conservative_lower_direction':str(exact_lower_direction),
                  'odd_actual_reference_upper':result['blocks'][1]['directional_check']['reference_upper'],
                  'interpretation':'Odd conservative lower is not positive; a positive upper does not determine the actual reference sign.'},sort_keys=True))
