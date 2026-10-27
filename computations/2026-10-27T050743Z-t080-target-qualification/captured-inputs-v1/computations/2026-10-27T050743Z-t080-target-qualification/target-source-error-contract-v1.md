# Complete target source/error and parameter-selection contract

- **Created:** 2026-10-27T05:07:43Z
- **Scope:** qualification at T=4/5; no actual target low/coupling matrix or positivity sign.

## Actual low and complete coupling

Use the source/domain and physical-mass convention of C-0063 and the complete
supported weighted-Gram direction of C-0112/C-0118. For ordinary Legendre P_n,
`d_n=2/(2n+1)`. At the target, reconstruct actual
`A_K=D(H-cT)+V+P+R_K`, with `cT=Euler+log(2piT)`. The diagonal/scalar part has
zero cross after the exact low projection. Thus `B_K=Q_N(V+P+R_K)Pi_N`.
Neither old bounded-reference A nor old T3/4 P/GP data are target sources.

At even K with2K<N, the exact finite residual cross has inputN-K..N-1 and
outputN..N+K-1. This is the universal finite-band statement of C-0117, not an
assertion inferred by sampling. All even/polar kernel contributions and odd
primitive boundary polynomials must still be retained in the LOW block. With
M=2N the finite model has no output at M or above; its true analytic remainder
is separately paid. Use the complete signed Q_M(V+P) output Gram, with VP+PV and
all arithmetic mixed squares. A finite output cut is not a finite-tail theorem.

## True canonical residual error and its multiplier

Let `k_d` be the complete positive-side canonical residual coefficients and
`c_d(T)=-T^(d+1) k_d`. At2T<pi, the frozen canonical Taylor theorem gives

`delta_K=2T[(2/pi)(2T/pi)^(K+1)/(1-2T/pi)+2T^(K+1)/((K+1)![1-T/(K+2)])]`.

This is a bound on the FULL residual-operator discrepancy, including regular
and signed polar pieces. It is not merely a first omitted coefficient.

A complete model-cross norm upper is

`B_K <= pi/2 + 2 sum_m c_m + 2 sum_(d<=K) |c_d(T)| 2^d`.

The first term bounds the CROSS of unbounded V, not V itself. C-0085's positive
Hilbert-kernel domination proves this universal cross bound in physical
coordinates. Each compressed translation has norm at most1, so the complete
combined P has norm at most2sum c_m, with c_4=log2/2. On [-1,1] the finite
residual kernel is bounded by sum|c_d|2^d; the interval has length2, so Schur's
kernel norm bound gives the final term. This coarse norm only multiplies the
TRUE small discrepancy. It does not charge the full residual norm squared as
an independent identity floor or discard residual correlation.

For the qualified h>=m and eta>0, multiplier norm1/h<=1/m gives

`||G_h(B_true)-G_h(B_K)|| <= (2 B_K delta_K+delta_K^2)/m`.

The low-model error is at mostdelta_K. Therefore the complete allowance is

`Lambda_K=delta_K+(2 B_K delta_K+delta_K^2)/(m eta)`.

All scalar roundings are outward. This bound is valid without assuming any
positive target low gap. Exact coefficient reconstruction also checks
`c_1(T)=T^2/48`. The degree policy selects the first even K whose PUBLISHED
complete allowance meets the accuracy goal, retains every preceding even order,
and independently checks2K<N. It is not an optimal residual degree theorem.

## Baseline measurement is not a transported target gap

For the accepted old control, `U^T S U >= margin I`. Ordinary physical mass is D.
Since `U^T D U <= tr(U^T D U) I`, the complete OLD selected-Schur lower in physical
mass is at least `margin/tr(U^T D U)`. The exact control-budget operation checks
this conversion and the inverse physical-coordinate Frobenius bound.

Component caps use the retained ACTUAL A_model as denominator. Each is a
whole-space bound proved by exact nonsingular congruence and all interval row
radii. Finite-head, complete-physical-tail, canonical-model-error and COMBINED
caps are separately certified. Their independent maxima need not occur on the
same direction and must not be added as an equality for the combined budget.

