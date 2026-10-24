# Fixed-support coercivity gives eventual Schur success, not a practical cutoff

- **Finding ID:** `F-20261024-005`
- **Created:** `2026-10-24T19:49:45Z`
- **Last updated:** `2026-10-24T19:49:45Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED` written derivation by independent mathematical review, with an exact conditional baseline calculation
- **Claim:** C-0086
- **Evidence:** [X-20261024-004](../computations/2026-10-24T191616Z-weighted-support-extension/record.md), `data/conditional-dimension-cost-v1.json`

## Statement

At a fixed locally admissible support T, assume the full closed scaled source form has a known coercive lower Q>=ell I with ell>0. Suppose the established complement lower is mu_N=H_N-cost(T), and the full low-to-tail cross norm is bounded uniformly by b(T). Then the exact scalar-complement criterion and harmonic-reference criterion are strictly positive for all sufficiently large N:

\[
A_N-\mu_N^{-1}B_N^*B_N
\succeq\left(\ell-\frac{b(T)^2}{\mu_N}\right)I,
\]
\[
S_{0,N}\succeq A_N-\mu_N^{-1}B_N^*B_N.
\]

In ordinary Legendre coordinates, replace the identity on the right by the physical mass D_N. The full-source grouped factor3 criterion also eventually succeeds under the component cross-norm bounds below.

This is a conditional mathematical completeness statement. It does not prove a gap at a new support, give a practical cutoff, authorize a theorem pair, or guarantee termination of a fixed-K/fixed-precision implementation.

## Proof

F-20261024-004 / C-0085 gives ||Q_N V P_N||<=pi/2 uniformly in N. Let p(T)=sum c_m b_m, with the established compressed-translation norm bounds, and let rho_R bound the full residual norm. The same absolute-series/remainder expression used for the truncated source bounds the full source without adding delta a second time. Therefore

\[
\|B_N\|\le b(T)=\pi/2+p(T)+\rho_R(T).
\]

Restricting the assumed coercivity to the polynomial low space gives A_N>=ell I. For sufficiently large N, mu_N>0, and the displayed scalar-complement inequality follows. Harmonic divergence gives mu_N->infinity, so b(T)^2/mu_N tends to zero.

For the three grouped full-source components V,P,R, the stronger scalar estimate

\[
\frac3{\mu_N}
\left[(\pi/2)^2+p(T)^2+\rho_R(T)^2\right]
\]

bounds the factor3 coupling loss. It also tends to zero. The grouping is essential: P is the combined arithmetic operator. A differently grouped inequality needs its own factor.

## Obtaining a full scaled-form gap from an already positive reference

Suppose a separately established reference inequality gives S0>=g I with g>0, the actual tail operator satisfies C>=mu I, and ||B||<=b. C-0072 gives Strue>=S0. Domain-safe square completion gives

\[
Q[u+q]\ge g\|u\|^2+\mu\|t\|^2,
\qquad t=q+C^{-1}Bu.
\]

Here C is the positive self-adjoint operator of the restricted closed tail form. C^-1 Bu belongs to its operator domain and hence its form domain, so the shift does not assume equality of the canonical domains. Since ||C^-1 B||<=b/mu,

\[
\|u+q\|^2
\le\left[1+2(b/\mu)^2\right]\|u\|^2+2\|t\|^2.
\]

Thus a conservative full scaled-form lower is

\[
\boxed{\ell=\min\left\{
\frac{g}{1+2(b/\mu)^2},\frac\mu2\right\}>0.}
\]

An ordinary-coordinate reference bound S0>=gD supplies exactly the normalized g used here. This is a lower for the closed source form on the scaled interval[-1,1], not an asserted best eigenvalue or an unadjusted coercivity constant for a differently normalized test-function convention.

## Executed baseline calculation

`scripts.weil_weighted_dimension_cost` reconstructs g from C-0084's accepted exact congruence margins and physical-mass traces. It uses that previous result as a premise, not a fresh replay. Outward512-bit source constants and exact rational arithmetic give the following displays; exact values and byte bindings are retained in the computation.

| Quantity | Display |
| --- | ---: |
| Existing whole-reference gap g at T=3/5 |1.5816571091127121e-9|
| Original mu |0.18491998558724346|
| Full cross-norm upper b |5.318922176703536|
| Conservative full scaled-form lower ell |9.553013337463224e-13|
| Sufficient log(N+1) threshold, flat full-source criterion |2.961466934301032e13|
| Sufficient log(N+1) threshold, grouped factor3 criterion |3.333683494997712e13|

The sufficient thresholds use H_N>=log(N+1). For example, log(N+1)>cost+b^2/ell suffices for the flat criterion. No astronomical N is constructed or attempted.

These thresholds are not necessary lower bounds on the dimension required by either exact matrix calculation or a sharper estimate. They show that this norm-only sufficient argument is computationally useless here. They do not show that the underlying Schur method inherently needs such dimensions.

## What this changes

A negative chosen conservative Schur matrix at one N does not constitute a mathematical no-go for that criterion at every dimension. At a support with an independently known full coercive gap, the exact full-source criteria eventually succeed under the cross-cut bound. That is stronger than merely observing that other dimensions have not been ruled out.

The practical lesson is different. Raising N until a dimension-free norm estimate overcomes a tiny gap can be hopeless. Retaining source correlation and harmonic weights is a computationally consequential mathematical refinement, not a replacement for rigorous verification or a claim of generic mathematical novelty.

For an unproved support, assuming ell>0 would assume the positivity one is trying to establish. This result cannot supply that missing premise. Current source/residual applicability remains2T<pi, and a globally proved support-covering family remains absent. No RH conclusion follows.

## Verification and limits

An independent read-only mathematical reviewer checked the constants, the full/truncated residual distinction, the form-domain shift and both eventual-success estimates. The actual CLI completed with exact positive baseline premises and rational output. It did not reconstruct the old analytical inputs, regenerate an old certificate, execute enormous dimensions, prove new support positivity, compare external implementations or change production admissions. Source/version and actual execution records are in X-20261024-004.
