# Form ordering, head refinement and the residual-only obstruction

- **Created:** `2026-10-24T23:28:30Z`
- **Status:** Qualified derivations used by X-20261024-006

## Review roles

A separate agent implemented the analytical auditor and supplied the written form-order and head-refinement qualification before numerical execution. It later inspected the residual-only diagnostic and retained results read-only. It did not execute numerical jobs/tests or independently recompute file hashes. The parent executed the source, auditor, exact assessment, controls and isolated regeneration. The final separate review verdict is captured in `independent-review.json`.

The review found no mathematical correction necessary in these arguments. This is not an end-to-end Lean proof of the source identity or an independent third-party mathematical audit.

## Stronger complement

C-0088 and the inherited source form give, on the restricted tail form domain,

\[
c[q]\ge j[q]-(c_T+p+\rho_{\rm tail})\|q\|^2.
\]

For any exact positive mu below the independently reconstructed complement H_N-c_T-p-rho_tail,

\[
c[q]\ge\langle q,(\mu+J-H_N)q\rangle.
\]

The inherited inclusion of form domains, not equality of operator domains, allows inverse ordering C^-1<=C0^-1. This supports the sufficient reference S0=A-B*C0^-1 B. The double-tail residual norm cannot replace the full cross norm b=pi/2+p+rho_global. The full residual allowance delta*(1+2b/mu)+delta²/mu remains intact.

## Head accuracy

For fixed source,N,mu, the complete majorant

\[
U_m=w_mG+\sum_{N\le k<m}(w_k-w_m)t_k^*t_k
\]

is nonincreasing with m. All omitted energy is paid. Geometrically increasing retained row count is a valid accuracy schedule, not a claim that its error halves. Fixed truncation/residual errors remain payable. A negative sufficient lower is inconclusive unless supported by a genuine reference upper. The actual run instead obtains genuine negative uppers, so no further head stage is needed to decide this reference.

## Genuine upper and the complete source error

For each rational trial, a full low-form upper includes A_K uncertainty and delta times its exact physical squared norm. The inverse-energy lower is

\[
\left(\max\{0,\sqrt{J_-}-\delta\sqrt{\|z\|_D^2/\mu}\}\right)^2,
\]

with all bounds rounded outward. It retains the full source remainder and its cross effect. Omitting unresolved inverse-energy tails is safe because they are nonnegative. This directional upper uses reverse triangle, so it need not separately subtract the uniform b-based whole-space residual allowance again.

## Optimistic residual-only limit

The diagnostic constructs bar_mu=H16-cT_lower-p_lower, a rational upper for mu_star=H16-cT-p, and independently encloses mu_star at1536 bits. Subtracting lower endpoints is the correct direction. It then changes only the reference parameter. Signed source arrays and delta are not changed.

For0<mu<=mu_star<=bar_mu, diagonal spectral ordering yields C0(mu)<=C0(bar_mu), the inverse inequality reverses, and S0(mu)<=S0(bar_mu). The actual negative reference uppers at bar_mu therefore exclude rescue by any improvement solely to a nonnegative residual norm charge in that fixed family. No domination of the actual tail by the hypothetical reference is asserted or needed for this diagnostic.

This proves neither actual Schur/Weil negativity nor failure at another N, changed arithmetic budget, stronger tail form, other support or another method. The positive C-0087 result at the same support remains distinct and unchanged.
