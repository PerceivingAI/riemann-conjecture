# Independent analytical verification of the combined-Schur positive research candidate

- **Finding ID:** F-20261017-012
- **Created:** 2026-10-17T15:32:22Z
- **Last updated:** 2026-10-17T15:34:11Z
- **Type:** SOURCE_VERIFIED / independent analytical review and separate-source reference checks
- **Status:** **VERIFIED within research-side analytic/Arb trust; POSITIVE_CANDIDATE still PRE-THEOREM**
- **Mathematical object:** Combined \(S_{\rm comb}=A_{192}-\mu_{192}^{-1}B^*B\) at exact \(T=11/20\), with every \(V/P/R\) and \(2/3\) cross term, full Suzuki residual allowance and correct ordinary Legendre normalization.
- **Evidence:** [X-20261017-003](../computations/2026-10-17T150153Z-combined-schur-bounded-test/record.md) and independent [X-20261017-004](../computations/2026-10-17T153222Z-analytic-source-review/record.md).

## Audit result

The independent mathematical review rederived the scalar, \(J\), potential, signed two-sided prime shift and full residual scaling from Suzuki's primary source (arXiv:2606.09096v3 eqs. (2.2)–(2.5), (4.4)–(4.5). It independently differentiated the logarithmic subinterval antiderivatives, checked their endpoint limits and interval-domain conditions, verified the exact \(KD_N^{-1}K\) projection and all nine ordered cross terms, and confirmed the **LOWER** matrix's rigorously correct implication direction using the full residual \(\delta_K^2D_N\), row-radius Loewner inflation and positive full-tail complement.

Additional **executed** independent controls: six current fixed \(N=192\) low-form input intervals overlap independently assembled \(N=12\) entries; the full-tail complement overlaps after exact \(H_{192}-H_{12}\) adjustment; direct \(95\)-digit numerical quadrature at degree 96 agrees with \(VP\) and singular logarithmic cell primitives to about \(10^{-96}\) and \(10^{-98}\) respectively (**nonproof**); and a historical rigorous finite-tail projected Gram **lower** bound of about \(0.58693\) lies below the new rigorous full-Gram **upper** bound of about \(1.13606\) along the very same retained exact dyadic direction. No inconsistency was found.

The independent exact rational checker was hardened against malformed dyadic precision and complement/residual interval endpoints and then replayed **on the unchanged complete \(N=192\) rational matrix packet and rational congruence witness**. It again recomputed strict positive exact rational Gershgorin margins (minimum decimal display \(0.9999999993343024\)); adversarial packet/margin mutations were correctly rejected. Source, output hashes, exact controls and prior audit-script-only diagnostic corrections are in X-20261017-004.

## Necessary qualification

This validates source-level mathematics and independently checks specific analytical inputs, **not a second completely independent rigorous reconstruction of every high-dimensional transcendental matrix entry**. The full exact rational sign is independently checked **conditional on the source-provided rigorous Arb enclosure arguments**. Domain identity with the full canonical source operator remains unproved (positivity on the stated original admissible class follows from source-form agreement). No new theorem profile, Rust/Lean formalization, v2 admission or RH proof follows automatically.

**Disposition: `POSITIVE_CANDIDATE`, pre-theorem, survives independent mathematical/source audit.** The proper next activity is to classify and close the bounded research phase with this trust boundary intact, not to extend dimensions or promote a theorem.
