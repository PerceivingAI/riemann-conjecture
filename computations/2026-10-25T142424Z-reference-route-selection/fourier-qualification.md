# Fourier-reference qualification

- Created: `2026-10-25T14:34:32Z`
- Last updated: `2026-10-25T14:34:32Z`
- Status: written mathematical qualification, conditional on the public Weil source identity. No numerical execution, production changes, theorem admission, or claim of Weil positivity at a new support.

## Conclusion

The proposed split gives a genuinely different reference if it uses the bounded coercive arithmetic operator `M = aI + P` and controls a frequency-truncated compact correction. It changes the outside lower operator, rather than relabeling finite coordinates of the harmonic reference. It is not a proof that the new sufficient criterion is stronger or cheaper. Dropping the positive exterior can discard precisely the energy needed for positivity.

Both proposed polynomial estimates are correct with the definitions below. The bump estimate is an upper bound on the best uniform exterior-energy gap. It cannot certify a positive lower gap. The Legendre estimate is an upper bound on projection error and does give a complete compact-complement estimate.

There are two separate quantitative questions. A rigorous lower bound for `1 - ||B||` is necessary if the argument spends a uniform exterior coercivity reserve. It is unnecessary if the bounded minorant `M + K` is already certified strictly positive. For the latter, the first unresolved lemma is a positive, complete finite-reference criterion at one specified support, with all arithmetic cross terms retained. Section 8 states that deliverable precisely. No such positive matrix witness is established here.

## 1. Sources and normalization

Public sources checked directly:

