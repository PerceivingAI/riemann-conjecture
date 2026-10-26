# Signed logarithmic discrepancy enclosure contract

- **Created:** `2026-10-26T11:42:58Z`
- **Last updated:** `2026-10-26T12:12:12Z`

This contract concerns only the already accepted support \(T=3/4\), with \(\alpha=1/4\) fixed before calculation. It supplies an analytic route to a one-sided logarithmic-energy bound. It does not assert that any numerical enclosure, outside positivity inequality, or finite low/cross sign has succeeded. The scalar program and its execution records are separate artifacts.

The source identities and reference-tail estimate are C-0107, as stated in [energy-discrepancy-reference-v1.md](../2026-10-26T044551Z-energy-reference-qualification/energy-discrepancy-reference-v1.md), sections 1, 2, and 4. That record remains unchanged. The executed parameters are fixed by [qualified-inputs-v1.json](qualified-inputs-v1.json), with [the initial declaration](input-pins.json) retained. Both reference anchors were declared before any scalar execution. The frequency boundary256 partitions this proof; it does not truncate the reference form or discard any frequency.

## 1. Complete arithmetic source and endpoint conventions

Work on \(H_T=L^2(-T,T)\), extending every function by zero to the real line. Use

\[
\widehat f(t)=\int_{\mathbb R}f(u)e^{-itu}\,du,
\qquad \|f\|^2=\int_{\mathbb R}|\widehat f(t)|^2\frac{dt}{2\pi}.
\]

Write \(U_l\) for the compressed translation by \(l\). The sum \(U_l+U_{-l}\) has whole-line multiplier \(2\cos(tl)\) when evaluated as a quadratic form on zero extensions. Let

\[
\Psi(x)=\sum_{m\le x}\Lambda(m),\quad
E(l)=\Psi(e^l)-e^l+1,\quad
\mathcal M_T=\{p^k:k\ge1,\ \log(p^k)<2T\},\quad
d_m=\frac{\Lambda(m)}{\sqrt m}.
\]

Here \(\Psi\) is the Chebyshev function; the digamma function below is denoted by \(\psi_{\rm dg}\). At the fixed support the complete active list is

\[
\mathcal M_{3/4}=\{2,3,4\},\qquad
(d_2,d_3,d_4)=\left(\frac{\log2}{\sqrt2},
\frac{\log3}{\sqrt3},\frac{\log2}{2}\right).
\]

In particular, 4 contributes \(\Lambda(4)=\log2\), not \(\log4\). The exact list follows from \(4<e^{3/2}<5\); for example the exponential series gives
\(e^{3/2}>67/16>4\), while its terms through degree four and a geometric bound on the remaining terms give \(e^{3/2}<2869/640<5\). Thus no active prime power is inferred from a floating-point cutoff.

The discrepancy measure and compressed operator are

\[
dE(l)=\sum_{m\in\mathcal M_T}\Lambda(m)\delta_{\log m}(dl)-e^l\,dl,
\qquad
D_E=\int_{(0,2T)}e^{-l/2}(U_l+U_{-l})\,dE(l).
\]

The continuous integral can equivalently use \([0,2T]\). There is no atom at zero because \(E(0)=0\). If an arithmetic atom were exactly at \(2T\), its compressed translation would vanish on \(H_T\); either endpoint convention would give the same form. The scalar symbol in this contract uses the strict active list, consistently throughout. Changing the endpoint convention can change a whole-line symbol even when its compressed quadratic form is unchanged, so the conventions must not be mixed in a pointwise proof. At \(T=3/4\) there is no such endpoint atom.

## 2. Exact signed multiplier on every real frequency

For zero extensions, Plancherel and the finite variation of the measure give

\[
d_E[f]:=\langle f,D_Ef\rangle
=\int_{\mathbb R}\rho_T(t)|\widehat f(t)|^2\frac{dt}{2\pi},
\]

where

\[
\begin{aligned}
\rho_T(t)
&=2\sum_{m\in\mathcal M_T}d_m\cos(t\log m)
 -2\int_0^{2T}e^{l/2}\cos(tl)\,dl\\
&=2\sum_{m\in\mathcal M_T}d_m\cos(t\log m)
 -2\operatorname{Re}\frac{e^{(1/2+it)2T}-1}{1/2+it}.
\end{aligned}
\]

