# Quantitative Fourier bounded-minorant closure

- **Created:** `2026-10-25T14:24:24Z`
- **Status:** derived sufficient full-space criterion, with executed scalar bounds; the finite low-matrix sign is not evaluated
- **Evidence:** source/sign qualification in [fourier-qualification.md](fourier-qualification.md); actual constants in [data/scalar-controls-v1.json](data/scalar-controls-v1.json)

## Source, normalization and domain

Use the original smooth-test Weil form in Suzuki [arXiv2606.09096v3, §§1.1,2.4](https://arxiv.org/html/2606.09096v3). On H_T=L²(-T,T), extend f by zero and set hat f(t)=integral f(u)exp(-itu)du. Parseval uses dt/(2pi). Define

\[
A(t)=\Re\psi(1/4+it/2)-\log\pi,
\quad P=-\sum_{\log m<2T}\frac{2\Lambda(m)}{\sqrt m}J_{\log m},
\]

where J is the average of the compressed shift and its adjoint. For a real a and a finite band [-Omega,Omega],

\[
Q_W[f]=\langle f,H_0f\rangle+
\int_{|t|>\Omega}(A(t)-a)|\widehat f(t)|^2\frac{dt}{2\pi},
\]

\[
H_0=M+K,\quad M=aI+P,\quad
K=K_{\rm pole}+F_\Omega^*(A-a)F_\Omega,
\]

\[
\langle f,K_{\rm pole}f\rangle
=2|\langle f,\cosh(u/2)\rangle|^2
-2|\langle f,\sinh(u/2)\rangle|^2.
\]

Here F_Omega includes the factor1/sqrt(2pi). M and K are bounded on all H_T, and K is compact. The original form and exterior term need their logarithmic Fourier form domain; they are not bounded operators on all H_T. A positive H0 and a nonnegative exterior imply positivity on the original smooth tests without asserting an equality of complete operator domains.

## Whole exterior, not a finite frequency sample

[DLMF5.7.6](https://dlmf.nist.gov/5.7.E6) gives, x_k=k+1/4,

\[
A'(t)=\frac t2\sum_{k\ge0}\frac{x_k}{(x_k^2+t^2/4)^2}>0\quad(t>0).
\]

The derivative series converges locally uniformly. A is even. The finite signed-tail enclosure in the independent qualification, using4096 summands and512-bit Arb, gives

\[
A(256)-7/2>1/5.
\]

Thus A(t)-7/2>1/5 for every |t|>=256. Direct Arb digamma and the separately derived DLMF finite series agree within the latter's rigorous two-sided tail. This is an independent formula check within the same Arb trust premise, not an independent numerical library or a formal proof.

## Explicit compact complement

Let Pi_N retain scaled Legendre degrees0,...,N-1 and Q_N=I-Pi_N. Set c=T Omega and

\[
E_N(z)=\frac{(2N+1)z^{2N}}{((2N+1)!!)^2}
\left(1-\frac{z^2}{(2N+1)(2N+3)}\right)^{-1}.
\]

It is used only when its geometric ratio is below1. Rodrigues' formula gives ||Q_N exp(itu)||²<=2T E_N(T|t|). With beta=2c/pi and W=max(|A(0)-a|,|A(Omega)-a|),

\[
\|Q_N K_{\rm band}Q_N\|\le W\beta E_N(c),\qquad
\|Q_N K_{\rm band}\|\le W\sqrt{\beta E_N(c)}.
\]

The second inequality uses ||F_Omega||<=1; it bounds the entire one-sided map, not only its low compression. The exact signed rank-two pole gives

\[
\|Q_N K_{\rm pole}Q_N\|\le4Te^T E_N(T/2),\qquad
\|Q_N K_{\rm pole}\|\le4Te^T\sqrt{E_N(T/2)}.
\]

At a=7/2, Omega256 and N312, the captured rigorous rational endpoints imply, for each T in {3/5,1353/2048},

\[
\|P\|<9/8,\quad M\succeq(19/8)I,\quad
\|Q_NKQ_N\|<10^{-82},\quad\|Q_NK\|<10^{-40}.
\]

Both active arithmetic terms2,3 and their mutual products are retained. The norm allowance follows because T<log m<2T for each term and ||J_logm||=1/2. These first-window arithmetic constants do not apply automatically to larger supports.

## Full mixed Gram paid without new mixed-Gram integration

Write A_N=Pi_N H0 Pi_N, F_P=Q_N P Pi_N and F_K=Q_N K Pi_N. Let

\[
G_P=F_P^*F_P=\Pi_N P^2\Pi_N-(\Pi_NP\Pi_N)^2.
\]

This is the combined arithmetic square, not a sum of independent prime squares. The complete cross Gram is

\[
G=(F_P+F_K)^*(F_P+F_K).
\]

Since ||F_P||<9/8 and ||F_K||<10^-40, its mixed terms and K-square obey the Loewner upper bound

\[
G\preceq G_P+(2\|F_P\|\|F_K\|+\|F_K\|^2)I
\prec G_P+3\cdot10^{-40}I.
\]

Nothing is omitted or assumed positive: the signed P/K interaction is bounded in norm. The double-tail block C_N=Q_NH0Q_N satisfies

\[
C_N\succeq dI,\qquad d=19/8-10^{-82}>0.
\]

Exact bounded-operator square completion therefore proves the finite sufficient criterion

\[
\boxed{\quad
A_N-\frac{G_P+3\cdot10^{-40}I}{19/8-10^{-82}}\succ0
\quad\Longrightarrow\quad H_0\succ0
\quad\Longrightarrow\quad Q_W>0\text{ on nonzero smooth tests}.
\quad}
\]

Rigorous low A_N and combined G_P enclosures, with all their errors paid, are still required to use this implication. The low-matrix sign has not been computed. A failed sufficient matrix does not prove H0 negative. A certified negative direction of H0 would reject this bounded minorant at the chosen parameters, not Weil positivity or the broader Fourier formulation.

## Why the time-band gap is not the pending positivity source

For the concentration operator B=F_Omega*F_Omega, delta*=1-||B|| is strictly positive qualitatively. Compactness plus the entire Fourier transform rules out an eigenvector of B with eigenvalue1. But the exact bump trial (1-(u/T)²)^p, p=floor(T Omega/2), gives

\[
\delta_*\le\frac{(p!)^2(4p+1)!}
{2^{2p}(2p+1)((2p)!)^2(T\Omega)^{2p}}.
\]

At the two supports this upper bound displays8.624e-66 and1.633e-72. These are upper obstructions, not lower certificates. The boxed criterion drops the nonnegative exterior and does not spend any delta* lower bound. Failure to compute a concentration lower gap therefore does not invalidate this strict-minorant route.

## Scope and support cost

This is a different full-space reference, not merely a new finite elimination order for C-0093's matched outside reference. It has no local2T<pi Taylor-radius condition. Nevertheless a>=m+sum c_m(1-log(m)/(2T)) is necessary for M>=mI, as seen from the normalized constant trial. Larger support can force larger a, hence larger Omega through A(Omega)>=a; c=T Omega enters every compact-tail bound. No unbounded support-covering family, cost advantage, optimal dimension, fresh fixed-support positivity or production admission follows from these controls.
