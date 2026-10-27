# Fixed-support scalar reference contract

Created 2026-10-27. This contract fixes \(T=4/5\), \(\alpha=1/4\), and the reference floor \(m=1/3\). It specifies a scalar qualification, not a finite low/coupling calculation or a positivity decision for the complete Weil form. A successful execution is required before any numerical constant is called qualified. No value of \(\beta,R,N\), or \(\kappa\) is asserted by this document alone.

The initial [input packet](qualification-inputs-v1.json) remains unchanged. Its combined policy includes \(N>2K\). The scalar programs establish the intermediate minimum over even \(N\ge312\) without selecting \(K\). The final declaration must separately establish \(2K<N\). If that condition fails, the combined-policy cutoff must be increased and its scalar inequalities certified again. This is not a change to the combined policy.

## 1. Space, normalization, and complete source

Let \(H_T=L^2(-T,T)\), with zero extension to the real line, and use

\[
\widehat f(t)=\int_{\mathbb R}f(u)e^{-itu}\,du,
\qquad \|f\|^2=\int_{\mathbb R}|\widehat f(t)|^2\frac{dt}{2\pi}.
\]

Translations below are compressed to \(H_T\) only after forming their whole-line quadratic forms. Write \(U_l\) for translation by \(l\), and

\[
\mathcal M_T=\{p^k:\log(p^k)<2T\},\qquad
c_{p^k}=\frac{\log p}{\sqrt{p^k}}.
\]

Certified strict comparisons \(\log4<8/5<\log5\) give the complete active list \(\{2,3,4\}\). In particular \(\Lambda(4)=\log2\), so \(c_4=\log2/2\), not \(\log4/2\). The next prime power 5 is inactive; all larger prime powers are inactive by monotonicity. The programs also certify \(2T<\pi\). These are interval comparisons, not floating-point cutoff decisions. The strict active convention is used throughout. There is no arithmetic atom at the support endpoint.

For \(0<l<2T\), set

\[
dE(l)=\sum_{r\in\mathcal M_T}\Lambda(r)\delta_{\log r}(dl)-e^l\,dl,
\qquad
D_E=\int e^{-l/2}(U_l+U_{-l})\,dE(l).
\]

This bounded operator has the signed whole-line form

\[
d_E[f]=\int_{\mathbb R}\rho_T(t)|\widehat f(t)|^2\frac{dt}{2\pi},
\]

where, at every real frequency,

\[
\begin{split}
\rho_T(t)
&=2\sum_{r=2,3,4}c_r\cos(t\log r)
 -2\int_0^{2T}e^{l/2}\cos(tl)\,dl\\
&=2\sum_{r=2,3,4}c_r\cos(t\log r)
 -2\operatorname{Re}\frac{e^{(1/2+it)2T}-1}{1/2+it}.
\end{split}
\]

The denominator is nonsingular, including at zero. The symbol is even, smooth, and bounded. Finite variation and Plancherel justify the identity on all of \(H_T\), not only on the proof partition.

Define the archimedean multiplier and full logarithmic domain by

\[
A_F(t)=\operatorname{Re}\psi(1/4+it/2)-\log\pi,\quad A_0=A_F(0),
\quad w(t)=A_F(t)-A_0+1,
\]

\[
\mathcal D=\left\{f\in H_T:\int_{\mathbb R}w(t)|\widehat f(t)|^2\frac{dt}{2\pi}<\infty\right\}.
\]

The digamma difference identity, with \(y=t/2\), is

\[
w(t)=1+\sum_{n=0}^\infty
\frac{y^2}{(n+1/4)((n+1/4)^2+y^2)}.
\]

Every summand is nonnegative, even, and strictly increasing in positive \(t\). Hence \(w\ge1\) and \(w\) is increasing on the positive half-line. The whole unbounded weight is retained.

The complete Weil source at this support is

\[
Q_W[f]=q_{A_F}[f]+\langle f,L_T f\rangle-d_E[f],
\qquad L_T(u,v)=e^{-|u-v|/2}\ge0.
\]