Both signs of the pole/continuum cancellation have been retained before taking any bound. The denominator never vanishes for real \(t\). In particular the exact value at zero is

\[
\rho_T(0)=2\sum_m d_m-4(e^T-1).
\]

There is no omitted limit, exclusion of zero, or frequency-endpoint exception. The symbol is real, even, and smooth on all of \(\mathbb R\). Its integral representation also shows that it is bounded. Finite sums and a finite-variation integral justify the Plancherel identity first on smooth functions and then on all of \(H_T\) by bounded-form continuity.

## 3. Retained logarithmic energy and the infinite tail

Set

\[
A(t)=\operatorname{Re}\psi_{\rm dg}(1/4+it/2)-\log\pi,
\quad A_0=A(0),\quad w(t)=A(t)-A_0+1,
\quad d_A[f]=\int_{\mathbb R}w(t)|\widehat f(t)|^2\frac{dt}{2\pi}.
\]

The reference is this full unbounded logarithmic form on its finite-energy domain. To see monotonicity without a sampling assumption, put \(a=1/4\), \(y=t/2\). The convergent digamma difference series gives

\[
w(t)=1+\sum_{n=0}^{\infty}
\frac{y^2}{(n+a)((n+a)^2+y^2)}.
\]

Every summand is even in \(t\), nonnegative, and increasing for \(t\ge0\). Thus \(w\) is even, \(w(0)=1\), and \(w(t)\ge w(s)\) for \(t\ge s\ge0\).

Write \(S=2\sum_m d_m\) and \(q=t^2+1/4\). Expanding the real part in section 2 gives the exact identity

\[
\rho_T(t)=2\sum_m d_m\cos(t\log m)
-\frac{2e^T}{q}\left(\frac12\cos(2Tt)+t\sin(2Tt)\right)
+\frac1q.
\]

Since \(|\tfrac12\cos\theta+t\sin\theta|\le\sqrt q\),

\[
\boxed{\rho_T(t)\le H_T(|t|):=
S+\frac{2e^T}{\sqrt{t^2+1/4}}+\frac1{t^2+1/4}.}
\]

This upper bound holds for every real \(t\), including zero. The function \(H_T(s)\) is decreasing for \(s\ge0\). Consequently, for \(r_\alpha(t)=\rho_T(t)-\alpha w(t)\) and any \(R\ge0\),

\[
\boxed{\sup_{|t|\ge R}r_\alpha(t)
\le H_T(R)-\alpha w(R).}
\]

The triangle bound on the complex quotient also gives the valid decreasing envelope \(S+2(e^T+1)/\sqrt{t^2+1/4}\). The producer uses this coarser alternative; the independent verifier uses the sharper real-form envelope displayed above. Either one, combined with monotone \(w\), certifies the full infinite tail.

Use \(R=256\) for the pinned infinite-tail certificate. This is a proof of the entire infinite tail, not a scan of a long but finite interval. In particular, no sign pattern or decay of the discrete cosine sum is assumed.

## 4. Two analytic global Lipschitz constants

Differentiation of the finite integral is legitimate and yields

\[
\rho_T'(t)=-2\sum_m d_m\log(m)\sin(t\log m)
+2\int_0^{2T}l e^{l/2}\sin(tl)\,dl.
\]

The elementary bound \(l\le2T\) gives the requested coarse constant

