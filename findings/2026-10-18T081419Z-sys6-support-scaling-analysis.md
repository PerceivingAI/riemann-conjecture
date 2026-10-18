# SYS-6.2 — Conservative complement growth and mixed-Gram scaling

- **Finding ID:** F-20261018-004
- **Created:** 2026-10-18T08:14:19Z
- **Last updated:** 2026-10-18T08:14:19Z
- **Type:** RIGOROUS SCALAR SUFFICIENT-BOUND SCALING + ARB TRUNCATED-GRAM DIAGNOSTIC SYNTHESIS
- **Status:** VERIFIED **for selected inputs and stated bounds**, with explicit limits on theorem conclusions
- **Evidence:** [X-20261018-004](../computations/2026-10-18T080600Z-sys6-support-scaling/record.md) and its four JSON outputs.
- **Dependencies:** Existing C-0058, C-0063..C-0068, unchanged mixed-Gram assembler, Suzuki/R-0028 normalization.
- **Theorem admission:** **NONE**. Original v1 eight retained claims and one v3 C-0067 unchanged. RH unresolved.

## Rigorous observed scalar-bound facts

In the same \(K=32\) Suzuki/Arb full-tail sufficient estimate, the exact rational positivity check for \(\mu_N=H_N-c_T-\sum_m c_m b_m-\rho_R\) gives first passing cutoffs:

| Support T | Active terms | First N with certified \(\mu_N>0\) |
| --- | --- | ---: |
| 11/20 = 0.55 | 2,3 | **109** |
| 3/5 = 0.60 | 2,3 | **160** |
| 13/20 = 0.65 | 2,3 | **238** |
| 69/100 = 0.69 | 2,3 | **331** |
| 7/10 = 0.70 | 2,3,4 | **624** |

Each cutoff was checked with outward Arb-256 scalar enclosures and exact rational strict inequalities; values are *properties of a conservative bound*, not proven necessary dimensions of the actual Weil form, nor dimension cutoffs for **Schur** positivity. At \(N=192\), the same conservative \(\mu\) is positive at 0.55 and 0.60, but negative at 0.65; using a dimension already successful at 0.55 does **not** automatically pass even the simpler complement gate at 0.65.

As the support increases from 0.55 to 0.65 inside the fixed \(\{2,3\}\) arithmetic window, \(\rho_R\) upper grows approximately 2.329 to 2.940; \(c_T\) grows approximately 1.817 to 1.984, and the discrete arithmetic loss is unchanged. Just beyond \(T=\log2\) the \(m=4\) term appears and the \(m=2\) compressed-shift norm jumps from 1 to \(\sqrt2\). This is **a discontinuity of the crude sufficient bound**, not a discontinuity of Suzuki's true lowest eigenvalue (external EXT-0002), and no counterexample to positivity.

The harmonic-number high-mode control grows logarithmically in \(N\); holding the other conservative losses fixed requires roughly exponential cutoff growth in their size. The table establishes strong **bound-driven** dimensional pressure but **no all-support lower-bound obstruction** to the actual form or proof that such cutoffs are optimal.

## Independent source-interval and numerical observations

An additive research-only profile evaluated the **complete truncated \(V/P/R_K\) image Gram**, including \(2/3\) mixed prime terms, at \(T=0.55,0.60,0.65\), \(N=64\), Arb-384, and at \(0.55,0.60\), \(N=128\), Arb-768. All five assemblies succeeded with narrow rigorous input intervals at the specified precision. The signed mixed cross trace at \(N=64\) switches from +0.111808 at 0.55 to -0.072120 at 0.60 and -0.139747 at 0.65; the associated combined/separate trace ratios are respectively 1.01538, 0.99341 and 0.98874. These are **approximate trace displays**, not eigenvalue or inequality margins; they establish nonconstant mixed-image behavior but not cancellation in every low direction or Schur positivity. Retaining the complete mixed Gram avoids the mathematical loss of the older factor-three separated upper bound regardless of average trace signs.

**Precision is a separate bottleneck:** at \(N=64,T=0.55\), max Arb Gram entry interval width contracts from \(1.96\times10^{-5}\) at 256 bits to \(5.77\times10^{-44}\) at 384 bits. At \(N=128,T=0.55\), Arb-768 yields \(4.61\times10^{-86}\) in 33.6 s, reproducing the earlier rigorous profile's enclosure scale; a previous 384-bit profile of the *same mathematical object* had a catastrophic \(1.86\times10^{30}\) interval width (X-20261017-002). Narrow enclosures can be recovered by increasing precision, but neither precision nor increasing \(N\) alone establishes the positivity criterion at a new support.

The residual truncation norm remainder \(\delta_{K=32}\) increases from approximately \(9.83\times10^{-16}\) at 0.55 to \(3.19\times10^{-13}\) at 0.65. Its rigorous full-remainder allowance remains essential; the displayed traces are for \(R_K\) images only. Rigorous \(\rho_R\) (used in the complement) is substantially more influential over the executed range than this tiny \(\delta_K\).

## Interpretation and SYS-6.2 closure

- **Verified arithmetic/complement scaling:** the existing sufficient \(\mu_N\) bound becomes more expensive; increasing \(N\) restores \(\mu_N>0\) at the five selected supports, but its increasing cost is substantial and shifts abruptly after the next prime-power boundary.
- **Verified mixed Gram geometry:** support changes the signed cross interactions; average trace ratios are not extremal spectral evidence.
- **Verified numerical conditioning:** large increases in Arb precision may be required even to obtain narrow analytical enclosures at moderate dimensions.
- **Not verified:** a quantitative right extension beyond C-0067, any exact full-Schur positivity or negative direction at selected \(T>0.55\), a uniform \(N(T)\) or a support-independent proof, or a general mathematical no-go for the combined method.

**Disposition:** **CONDITIONALLY EXTENSIBLE, WITH A SCALING/CERTIFICATION BOTTLENECK AND NO NEW THEOREM.** This is enough to close the diagnostic obligations of SYS-6.2. The existing data argue **against multiplying isolated finite certificates without a general mathematical mechanism**, but do not justify declaring the combined-Schur route impossible. This finding records as-run evidence and the present mathematical classification; it is not a public prospective research roadmap.
