# Source-sensitive tail concentration from endpoint logs and translated polynomial jumps

- **Finding ID:** `F-20261023-002`
- **Created:** `2026-10-23T13:18:36Z`
- **Last updated:** `2026-10-23T13:25:32Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `PROVISIONAL` — source-inspected analytical qualification; not independently reviewed, not an evaluated bound for the original trial, and not a positivity theorem.
- **Claim:** `C-0075`
- **Source revision inspected:** `acc63ac6d41138280236850c3fbc586e20998cc4`.

## Statement and scope

In C-0072/C-0074's local source setting, use ordinary Legendre polynomials P_j, orthonormal e_k=sqrt((2k+1)/2)P_k and u=sum_{j=0}^d z_j P_j. Let

\[
f=(V+\mathcal P_T+R_T)u,\qquad t_k=\langle e_k,f\rangle,
\quad V(x)=-\tfrac12\log(1-x^2).
\]

The arithmetic operator is denoted by mathcal P_T, not by the prefix scalar P. Suppose R_K u is a polynomial of degree at most r and ||R_T-R_K||<=delta. Set q=mathcal P_T u. On its global translation partition, q is piecewise polynomial. Define its weighted total variation

\[
D(q)=\int_{-1}^{1}\frac{|q'(x)|}{\sqrt{1-x^2}}\,dx
 +\sum_{b\in\mathcal B}\frac{|q(b+)-q(b-)|}{\sqrt{1-b^2}},
\tag{1}
\]

where the derivative is taken inside cells and B contains only interior breakpoints. This quantity is finite; q need not be globally H^1 or continuous. Combine signed arithmetic terms before taking the cell derivative and jumps.

For every integer L>max(d,r,2), define

\[
A_z=\sum_{j=0}^d|z_j|,\quad
\eta_L=1-\frac{d(d+1)}{L(L+1)},\quad
E_L=\left(
 \frac{\sqrt2 A_z}{\eta_L L}
 +D(q)\sqrt{\frac{\pi}{2(L-2)}}
 +\delta\|u\|_2\right)^2.
\tag{2}
\]

The proposed explicit source-tail bound is

\[
\sum_{k\ge L}|t_k|^2=\|Q_L f\|_2^2\le E_L.
\tag{3}
\]

For the original trial, the retained residual image degree is r=223 and d=191, so (2) applies for any proof parameter L>=224. L is an auxiliary index in an inequality: no new source prefix, trial, numerical cutoff run or moment evaluation is performed here.

Let M0=211, R=sum_{k>=211}|t_k|^2, R_->=0 be a valid lower bound on R, and w_k=(mu+H_k-H_192)^-1 with mu>0. Then for each such L,

\[
J=\sum_{k\ge211}w_k|t_k|^2
\ \ge\ w_{L-1}\max(0,R_--E_L).
\tag{4}
\]

This is a **lower** bound on J, suited to a directional reference upper

\[
s_0\le a_{\rm up}-P_- -w_{L-1}\max(0,R_--E_L).
\tag{5}
\]

A negative right side would reject only the exact diagonal-reference sufficient matrix on that trial. No E_L, D(q), proof index L or resulting directional sign has been evaluated for the original source. The constants may be too conservative to decide its sign.

## Derivation: logarithmic endpoint contribution

For n>j, Legendre's differential equation and orthogonality give

\[
\int_{-1}^1 P_n(x)P_j(x)\log(1-x)\,dx
 =-\frac{2}{n(n+1)-j(j+1)}.
\tag{6}
\]

Indeed, subtract the two Sturm-Liouville equations after multiplication by log(1-x). The boundary terms vanish since (1-x^2)log(1-x) tends to zero. The remaining integral is minus the integral of (1+x)(P_n'P_j-P_j'P_n). The second term vanishes by orthogonality; integrating the first by parts leaves the boundary value 2, since the remaining polynomial has degree at most j<n. Reflection gives the log(1+x) identity. Consequently

\[
\langle P_n,VP_j\rangle
 =\frac{1+(-1)^{n+j}}{n(n+1)-j(j+1)}.
\tag{7}
\]

For k>=L>d, (7) and the mass normalization imply

\[
|\langle e_k,Vu\rangle|^2
\le\frac{2(2k+1)A_z^2}{\eta_L^2 k^2(k+1)^2}.
\]

Use (2k+1)/(k^2(k+1)^2)=1/k^2-1/(k+1)^2 and telescope over all k>=L. This gives ||Q_L Vu||<=sqrt(2)A_z/(eta_L L). It conservatively includes both parity sectors; the actual odd source has zero even coefficients. The estimate does not incorrectly treat the logarithmic multiplier as globally bounded or globally H^1.

## Derivation: piecewise arithmetic contribution

For interior x and n>=1, Laplace's integral representation yields the elementary bound

\[
|P_n(x)|\le\sqrt{\frac{\pi}{2n}}\,(1-x^2)^{-1/2}.
\tag{8}
\]

One derivation starts from P_n(x)=pi^-1 int_0^pi (x+i sqrt(1-x^2)cos(phi))^n dphi. Its generating function is (1-2xz+z^2)^-1/2, identifying it with P_n. Taking absolute values bounds the integrand by exp(-n(1-x^2)sin(phi)^2/2). Symmetry, sin(phi)>=2phi/pi on [0,pi/2], and the Gaussian integral prove (8). No sharp Bernstein constant is assumed.

The antiderivative (P_{k+1}-P_{k-1})/(2k+1) vanishes at both endpoints. Integrating against the distributional derivative of q, including its interior jumps, gives for k>=2

\[
|\langle e_k,q\rangle|^2
\le \frac{\pi D(q)^2}{(2k+1)(k-1)}
\le \frac{\pi D(q)^2}{2(k-1)^2}.
\tag{9}
\]

Since sum_{k>=L}(k-1)^-2 <= 1/(L-2), this proves the arithmetic term in (2). Dropping the jumps would invalidate this argument.

There is also an explicit, though potentially very loose, finite-sum upper on D(q). At the fixed first-window geometry 1<tau_m<2, put

\[
U_1=\frac12\sum_j|z_j|j(j+1),\qquad U_e=\left|\sum_j z_j\right|.
\]

For the odd trial, |u(-1)|=|u(1)|=U_e. With c_m=Lambda(m)/sqrt(m)>0,

\[
D(q)\le\pi U_1\sum_{m\in\{2,3\}}c_m
 +2U_e\sum_{m\in\{2,3\}}
 \frac{c_m}{\sqrt{\tau_m(2-\tau_m)}}.
\tag{10}
\]

Here |u'|<=U_1 follows from the derivative expansion of P_j in lower Legendre polynomials and |P_i|<=1. The active intervals for each m are disjoint, so their total arcsine-weighted measure is at most pi. The two jumps for that m have size c_m U_e, and 1-b^2=tau_m(2-tau_m). Formula (10) discards arithmetic cancellation and may be much looser than (1). It nevertheless makes the required constant an explicit finite operation on existing trial coefficients and arithmetic constants, not an assumed decay rate.

## Full residual and concentration step

For L>r, Q_L R_K u=0, but Q_L R_T u is not zero. Its norm is at most delta||u||. Applying the triangle inequality to Q_L Vu, Q_L q and Q_L(R_T-R_K)u proves (2)-(3). This loses cross-component cancellation and is not claimed to be sharp. The residual error is one collective L2 norm; assigning delta independently to infinitely many coefficients and summing would not give a valid remainder.

At least max(0,R_--E_L) mass must lie in 211<=k<L. Each of those weights is at least w_{L-1}. Dropping the nonnegative remainder proves (4); C-0074's one-sided low-form/prefix bounds then give (5). No a_lower or full-Gram upper is needed for this negative-direction upper.

This adds source-dependent concentration information absent from C-0074's abstract scalar completions. It is not merely another worst-weight bound on the same total mass. Conversely, a lower bound on J does not establish a positive reference direction.

### An explicit nonzero-bound witness, not a sign certificate

In the original d=191, r=223 setting, if R_->0 and delta||u||<=sqrt(R_-)/4, choose any integer L satisfying

\[
L\ge\max\left\{224,\ 2(d+1),\
 \frac{16\sqrt2 A_z}{3\sqrt{R_-}},\
 2+\frac{8\pi D(q)^2}{R_-}\right\}.
\tag{11}
\]

Then eta_L>=3/4, each of the three terms inside (2) is at most sqrt(R_-)/4, and E_L<=9R_-/16. Thus J>=7w_{L-1}R_-/16>0. This is a finite quantitative construction, but L may be enormous and the resulting lower bound useless for deciding the sign. No value of L in (11) was selected or evaluated for the original trial. Nontrivial information is not the same as enough information to resolve s0.

## Required inputs and evidence boundaries

| Quantity | Available evidence / remaining issue |
| --- | --- |
| Exact z_j, odd parity, mass norm, a_up and mu lower | Original SHA-pinned SYS-6.4 packet and C-0072; original A/G analytical trust remains generator-source-qualified. |
| Accepted P_- and omitted-mass R_- | C-0074 and its immutable retained-data audit. |
| Residual degree r=223 and delta upper | Accepted nine-mode source packet and existing residual formula/degree argument; not a license to omit the full residual. |
| A_z and U_1, U_e | Explicit finite functions of the existing exact coefficients; not evaluated here. |
| A certified useful D(q) upper | Formula (10) is available as a conservative finite expression. The tightness of it or of the combined-cell variation in (1) has not been evaluated. Existing arithmetic constants/cell formulas supply its inputs; no new analytical primitive is established as necessary. |
| Comparison against a_up-P_- | Requires an actually enclosed E_L and a checked rational comparison. No such target evaluation is claimed. |

The source audit inspected `scripts/cert/legendre_schur.py:164-171`, `multi_prime_legendre_schur.py:47-85,88-148`, `prime_power_terms.py:311-324,422-447` and `residual_kernel.py:230-279`, together with the existing closed-form and degree arguments C-0063/C-0072. It did not change or execute a target source generator. This is qualification of one concentration mechanism; it does not establish the sharpness of its constants for this source.

## Verification scope

The fixed lightweight control below is declared before execution: 78 exact log-product checks (1<=n<=12, 0<=j<n); 23 exact integration-by-parts checks on a two-cell discontinuous arithmetic fixture (2<=k<=24); three finite partial-tail controls each for the potential and arithmetic fixture; twelve exact concentration/boundary controls; and the retained-packet comparison 16 delta^2 ||u||^2<R_-. All are small fixed controls, not a target moment evaluation or numerical proof of the infinite-tail lemma.

Execution ceiling: one direct child, 60 seconds; cumulative analytical-cycle check ceiling 180 seconds. Record actual process wall time including startup. No target trial coefficient aggregates, target proof index or source-derived target constant is evaluated. General validity rests on the displayed analytical argument, still provisional pending independent review.

### Reproducible lightweight control

From the repository root, pass this block to `uv run --locked python -c`. It uses only small synthetic source fixtures and pinned retained scalars; it does not call a target source evaluator or sign screen.

```python
import hashlib, json, time
from pathlib import Path
from fractions import Fraction as Q
from flint import arb, ctx
from scripts.cert.legendre_schur import legendre_polynomials