The target accuracy goal is the certified OLD selected-Schur physical lower
DIVIDED BY2^20. This is an explicit working-accuracy choice with a large reserve
relative to the control. It is neither an assumed target gap nor a transported
full-Weil coercivity theorem. A target whose actual margin is smaller may need
more accurate models or a different sound bound. No target positivity is
inferred from the accuracy policy.

## Inverse weight and both infinities

The independently accepted [scalar contract](reference-contract-v1.md) supplies
g, h=max(m,g), eta and the complete inverse-multiplier bound on Q_M. For exact
reference endpoints a_up and lambda_up, use
`kappa_up=a_up+(1/m-a_up)lambda_up`. Monotonicity in both variables proves this
is conservative when0<a_up<=1/m and0<=lambda_up<=1. It bounds a compressed
WHOLE-LINE inverse multiplier, not the inverse of a compressed unbounded form.

Choose exact frequency anchors0,R, successive positive values multiplied by
17/16 strictly below32R, then exactly32R. Publish positive nonincreasing rational
b_0=1/m and b_j>=1/g(Omega_j). On the whole frequency line,

`1/h <= b_last + sum_j(b_j-b_(j+1))1_[|t|<=Omega_(j+1)]`.

Use the exact Bessel band matrices with both frequency halves and the physical
mass convention of C-0118. The b_last D term pays frequency infinity. Native
half-integer Bessel source seeds and independently organized upward recurrence
avoid reintroducing the observed unqualified 0F1 width regime.

For each parity and exact positive theta,

`G_h(B_K) <= (1+theta)H_head +(1+1/theta)kappa_up E*E`.

Here the finite head retains signed V/P/R_K; E=Q_M(V+P)Pi_N has its COMPLETE
signed VP Gram. The target sufficient matrix is

`S_theta=A_K-eta^-1[(1+theta)H_head+(1+1/theta)H_tail]-Lambda_K D`.

Only complete analytical source acceptance and exact whole-matrix positivity
in both parities can prove that sign. No such target matrix is generated by
this qualification. A failed conservative lower alone cannot reject the actual
criterion, the Weil form or the wider method.

## Starting precision and acceptance, not a priori numerical success

On exact polynomial translation cells, an l1 coefficient bound for P_n is3^n;
for P_n(x+tau) with|tau|<2 it is7^n. Producer VP contractions are bounded by
21^(N-1); the independent high/low monomial contraction uses
3^(M-1)7^(N-1). The direct piecewise combined arithmetic square uses Gaussian
integration of degree at most2N-2. Tail P integrands have maximum degreeM+N-2.
The corresponding minimum Gaussian orders are N and ceil((M+N-1)/2).

A conservative upward-recurrence amplification factor on positive anchors is
`(M+1) product_(n=1..M)[1+(2n+1)/(T R)]`. It follows from the infinity norm of
the adjacent-pair recurrence and covers accumulated perturbation amplification.
These explicit coefficient/recurrence factors inform starting precision.
They are not a complete error bound for every native operation.

The machine declaration computes their exact ceil-log2 values, adds256
publication and512 guard bits, rounds to512-bit blocks, and applies source3072
and independent4096 floors with an extra1024 bits over the source. All later
matrix intervals still require independent acceptance. The complete paid matrix
numerical radius must have a verified physical-operator upper at most one
quarter of the declared accuracy goal. For a symmetric entry-radius matrix R,
`max_i sum_j R_ij / min_n d_n` is one valid physical bound. A published bit count
alone is not evidence that this condition or a positive target margin holds.

Start target coordinate proposals with the accepted exact old low-coordinate
transform padded by identity for new low modes, if useful. These are coordinates
ONLY. Contract the FRESH target matrices in Arb before converting to float.
Check any final rational transform's nonsingularity exactly; do not inherit an
old sign or interpret a floating near-zero as a target rejection.

## Integrity and outcome

All consumed sources/audits and exact parameters are SHA-bound. The first
attempt declaration fixes the selected support, scalar inequalities, N,K,M,
frequency/rounding/precision policies and complete error budgets. A change in
method or controls needs a new version and separately recorded outcome.

New support positivity, a useful target low gap, global viability, external
proof correctness, production admission and RH remain unproved by this work.
The current scalar/error qualification and its source, independent consumers,
rejection controls and captured replay are distinct from any later target
low/coupling calculation.
