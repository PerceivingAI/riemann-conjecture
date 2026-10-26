# Compact corrections do not lower the arithmetic scalar floor

- **Created:** `2026-10-26T04:45:51Z`
- **Last updated:** `2026-10-26T05:00:39Z`

## Statement and scope

Fix a finite real number \(T\ge 7/2\). Work on the complex Hilbert space
\[
H_T=L^2((-T,T),dx),\qquad
\langle f,g\rangle=\int_{-T}^T\overline{f(x)}g(x)\,dx.
\]
Extend functions by zero to the real line and define the compressed physical translation by
\[
(U_\ell f)(x)=\widetilde f(x-\ell),\qquad -T<x<T.
\]
Then \(U_\ell^*=U_{-\ell}\) and \(\|U_\ell\|\le1\). Put
\[
\mathcal M_T=\{m\ge2:\Lambda(m)>0,\ \log m<2T\},\qquad
d_m=\frac{\Lambda(m)}{\sqrt m},\qquad
P_T=-\sum_{m\in\mathcal M_T}d_m(U_{\log m}+U_{-\log m}).
\]
The set \(\mathcal M_T\) is finite. In particular, \(P_T\) is bounded and self-adjoint. No commutativity of compressed translations is assumed.

**Theorem.** For every such \(T\), every bounded compact self-adjoint operator \(C:H_T\to H_T\), every \(b\in\mathbb R\), and every real \(\mu\ge0\),
\[
bI+P_T+C\ \ge\ \mu I
\quad\Longrightarrow\quad
b\ge\mu+a_*(T)>\mu+\frac3{20}e^T,
\tag{1}
\]
where
\[
a_*(T)=\sup_{\|h\|_2=1}\{-\langle h,P_Th\rangle\}.
\]
Thus nonnegativity requires the strict inequality \(b>(3/20)e^T\). Coercivity with a specified margin \(\mu>0\) requires \(b>\mu+(3/20)e^T\). The compact correction may depend arbitrarily on \(T\); no bound uniform in \(T\) is needed.

The first inequality in (1) is non-strict. The strict second inequality comes from the quantitative cap bound, not from a spectral endpoint argument. This distinction matters: with \(C=0\), the choice \(b=\mu+a_*(T)\) does satisfy \(bI+P_T\ge\mu I\).

The theorem concerns precisely a scalar multiple of the identity, the bounded arithmetic operator, and a bounded compact correction at fixed support. It says nothing of this form about an arbitrary energy-dependent reference.

The non-strict floor \(b\ge\mu+a_*(T)\) also holds for every fixed \(T>0\), by exactly the recurrence and modulation proof below. Only the explicit exponential lower bound on \(a_*(T)\) needs \(T\ge7/2\). This includes an empty active set, for which \(P_T=0\) and \(a_*(T)=0\).

## The cap bound and its numerical constant

