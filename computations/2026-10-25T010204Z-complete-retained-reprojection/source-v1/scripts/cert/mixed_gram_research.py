"""Research-only rigorous mixed V/P/R_K image Gram.

This is not a v1/v2 certificate or theorem-admission assembler. All numerical
outputs are outward Arb balls. The full Suzuki residual is included only through
the mathematically separate operator-norm remainder bound.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Sequence

from flint import arb, ctx, fmpq, fmpq_poly

from scripts.cert.legendre_schur import legendre_norm_sq, legendre_polynomials
from scripts.cert.multi_prime_legendre_schur import (
    _arb_fraction, _mat_mul_diag_inverse, _potential_matrices,
    _residual_truncation_operator, _zero_matrix,
)
from scripts.cert.prime_power_terms import (
    _exact_polynomials, assemble_active_prime_power_operator,
)


def _log_primitive(n: int, x: arb, side: int) -> arb:
    """Primitive of x^n log(1+side*x), side ±1; exact singular endpoint limit."""
    if n < 0 or side not in (-1, 1):
        raise ValueError("invalid logarithmic primitive")
    h = sum((Fraction(1, k) for k in range(1, n + 2)), Fraction())
    if side == -1 and x == 1:
        return -_arb_fraction(h) / (n + 1)
    if side == 1 and x == -1:
        return _arb_fraction(h) * (-1 if n % 2 else 1) / (n + 1)
    arg = 1 + side * x
    if not arg.lower() > 0:
        raise ValueError("unresolved logarithm branch/endpoint; increase precision")
    power = x ** (n + 1)
    if side == -1:
        poly = sum((x**k / k for k in range(1, n+2)), arb(0))
        return ((power-1)*arg.log()-poly)/(n+1)
    poly = sum(((-1)**k*x**(n-k+1)/(n-k+1) for k in range(n+1)), arb(0))
    return ((power-(-1)**(n+1))*arg.log()-poly)/(n+1)


def logarithmic_cell_moments(lower: arb, upper: arb, max_degree: int) -> list[arb]:
    """Rigorous moments int_a^b x^n [-log(1-x²)/2] dx, n=0..max_degree.

    Only exact ±1 endpoint balls are accepted. Moving Arb breakpoints must
    certify strict interior position; no midpoint-based topology decisions.
    """
    if max_degree < 0:
        raise ValueError("max_degree must be nonnegative")
    if not lower < upper or lower < -1 or upper > 1:
        raise ValueError("invalid or unresolved cell bounds")
    if lower != -1 and not lower > -1:
        raise ValueError("uncertain lower endpoint")
    if upper != 1 and not upper < 1:
        raise ValueError("uncertain upper endpoint")
    return [
        -(_log_primitive(n, upper, -1)-_log_primitive(n, lower, -1)
           +_log_primitive(n, upper, 1)-_log_primitive(n, lower, 1))/2
        for n in range(max_degree+1)
    ]


def _shift_poly(poly: fmpq_poly, shift: arb) -> list[arb]:
    """Rigorous monomial coefficients for exact poly(x+shift), via Horner."""
    out: list[arb] = []
    for coefficient in reversed(poly.coeffs()):
        nxt = [arb(0) for _ in range(len(out)+1)]
        for i, value in enumerate(out):
            nxt[i] += value*shift
            nxt[i+1] += value
        nxt[0] += arb(coefficient)
        out = nxt
    return out


def _simple_cell_moments(a: arb, b: arb, count: int) -> list[arb]:
    return [(b**(n+1)-a**(n+1))/(n+1) for n in range(count)]


def _vr_image_matrix(polys: Sequence[fmpq_poly],
                     residual: Sequence[fmpq_poly]) -> list[list[arb]]:
    """Global grouped exact rational V × R_K moments (ordered)."""
    max_deg = max(p.degree()+q.degree() for p in polys for q in residual)
    rationals: list[tuple[fmpq, fmpq]] = []
    harmonics = [fmpq(0)]
    for k in range(1, max_deg+3):
        harmonics.append(harmonics[-1]+fmpq(1,k))
    for degree in range(max_deg+1):
        if degree % 2:
            rationals.append((fmpq(0), fmpq(0)))
        else:
            k=degree//2
            u=fmpq(1,degree+1)
            alpha=2*harmonics[degree+2]-harmonics[k+1]
            rationals.append((u,alpha*u))
    logtwo = arb.const_log2()
    out = _zero_matrix(len(polys))
    for i, p in enumerate(polys):
        for j, q in enumerate(residual):
            product = p*q
            u=e=fmpq(0)
            for k, c in enumerate(product.coeffs()):
                if c:
                    u += c*rationals[k][0]
                    e += c*rationals[k][1]
            out[i][j] = arb(e)-2*logtwo*arb(u)
    return out


def _mixed_by_shifts(polys: Sequence[fmpq_poly],
                     residual: Sequence[fmpq_poly], terms: Sequence,
                     *, potential: bool) -> list[list[arb]]:
    """Ordered VP (if potential), otherwise PR_K; includes each signed shift."""
    n=len(polys)
    out=_zero_matrix(n)
    source = polys if potential else residual
    degree=max(p.degree() for p in polys)+max(p.degree() for p in source)
    for term in terms:
        tau, coefficient = term.tau, -term.coefficient
        for shift, a, b in ((tau,arb(-1),1-tau),(-tau,-1+tau,arb(1))):
            if not a < b or not a >= -1 or not b <= 1:
                raise ValueError("uncertain translated support interval")
            moments=(logarithmic_cell_moments(a,b,degree)
                     if potential else _simple_cell_moments(a,b,degree+1))
            # VP rows are V P_i and columns P P_j; PR rows P P_i,
            # columns R_K P_j. Contract one moment direction *before*
            # the dense matrix products to avoid a quartic loop.
            shifted=[_shift_poly(p,shift) for p in polys]
            if potential:
                transformed=[
                    [sum((val*moments[k+l] for l,val in enumerate(poly)),arb(0))
                     for k in range(max(p.degree() for p in polys)+1)]
                    for poly in shifted
                ]
                for i,p in enumerate(polys):
                    coefficients=[arb(c) for c in p.coeffs()]
                    for j in range(n):
                        out[i][j] += coefficient*sum(
                            (c*transformed[j][k] for k,c in enumerate(coefficients)),
                            arb(0))
            else:
                transformed=[
                    [sum((arb(val)*moments[k+l] for l,val in enumerate(q.coeffs())),arb(0))
                     for k in range(max(p.degree() for p in polys)+1)]
                    for q in residual
                ]
                for i,p in enumerate(shifted):
                    for j in range(n):
                        out[i][j] += coefficient*sum(
                            (c*transformed[j][k] for k,c in enumerate(p)),arb(0))
    return out




def _rational_order_bounds(
    matrix: Sequence[Sequence[arb]],
) -> tuple[list[list[Fraction]],list[list[Fraction]]]:
    """Two exact Loewner bounds, from symmetric entry balls and row radii.

    Entrywise interval endpoints are not Loewner order; row-sum inflation is.
    """
    from scripts.cert.constants import arb_to_rational_enclosure

    n=len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise ValueError("Loewner enclosure requires a nonempty square matrix")
    center=[[Fraction() for _ in range(n)] for _ in range(n)]
    radius=[[Fraction() for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(i,n):
            # The represented target is a *symmetric* Gram. A missing or
            # contradictory lower-triangle enclosure is not disposable data.
            if i != j and not matrix[i][j].overlaps(matrix[j][i]):
                raise ValueError("asymmetric matrix intervals cannot define a symmetric Loewner enclosure")
            lo,hi=arb_to_rational_enclosure(matrix[i][j])
            if lo>hi:
                raise ValueError("invalid Arb matrix interval")
            c=(lo+hi)/2
            rad=(hi-lo)/2
            center[i][j]=center[j][i]=c
            radius[i][j]=radius[j][i]=rad
    upper=[row[:] for row in center]
    lower=[row[:] for row in center]
    for i in range(n):
        uncertainty=sum(radius[i],Fraction())
        upper[i][i]+=uncertainty
        lower[i][i]-=uncertainty
    return lower,upper


def rigorous_full_gram_upper(
    truncated: dict[str,object], eta: Fraction=Fraction(1,1<<24),
) -> dict[str,object]:
    """Exact rational Loewner upper bound with the full Suzuki R error.

    Does not declare a certificate, apply an admission whitelist, or assert PD.
    """
    from scripts.cert.constants import arb_to_rational_enclosure

    if not isinstance(eta, Fraction):
        raise TypeError("Young parameter eta must be an exact Fraction")
    if eta<=0:
        raise ValueError("Young parameter eta must be strictly positive")
    n=truncated["dimension"]
    _, g_upper=_rational_order_bounds(truncated["Gk"])
    delta=truncated["delta_R"]
    dlo,dhi=arb_to_rational_enclosure(delta)
    if dlo<0 or dhi<0:
        raise ValueError("invalid nonnegative residual bound")
    residual=(1+1/eta)*dhi*dhi
    scale=1+eta
    norms=truncated["norms"]
    full=[
        [scale*g_upper[i][j]+(residual*norms[i] if i==j else Fraction(0))
         for j in range(n)]
        for i in range(n)
    ]
    return {
        "dimension":n, "eta":eta, "upper":full,
        "residual_delta_upper":dhi,
        "operator_order":"G_full_coordinate <= upper (unnormalized Legendre)",
    }


def rigorous_combined_schur_lower(
    truncated: dict[str,object],
    eta: Fraction=Fraction(1,1<<24),
) -> dict[str,object]:
    """Exact rational Schur lower enclosure; only when mu is certified > 0."""
    from scripts.cert.constants import c_T_enclosure,arb_to_rational_enclosure
    from scripts.cert.legendre_schur import harmonic
    from scripts.cert.multi_prime_legendre_schur import (
        _residual_rho, compressed_shift_norm_bound,
    )
    n=truncated["dimension"]
    prec=truncated["precision_bits"]
    norms=truncated["norms"]
    with ctx.workprec(prec):
        T=arb(truncated["support_num"])/truncated["support_den"]
        cT=c_T_enclosure(prec,truncated["support_num"],truncated["support_den"])
        rho=_residual_rho(T,truncated["residual_order"])
        loss=sum((term.coefficient*compressed_shift_norm_bound(term,prec)
                  for term in truncated["active_terms"]),arb(0))
        mu=_arb_fraction(harmonic(n))-cT-rho-loss
        mu_lo,_=arb_to_rational_enclosure(mu)
        if mu_lo<=0:
            raise ValueError("no rigorous positive full complement")
        A=_zero_matrix(n)
        for i in range(n):
            for j in range(n):
                A[i][j]=truncated["V"][i][j]+truncated["P"][i][j]+truncated["Rk"][i][j]
                if i==j:
                    A[i][i]+=_arb_fraction(norms[i])*(
                        _arb_fraction(harmonic(i))-cT-truncated["delta_R"])
        a_lower,_=_rational_order_bounds(A)
        bound=rigorous_full_gram_upper(truncated,eta)
        upper=bound["upper"]
        schur=[[a_lower[i][j]-upper[i][j]/mu_lo for j in range(n)]
               for i in range(n)]
        return {
            "dimension":n,"mu_lower":mu_lo,
            "schur_lower":schur,"gram_majorant":bound,
            "semantics":"rigorous matrix-order lower bound; positivity NOT presumed",
        }


def assemble_truncated_mixed_gram(
    n: int, prec: int=256, residual_order: int=32,
    support_num: int=11, support_den: int=20,
) -> dict[str,object]:
    """Rigorous mixed-image Gram, with separate full-residual bound metadata.

    Research-only: high-dimension interval widths are not presumed useful.
    """
    if n<1 or prec<64 or residual_order<8:
        raise ValueError("invalid dimension, precision or truncation order")
    with ctx.workprec(prec):
        polys=legendre_polynomials(n-1)
        exact=_exact_polynomials(polys)
        norms=[legendre_norm_sq(i) for i in range(n)]
        v,v2=_potential_matrices(polys,prec)
        arithmetic=assemble_active_prime_power_operator(
            polys,support_num,support_den,prec=prec)
        images,rk,rk2,delta=_residual_truncation_operator(
            polys,residual_order,prec,support_num,support_den)
        vp=_mixed_by_shifts(exact,images,arithmetic.terms,potential=True)
        pr=_mixed_by_shifts(exact,images,arithmetic.terms,potential=False)
        vr=_vr_image_matrix(exact,images)

        k=[[v[i][j]+arithmetic.p_matrix[i][j]+rk[i][j] for j in range(n)]
           for i in range(n)]
        sumdiag=[[v2[i][j]+arithmetic.p_squared_matrix[i][j]+rk2[i][j]
                  for j in range(n)] for i in range(n)]
        for cross in (vp,pr,vr):
            for i in range(n):
                for j in range(n):
                    sumdiag[i][j] += cross[i][j]+cross[j][i]
        low_sq=_mat_mul_diag_inverse(k,norms)
        gram=[[sumdiag[i][j]-low_sq[i][j] for j in range(n)] for i in range(n)]
        # The standard Legendre basis has reflection parity. W_K and Q_N
        # commute with reflection, so opposite-parity entries are exactly 0.
        # Certify containment before imposing these *mathematical* zeros.
        for i in range(n):
            for j in range(i+1,n):
                if (i-j)%2:
                    if not gram[i][j].contains(0) or not gram[j][i].contains(0):
                        raise RuntimeError("exact parity zero excluded by interval")
                    gram[i][j]=gram[j][i]=arb(0)
                    continue
                if not gram[i][j].overlaps(gram[j][i]):
                    raise RuntimeError("mixed Gram symmetry enclosure mismatch")
                # Both intervals contain the same true entry; their mean
                # retains containment, without inventing exact equality.
                common=(gram[i][j]+gram[j][i])/2
                gram[i][j]=gram[j][i]=common
        return {
            "dimension":n,"precision_bits":prec,
            "residual_order":residual_order,
            "support_num":support_num,"support_den":support_den,
            "active_terms":arithmetic.terms,
            "norms":norms,"V":v,"P":arithmetic.p_matrix,"Rk":rk,
            "VP":vp,"PRk":pr,"VRk":vr,
            "Gk":gram,"delta_R":delta,
            "semantics":"rigorous truncated-image Gram; full residual only by delta_R",
        }