\[
\boxed{L_{\rho,\rm coarse}
=2\sum_m d_m\log m+8T(e^T-1),\qquad
|\rho_T'(t)|\le L_{\rho,\rm coarse}.}
\]

An independent evaluation of the continuum moment gives a sharper certified constant without using sampled derivative values:

\[
2\int_0^{2T}l e^{l/2}\,dl
=8\big((T-1)e^T+1\big),
\]

\[
\boxed{L_{\rho,\rm sharp}
=2\sum_m d_m\log m+8\big((T-1)e^T+1\big).}
\]

For \(T>0\) the sharp continuum term is positive and strictly smaller than \(8T(e^T-1)\), since the inequality \(l<2T\) is strict almost everywhere under its positive integration measure. At this support the exact sharp continuum term is \(8-2e^{3/4}\), whereas the coarse term is \(6(e^{3/4}-1)\). Either rigorously upward-rounded constant is valid. Subtractive cancellation in the sharp expression must be enclosed, not evaluated with an untracked ordinary floating-point subtraction.

Let \(0\le l\le r\), \(c=(l+r)/2\), and let \(L_\rho\) be either valid constant. For every \(t\in[l,r]\),

\[
\rho_T(t)\le\rho_T(c)+L_\rho\frac{r-l}{2},
\qquad -\alpha w(t)\le-\alpha w(l).
\]

It follows that

\[
\boxed{\sup_{t\in[l,r]}r_\alpha(t)
\le\rho_T(c)+L_\rho\frac{r-l}{2}-\alpha w(l).}
\]

This encloses the whole closed interval, including both endpoints. It does not assert that a mesh of samples bounds an unsampled supremum. No derivative norm of \(f\), or Lipschitz estimate for \(w\), is needed.

## 5. Exact cover and directed-rounding obligations

The pinned initial cover of \([0,256]\) consists of the 2048 closed intervals

\[
I_k=[k/8,(k+1)/8],\qquad k=0,\ldots,2047.
\]

An adaptive refinement may replace any interval by its two closed midpoint halves. All endpoints and midpoints remain exact dyadic rationals. The final ordered leaf list must start at zero, end at 256, and have each right endpoint equal to the next left endpoint by exact rational equality. Parent-to-child replacement must preserve the union. These checks prove exhaustive coverage; shared endpoints are harmless. Evenness supplies \([-256,0]\), and section 3 supplies both infinite tails.

For a leaf \(I=[l,r]\), use outward enclosures to form

\[
U_I=\overline{\rho_T(c)}
+\overline{L_\rho}\,(r-l)/2-\alpha\,\underline{w(l)},
\]

with all additions and the final subtraction rounded upward. A lower certificate at an evaluated point is

\[
B_c=\underline{\rho_T(c)}-\alpha\,\overline{w(c)},
\]

rounded downward. Thus \(B_{\rm fin}=\max_c B_c\) and \(U_{\rm fin}=\max_I U_I\) enclose the finite-interval supremum from below and above. The pinned finite gap target is \(U_{\rm fin}-B_{\rm fin}\le1/256\); any claim that it was met requires the actual exhaustive leaf record and rounded comparison. Refinement is not evidence of success until that comparison is recorded. This finite gap says nothing by itself about the global supremum, which must still include the infinite-tail upper bound.

Enclose every transcendental operation, including logarithms, square roots, exponentials, trigonometric functions, digamma values, and \(\pi\). In particular, forming an interval cosine by taking only endpoint cosines is not valid across an interior extremum. Use certified interval range reduction or another proved enclosure. The complex exponential quotient may instead be evaluated through the real formula in section 3; both must enclose the same signed quantity. The exact zero-frequency formula provides a nonsingular endpoint evaluation.

For example, the positive series for \(w\) can be evaluated with an explicit remainder. After retaining \(n=0,\ldots,M-1\), \(M\ge1\), its remainder is between zero and

\[
\frac{t^2}{4}\left(\frac1{(M+1/4)^3}
+\frac1{2(M+1/4)^2}\right).
\]

This follows by bounding each summand by \((t^2/4)(n+1/4)^{-3}\) and using the decreasing-function integral bound for the tail. A different digamma evaluator is acceptable only with its own rigorous remainder and directed-rounding justification. Numerical agreement between two unvalidated evaluations is not a substitute for an enclosure.

The infinite-tail upper endpoint is

\[
U_{\infty}=\overline S+
\overline{\frac{2e^T}{\sqrt{256^2+1/4}}}
+\overline{\frac1{256^2+1/4}}
-\alpha\,\underline{w(256)},
\]

rounded upward. The published nonnegative additive constant must satisfy

\[
b\ge\max(0,U_{\rm fin},U_{\infty}).
\]

On the pinned publication grid one may take

\[
b=\frac1{1024}
\left\lceil1024\max(0,U_{\rm fin},U_{\infty})\right\rceil,
\]

where the maximum and ceiling use exact certified endpoint values and cannot round downward. The pinned producer and independent precisions are 256 and 384 bits. An independent execution must re-establish interval enclosures and exact coverage, rather than merely compare decimal output strings. This contract asserts no value of \(b\), no attained gap, and no successful execution at either precision.

## 6. From the scalar enclosure to the outside Weil lower

Once the finite cover and infinite-tail certificates establish \(\rho_T(t)\le\alpha w(t)+b\) on all real frequencies, multiplication by \(|\widehat f(t)|^2\) and integration give

\[
\boxed{d_E[f]\le\alpha d_A[f]+b\|f\|^2}
\]

for every \(f\) in the logarithmic form domain. Both terms on the right are integrable there, and the bounded symbol makes the left side finite already on \(H_T\). This is a sufficient pointwise-to-form argument. A pointwise bound need not be necessary for functions supported in \((-T,T)\), and failure of this particular scalar enclosure would not prove failure of every possible form estimate.

C-0107 gives the exact bounded identity

\[
P+K_{\rm pole}=L_T-D_E,\qquad
L_T(u,v)=e^{-|u-v|/2},\qquad L_T\ge0.
\]

Indeed its whole-line kernel has Fourier transform \(1/(t^2+1/4)\). Therefore the unchanged complete Weil form satisfies

\[
Q_W[f]=d_A[f]+(A_0-1)\|f\|^2
+\langle f,L_Tf\rangle-d_E[f]
\ge(1-\alpha)d_A[f]+(A_0-1-b)\|f\|^2.
\]

Keep the C-0107 Legendre-tail parameter distinct from the proof boundary 256. Write it as \(R_{\rm out}\). For \(f\in Q_NH_T\), the complete-band leakage bound and its reference coercivity are

\[
\int_{|t|\le R_{\rm out}}|\widehat f(t)|^2\frac{dt}{2\pi}
\le\min(1,\lambda_N(R_{\rm out}))\|f\|^2,
\]

\[
\mu_N(R_{\rm out})
=1+\big(w(R_{\rm out})-1\big)
\max\big(0,1-\lambda_N(R_{\rm out})\big),
\qquad d_A[f]\ge\mu_N(R_{\rm out})\|f\|^2.
\]

These follow by using \(w\ge1\) inside the band and \(w\ge w(R_{\rm out})\) outside it. The existing C-0104/C-0107 geometric estimate at \(R_{\rm out}=N/(3T)\) permits the explicit leakage upper bound

\[
\lambda_N(R_{\rm out})\le\frac{2N}{\pi}2^{-N}.
\]

One may substitute that upper bound for \(\lambda_N\) in the formula for \(\mu_N\) to obtain a valid, possibly weaker, lower bound. The qualified inputs declare both the inherited closed-policy anchor \(416/3\) and the already established fixed-source frequency256, always at the same \(N=312\). At the latter anchor use the exact complete formula \(\lambda_N(R)=(2TR/\pi)E_N(TR)\) from C-0104/C-0107, not the coarser \(N\ge3TR\) estimate. Its geometric ratio is \(192^2/(625\cdot627)<1\). This compares two previously justified reference estimates, not a support/dimension search, and neither anchor discards any archimedean energy.

Combining the estimates, with \(\alpha=1/4\), yields

\[
\boxed{Q_W[f]\ge
\left[\frac34\mu_N(R_{\rm out})+A_0-1-b\right]\|f\|^2,
\qquad f\in Q_NH_T\cap\mathcal D(d_A).}
\]

An executed certificate must round \(\mu_N\) and \(A_0\) downward and \(b\) upward before claiming a positive lower endpoint. A lower bound for \(w(R_{\rm out})\), together with an upper leakage bound, gives the required lower \(\mu_N\). No numerical positivity is asserted here. Even a strictly positive outside endpoint establishes only this outside form estimate. It supplies neither a new finite low/cross source nor a Schur sign; those cannot be inherited from an earlier matrix merely because the support is unchanged.

## 7. Limits of the conclusion

The compact-correction floor concerns a bounded scalar reference plus the discrete translations and compact corrections. Here \(d_A\) remains unbounded. Its logarithmic weight grows along the high modulations used to test compact-correction obstructions, so that theorem does not impose the same scalar floor on an estimate that retains \(\alpha d_A\). The algebraic cancellation alone would not evade that obstruction if this unbounded energy were discarded. A finite proof partition at 256 does not turn \(d_A\) into a compact-band reference.

This contract neither varies \(T\), \(\alpha\), support, nor matrix dimension. A successful scalar enclosure at this one fixed case would not prove an all-support family, a uniform coercivity margin, lower global computational cost, or an improvement in global-support efficiency. It would qualify only the stated discrepancy-to-energy interface and any separately executed outside inequality. It makes no production admission and leaves every earlier record immutable.
