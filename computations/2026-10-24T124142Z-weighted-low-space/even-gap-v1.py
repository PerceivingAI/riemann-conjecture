"""Derive a physical-mass gap from the independently replayed even witness."""
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
from flint import fmpq_mat
from scripts.verify_weighted_low_space import weighted_matrices, _verify_congruence

DATA = Path(__file__).resolve().parent/'data'
raw = (DATA/'assessment-m316-native.json').read_bytes()
result = json.loads(raw)
packet = json.loads(gzip.decompress((DATA/'source-m316-v1.json.gz').read_bytes()))
matrices = weighted_matrices(packet)
indices = list(range(0,packet['dimension'],2))
block = fmpq_mat([[matrices['lower'][i,j] for j in indices] for i in indices])
proof = result['blocks'][0]['positive_lower_witness']
margin = _verify_congruence(block,proof)
assert margin == Q(proof['exact_margin']) and margin > 0
scale = proof['denominator']
trace = sum((Q(v*v,scale*scale)*Q(2,2*indices[j]+1)
             for row in proof['numerators'] for j,v in enumerate(row)),Q())
assert trace > 0
# W L W^T >= margin I; W D W^T <= trace I. Congruence back gives L>=gap D.
gap = margin/trace
assert gap > 0
print(json.dumps({'status':'PASS','assessment_sha256':hashlib.sha256(raw).hexdigest(),
                  'parity':'even','low_degrees':indices,
                  'gershgorin_margin_exact':str(margin),
                  'trace_W_D_Wtranspose_exact':str(trace),
                  'mass_normalized_reference_gap_lower_exact':str(gap),
                  'gap_lower_display':float(gap),
                  'scope':'Uniform positive gap on the even low reference block; no odd or full Weil positivity.'},sort_keys=True))
