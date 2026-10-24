"""Exact mass gaps and directional loss diagnostics for the retained m626 run."""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from flint import fmpq, fmpq_mat
from scripts.verify_weighted_low_space import _load, _q, _verify_congruence, weighted_matrices, replay

DATA = Path(__file__).resolve().parent/'data'
packet,original,packet_sha,audit_sha = _load(DATA/'source-m626-v1.json.gz', DATA/'audit-m626-v1.json.gz')
raw = (DATA/'assessment-m626-v1.json').read_bytes()
result = json.loads(raw)
assert result['packet_sha256']==packet_sha and result['audit_sha256']==audit_sha
replay(packet,result,original)
matrices = weighted_matrices(packet)
blocks=[]
for parity,entry in enumerate(result['blocks']):
    indices=list(range(parity,packet['dimension'],2))
    lower=fmpq_mat([[matrices['lower'][i,j] for j in indices] for i in indices])
    output={'parity':parity,'positive_lower':entry['positive_lower_witness'] is not None}
    if entry['positive_lower_witness'] is not None:
        proof=entry['positive_lower_witness']
        eta=_verify_congruence(lower,proof)
        scale=proof['denominator']
        trace=sum((Q(v*v,scale*scale)*Q(2,2*indices[j]+1) for row in proof['numerators'] for j,v in enumerate(row)),Q())
        assert eta==Q(proof['exact_margin']) and eta>0 and trace>0
        gap=eta/trace
        output.update(mass_gap_lower_exact=str(gap),mass_gap_display=float(gap),eta_exact=str(eta),trace_W_D_Wtranspose_exact=str(trace))
    z=[Q(v) for v in entry['trial']]
    column=fmpq_mat([[fmpq(v.numerator,v.denominator)] for v in z])
    low=_q((column.transpose()*matrices['lower']*column)[0,0])
    upper=Q(entry['directional_check']['reference_upper'])
    assert low<=upper
    output.update(selected_direction_lower_exact=str(low),selected_direction_lower_display=float(low),selected_direction_reference_upper_exact=str(upper),selected_direction_reference_upper_display=float(upper))
    blocks.append(output)
print(json.dumps({'status':'EXACT_DIAGNOSTIC_PASS','packet_sha256':packet_sha,'audit_sha256':audit_sha,'assessment_sha256':hashlib.sha256(raw).hexdigest(),'blocks':blocks,'tail_loss_upper_exact':result['tail_loss_upper'],'tail_loss_display':float(Q(result['tail_loss_upper'])),'residual_allowance_display':float(Q(result['residual_allowance'])),'accuracy_selected_next_boundary':result['accuracy_selected_next_boundary'],'scope':'Reference block bounds only; no admission or full Weil theorem.'},sort_keys=True))
