# EXT-0002 — Suzuki localized lowest-eigenvalue continuity and smooth-core characterization

- **External result ID:** `EXT-0002`
- **Recorded:** `2026-10-18T07:53:59Z`
- **Author:** Masatoshi Suzuki
- **Source:** *Weil's quadratic form via the screw function*, arXiv `2606.09096v3`, dated September 23, 2026, https://arxiv.org/html/2606.09096v3
- **Bibliography:** `R-0028`, whose earlier version/normalization citations are historical. **The statements relied upon here were checked against v3 specifically.**
- **Upstream theorem identifiers:** Theorem 1.1, Corollary 1.2, Theorem 1.3; introductory Weil equivalence in §1.1
- **Status:** EXTERNAL PAPER-LEVEL SOURCE STATEMENTS CHECKED; independent reproof/Lean kernel replay **NOT PERFORMED**
- **Provenance/license:** arXiv-hosted author manuscript; arXiv page marks an arXiv.org perpetual non-exclusive license. No paper/source code has been imported or copied into this project; mathematical statements are cited and attributed.

## Exact externally sourced statements used

Fix \(a>0\). Suzuki defines the closed localized Weil quadratic form \(Q_W^a\), its self-adjoint operator \(A_a\) and the bottom of its spectrum
\[
\lambda_a=\inf_{0\ne f\in \mathfrak D(Q_W^a)}
\frac{Q_W^a(f)}{\|f\|_{L^2(-a,a)}^2}
\quad\text{(equation 1.7).}
\]

1. **Theorem 1.1** identifies \(A_a\) as the Friedrichs extension of the source's symmetric operator \(B_a\). This is an *external theorem*, not a proof that this repository's separately constructed full form operator has the identical entire operator domain.
2. **Corollary 1.2** identifies \(\lambda_a\) with the infimum of the localized Weil Rayleigh quotient over \(C_c^\infty(-a,a)\), not only an abstract extension-domain infimum.
3. **Theorem 1.3:** the function \(a\mapsto\lambda_a\) is continuous for \(a>0\), without assuming RH.
4. **Introduction §1.1:** Weil's classical criterion is \(Q_W(f)\ge0\) for all \(f\in C_c^\infty(\mathbb R)\), equivalent to RH. It does not demand a single positive support-independent coercivity constant.

**Repository use:** `C-0068` applies Corollary 1.2 and Theorem 1.3 to already verified, exactly fixed-support `C-0067`. Continuity implies an **existential** right neighborhood of positive \(\lambda_a\); it gives **no numerical radius**, no arbitrary chosen larger support, and no new local Arb/Rust certificate.

## Trust and source-version boundaries

- Checked against the v3 HTML manuscript sections, not by locally rederiving the source's continuity argument or independently proving all the canonical-domain results.
- The local source identification on the *smooth test class* is the separately audited `C-0063`/`C-0067` boundary. This deduction does **not** assert equality of the full independently constructed closed-form operator domain with Suzuki's canonical operator domain.
- Any unsupported identification of \(\lambda_a\) with a non-source, altered-normalization operator is invalid. The application is to **the same unscaled Weil functional on the shared test class**.
- This is *external theorem provenance*, **not** an independently replayed Lean theorem and **not** v1/v2/v3 certificate admission. No RH conclusion is obtained.
