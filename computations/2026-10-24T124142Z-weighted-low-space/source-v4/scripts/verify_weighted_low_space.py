"""Exact weighted low-space research assessment and replay, not theorem admission."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
from math import isqrt
from pathlib import Path
import sys

from flint import fmpq, fmpq_mat
from scripts import verify_weighted_low_space_inputs as inputs

ROOT = Path(__file__).resolve().parents[1]


def _q(value) -> Q:
    return Q(int(value.p),int(value.q))


def _up(value: Q, bits: int) -> Q:
    den = 1 << bits
    return Q((value*den).__ceil__(),den)


def _sqrt(value: Q, bits: int, upward: bool) -> Q:
    if value < 0:
        raise ValueError('negative square root')
    den = 1 << bits
    integer = isqrt((value.numerator*den*den)//value.denominator)
    if upward and integer*integer*value.denominator < value.numerator*den*den:
        integer += 1
    return Q(integer,den)


def _product(a: list[int], b: list[int]) -> tuple[int,int]:
    values = [x*y for x in a for y in b]
    return min(values),max(values)


def _square(a: list[int]) -> tuple[int,int]:
    return (0 if a[0]<=0<=a[1] else min(x*x for x in a),max(x*x for x in a))


def _round_pair(lo: int, hi: int, shift: int) -> list[int]:
    if lo>hi or shift<0:
        raise ValueError('invalid directed dyadic rounding')
    return [lo >> shift,-((-hi) >> shift)]


def _harmonic(n: int) -> Q:
    return sum((Q(1,k) for k in range(1,n+1)),Q())


def _weight(value: Q,bits: int) -> list[int]:
    den = 1 << bits
    return [(value*den).__floor__(),(value*den).__ceil__()]


def _order_bounds(triangle: list, bits: int) -> tuple[fmpq_mat,fmpq_mat,Q]:
    n = len(triangle)
    lo,hi = fmpq_mat(n,n),fmpq_mat(n,n)
    radii = [0]*n
    for i,row in enumerate(triangle):
        for offset,(left,right) in enumerate(row):
            j = i+offset
            if left>right:
                raise ValueError('reversed matrix interval')
            midpoint = fmpq(left+right,1 << (bits+1))
            lo[i,j]=lo[j,i]=hi[i,j]=hi[j,i]=midpoint
            radii[i] += right-left
            if i!=j:
                radii[j] += right-left
    for i,radius in enumerate(radii):
        error = fmpq(radius,1 << (bits+1))
        lo[i,i] -= error
        hi[i,i] += error
    one_sided = max((Q(r*(2*i+1),1 << (bits+1)) for i,r in enumerate(radii)),default=Q())
    return lo,hi,one_sided


def weighted_matrices(packet: dict) -> dict:
    """Complete integer-interval weighted lift, also usable on finite controls."""
    n,m,bits = packet['dimension'],packet['boundary'],packet['bits']
    den = 1 << bits
    mu = Q(packet['mu_reference_exact'])
    delta = Q(packet['delta'][1],den)
    if mu<=0 or packet['delta'][0]<0 or delta<0:
        raise ValueError('invalid positive complement or full residual bound')
    weights = []
    h = Q()
    for k in range(n,m+1):
        if k>n:
            h += Q(1,k)
        weights.append(1/(mu+h))
    pairs = [_weight(w,bits) for w in weights]
    wm = pairs[-1]
    differences = [_weight(w-weights[-1],bits) for w in weights[:-1]]
    heads = []
    for row in range(m-n):
        heads.append([[sum(packet['heads'][name][row][j][endpoint] for name in ('V','P','R32'))
                       for endpoint in range(2)] for j in range(n)])
    upper_intervals = []
    for i in range(n):
        row = []
        for j in range(i,n):
            gl,gh = _product(packet['matrices']['G_K'][i][j-i],wm)
            left,right = gl << (bits+1),gh << (bits+1)
            for offset,k in enumerate(range(n,m)):
                if (heads[offset][i] == [0,0]
                        or heads[offset][j] == [0,0]):
                    continue
                al,ah = _product(heads[offset][i],heads[offset][j])
                ll,hh = _product([al,ah],differences[offset])
                left += ll*(2*k+1)
                right += hh*(2*k+1)
            row.append(_round_pair(left,right,2*bits+1))
        upper_intervals.append(row)
    trace_numerator = 0
    for j in range(n):
        diagonal = packet['matrices']['G_K'][j][0][1] << (bits+1)
        for offset,k in enumerate(range(n,m)):
            square_lower,_ = _square(heads[offset][j])
            diagonal -= square_lower*(2*k+1)
        if diagonal<0:
            raise ValueError('complete tail diagonal upper contradicts PSD')
        trace_numerator += diagonal*(2*j+1)
    gamma = Q(trace_numerator,1 << (2*bits+2))
    a_minus,a_plus,a_error = _order_bounds(packet['matrices']['A_K'],bits)
    _,u_plus,u_error = _order_bounds(upper_intervals,bits)
    trace = sum((_q(u_plus[j,j])*Q(2*j+1,2) for j in range(n)),Q())
    if trace<0:
        raise ValueError('weighted trace upper contradicts PSD')
    residual = _up(delta+2*delta*_sqrt(trace/mu,bits,True)+delta*delta/mu,bits)
    lower = a_minus-u_plus
    for j in range(n):
        penalty = residual*Q(2,2*j+1)
        lower[j,j] -= fmpq(penalty.numerator,penalty.denominator)
    return {'lower':lower,'a_plus':a_plus,'u_plus':u_plus,'heads':heads,
            'weights':weights,'weight_pairs':pairs,'gamma':gamma,
            'theta':_up(weights[-1]*gamma,bits),'residual':residual,
            'A_one_sided_error':a_error,'U_one_sided_error':u_error,
            'bits':bits,'mu':mu,'delta':delta,'upper_intervals':upper_intervals}


def directional_upper(packet: dict, matrices: dict, z: list[Q]) -> dict:
    n,bits = packet['dimension'],packet['bits']
    norm = sum((v*v*Q(2,2*j+1) for j,v in enumerate(z)),Q())
    column = fmpq_mat([[fmpq(v.numerator,v.denominator)] for v in z])
    a = _q((column.transpose()*matrices['a_plus']*column)[0,0])+matrices['delta']*norm
    head = Q()
    for offset,k in enumerate(range(n,packet['boundary'])):
        lo=hi=Q()
        for v,pair in zip(z,matrices['heads'][offset]):
            left,right = (Q(x,1 << bits)*v for x in pair)
            lo += min(left,right)
            hi += max(left,right)
        square = Q() if lo<=0<=hi else min(lo*lo,hi*hi)
        head += square*Q(2*k+1,2)*Q(matrices['weight_pairs'][offset][0],1 << bits)
    root = max(Q(),_sqrt(head,bits,False)-matrices['delta']*_sqrt(norm/matrices['mu'],bits,True))
    inverse_lower = root*root
    bound = a-inverse_lower
    return {'norm':str(_up(norm,bits)),'a_full_upper':str(_up(a,bits)),
            'full_inverse_energy_lower':str(Q((inverse_lower*(1 << bits)).__floor__(),1 << bits)),
            'reference_upper':str(_up(bound,bits))}


def _verify_congruence(lower: fmpq_mat, proof: dict) -> Q:
    nums,den = proof['numerators'],proof['denominator']
    n = lower.nrows()
    if den!=1 << 48 or len(nums)!=n or any(len(row)!=n for row in nums):
        raise ValueError('invalid congruence dimensions')
    if any(type(v) is not int for row in nums for v in row):
        raise ValueError('noninteger congruence witness')
    if any(nums[i][i]==0 or any(nums[i][j] for j in range(i+1,n)) for i in range(n)):
        raise ValueError('singular or nontriangular witness')
    witness = fmpq_mat([[fmpq(v,den) for v in row] for row in nums])
    c = witness*lower*witness.transpose()
    margin = min(c[i,i]-sum((abs(c[i,j]) for j in range(n) if i!=j),fmpq(0)) for i in range(n))
    if margin<=0:
        raise ValueError('nonpositive exact congruence margin')
    return _q(margin)


def _positive_proof(lower: fmpq_mat) -> dict | None:
    import numpy as np
    a = np.array([[float(lower[i,j]) for j in range(lower.ncols())] for i in range(lower.nrows())])
    try:
        inverse = np.linalg.inv(np.linalg.cholesky(a))
    except np.linalg.LinAlgError:
        return None
    den = 1 << 48
    proof = {'denominator':den,'numerators':[[int(round(v*den)) if j<=i else 0
              for j,v in enumerate(row)] for i,row in enumerate(inverse)]}
    try:
        margin = _verify_congruence(lower,proof)
    except ValueError:
        return None
    proof['exact_margin'] = str(margin)
    return proof


def _candidate(lower: fmpq_mat, indices: list[int], n: int) -> list[Q]:
    import numpy as np
    mass = np.array([(2*j+1)/2 for j in indices])**0.5
    a = np.array([[float(lower[i,j]) for j in range(len(indices))] for i in range(len(indices))])
    _,vectors = np.linalg.eigh(a*mass[:,None]*mass[None,:])
    v = vectors[:,0]*mass
    result = [Q()]*n
    for j,value in zip(indices,v):
        result[j] = Q(int(round(float(value)*(1 << 48))),1 << 48)
    return result


def _load(packet_path: Path, audit_path: Path) -> tuple[dict,dict,str,str]:
    raw,raw_audit = packet_path.read_bytes(),audit_path.read_bytes()
    packet = inputs.decode_json(gzip.decompress(raw))
    receipt = inputs.decode_json(gzip.decompress(raw_audit) if audit_path.suffix=='.gz' else raw_audit)
    original_bytes = (ROOT/inputs.MU_INPUT).read_bytes()
    if hashlib.sha256(original_bytes).hexdigest()!=inputs.MU_INPUT_SHA256:
        raise ValueError('original reference identity mismatch')
    original = inputs.decode_json(original_bytes)
    inputs.validate_packet(packet,original['mu_lower_exact'])
    sha = hashlib.sha256(raw).hexdigest()
    if (receipt.get('format'),receipt.get('status'),receipt.get('passes_all_stored_intervals'),
        receipt.get('packet_sha256'),receipt.get('bits'),receipt.get('residual_signature')) != (
            inputs.AUDIT_FORMAT,'SOURCE_INPUTS_ACCEPTED',True,sha,512,packet['residual_signature']):
        raise ValueError('analytical receipt identity or acceptance mismatch')
    if not 0<Q(original['mu_lower_exact'])<=Q(receipt['complement_lower_exact']):
        raise ValueError('fixed reference exceeds accepted complement')
    shift = 512-packet['bits']
    def compare(source,reference):
        inputs.validate_pair(reference,'reference receipt')
        if not source[0] << shift <= reference[0] <= reference[1] <= source[1] << shift:
            raise ValueError('serialized independent reference not contained')
    for name in ('A_K','G_K'):
        if len(receipt['matrices'][name])!=packet['dimension']:
            raise ValueError('incomplete matrix reference receipt')
        for row,other in zip(packet['matrices'][name],receipt['matrices'][name],strict=True):
            for source,reference in zip(row,other,strict=True):
                compare(source,reference)
    for name in ('V','P','R32'):
        for row,other in zip(packet['heads'][name],receipt['heads'][name],strict=True):
            for source,reference in zip(row,other,strict=True):
                compare(source,reference)
    for name in ('delta','complement'):
        compare(packet[name],receipt[name])
    return packet,original,sha,hashlib.sha256(raw_audit).hexdigest()


def assess(packet: dict, original: dict) -> dict:
    matrices = weighted_matrices(packet)
    n = packet['dimension']
    blocks = []
    for parity in (0,1):
        indices = list(range(parity,n,2))
        lower = fmpq_mat([[matrices['lower'][i,j] for j in indices] for i in indices])
        positive = _positive_proof(lower)
        z = _candidate(lower,indices,n)
        upper = directional_upper(packet,matrices,z)
        blocks.append({'parity':parity,'positive_lower_witness':positive,
                       'trial':[str(v) for v in z],'directional_check':upper,
                       'negative_reference_direction':Q(upper['reference_upper'])<0})
    old_trial = [Q(v) for v in original['trial_rational_vector']]
    old_upper = directional_upper(packet,matrices,old_trial)
    z = fmpq_mat([[fmpq(v.numerator,v.denominator)] for v in old_trial])
    old_lower = _q((z.transpose()*matrices['lower']*z)[0,0])
    negative = any(b['negative_reference_direction'] for b in blocks)
    positive = all(b['positive_lower_witness'] is not None for b in blocks)
    if negative and positive:
        raise ValueError('inconsistent rigorous positive and negative predicates')
    status = 'NEGATIVE_REFERENCE_DIRECTION' if negative else 'POSITIVE_REFERENCE_LOWER' if positive else 'INCONCLUSIVE_LOWER'
    next_boundary = None
    if not negative and not positive and matrices['gamma']>0:
        h = _harmonic(packet['boundary'])-_harmonic(n)
        current = 1/(matrices['mu']+h)
        for k in range(packet['boundary']+1,1025):
            h += Q(1,k)
            if k%2==0 and 1/(matrices['mu']+h)<=current/2:
                next_boundary=k
                break
    return {'format':'research-weighted-low-space-assessment-v1','status':status,
            'boundary':packet['boundary'],'blocks':blocks,
            'gamma_upper':str(_up(matrices['gamma'],packet['bits'])),
            'tail_loss_upper':str(matrices['theta']),'residual_allowance':str(matrices['residual']),
            'A_one_sided_error':str(matrices['A_one_sided_error']),
            'U_one_sided_error':str(matrices['U_one_sided_error']),
            'accuracy_selected_next_boundary':next_boundary,
            'original_trial_reference_lower':str(Q((old_lower*(1 << packet['bits'])).__floor__(),1 << packet['bits'])),
            'original_trial_directional_upper':old_upper,
            'scope':'Fixed diagonal reference; no actual true-inverse evaluation, admission or RH claim'}


def replay(packet: dict, result: dict, original: dict) -> None:
    matrices = weighted_matrices(packet)
    if (result.get('format'),result.get('boundary')) != (
            'research-weighted-low-space-assessment-v1',packet['boundary']):
        raise ValueError('result format or boundary mismatch')
    for key,value in {
        'gamma_upper':str(_up(matrices['gamma'],packet['bits'])),
        'tail_loss_upper':str(matrices['theta']),
        'residual_allowance':str(matrices['residual']),
        'A_one_sided_error':str(matrices['A_one_sided_error']),
        'U_one_sided_error':str(matrices['U_one_sided_error']),
    }.items():
        if result.get(key)!=value:
            raise ValueError('altered matrix error allowance: '+key)
    old_trial = [Q(v) for v in original['trial_rational_vector']]
    if result.get('original_trial_directional_upper')!=directional_upper(packet,matrices,old_trial):
        raise ValueError('altered original-trial upper')
    z = fmpq_mat([[fmpq(v.numerator,v.denominator)] for v in old_trial])
    value = _q((z.transpose()*matrices['lower']*z)[0,0])
    old_lower = str(Q((value*(1 << packet['bits'])).__floor__(),1 << packet['bits']))
    if result.get('original_trial_reference_lower')!=old_lower:
        raise ValueError('altered original-trial lower')
    for block,parity in zip(result['blocks'],(0,1),strict=True):
        if block['parity']!=parity:
            raise ValueError('wrong parity inventory')
        indices = list(range(parity,packet['dimension'],2))
        lower = fmpq_mat([[matrices['lower'][i,j] for j in indices] for i in indices])
        proof = block['positive_lower_witness']
        if proof is not None and _verify_congruence(lower,proof)!=Q(proof['exact_margin']):
            raise ValueError('altered exact margin')
        trial = [Q(v) for v in block['trial']]
        if len(trial)!=packet['dimension'] or any(trial[j] for j in range(1-parity,packet['dimension'],2)):
            raise ValueError('invalid directional parity or dimension')
        upper = directional_upper(packet,matrices,trial)
        if upper!=block['directional_check'] or (Q(upper['reference_upper'])<0)!=block['negative_reference_direction']:
            raise ValueError('altered directional result')
    positive = all(b['positive_lower_witness'] is not None for b in result['blocks'])
    negative = any(b['negative_reference_direction'] for b in result['blocks'])
    expected = 'NEGATIVE_REFERENCE_DIRECTION' if negative else 'POSITIVE_REFERENCE_LOWER' if positive else 'INCONCLUSIVE_LOWER'
    if result['status']!=expected or (positive and negative):
        raise ValueError('incorrect matrix classification')
    next_boundary = None
    if not positive and not negative and matrices['gamma']>0:
        h = _harmonic(packet['boundary'])-_harmonic(packet['dimension'])
        current = 1/(matrices['mu']+h)
        for k in range(packet['boundary']+1,1025):
            h += Q(1,k)
            if k%2==0 and 1/(matrices['mu']+h)<=current/2:
                next_boundary=k
                break
    if result.get('accuracy_selected_next_boundary')!=next_boundary:
        raise ValueError('altered accuracy-selected boundary')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet',type=Path,required=True)
    parser.add_argument('--audit',type=Path,required=True)
    parser.add_argument('--result',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError('output already exists')
        packet,old,sha,audit_sha = _load(args.packet,args.audit)
        if args.result:
            result_raw = args.result.read_bytes()
            result = inputs.decode_json(result_raw)
            if result.get('packet_sha256')!=sha or result.get('audit_sha256')!=audit_sha:
                raise ValueError('result input byte binding mismatch')
            replay(packet,result,old)
            output = {'status':'EXACT_REPLAY_PASS','packet_sha256':sha,
                      'result_sha256':hashlib.sha256(result_raw).hexdigest(),
                      'mathematical_status':result['status']}
        else:
            output = assess(packet,old)
            output.update(packet_sha256=sha,audit_sha256=audit_sha)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(output,stream,sort_keys=True,indent=2)
            stream.write('\n')
        print(json.dumps({'status':output['status'],'output':str(args.output)}))
        return 0
    except (ValueError,KeyError,TypeError,OSError) as exc:
        print(str(exc),file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