start = time.perf_counter()
basis = legendre_polynomials(25)
def h(n):
    return sum((Q(1,j) for j in range(1,n+1)),Q())
def mul(a,b):
    out=[Q() for _ in range(len(a)+len(b)-1)]
    for i,x in enumerate(a):
        for j,y in enumerate(b): out[i+j]+=x*y
    return out
def integral(p,a,b):
    return sum((c*(b**(i+1)-a**(i+1))/(i+1) for i,c in enumerate(p)),Q())
def value(p,x):
    return sum((c*x**i for i,c in enumerate(p)),Q())
def raw_v(n,j):
    p=mul(basis[n],basis[j]); rational=Q(); logpart=Q()
    for power,c in enumerate(p):
        if power%2==0:
            r=power//2
            rational+=c*(2*h(2*r+2)-h(r+1))/(2*r+1)
            logpart-=2*c/(2*r+1)
    assert logpart==0
    return rational
pairs=0
for n in range(1,13):
    for j in range(n):
        expected=Q(1+(-1)**(n+j),n*(n+1)-j*(j+1))
        assert raw_v(n,j)==expected
        pairs+=1

# q(x)=-2(x+3/2) on (-1,-1/2), -2(x-3/2) on (1/2,1).
# Its density derivative is -2 on both cells; both interior jumps are +2.
a,b=Q(-1,2),Q(1,2)
raw={}
for k in range(2,25):
    pk=basis[k]
    raw[k]=integral(mul(pk,[Q(-3),Q(-2)]),Q(-1),a)+integral(mul(pk,[Q(3),Q(-2)]),b,Q(1))
    primitive=[(basis[k-1][i] if i<len(basis[k-1]) else Q())-(basis[k+1][i] if i<len(basis[k+1]) else Q()) for i in range(k+2)]
    stieltjes=(-2*(integral(primitive,Q(-1),a)+integral(primitive,b,Q(1)))+2*(value(primitive,a)+value(primitive,b)))/(2*k+1)
    assert raw[k]==stieltjes
    if k%2==0: assert raw[k]==0