Indeed, the continuum kernel in \(-D_E\), together with \(L_T\), is \(e^{|u-v|/2}+e^{-|u-v|/2}=2\cosh((u-v)/2)\), the signed pole kernel; the arithmetic term retains its negative sign. The full-line Fourier multiplier of \(L_T\) is \(1/(t^2+1/4)\). This proves its positive quadratic form without discarding the odd negative rank-one part of the pole representation. No source low matrix is evaluated here.

## 2. All-frequency discrepancy enclosure

The required scalar inequality is

\[
\rho_T(t)\le\alpha w(t)+\beta\qquad(t\in\mathbb R).
\]

Let \(S=2\sum c_r\). A global derivative bound is

\[
L_c=2\sum c_r\log r+8T(e^T-1),\qquad |\rho'_T|\le L_c.
\]

It follows by differentiating the finite continuum integral and using \(l\le2T\). Independent reconstruction also uses

\[
L_s=2\sum c_r\log r+8((T-1)e^T+1),\qquad 0<L_s<L_c,
\]

from evaluating \(2\int_0^{2T}l e^{l/2}\,dl\) exactly.

For a closed cell \([a,b]\), center \(z=(a+b)/2\), monotonicity gives

\[
\sup_{[a,b]}(\rho_T-\alpha w)
\le\rho_T(z)+L_c(b-a)/2-\alpha w(a).
\]

The initial cells have width \(1/4\) and exactly cover \([0,256]\). Adaptive midpoint replacement continues until the maximum certified leaf upper endpoint minus a certified pointwise lower witness is at most \(1/256\). All endpoints are exact rationals. The consumer checks the complete ordered partition, midpoint-subdivision lengths and alignment, every cell enclosure, the witness, the maximum, the gap, and refinement accounting. Shared closed endpoints cause no omission. This is a supremum enclosure, not a sampled maximum assumption.

The producer uses, for every \(t\ge256\),

\[
\rho_T(t)-\alpha w(t)
\le S+\frac{2(e^T+1)}{\sqrt{256^2+1/4}}-\alpha w(256).
\]

The consumer separately expands the real quotient, with \(q=t^2+1/4\), as

\[
\rho_T(t)=2\sum c_r\cos(t\log r)
-\frac{2e^T}{q}\left(\tfrac12\cos(2Tt)+t\sin(2Tt)\right)+\frac1q.
\]

Cauchy-Schwarz yields the sharper decreasing envelope

\[
\rho_T(t)-\alpha w(t)
\le S+\frac{2e^T}{\sqrt{256^2+1/4}}+\frac1{256^2+1/4}-\alpha w(256).
\]

Both estimates cover the entire infinite tail analytically. Evenness covers all negative frequencies. The publication rule is exactly

\[
\beta=\frac1{1024}\left\lceil1024\max(0,U_{\rm finite},U_\infty)\right\rceil.
\]

The finite gap is not a claimed global gap if the infinite-tail envelope dominates.

## 3. Independent energy reconstruction and arithmetic trust

The producer uses the unchanged canonical prime-power enumerator, archimedean evaluator, and complete Legendre-tail helper. Its symbol uses the complex exponential quotient. The consumer imports no project mathematics and uses the real trigonometric formula above. Both trust FLINT/Arb for enclosed arithmetic and transcendental operations. This is independent organization, not an independent implementation of arbitrary-precision arithmetic.

The consumer obtains

\[
A_0=-\gamma-\pi/2-3\log2-\log\pi
\]

from reflection and duplication. For \(w\), it sums the first \(L=128\) positive digamma-difference summands. With \(x=L+1/4\), the remaining sum is exactly

\[
\operatorname{Re}\psi(x+iy)-\psi(x).
\]

For \(p=64\) use

\[
D_p(z)=\log z-\frac1{2z}-\sum_{k=1}^{p-1}\frac{B_{2k}}{2kz^{2k}},\qquad
|\psi(z)-D_p(z)|\le\frac{|B_{2p}|}{2p(\operatorname{Re}z)^{2p}}
\quad(\operatorname{Re}z>0).
\]

Binet's digamma integral on the right half-plane gives the finite-expansion remainder

\[
R_p(z)=\frac{2(-1)^p}{z^{2p-2}}
\int_0^\infty\frac{t^{2p-1}}{(t^2+z^2)(e^{2\pi t}-1)}\,dt.
\]

