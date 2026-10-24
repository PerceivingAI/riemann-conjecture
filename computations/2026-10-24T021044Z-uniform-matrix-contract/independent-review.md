Confirmed. Use the complete Schur lower enclosure
\[
L_m=A^- - U_m^+ - r_{\mathrm{res},m}D
\]
for the two exact parity-block tests, not a lower enclosure of \(U_m\).

For \(\Gamma_m>0\), choose the smallest even \(\ell>m\) satisfying
\[
w_\ell\Gamma_m\le \tfrac12\theta_m,
\qquad \theta_m=w_m\Gamma_m.
\]
Such an \(\ell\) exists because \(w_\ell\to0\). Tail nesting gives
\[
0\preceq U_\ell-H_K
\preceq w_\ell G_{K,\ell}
\preceq w_\ell G_{K,m}
\preceq w_\ell\Gamma_mD
\preceq\tfrac12\theta_mD.
\]
No new rows, new trace bound, or positive head margin are needed to justify this selection. A newly certified \(\Gamma_\ell\) may improve the bound further.

Qualifications:

- The selection is equivalent to \(w_\ell\le w_m/2\). Harmonic growth can make \(\ell\) very large; existence is not practical feasibility.
- If \(\Gamma_m=0\), the exact truncated tail vanishes, so no tail-driven refinement is needed.
- Each one-sided interval error may be budgeted at \(\theta_m/8\). Failure to attain that width must be addressed or reported; midpoint radii require the factor-two conversion already discussed.
- The full-residual allowance remains a nonvanishing floor.
- Exact positive definiteness of both blocks of \(L_m\) certifies positivity. An unsuccessful test is inconclusive without a separate negative directional upper.
- A hard degree/work budget is a resource stop with an unresolved result. It does not justify dropping the uncomputed tail.

This is valid accuracy-driven conditional refinement, without a positivity or practical-feasibility claim.
