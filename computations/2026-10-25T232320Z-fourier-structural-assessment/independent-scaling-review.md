# Independent review of necessary reference growth

This written review preceded execution of the retained comparison calculation. Its mathematical verdict and explicit numerical-evidence limitation are preserved as received. The later canonical/isolated calculation receipts supply separate computational evidence.

Overall correctness: correct.

No mathematical findings requiring repair in `reference-scaling-obligation-v1.md`. The conclusions follow under the stated bounded-reference and complete-exterior hypotheses.

- **Constant trial and normalization (§1).** For \(0<\ell<2T\),
  \[
  \langle u_T,U_\ell u_T\rangle=\frac{2T-\ell}{2T}.
  \]
  Both signed shifts therefore contribute \(2-\ell/T\), giving the stated \(r(T)\). Nonnegativity implies \(a(T)\ge r(T)\); \(M_T\ge m(T)I\) implies \(a(T)\ge r(T)+m(T)\). C98’s arithmetic conventions assign \(d_m\) to **each** one-sided shift and give ordinary Legendre mass \(D_{00}=2\), confirming \(r(T)=-P_{00}/2\). The argument only tests the bounded arithmetic reference; it does not require the constant function to belong to the smooth Weil source domain.

- **Divergence (§2).** The finite Euler products contain every reciprocal \(1/n\) with \(n\le X\), so hypothetical convergence of \(\sum_p1/p\) contradicts harmonic-series divergence. The comparison \(\log p/\sqrt p\ge(\log2)/p\) is valid. Primes \(p\le e^T\) are active and have trial weight at least one. Thus \(r(T)\to\infty\), and \(a(T_j)\to\infty\) whenever \(T_j\to\infty\) and \(M_{T_j}\ge0\). No common coercivity constant is needed; even individual strict coercivity is unnecessary for this conclusion.

- **Exterior implication (§3).** With the usual finite nonnegative cutoff \(\Omega(T)\), nonnegativity of \(A(t)-a(T)\) for \(|t|>\Omega(T)\), followed by continuity from above, gives the correctly directed inequality
  \[
  a(T)\le A(\Omega(T)).
  \]
  C98 §2 supplies the same multiplier and its monotonicity. Boundedness of \(A\) on compact intervals then rules out any bounded subsequence of \(\Omega(T_j)\) when \(a(T_j)\to\infty\), proving \(\Omega(T_j)\to\infty\).

- **Tail prerequisite (§4).** C98 §3 uses exactly the displayed geometric ratio. For nonnegative integer \(N\),
  \[
  c^2<(2N+1)(2N+3)=4(N+1)^2-1
  \iff N>\frac{\sqrt{c^2+1}}2-1.
  \]
  Since \(T_j\Omega(T_j)\to\infty\), this particular enclosure requires \(N_j\to\infty\). This is not a minimum positivity dimension or a sufficient small-error condition.

The scope restrictions are preserved: failure of positivity of \(M_T\) is not identified with negativity of \(H_0\) or the Weil form; no quantitative growth rate, global computational law, or obstruction to other decompositions is established.

**Evidence limitation:** the sentence in §1 about an “accompanying comparison calculation” was not substantiated by the inspected bundle: its `data/` directory was empty. That numerical comparison is not needed for the mathematical proof and is not endorsed by this review. No numerical verification, source replay, tests, builds, linting, formatting, or edits were performed.

Confidence: 0.99 for the mathematical assessment.