For \(x=\operatorname{Re}z>0\), \(|z|\ge x\) and \(|t^2+z^2|\ge x^2\). Integrating the positive Bose moment gives \(2\int_0^\infty t^{2p-1}/(e^{2\pi t}-1)\,dt=|B_{2p}|/(2p)\), proving the displayed bound. Thus the difference of the two shifted digamma values has error at most twice that bound at \(x\), uniformly in \(y\). The complex logarithm is on the right half-plane. This is an explicit logarithmic remainder after a positive difference-series prefix, not a call to the producer's digamma evaluator. The consumer propagates rational interval endpoints for these errors.

Source evaluation uses 512 bits; audit evaluation uses 768 bits. Published rational intervals use at least 192 relative binary bits for small quantities and the same outward dyadic policy for quantities of larger magnitude. The nonnegative grid ceiling is exact. No decimal display is evidence. An unresolved comparison fails closed at the fixed precision; it does not select another alpha.

## 4. Whole-line reference and the first integer anchor

Integration of the discrepancy inequality on \(\mathcal D\) gives

\[
d_E[f]\le\alpha q_w[f]+\beta\|f\|^2.
\]

Consequently

\[
Q_W[f]\ge q_g[f],\qquad
 g(t)=(1-\alpha)A_F(t)+\alpha A_0-\alpha-\beta.
\]

The notation \(q_g\) always means the entire integral \(\int_{\mathbb R}g(t)|\widehat f(t)|^2dt/(2\pi)\). It is not a band restriction. Its form domain is \(\mathcal D\), since it differs from a positive multiple of \(w\) by a constant. Write \(g_0=g(0)=A_0-\alpha-\beta\). The multiplier \(g\) is even and increasing on nonnegative frequencies.

Choose the least integer \(R\ge256\) for which

\[
g(R)\ge m+1/64.
\]

If \(R>256\), the consumer certifies \(g(R-1)<m+1/64\). Monotonicity then proves failure of every preceding allowed integer. If \(R=256\), no predecessor is in the allowed set. The old support's comparison at 256 is not reused. All target constants are recomputed. The scalar construction also requires \(g_0<m\); failure of that comparison or any strict inverse-weight comparison is reported as a missing premise, not hidden by a parameter search.

## 5. Complete Legendre leakage and the scalar policy minimum

The physical orthonormal basis is

\[
\phi_n(u)=\sqrt{\frac{2n+1}{2T}}P_n(u/T),\qquad
\widehat\phi_n(t)=\sqrt{2T(2n+1)}(-i)^n j_n(Tt).
\]

Let \(\Pi_N\) project onto degrees \(0,\ldots,N-1\), and \(Q_N=I-\Pi_N\). This specifies both parities and the physical mass normalization. For \(c=TR\), define

\[
r_N(c)=\frac{c^2}{(2N+1)(2N+3)},\qquad
\lambda_N(R)=\frac{2c}{\pi}
\frac{(2N+1)c^{2N}}{((2N+1)!!)^2}\frac1{1-r_N(c)}.
\]

The formula is used only when \(r_N(c)<1\). The complete spherical-Bessel bound \(|j_n(s)|\le |s|^n/(2n+1)!!\), followed by the geometric ratio bound for every \(n\ge N\), proves

\[
\int_{|t|\le R}|\widehat f(t)|^2\frac{dt}{2\pi}
\le\lambda_N(R)\|f\|^2\qquad(f\in Q_NH_T).
\]

For clarity, the trace estimate before the geometric sum is \((2c/\pi)\sum_{n\ge N}(2n+1)c^{2n}/((2n+1)!!)^2\). It bounds the complete infinite Legendre complement, not a sampled finite tail. No parity or physical factor is omitted. The independent consumer reconstructs the double factorial by \((2N+1)!/(2^N N!)\).

Since \(g\ge g_0\) everywhere and \(g\ge g(R)\) outside the band,

\[
q_g[f]\ge\left[g(R)-(g(R)-g_0)\lambda_N(R)\right]\|f\|^2.
\]

Choose the least even \(N\ge312\) for which the ratio is below one and both

