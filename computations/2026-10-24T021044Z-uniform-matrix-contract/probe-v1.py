"""Fixed source-interface and exact matrix-order smoke; not a target matrix run."""
from fractions import Fraction as Q
import json
from math import isqrt
from flint import arb, arb_mat, ctx, fmpq, fmpq_poly
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.multi_prime_legendre_schur import _potential_matrices, _residual_truncation_operator
from scripts.cert.prime_power_terms import assemble_active_prime_power_operator
from scripts.verify_combined_schur_analytic_entries import (
    poly_basis, coeffs, hankel, global_v_moments, integrate_power, translate,
    residual_polys, exact_residual_coefficients, bound_tail, endpoints, qarb,
)

LOW = [0, 1, 190, 191]
ROWS = LOW + [192, 193, 224, 225]
BITS = 352
DEN = 1 << BITS

def publish(x):
    lo, hi = endpoints(x)
    return [lo.numerator * DEN // lo.denominator,
            -((-hi.numerator * DEN) // hi.denominator)]

def inside(x, pair):
    lo, hi = endpoints(x)
    return Q(pair[0], DEN) <= lo <= hi <= Q(pair[1], DEN)

def inner(p, q):
    return sum((c * fmpq(2, k+1) for k,c in enumerate((p*q).coeffs()) if k % 2 == 0), fmpq(0))

def source_probe():
    with ctx.workprec(1024):
        basis = poly_basis(max(ROWS)+1)
        selected = [basis[k] for k in ROWS]
        selected_q = [[Q(int(c.p), int(c.q)) for c in p.coeffs()] for p in selected]
        v, _ = _potential_matrices(selected_q, 1024)
        arithmetic = assemble_active_prime_power_operator(selected_q, 3, 5, prec=1024)
        assert [t.m for t in arithmetic.terms] == [2, 3]
        images, _, _, delta = _residual_truncation_operator(selected_q[:4], 32, 1024, 3, 5)
        receipts = []
        for i,k in enumerate(ROWS):
            for j,degree in enumerate(LOW):
                values = [v[i][j], arithmetic.p_matrix[i][j], arb(inner(selected[i], images[j]))]
                if (k-degree) % 2:
                    assert all(x.contains(0) for x in values)
                    values = [arb(0)] * 3
                receipts.append({'row':k,'column':degree,'V':publish(values[0]),
                                 'P':publish(values[1]),'R32':publish(values[2])})
        delta_pair = publish(delta)
        masses = [str(Q(2,2*k+1)) for k in LOW]
    with ctx.workprec(2048):
        # Independent global monomial contractions and Taylor translations.
        C = coeffs([basis[k] for k in ROWS], max(ROWS)+1)
        L = coeffs([basis[k] for k in LOW], max(LOW)+1)
        vv = C*hankel(global_v_moments(max(ROWS)+max(LOW)),max(ROWS)+1,max(LOW)+1)*L.transpose()
        rebuilt = residual_polys([basis[k] for k in LOW],32,fmpq(3,5),exact_residual_coefficients(32))
        assert rebuilt == images
        terms = []
        T = arb(3)/5
        for m in (2,3):
            logm = arb(m).log()
            assert logm < 2*T
            terms.append((logm/T,logm/arb(m).sqrt()))
        assert arb(4).log() > 2*T
        points = [arb(-1),arb(1)]
        for tau,c in terms:
            points += [-1+tau,1-tau]
        points.sort(key=lambda a: float(a.mid()))
        assert all(a < b for a,b in zip(points[:-1],points[1:]))
        pp = arb_mat(len(ROWS),len(LOW))
        for a,b in zip(points[:-1],points[1:]):
            center = (a+b)/2
            translated = arb_mat(len(LOW),max(LOW)+1)
            for tau,c in terms:
                for shift,left,right in ((tau,arb(-1),1-tau),(-tau,-1+tau,arb(1))):
                    if left < center and center < right:
                        for j,k in enumerate(LOW):
                            row = translate(basis[k],shift,max(LOW)+1)
                            for r,value in enumerate(row):
                                translated[j,r] -= c*value
                    else:
                        assert center < left or center > right
            pp += C*hankel(integrate_power(a,b,max(ROWS)+max(LOW)),max(ROWS)+1,max(LOW)+1)*translated.transpose()
        checks = 0
        for item in receipts:
            k,jdegree = item['row'],item['column']
            i,j = ROWS.index(k),LOW.index(jdegree)
            values = [vv[i,j], pp[i,j], arb(inner(basis[k],rebuilt[j]))]
            if (k-jdegree) % 2:
                assert all(x.contains(0) for x in values)
                values = [arb(0)]*3
            item['reference'] = {}
            for name,value in zip(('V','P','R32'),values):
                assert inside(value,item[name]), (k,jdegree,name,str(value))
                item['reference'][name] = [str(q) for q in endpoints(value)]
                checks += 1
            if k >= 224:
                assert item['R32'] == [0,0]
        delta_ref,_ = bound_tail(T,exact_residual_coefficients(32),32)
        assert inside(delta_ref,delta_pair)
        return {'status':'PASS','component_containments':checks,'delta_containment':True,
                'independent_exact_residual_images':4,'masses':masses,
                'active_terms':[2,3],'publication_bits':BITS,'receipts':receipts,
                'delta':delta_pair,'delta_reference':[str(q) for q in endpoints(delta_ref)],
                'scope':'32 selected unnormalized pairings, not all Q_192 projections or any full target Gram'}

def transpose(a): return [list(row) for row in zip(*a)]
def add(a,b,scale=Q(1)): return [[x+scale*y for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def mul(a,b): return [[sum((x*y for x,y in zip(row,col)),Q()) for col in zip(*b)] for row in a]
def scale(a,s): return [[s*x for x in row] for row in a]
def gram(a,weights): return mul(transpose(a),[[w*x for x in row] for w,row in zip(weights,a)])
def psd2(a):
    assert a[0][1] == a[1][0]
    return a[0][0]>=0 and a[1][1]>=0 and a[0][0]*a[1][1]-a[0][1]**2>=0

def exact_probe():
    D = [[Q(2),Q()],[Q(),Q(2,3)]]
    B = [[Q(1),Q(1)],[Q(1),Q(-2)],[Q(2),Q(1)]]
    delta,mu = Q(1,100),Q(1,2)
    E = [[delta/4,delta/6],[-delta/5,delta/7],[delta/8,-delta/9]]
    assert sum((sum(row[j]**2 / D[j][j] for row in E) for j in range(2)),Q()) <= delta**2
    weights = [Q(2),Q(6,5),Q(12,13)]
    G,H = gram(B,[Q(1)]*3),gram(B,weights)
    head = gram(B[:1],weights[:1])
    tail = gram(B[1:],[Q(1)]*2)
    U = add(head,scale(tail,weights[1]))
    equivalent = add(scale(G,weights[1]),gram(B[:1],[weights[0]-weights[1]]))
    assert U == equivalent
    assert psd2(add(U,H,-1))
    assert psd2(add(scale(tail,weights[1]),add(U,H,-1),-1))
    gamma = sum((tail[j][j]/D[j][j] for j in range(2)),Q())
    assert psd2(add(scale(D,gamma),tail,-1))
    h = sum((U[j][j]/D[j][j] for j in range(2)),Q())
    square = h/mu
    sqrt_up = Q(isqrt(square.numerator*(1<<128)//square.denominator)+1,1<<64)
    assert sqrt_up**2 >= square
    penalty = 2*delta*sqrt_up+delta**2/mu
    full = gram(add(B,E),weights)
    assert psd2(add(add(U,scale(D,penalty)),full,-1))
    # The conservative lower is negative while the actual Schur is positive.
    A = add(full,scale(D,Q(1,1000)))
    lower = add(add(A,U,-1),scale(D,delta+penalty),-1)
    actual = add(A,full,-1)
    assert psd2(actual) and actual[0][0]*actual[1][1] > actual[0][1]**2
    assert lower[0][0] < 0
    # Entrywise endpoints do not replace a matrix-order upper.
    offdiag = [[Q(),Q(1)],[Q(1),Q()]]
    assert not psd2(offdiag)
    return {'status':'PASS','mass_diagonal':[str(D[j][j]) for j in range(2)],
            'tail_trace_upper':str(gamma),'weighted_norm_trace_upper':str(h),
            'cross_residual_penalty_upper':str(penalty),
            'indefinite_lower_actual_positive':True,'non_diagonal_exact_psd_checks':5}

if __name__ == '__main__':
    print(json.dumps({'source':source_probe(),'matrix_algebra':exact_probe()},sort_keys=True))
