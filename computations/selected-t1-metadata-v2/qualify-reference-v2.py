"""Qualify the inherited T=1 reference and declared shape without measurements."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.set_int_max_str_digits(0)
from flint import acb, arb, ctx, fmpq
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms
from scripts.cert.residual_kernel import _suzuki_residual_series_coefficients, _suzuki_residual_tail_radius
from scripts.weil_reference_route_controls import archimedean, ball


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def enc(value, bits=192):
    scale = 1 << bits
    lo = Q(str(value.lower().fmpq()))
    hi = Q(str(value.upper().fmpq()))
    return {"lower": str(Q(math.floor(lo*scale)-1, scale)),
            "upper": str(Q(math.ceil(hi*scale)+1, scale))}


def ceil_log2(value):
    value = fmpq(value)
    exponent = int(value.numerator).bit_length()-int(value.denominator).bit_length()
    return exponent if value <= fmpq(2)**exponent else exponent+1


def evaluate(inputs_path):
    pins = json.loads(inputs_path.read_bytes())
    if pins['format'] != 't1-scalar-reference-cost-inputs-v2' or pins['support'] != '1':
        raise ValueError('fixed scalar input identity')
    for binding in pins['pins'].values():
        if digest(ROOT/binding['path']) != binding['sha256']:
            raise ValueError('changed retained premise')
    old = json.loads((ROOT/pins['pins']['baseline_source']['path']).read_bytes())
    control = json.loads((ROOT/pins['pins']['accuracy_control']['path']).read_bytes())
    if (old['support'], old['alpha'], old['beta']) != ('4/5', '1/4', '859/1024'):
        raise ValueError('unsupported whole-line scalar premise')
    goal = Q(pins['accuracy_goal'])
    if not 0 < goal <= Q(control['sigma_selected_low_Schur'])/pins['accuracy_control_divisor']:
        raise ValueError('accuracy choice exceeds retained policy; never a target gap')
    ctx.prec = pins['scalar_precision_bits']
    T, alpha, m = Q(1), Q(pins['alpha']), Q(pins['m'])
    eta = 1-Q(pins['eta_loss'])
    terms = enumerate_active_prime_power_terms(1, 1, prec=ctx.prec)
    if [term.m for term in terms] != [2,3,4,5,7]:
        raise ValueError('strict active set')
    if not (arb(7).log() < 2 < arb(8).log() and 2 < arb.pi() and T < Q(8,5)):
        raise ValueError('strict domain or disjoint-shift geometry')
    added = sum((term.coefficient for term in terms if term.m in (5,7)), arb(0))
    continuum = 2*(arb(1).exp()-ball(Q(4,5)).exp())
    beta_raw = ball(Q(pins['baseline_beta']))+added+continuum
    grid = Q(pins['beta_grid'])
    beta = grid*math.ceil(Q(enc(beta_raw)['upper'])/grid)
    a0 = archimedean(Q(0))

    def g(t):
        return a0+(1-ball(alpha))*(archimedean(Q(t))-a0)-ball(alpha+beta)

    R = 1
    while not g(R) > ball(m+Q(pins['anchor_reserve'])):
        R += 1
    if not g(R-1) < ball(m+Q(pins['anchor_reserve'])):
        raise ValueError('unresolved anchor predecessor')
    g0, gR = g(0), g(R)
    c = T*R
    factor, previous, selected = arb(1), None, None
    for n in range(1, 100000):
        factor *= ball(c*c)/(2*n+1)**2
        if n % 2:
            continue
        ratio = c*c/((2*n+1)*(2*n+3))
        if ratio >= 1:
            continue
        leakage = 2*ball(c)/arb.pi()*(2*n+1)*factor/(1-ball(ratio))
        outside = gR-(gR-g0)*leakage
        loss = (ball(m)-g0)*leakage/ball(m)
        row = {'N':n,'ratio':str(ratio),'leakage':enc(leakage),
               'outside':enc(outside),'eta_loss':enc(loss)}
        if outside > ball(m) and loss < ball(1-eta):
            N, selected = n, row
            break
        previous = row
    else:
        raise ValueError('scalar search exhausted, no mathematical failure claimed')
    M, Rc = 2*N, 2*R
    cm = T*Rc
    odd_product = math.prod(range(1,2*M+2,2))
    ratio_m = cm*cm/((2*M+1)*(2*M+3))
    leak_m = 2*ball(cm)/arb.pi()*ball(Q((2*M+1)*cm**(2*M), odd_product**2)/(1-ratio_m))
    a = 1/g(Rc)
    a_bounds, leak_bounds = enc(a), enc(leak_m)
    aa, ll = Q(a_bounds['upper']), Q(leak_bounds['upper'])
    kappa = aa+(1/m-aa)*ll
    if not 0 < kappa < 1/m:
        raise ValueError('complete inverse gain unresolved')
    ladder = []
    for K in range(2, N//2, 2):
        coefficients = [-T**(d+1)*Q(str(value)) for d,value in enumerate(_suzuki_residual_series_coefficients(K))]
        delta = 2*ball(T)*_suzuki_residual_tail_radius(acb(2*ball(T)),K)
        cross = arb.pi()/2+2*sum((term.coefficient for term in terms),arb(0))+ball(2*sum((abs(value)*2**d for d,value in enumerate(coefficients)),Q(0)))
        db, bb = enc(delta), enc(cross)
        du, bu = Q(db['upper']), Q(bb['upper'])
        allowance = du+(2*bu*du+du*du)/(m*eta)
        ladder.append({'K':K,'delta':db,'cross':bb,'Lambda_upper':str(allowance),'passes':allowance<=goal})
        if allowance <= goal:
            break
    else:
        raise ValueError('residual goal not qualified')
    if not 2*K < N or not M >= N+K or coefficients[1] != T*T/48:
        raise ValueError('exact residual cross band')
    edges, weights = [Q(0),Q(R)], [1/m]
    while edges[-1]*Q(17,16) < 32*R:
        edges.append(edges[-1]*Q(17,16))
    edges.append(Q(32*R))
    for edge in edges[1:]:
        weights.append(Q(enc(1/g(edge),pins['matrix_publication_bits'])['upper']))
    amp_source = ceil_log2(fmpq(21)**(N-1))
    amp_audit = ceil_log2(fmpq(3)**(M-1)*fmpq(7)**(N-1))
    upward = fmpq(M+1)
    for n in range(1,M+1):
        upward *= 1+fmpq(2*n+1)/fmpq(c.numerator,c.denominator)
    amp_bessel = ceil_log2(upward)
    base, block = pins['matrix_publication_bits']+pins['numerical_guard_bits'], pins['precision_block_bits']
    def blockceil(value):
        return ((value+block-1)//block)*block
    source_bits = max(pins['source_precision_floor_bits'],blockceil(base+amp_source))
    audit_bits = max(pins['audit_precision_floor_bits'],source_bits+1024,blockceil(base+amp_audit),blockceil(base+amp_bessel))
    modules = {}
    for name,module in sorted(sys.modules.items()):
        if name.startswith('scripts') and getattr(module,'__file__',None):
            path = Path(module.__file__).resolve()
            modules[path.relative_to(ROOT).as_posix()] = digest(path)
    return {'format':'t1-reference-cost-source-v2','status':'SCALAR_REFERENCE_AND_ERROR_QUALIFIED_NOT_POSITIVITY',
            'support':'1','alpha':str(alpha),'m':str(m),'eta':str(eta),'beta':str(beta),'R':R,'N':N,'M':M,'Rc':Rc,'K':K,
            'active_terms':[{'m':term.m,'prime':term.prime,'exponent':term.exponent,'coefficient':enc(term.coefficient)} for term in terms],
            'transfer':{'added_prime_norm':enc(added),'added_continuum_norm':enc(continuum),'unrounded_beta':enc(beta_raw)},
            'reference':{'g0':enc(g0),'gR':enc(gR),'g_predecessor':enc(g(R-1)),'selected':selected,'previous':previous,
                         'inverse':{'a':a_bounds,'complete_leakage':leak_bounds,'kappa_upper':str(kappa)}},
            'residual':{'coefficients':[str(value) for value in coefficients],'accuracy_goal':str(goal),'accuracy_is_not_target_gap':True,'ladder':ladder},
            'frequency':{'edges':[str(edge) for edge in edges],'inverse_weight_step_uppers':[str(value) for value in weights]},
            'precision':{'source_bits':source_bits,'audit_bits':audit_bits,'matrix_publication_bits':pins['matrix_publication_bits'],
                         'source_amplification_bits':amp_source,'audit_amplification_bits':amp_audit,'bessel_amplification_bits':amp_bessel,
                         'source_gauss_order':3*N//2,'audit_square_gauss_order':N},
            'shape':{'parity_dimension':N//2,'six_triangular_entries':3*(N//2)*(N//2+1),'translation_cells':2*len(terms)+1},
            'inputs_sha256':digest(inputs_path),'producer_sha256':digest(Path(__file__)), 'imported_project_module_sha256':modules,
            'target_matrix_computed':False,'target_positivity_proved':False,'production_admission':False,'RH_status':'UNRESOLVED'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    result = evaluate(args.inputs)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({key:result[key] for key in ('status','support','beta','R','N','M','K','precision','shape')}))


if __name__ == '__main__':
    main()