1. Masatoshi Suzuki, [Weil's quadratic form via the screw function, arXiv:2606.09096v3](https://arxiv.org/html/2606.09096v3), version dated 23 September 2026, especially [§1.1](https://arxiv.org/html/2606.09096v3#S1.SS1), [§2.4](https://arxiv.org/html/2606.09096v3#S2.SS4), and [§4.2](https://arxiv.org/html/2606.09096v3#S4.SS2).
2. NIST DLMF, [5.7.E6](https://dlmf.nist.gov/5.7.E6), including its [exact TeX formula](https://dlmf.nist.gov/5.7.E6.tex).
3. Public claim ledger [C-0063, C-0070, C-0072, C-0093](../../docs/CLAIMS.md), used to delimit the existing local form, harmonic-reference, and matched finite-elimination claims. None substitutes for the derivations below.

Use `H_T = L²(-T,T)`, with zero extension, and

\[
\widehat f(t)=\int_{-T}^{T}f(u)e^{-itu}\,du,
\qquad
\|f\|^2=\frac1{2\pi}\int_{\mathbb R}|\widehat f(t)|^2\,dt.
\]

Suzuki defines the transform with a plus sign. Replacing `t` by `-t` changes neither the even real multiplier nor the cosine arithmetic term. It interchanges the two imaginary evaluation points, which leaves the real polar product unchanged.

Set

\[
A(t)=\Re\psi\!\left(\frac14+\frac{it}{2}\right)-\log\pi,
\quad \ell_m=\log m,
\quad c_m=\frac{2\Lambda(m)}{\sqrt m}.
\]

Let `S_ell` be the compressed translation `S_ell f(u) = f(u-ell)`, using zero extension, and `J_ell = (S_ell + S_ell*)/2`. For `f` in `C_c^infinity(-T,T)`, the source formula gives exactly

\[
Q_W(f)=\frac1{2\pi}\int_{\mathbb R}A(t)|\widehat f(t)|^2\,dt
+\langle Pf,f\rangle+q_{\rm pole}(f),
\tag{1}
\]

\[
P=-\sum_{\ell_m<2T}c_mJ_{\ell_m},
\qquad
q_{\rm pole}(f)=2\Re\!\left(
\widehat f(i/2)\overline{\widehat f(-i/2)}\right).
\tag{2}
\]

The source's `n <= exp(2T)` and the strict inequality here agree. At equality, the two zero-extended supports overlap only on a null set, so that translation contributes zero.

### Independent checks of the constants and polar sign

Write `g = f * tilde(f)`. Then `g(0) = ||f||²` and the two polar integrals in Suzuki §1.1 are the two conjugate products in (2). With `h_c(u)=cosh(u/2)` and `h_s(u)=sinh(u/2)`,

\[
q_{\rm pole}(f)=2|\langle f,h_c\rangle|^2
-2|\langle f,h_s\rangle|^2.
\tag{3}
\]

Thus the pole is positive in the even sector and negative in the odd sector. It is not a positive rank-two correction. Its kernel is `2 cosh((u-v)/2)`, not `2 cosh((u+v)/2)`.

The arithmetic evaluations `g(ell)+g(-ell)` equal `2 Re <S_ell f,f>`. This accounts for both the minus sign and the factor `2 Lambda(m)/sqrt(m)` in (2).

The archimedean normalization can also be checked directly from §1.1, without treating an asymptotic formula as an exact identity. The DLMF series gives the integral representation

\[
A(t)=-\gamma-\log\pi+
2\int_0^\infty
\frac{e^{-2x}-e^{-x/2}\cos(tx)}{1-e^{-2x}}\,dx.
\]

Suzuki's regularized archimedean functional instead starts with `-log(4pi)-gamma` and has `e^{-x}` in place of `e^{-2x}` in this numerator. The difference of the integrals is

\[
2\int_0^\infty\frac{e^{-x}-e^{-2x}}{1-e^{-2x}}\,dx
=2\log2=\log4.
\]

It cancels the difference in the constants. These regularized expressions, integrated against `|hat f|²/(2pi)`, therefore give precisely `A`, not `A/2` or a multiplier with `-log(2pi)` in place of `-log(pi)`.

### Source correction and domain caution

There is a literal scaling typo in the display preceding Suzuki (4.4). The correct identity is

\[
\int_{-T}^{T}|v(x)|^2\log(T^2-x^2)\,dx
=2\|v\|^2\log T
+T\int_{-1}^{1}|v(Tx)|^2\log(1-x^2)\,dx.
\tag{4}
\]

The last factor `T` is absent in that display. The Rayleigh quotient identities (4.2) and (4.5) have the consistent scaling after correcting it. Under the unitary map `f(u)=T^{-1/2}w(u/T)`, `hat f(t)=sqrt(T) hat w(Tt)`, the multiplier is `A(z/T)`, the arithmetic shift is `ell_m/T`, and the polar kernel becomes `2T cosh(T(x-y)/2)`.

Suzuki §2.4 initially states its operator-form Fourier formula on `H_0^1`. Its `O(T)||f||²` notation means a bounded perturbation depending on the fixed support, not a usable explicit bound and not a small-support uniform error. Neither that notation nor the Fourier formula authorizes treating the full Weil form as bounded on all `H_T`.

## 2. The new reference and its exact scope

For `a` real and `Omega > 0`, define

\[
M=aI+P,
\]

\[
K=K_{\rm pole}+F_\Omega^*\,\operatorname{mult}(A-a)\,F_\Omega,
\qquad
(F_\Omega f)(t)=\frac{\widehat f(t)}{\sqrt{2\pi}},\quad |t|\le\Omega.
\]

`K_pole` is the rank-two operator in (3). The finite-band operator has a continuous difference kernel on the compact time square and is compact. `M` and `K` are bounded self-adjoint operators on all `H_T`. The arithmetic part of `M` need not be compact.

Equation (1) becomes

\[
Q_W(f)=\langle(M+K)f,f\rangle+r_{\rm ext}(f),
\qquad
r_{\rm ext}(f)=\frac1{2\pi}\int_{|t|>\Omega}(A(t)-a)|\widehat f(t)|^2\,dt.
\tag{5}
\]

This is first an identity on the smooth core. The exterior form is generally unbounded and cannot be evaluated as a finite quadratic form on every `L²` function. Its natural domain, once the exterior multiplier is nonnegative, is

\[
\mathcal D=\left\{f\in H_T:
\int_{\mathbb R}\log(2+|t|)|\widehat f(t)|^2\,dt<\infty\right\}.
\]

Here one uses the source's fixed-vertical-line logarithmic asymptotic only to identify the weight, not to manufacture an explicit exterior lower bound. The nonnegative exterior multiplier gives a closed form on `D`, and adding bounded `M+K` preserves closedness and lower semiboundedness. Smooth compactly supported functions form a core: first contract the time support by a dilation, then convolve with a compactly supported smooth approximate identity. Dilation is strongly continuous for the weighted Fourier norm because the logarithmic weights under nearby dilations are uniformly comparable. Mollification converges in that norm by its bounded Fourier multipliers and dominated convergence. This constructs the closure from (5); it is not an unsupported assertion about equality of every operator domain in the existing physical representation.

If `A(Omega) >= a`, the exterior is nonnegative. Therefore a strict all-`H_T` lower bound for the bounded operator `M+K` immediately proves the corresponding smooth-core Weil bound. The split has no Bernoulli/Taylor radius `2T < pi`. This removes that particular representation restriction, not the all-support positivity problem.

If `M >= mI > 0`, the bounded minorant is equivalent by congruence to

\[
I+M^{-1/2}KM^{-1/2}.
\]

This is a compact perturbation of the identity. It is a different reference from the harmonic tail inverse in C-0072. C-0093's matched-reference equivalence still applies to any later finite regrouping that keeps this same outside reference. A basis change alone supplies no improvement.

## 3. Exterior monotonicity, without an unverified digamma envelope

Put `x_k = k+1/4` and `y=t/2`. The DLMF series is

\[
A(t)=-\gamma-\log\pi+
\sum_{k=0}^{\infty}\left(\frac1{k+1}-\frac{x_k}{x_k^2+t^2/4}\right).
\]

It and its differentiated series converge uniformly on bounded real `t` intervals. In particular,

\[
A'(t)=\frac t2\sum_{k=0}^{\infty}
\frac{x_k}{(x_k^2+t^2/4)^2}>0\qquad(t>0).
\tag{6}
\]

`A` is even. A rigorous point enclosure `A(Omega)-a >= e >= 0` consequently certifies the whole exterior. No asymptotic remainder estimate is needed for this implication.

A finite series is not automatically a lower bound. Its summands eventually become negative. An elementary explicit tail enclosure is available. For an integer `L >= 1`, let `q=L-3/4` and

\[
S_L(y)=\sum_{k=0}^{L-1}\left(\frac1{k+1}-\frac{x_k}{x_k^2+y^2}\right).
\]

Since the summand equals

\[
\frac{y^2-3x_k/4}{(k+1)(x_k^2+y^2)},
\]

its omitted sum lies between `-3/(4q)` and `y²/(2q²)`, by comparison with the integrals of `(x+1/4)^(-2)` and `(x+1/4)^(-3)` from `L-1` to infinity. Thus

\[
-\gamma-\log\pi+S_L(y)-\frac3{4q}
\le A(2y)\le
-\gamma-\log\pi+S_L(y)+\frac{y^2}{2q^2}.
\tag{7}
\]

This is a valid scalar certificate route, not a claim that these crude enclosures are the most efficient ones. No scalar instance was evaluated here.

## 4. Arithmetic price of the shifted reference

Always,

\[
M\succeq\left(a-\sum_{\ell_m<2T}c_m\|J_{\ell_m}\|\right)I.
\tag{8}
\]

For `T=3/5` and `T=1353/2048`, the active prime powers are exactly `{2,3}` and both shifts have `T < ell_m < 2T`. The input and output supports of each one-sided shift are disjoint, and `S_ell²=0`. On the two paired translated subspaces, `J_ell` is the two-by-two off-diagonal operator with entries `1/2`. Hence `||J_ell||=1/2` exactly. It follows that

\[
\|P\|\le\frac{\log2}{\sqrt2}+\frac{\log3}{\sqrt3}.
\]

For example, `log2 < 3/4`, `log3 < 5/4`, `sqrt2 > 7/5`, and `sqrt3 > 5/3` imply this sum is less than `9/7 < 3/2`. The logarithm bounds follow already from positive partial sums of the exponential series. Thus the historical choice `a=7/2` does satisfy `2I < M < 5I` at either support. This proves the reference bound alone. It does not certify the separate scalar condition `A(256) >= 7/2` or the sign of `M+K`.

There is also a necessary support-dependent price. For the normalized constant function,

\[
\langle J_{\ell_m}f,f\rangle=1-\frac{\ell_m}{2T}.
\]

Therefore `M >= mI` requires

\[
a\ge m+\sum_{\ell_m<2T}c_m\left(1-\frac{\ell_m}{2T}\right).
\tag{9}
\]

Constants are legitimate here because `M` is bounded on all `H_T`. This exposes a cost of shifting the entire arithmetic operator into a positive reference. It does not prove a universal complexity lower bound or a no-go theorem for this route. In particular, the two-prime bounds above must not be exported unchanged to larger supports.

## 5. Bump obstruction to a uniform exterior gap

Define the positive time-band concentration operator

\[
B=F_\Omega^*F_\Omega,
\qquad
B(u,v)=\frac{\sin(\Omega(u-v))}{\pi(u-v)},
\quad B(u,u)=\frac\Omega\pi.
\]

It is compact and `0 <= B <= I`. Its exterior-energy infimum is

\[
\delta_* = 1-\|B\|
=\inf_{f\ne0}\frac{\int_{|t|>\Omega}|\widehat f(t)|^2\,dt}{2\pi\|f\|^2}>0.
\tag{10}
\]

The strict inequality is qualitative. If a compact positive contraction had norm one, it would have an eigenvector with Fourier transform zero outside the band. A compactly supported `L²` function is `L¹` and its Fourier transform is entire. Vanishing on an exterior real interval forces that transform, and then the function, to vanish. This contradiction proves (10), but supplies no useful numerical lower bound.

For an integer `p >= 1`, take

\[
f_p(u)=\left(1-(u/T)^2\right)^p\mathbf1_{[-T,T]}(u),\qquad c=T\Omega.
\]

The interior polynomial and its derivatives of orders `0,...,p-1` vanish at the endpoints. Consequently its zero extension belongs to `H^p(R)` and its `p`th weak derivative is the zero extension of the interior derivative. There is no endpoint delta at that order. Its `p`th derivative has nonzero endpoint traces, so in general the zero extension is not in `H^(p+1)`.

Rodrigues' formula gives

\[
\frac{d^p}{dx^p}(1-x^2)^p=(-1)^p2^p p!P_p(x),
\]

\[
\int_{-1}^{1}\left|\frac{d^p}{dx^p}(1-x^2)^p\right|^2dx
=\frac{2^{2p+1}(p!)^2}{2p+1},
\qquad
\int_{-1}^{1}(1-x^2)^{2p}dx
=\frac{2^{4p+1}((2p)!)^2}{(4p+1)!}.
\]

Parseval for the `p`th weak derivative now yields exactly

\[
0<\delta_*\le
\frac1{c^{2p}}
\frac{(p!)^2(4p+1)!}
{2^{2p}(2p+1)((2p)!)^2}
=\frac{R_p}{c^{2p}}.
\tag{11}
\]

One may intersect the upper bound with `1`. The factorial expression in the question is correct. A fixed integer choice `p=floor(c/2)` is allowed for `c >= 2`; its near-optimal scale for this particular bound follows from

\[
\frac{R_{p+1}/c^{2p+2}}{R_p/c^{2p}}
=\frac{(p+1)(4p+3)(4p+5)}{2(2p+3)c^2}.
\]

No value of (11) was computed here. Every certified lower bound `delta_0 <= delta_*` must be consistent with this upper obstruction. Multiplying by `e` gives an upper obstruction on the reserve `e delta_*` obtainable from the scalar exterior lower bound alone. It does not upper-bound the actual weighted exterior form, whose weight grows, and does not obstruct a reference argument that never spends `delta_*`.

## 6. Legendre plane-wave estimate

Let `Pi_N` project onto polynomials of degrees `0,...,N-1` on `(-T,T)` and `Q_N=I-Pi_N`. Define the normalized uniform projection error

\[
\epsilon_N^2=
\sup_{|t|\le\Omega}\frac{\|Q_N e^{it(\cdot)}\|_{H_T}^2}{2T}.
\]

For `N >= 0`, put

\[
a_n(c)=\frac{(2n+1)c^{2n}}{((2n+1)!!)^2},
\quad r_N(c)=\frac{c^2}{(2N+1)(2N+3)}.
\]

For real `z`, integration by parts `n` times in Rodrigues' formula gives

\[
\left|\int_{-1}^{1}e^{izx}P_n(x)\,dx\right|
\le\frac{|z|^n}{2^n n!}\int_{-1}^{1}(1-x^2)^n dx
=\frac{2|z|^n}{(2n+1)!!}.
\tag{12}
\]

There are no boundary terms because `(1-x²)^n` has endpoint zeros of multiplicity `n`. Expanding in the orthonormal Legendre basis, and dividing the squared plane-wave norm by `2`, gives the termwise tail bound `a_n(|z|)`. Moreover,

\[
\frac{a_{n+1}(c)}{a_n(c)}
=\frac{c^2}{(2n+1)(2n+3)}\le r_N(c)\quad(n\ge N).
\]

Thus, when `r_N(c)<1`,

\[
\epsilon_N^2\le E_N(c):=
\frac{(2N+1)c^{2N}}{((2N+1)!!)^2}
\frac1{1-c^2/((2N+1)(2N+3))}.
\tag{13}
\]

This is exactly the proposed formula. An indexing convention that retains degrees through `N` must replace `N` here by `N+1`. A ratio less than one is required; it does not by itself make the upper bound small. The bound can also be intersected with `1` for real plane waves.

### Complete compact-complement consequences

The Hilbert-Schmidt calculation is

\[
\|F_\Omega Q_N\|^2\le\|F_\Omega Q_N\|_{\rm HS}^2
\le\frac{2c}{\pi}E_N(c)=:\eta_N^2.
\tag{14}
\]

The factor `2c/pi` is the band concentration trace, not a lower bound on a required matrix rank. With

\[
W=\sup_{|t|\le\Omega}|A(t)-a|
=\max\{|A(0)-a|,|A(\Omega)-a|\},
\]

monotonicity gives

\[
\|Q_NK_{\rm band}Q_N\|\le W\eta_N^2,
\qquad
\|\Pi_NK_{\rm band}Q_N\|\le W\eta_N.
\tag{15}
\]

The polar term needs its own estimate; a real-band statement alone does not include the imaginary evaluation points. The proof of (12) for complex `z` gains only `exp(|Im z|)`. Taking `z=+iT/2` and `z=-iT/2` therefore gives

\[
\|Q_N e^{\pm u/2}\|^2\le 2T e^T E_N(T/2).
\]

Writing the polar operator as the sum of the two cross rank-one operators yields

\[
\|Q_NK_{\rm pole}Q_N\|
\le4T e^T E_N(T/2),
\qquad
\|\Pi_NK_{\rm pole}Q_N\|
\le4T e^T\sqrt{E_N(T/2)}.
\tag{16}
\]

Consequently a completely explicit whole-complement bound is

\[
\boxed{\ \|Q_NKQ_N\|\le\kappa_N
:=\frac{2cW}{\pi}E_N(c)+4T e^T E_N(T/2).\ }
\tag{17}
\]

The ratio hypotheses of (13) must hold at both arguments. These are analytical inequalities for the full operators, not finite-frequency quadrature estimates. They establish convergence for each fixed `T,Omega,a`. They say nothing yet about the sign of the retained low matrix or the efficiency of obtaining accurate entries.

## 7. What is established and what is missing

Established here by direct derivation:

- The Fourier normalization, the signed pole, and the finite arithmetic operator in (1)-(3).
- The correction to the source's intermediate scaling display.
- A globally meaningful frequency split on the smooth core and its natural closed-form construction.
- Monotonicity of the digamma multiplier and the explicit scalar tail enclosure (7).
- The two-prime coercivity of `M` for `a=7/2`, plus the necessary support-dependent arithmetic price (9).
- Qualitative positivity of the concentration gap, its bump upper obstruction (11), the exact Legendre projection-error estimate (13), and the complete compact-complement estimate (17).

Not established here:

- An evaluated rigorous point bound `A(Omega)-a >= 0` at a selected parameter pair.
- A useful explicit lower bound for `delta_*`, or a claim that the exterior-energy reserve is numerically usable.
- A positive bounded-minorant witness, including its exact low block and complete cross Gram, at either support named above.
- A practical rank, working precision, runtime, memory requirement, speed advantage, or a comparison at matched one-sided errors.
- Positivity for an unbounded covering family of supports, any new theorem admission, or RH.

A finite upper bound on `||B||` strictly below one could certify a gap, but must include the complete complement and enough absolute accuracy to resolve its distance from one. A floating concentration eigenvalue rounded to one does not refute the qualitative theorem and cannot certify the gap. Conversely, an approximate eigenvalue below one is not a certified operator-norm upper bound.

## 8. Selected first unresolved Fourier lemma

The useful first target is the following fixed-support Fourier-reference closure lemma, initially at `T=3/5`. The larger support `1353/2048` is a separate target, not a consequence.

Choose explicit `a,Omega,N`. Prove `A(Omega)>=a`, `M>=mI>0`, and `d=m-kappa_N>0`, using either (17) or a tighter complete bound with the same meaning. Define the exact bounded minorant and its low quantities by

\[
H_0=M+K,\qquad
A_N=\Pi_NH_0\Pi_N,\qquad
G_N=\Pi_NH_0Q_NH_0\Pi_N.
\]

The required finite certificate is a rigorous matrix lower bound `underline(A_N) <= A_N`, a rigorous matrix upper bound `overline(G_N) >= G_N`, and

\[
\underline{A_N}-d^{-1}\overline{G_N}\succ0.
\tag{18}
\]

Then `Q_NH_0Q_N >= dI`, and square completion proves `H_0` uniformly positive. Equation (5) proves the desired fixed-support smooth-core Weil bound. This argument never requires a concentration-gap lower bound.

`G_N` is the Gram of the total cross map. It includes the finite-column arithmetic shifts, the band correction, the pole, and all their mixed products. Bounding only the compact cross map would omit the noncompact arithmetic contribution. Replacing the total Gram by an unproved sum of separate Grams is unsound. The finite arithmetic columns are explicit shifted polynomial pieces, so retaining them is a concrete integration problem, not a justification for dropping them.

Equation (18) is currently an unresolved positivity requirement, not an asserted lemma already proved by compactness. The ingredients established in §6 make its infinite-complement obligation explicit. The remaining evidence must show whether its actual finite part is positive with usable margins and attainable rigorous integration errors. If a certified negative direction is found in `H_0`, that rejects this minorant for those parameters, not `Q_W`; the discarded exterior may repair it.

If no useful bounded minorant exists for the selected parameters, an exterior-assisted reference requires a new lemma instead. It must bound the weighted exterior on the relevant subspaces, including the cross terms, or provide a certified lower gap `delta_0` and show its reserve closes the actual deficit. The bump bound shows why a qualitative appeal to uncertainty is insufficient. It does not prove such an assisted argument impossible.

## 9. Honest viability assessment

This is a mathematically distinct candidate with an explicit complete-tail mechanism. It avoids the local Taylor radius and gives a compact correction to a coercive arithmetic reference. Those are concrete reasons to investigate it.

Its practical case remains unproved. The exterior threshold competes with the support-dependent price of `a`; the resulting `c=T Omega` controls the Legendre bound; and the signed low-frequency and odd polar contributions still determine whether the bounded minorant is positive. None of these effects is resolved by saying that the correction is compact.

Evidence that would make the route practical is a single fixed-support instance of (18) with rigorous scalar enclosures, attainable complete-tail bounds, and a positive matrix margin exceeding all enclosure errors, followed by recorded resource use at matched mathematical obligations. No claim of superiority or global positivity follows in advance. The present record contains derivations only and leaves all prior research and admissions unchanged.