with ctx.workprec(256):
    D=4*arb.pi()/3+8/arb(3).sqrt()
    for L in [4,8,12]:
        partial=sum((Q(2*k+1,2)*raw[k]**2 for k in range(L,25)),Q())
        assert arb(partial.numerator)/partial.denominator < arb.pi()*D**2/(2*(L-2))
        # u=P1+P3/7: independent raw polynomial integration vs the envelope.
        pv=sum((Q(2*k+1,2)*(raw_v(k,1)+raw_v(k,3)/7)**2 for k in range(L,25)),Q())
        eta=1-Q(12,L*(L+1))
        assert pv <= 2*Q(8,7)**2/(eta**2*L**2)

N,M,L=2,3,7
w=lambda k: 1/(Q(1,5)+h(k)-h(N))
cases=[{}, {3:Q(1)}, {6:Q(1)}, {7:Q(1)}, {9:Q(1)}, {3:Q(3,5),6:Q(2,7),9:Q(1,9)}]
checks=0
for masses in cases:
    R=sum(masses.values(),Q())
    E=sum((v for k,v in masses.items() if k>=L),Q())
    J=sum((w(k)*v for k,v in masses.items()),Q())
    exact_lower=w(L-1)*max(Q(),R-E)
    assert J>=exact_lower
    assert J>=w(L-1)*max(Q(),max(Q(),R-Q(1,17))-(E+Q(1,13)))
    if masses=={6:Q(1)}: assert J==exact_lower
    checks+=2