For completeness, the arithmetic input used in [C0102's cap proof](../2026-10-26T001954Z-quantitative-reference-cutoff/quantitative-envelope-v1.md) is recorded explicitly. Write
\[
\psi(x)=\sum_{m\le x}\Lambda(m).
\]
The only external arithmetic estimates needed here are the unconditional Rosser–Schoenfeld inequalities
\[
\psi(x)\ge\frac9{10}x\quad(x\ge563),\qquad
\psi(x)\le\frac{21}{20}x\quad(x>0).
\tag{2}
\]
They follow from their 1962 Theorem 4, equation 3.14, and Theorem 12, equation 3.35, as detailed in the cited cap proof. The source is [Rosser and Schoenfeld, Illinois Journal of Mathematics 6, 64–94](https://doi.org/10.1215/ijm/1255631807). No zero-free premise or Weil positivity assumption is used.

Let
\[
f_T=\frac1{\sqrt2}\mathbf1_{[-T,-T+1]\,\cup\,[T-1,T]}.
\]
Its norm is one. For \(\ell=2T-\delta\) with \(1/2\le\delta\le3/2\), the overlap of a translated left cap with the right cap has length
\[
w(\ell)=1-|\delta-1|\ge\frac12.
\]
Each signed translation contributes half this length because of the normalization. Therefore
\[
\langle f_T,(U_\ell+U_{-\ell})f_T\rangle=w(\ell)\ge\frac12.
\]
All other translation correlations of this nonnegative function are nonnegative. Set
\[
L=e^{2T-3/2},\qquad V=e^{2T-1/2}.
\]
Every \(m\) with \(L<m\le V\) is strictly active and satisfies \(1/\sqrt m\ge e^{-T}\). Also \(V\ge e^{13/2}>563\). Consequently (2) gives
\[
\begin{aligned}
r_T:=-\langle f_T,P_Tf_T\rangle
&\ge\frac12e^{-T}\{\psi(V)-\psi(L)\}\\
&\ge\frac12\left(\frac9{10}e^{-1/2}-\frac{21}{20}e^{-3/2}\right)e^T
>\frac3{20}e^T.
\end{aligned}
\tag{3}
\]
Endpoints cause no extra term: the difference of \(\psi\) counts exactly \(L<m\le V\), and \(V<e^{2T}\).

The strict numerical comparison in (3) can be checked without decimal approximations. The exponential series gives \(e^{1/2}<5/3\), by bounding \(1/k!\le2^{1-k}\) for \(k\ge2\), with strictness for some terms. It also gives
\[
e^{3/2}>\sum_{k=0}^5\frac{(3/2)^k}{k!}=\frac{5711}{1280}>\frac{40}{9}.
\]
Hence the constant multiplying \(e^T\) in (3) is greater than
\[
\frac12\left(\frac9{10}\frac35-\frac{21}{20}\frac9{40}\right)
=\frac{243}{1600}>\frac3{20}.
\]
This establishes the strict margin needed below.

## An unbounded simultaneous recurrence sequence

We first prove an elementary recurrence statement for arbitrary finitely many real numbers \(\ell_1,\ldots,\ell_N\). There exist positive integers \(n_j\to\infty\) such that
\[
\max_{1\le k\le N}|e^{in_j\ell_k}-1|\longrightarrow0.
\tag{4}
\]
No rational independence is required.

Put \(\alpha_k=\ell_k/(2\pi)\), and let \(\|u\|_{\mathbb R/\mathbb Z}\) denote the distance to the nearest integer. For each integer \(Q\ge2\), partition \([0,1)^N\) into \(Q^N\) half-open cubes of side \(1/Q\). Consider the \(Q^N+1\) points
\[
(\{r\alpha_1\},\ldots,\{r\alpha_N\}),\qquad 0\le r\le Q^N.
\]
Two lie in the same cube. Subtracting their indices produces an integer \(q_Q\) with
\[
1\le q_Q\le Q^N,\qquad
\max_k\|q_Q\alpha_k\|_{\mathbb R/\mathbb Z}<\frac1Q.
\tag{5}
\]
Choose one such \(q_Q\) for every \(Q\).

If the integers \(q_Q\) are unbounded, they have a subsequence \(q_{Q_j}\to\infty\) with \(Q_j\to\infty\). To see that both can increase, discard the finitely many indices \(Q\) below any prescribed bound, then choose a remaining value exceeding the preceding chosen value. Set \(n_j=q_{Q_j}\). Equation (5), together with
\[
|e^{2\pi iu}-1|\le2\pi\|u\|_{\mathbb R/\mathbb Z},
\]
proves (4).

If the integers \(q_Q\) are bounded, some fixed positive integer \(q_0\) occurs for infinitely many \(Q\). Passing to those \(Q\to\infty\) in (5) yields
\[
\|q_0\alpha_k\|_{\mathbb R/\mathbb Z}=0\quad\text{for every }k.
\]
Thus \(q_0\) is an exact common period of all phases. Take \(n_j=jq_0\); the phases in (4) are then identically one. More generally, even a bounded subsequence of the chosen denominators already gives this exact-period alternative. This treats the case that an argument using small denominators alone would otherwise miss. For an empty list of phases, simply take \(n_j=j\).

Apply this result to the finite list \(\ell_m=\log m\), \(m\in\mathcal M_T\), at the fixed value of \(T\). The recurrence sequence need not work uniformly over different supports.

## Modulations preserve the arithmetic Rayleigh quotient

Define the unitary modulation
\[
(M_nf)(x)=e^{inx}f(x).
\]
Zero extension does not change the identity
\[
M_n^*U_\ell M_n=e^{-in\ell}U_\ell.
\]
For the recurrence sequence just constructed,
\[
\begin{aligned}
\|M_{n_j}^*P_TM_{n_j}-P_T\|
&\le2\sum_{m\in\mathcal M_T}d_m|e^{in_j\log m}-1|\\
&\longrightarrow0.
\end{aligned}
\tag{6}
\]
The finite sum is essential here. In particular, for every fixed unit vector \(h\in H_T\), the vectors \(h_j=M_{n_j}h\) satisfy
\[
\|h_j\|_2=1,\qquad
\langle h_j,P_Th_j\rangle\longrightarrow\langle h,P_Th\rangle.
\tag{7}
\]

These same vectors converge weakly to zero. Indeed, for any \(g\in H_T\), the product \(\overline g h\) lies in \(L^1(-T,T)\) by Cauchy–Schwarz, and
\[
\langle g,h_j\rangle=\int_{-T}^T\overline{g(x)}h(x)e^{in_jx}\,dx\longrightarrow0.
\tag{8}
\]
An elementary proof of this last limit is to approximate \(\overline gh\) in \(L^1\) by a finite step function on intervals. The integral of \(e^{inx}\) on one interval has modulus at most \(2/|n|\), so the step-function integral tends to zero. The approximation error is at most its \(L^1\) norm, independently of \(n\). Letting that error tend to zero proves (8).

Compactness now implies
\[
\|Ch_j\|_2\longrightarrow0,\qquad
\langle h_j,Ch_j\rangle\longrightarrow0.
\tag{9}
\]
For a direct proof, if the first limit failed there would be a subsequence with norms bounded away from zero. Compactness would give a further subsequence converging in norm to some \(y\). For every \(g\), boundedness of \(C^*\) and (8) give \(\langle g,Ch_j\rangle=\langle C^*g,h_j\rangle\to0\); hence \(y=0\), a contradiction. The form limit follows from Cauchy–Schwarz.

If \(bI+P_T+C\ge\mu I\), apply it to \(h_j\) and pass to the limit using (7) and (9). This yields
\[
b+\langle h,P_Th\rangle\ge\mu.
\]
It holds for every fixed unit \(h\), so \(b\ge\mu+a_*(T)\). Taking \(h=f_T\) and using (3) proves (1). The result supplies a necessary condition, not a sufficient condition for a prescribed compact correction.

### Smooth trial vectors are available

The indicator caps are legitimate vectors for the bounded operators above. If a smooth source domain is required, choose normalized \(h\in C_c^\infty(-T,T)\) arbitrarily close to \(f_T\) in \(L^2\). Density and boundedness give
\[
|\langle h,P_Th\rangle-\langle f_T,P_Tf_T\rangle|
\le2\|P_T\|\,\|h-f_T\|_2.
\]
The strict margin in (3) therefore allows a fixed smooth unit \(h\) with \(-\langle h,P_Th\rangle>(3/20)e^T\). Every \(M_{n_j}h\) remains in \(C_c^\infty(-T,T)\). Thus the stated strict floor already follows if the bounded-operator inequality is initially asserted only on that dense smooth domain. No passage involving an unbounded energy form is used in this density argument.

## Why logarithmic archimedean energy is different

The compact operator \(C\) in the theorem is not the unbounded archimedean multiplier. For example, with the unitary Fourier transform, the usual multiplier
\[
A(t)=\operatorname{Re}\psi\!\left(\frac14+\frac{it}{2}\right)-\log\pi
\]
is continuous, bounded below, and satisfies \(A(t)=\log(|t|/(2\pi))+o(1)\) as \(|t|\to\infty\). These multiplier properties, also used in the cited quantitative envelope, are relevant only to the following distinction. They are not inputs to (1).

For a nonzero smooth compactly supported \(h\), every modulation has finite archimedean form energy, but those energies tend to positive infinity:
\[
\int_{\mathbb R}A(t)|\widehat{M_{n_j}h}(t)|^2\,dt
=\int_{\mathbb R}A(s+n_j)|\widehat h(s)|^2\,ds\longrightarrow+\infty.
\tag{10}
\]
Here is a direct lower-bound argument. Choose \(R\) such that \(\int_{-R}^R|\widehat h(s)|^2ds>0\). The infimum of \(A(s+n_j)\) on \([-R,R]\) tends to positive infinity. The integral on the complement is bounded below by a fixed lower bound for \(A\), times the remaining Fourier mass. This proves (10). Finiteness for each \(j\) follows from the rapid decay of \(\widehat h\) and the logarithmic growth of \(A\).

Thus weakly null modulations make a bounded compact correction vanish, but make logarithmic energy grow. There is no contradiction. The theorem does not prohibit a genuinely energy-dependent positive comparison, and it does not decide the sign of the full Weil form.

## Finite-dimensional changes and Schur complements

Several common bounded corrections fall within the theorem at each fixed finite \(T\).

* A signed rank-two pole form represented by
  \[
  R=\gamma\,u\langle v,\cdot\rangle+\overline\gamma\,v\langle u,\cdot\rangle,
  \qquad u,v\in H_T,
  \]
  is bounded, self-adjoint and of rank at most two. Either sign is allowed. In particular, fixed exponential vectors on a finite interval belong to \(H_T\). The statement concerns such a bounded rank-two representation, not an identification of the entire archimedean form with it.
* If \(a\in L^\infty(\mathbb R)\) is real and supported in a finite frequency interval, its zero-extension, Fourier-multiplier, restriction operator on \(H_T\) is compact and self-adjoint. Indeed its convolution kernel \(k\) belongs to \(L^2(\mathbb R)\), and
  \[
  \int_{-T}^T\int_{-T}^T|k(x-y)|^2\,dx\,dy\le2T\|k\|_2^2<\infty.
  \]
  It is therefore Hilbert–Schmidt. Any finite sum of these pieces and finite-rank pieces is again compact. The bounded-symbol assumption is explicit; a singular or unbounded band contribution requires its own analysis.

Removing finitely many directions does not evade the same obstruction. Let \(F\subset H_T\) be finite-dimensional and \(\Pi_F\) its orthogonal projection. Weak convergence gives \(\|\Pi_Fh_j\|_2\to0\). Therefore
\[
v_j=(I-\Pi_F)h_j\in F^\perp,\qquad
\|v_j\|_2\to1,\qquad
\|v_j-h_j\|_2\to0.
\]
For all sufficiently large \(j\), normalize \(v_j\) to unit norm. Boundedness preserves both the limiting arithmetic Rayleigh quotient and the vanishing compact form. Consequently the same scalar floor is necessary even if the inequality is required only on \(F^\perp\).

An exact Schur rearrangement also cannot change positivity of the operator it represents. More specifically, consider a bounded self-adjoint block operator on \(F\oplus F^\perp\), with finite-dimensional \(F\), whose \(F\)-block \(B\) is strictly positive. If the off-diagonal block is \(L:F^\perp\to F\), the Schur complement is
\[
D-L^*B^{-1}L.
\]
The subtracted term is bounded, self-adjoint and finite-rank. If \(D\) is the compression of \(bI+P_T+C\), the normalized vectors above prove exactly the same necessary floor for this Schur complement. Even without the invertibility needed for that formula, positivity of the full block operator implies positivity on \(F^\perp\), which already gives the floor. Merely checking a finite-dimensional principal block does not establish positivity of the full operator.

These conclusions apply to exact bounded finite-dimensional eliminations and to corrections proved compact at fixed \(T\). They do not identify every reference, every Schur construction, or an unbounded inverse as compact. A reduction that retains an unbounded logarithmic energy is outside the scalar-plus-compact premise. Finite rearrangements and bounded signed pole or finite-band compact additions cannot remove the cost in (1), while the possibility of a genuinely energy-dependent argument remains open.