\[
g(R)-(g(R)-g_0)\lambda_N(R)\ge m,
\qquad
\frac{\epsilon}{m}\le2^{-128},\qquad
\epsilon=(m-g_0)\lambda_N(R)
\]

hold with certified directed endpoints. The consumer independently evaluates every preceding even \(N\). Each must have ratio at least one, or a certified upper endpoint for the outside expression strictly below \(m\), or a certified lower endpoint for \(\epsilon/m\) strictly above \(2^{-128}\). The final candidate must pass both comparisons. Indeterminate interval overlap is not evidence of failure or success.

This is the minimum for these declared sufficient scalar inequalities. It is not the minimum dimension for positivity, nor the combined-policy minimum until \(2K<N\) is separately established. No target low gap is assumed.

## 6. Entire positive reference and relative domination

Set \(h(t)=\max(m,g(t))\) on the whole line. The domains of \(q_h\) and \(q_g\) are both \(\mathcal D\), because their difference is bounded. Since \(g(R)>m\),

\[
0\le h(t)-g(t)\le(m-g_0)\mathbf1_{[-R,R]}(t).
\]

For \(f\in Q_NH_T\cap\mathcal D\), the complete leakage estimate gives

\[
q_h[f]-q_g[f]\le\epsilon\|f\|^2,
\qquad q_h[f]\ge m\|f\|^2.
\]

Therefore, with the exact qualified lower constant \(\eta=1-2^{-128}\),

\[
q_g[f]\ge(1-\epsilon/m)q_h[f]\ge\eta q_h[f].
\]

The separate outside inequality also proves \(q_g[f]\ge m\|f\|^2\). Relative domination does not follow merely from that latter scalar coercivity; the floor-difference leakage is explicitly paid.

## 7. Complete inverse-weight bound at the doubled cutoff

Set \(M=2N\), \(R_c=2R\), and \(a=1/g(R_c)\). Fresh evaluation must certify

\[
0<a<1/m.
\]

As \(h\ge m\) globally and \(h\ge g(R_c)\) outside \([-R_c,R_c]\),

\[
\frac1{h(t)}\le a+(1/m-a)\mathbf1_{[-R_c,R_c]}(t).
\]

Recompute the complete leakage \(\lambda_M(R_c)\) with its own exact geometric ratio. The consumer requires \(\lambda_M(R_c)<1\). For the bounded whole-line inverse-weight form compressed to the physical space,

\[
\langle f,\mathcal F^{-1}h^{-1}\mathcal F f\rangle
\le\kappa\|f\|^2,\qquad f\in Q_MH_T,
\]

\[
\kappa=a+(1/m-a)\lambda_M(R_c)<1/m.
\]

Fourier norms here use \(dt/(2\pi)\). This is an inverse Fourier-multiplier weight bound on the complete complement. It is not a claim that physical restriction, projection, Fourier multiplication, or an operator inverse commute. Any use in a supported inverse comparison needs its own valid variational argument.

## 8. Packet binding, execution, and scope

Producer CLI:

```text
python scripts/weil_t080_reference_qualification.py --inputs PATH --output FRESH_PATH
```

Independent consumer CLI:

```text
python scripts/verify_t080_reference_qualification.py --source PATH --inputs PATH --output FRESH_PATH
```

Both outputs require exclusive creation of a fresh path. Inputs and source packets reject nonexact JSON numbers and duplicate object keys. The source binds the exact input bytes, producer bytes, imported project module bytes, and namespace paths by SHA-256. The consumer checks those fingerprints and emits its own source/input/code hashes. The consumer contains no producer-math imports. Existing shared helpers and all earlier research versions remain unchanged.

Source format `t080-reference-qualification-v1` includes the full finite leaf partition, witness and gap, infinite-tail bound, beta, exact policy declarations, anchor and predecessor enclosures, every even-N policy trial, exact eta, and doubled-cutoff inverse controls. The audit format is `t080-reference-qualification-audit-v1`. Neither format exports a theorem proof, admits a production certificate, constructs the target low/Gram source, or asserts a complete positivity sign. The flags for those claims remain false. Parent selection of a low-model degree, error budgets, and any final target declaration are separate obligations.