paths={
 'computations/2026-10-22T185054Z-directional-source-validation/data/source-validation-1024.json':'9b9a1a0a0b420df0147f07c6fa1f5d9ee9005fb68dc8213cd8880d98556dd843',
 'computations/2026-10-23T105408Z-directional-loss-review/data/loss-audit.json':'0a2458b5ead5245a439647b2a127ef267e7c8c98f11b9d4cfdb63b2bd49bcc18',
}
packets=[]
for path,digest in paths.items():
    data=Path(path).read_bytes()
    assert hashlib.sha256(data).hexdigest()==digest
    packets.append(json.loads(data))
source,audit=packets
assert source['residual_image_degree']==223
assert 16*Q(source['delta_upper_exact'])**2*Q(source['exact_trial_mass_norm']) < Q(audit['exact']['omitted_mass_lower'])
print('PASS',pairs,'log-product identities; 23 jump-aware identities; 3+3 partial-tail controls;',checks,'concentration controls; retained collective residual condition')
print('Internal seconds:',time.perf_counter()-start)
```

## Significance, circularity and limits

The argument uses explicit source regularity, jumps and operator-norm error; it does not assume a zero-free region, unknown cancellation estimate, source positivity or RH. It offers a quantitative distribution-sensitive implication unavailable from scalar mass alone. No actual numerical reference sign, all-direction matrix statement, new support positivity, global source extension or all-support result is established.

The cheap variation bound can discard substantial cancellation. A nonzero J lower bound may be far too small to beat the positive retained headroom. Those limitations are part of the result, not reasons to silently change the trial or regard the criterion as positive. Source trust remains Suzuki/Arb plus the original A/G qualification. Admissions remain eight frozen v1, zero v2 and one v3 C-0067; RH remains unresolved.

## Executed control result — 2026-10-23T13:24:31Z

The exact block above was extracted from this finding and executed once with the locked project environment's Python interpreter as a direct `python -c` child. CPython 3.14.0, python-flint 0.9.0; exit 0, empty stderr, owned process exit confirmed. No retry or descendant process.

```text
PASS 78 log-product identities; 23 jump-aware identities; 3+3 partial-tail controls; 12 concentration controls; retained collective residual condition
Internal seconds: 0.0786386999534443
```

Whole-process wall time, including startup: **1.7601745000574738 seconds**, charged once against the 180-second analytical-check ceiling. The pinned retained packet comparison establishes the residual-floor precondition used in (11), not a value of its source-dependent proof index or a sign of s0. Finite partial-tail controls are checks of normalization and formulas, not proofs of an infinite-tail inequality. The general argument and its unassessed target sharpness retain PROVISIONAL status; no independent mathematical review was performed.

## Dependencies

C-0063 through C-0065 supply the scaled source, Hilbert-space normalization, combined low-to-tail map and full residual premises under existing Suzuki source R-0028. C-0072 supplies the harmonic reference weights and C-0074 the retained one-sided prefix/mass information. The original SYS-6.4 packet and accepted source/audit bytes remain unchanged. Equations (6)-(10) are derived here using elementary Legendre identities; no external source code or new theorem admission is imported.
