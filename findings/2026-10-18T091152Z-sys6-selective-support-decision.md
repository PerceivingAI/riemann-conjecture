# SYS-6.4 — A larger two-prime support fails the chosen N=192 Schur bound

- **Finding ID:** F-20261018-006
- **Created:** 2026-10-18T09:11:52Z
- **Last updated:** 2026-10-18T09:11:52Z
- **Type:** SELECTIVE SUPPORT PROOF-ADMISSION DECISION / SOURCE-ENCLOSED NEGATIVE SUFFICIENT-CRITERION DIRECTION
- **Status:** **RESEARCH-SOURCE NEGATIVE FOR CHOSEN BOUND, EXACT RATIONAL ARITHMETIC INDEPENDENTLY VERIFIED; NO NEW THEOREM ADMISSION**
- **Evidence:** [X-20261018-005](../computations/2026-10-18T090311Z-sys6-selective-support/record.md); original packet SHA-256 `44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b`.
- **Dependencies:** C-0058, C-0063–C-0067, C-0071, full mixed-Gram and residual source calculus. RH unresolved.

## Mathematical conclusion from the executed scope

At **T=3/5=0.60**, \(N=192,K=32,\eta=2^{-24}\), with active prime powers \(\{2,3\}\), the conservative high-tail coercivity bound **passes** (\(\underline\mu_{192}>0.184919985587\) as decimal display). Yet generator-side rigorously enclosed 1024-bit Arb full combined \(V/P/R_K\) input enclosures and an **exact rational odd-parity trial direction** give the strict negative upper inequality
\[
u^*\left(A_{T,192}-\underline\mu_{192}^{-1}B_{T,192}^*B_{T,192}\right)u
\ \le\ -3.12334042185\ldots<0.
\]
The strict sign uses exact rational fraction arithmetic; displayed decimals are not themselves proofs. The full Suzuki residual is covered by its norm remainder; all mixed Gram products are retained. A separate checker verified original source hashes and recomputed the exact negative bound without accepting the saved sign label. **It did not independently reconstruct the full analytical matrix**, so the outcome is a **source-trust-qualified research sign result, not new theorem admission**.

In particular, this establishes failure of the **specific selected conservative complement and full combined-Schur sufficient criterion at (0.60,192)**. It does **not** prove the actual Weil form has a negative direction, imply RH is false, or rule out different N, a stronger complementary estimate, or a different proof. The trial direction is in the **odd** Legendre parity sector; the conservative complement is not the failed gate. Floating min-eigenvalue \(-3.12334165635\) was only a direction selector. The exact vector, complete scalar rational enclosures and source fingerprints are retained.

## Why this changes the research assessment

The SYS-5 success at \(T=0.55,N=192\) cannot be **transported to a materially larger two-prime support** by holding N and the existing complement strategy fixed. SYS-6.2 only showed support-variable signed mixed *trace* corrections and increasing minimum complement dimensions; the present single bounded result decisively resolves a **full odd-parity sufficient-Schur sign** at \(T=0.60,N=192\).

It does **not** establish a structural no-go for all supports: the negative value is bound-specific, and the current \(\underline\mu\approx0.18492\) is weaker than the dimension's \(T=0.55\) complement. At the fixed tested direction \(\underline g/\overline a\approx0.27506\) identifies when the present derived negative certificate would cease being decisive, but that threshold does not imply that a stronger actual complement exists or that a larger N will be positive.

**Explicit SYS-6.4 admission decision: NO NEW ADMISSIONS.** There is no independently source-accepted positive new v3 certificate or new support theorem. Any selective proof extension must first have an independently justified *positive* full criterion and a full acceptance chain; none was obtained here. The existing eight v1 plus one v3 admitted results and the published C-0067 mathematical evidence are unchanged.

**SYS-6.4 COMPLETE:** one high-information support-selection test, a decisive bound-specific negative criterion and a transparent decision not to proliferate isolated new proof artifacts. All-Suzuki-support positivity remains open; RH unresolved. Private roadmap remains private.
