# X-20261017-005 — Mathematical analytic-input source checks for the finite-support theorem gate

- **Created:** 2026-10-17T21:40:44Z
- **Last updated:** 2026-10-17T21:41:29Z
- **Type:** MATHEMATICAL_SOURCE_AUDIT / independent rational identity verification and nonproof reference integrals
- **Status:** **PASS for the scoped identities; NOT an independent all-entry analytical acceptance of the N=192 packet**
- **Related finding:** [F-20261017-014](../../findings/2026-10-17T214129Z-finite-support-theorem-analytic-proof-obligations.md).
- **Research input:** [X-20261017-003](../2026-10-17T150153Z-combined-schur-bounded-test/record.md) original immutable rational `T=11/20,N=192` packet.

## Reproducible command

```text
uv run --locked python -m scripts.audit_suzuki_math_closure --packet computations/2026-10-17T150153Z-combined-schur-bounded-test/data/matrix-N192.json.gz --output computations/2026-10-17T214044Z-sys5-analytic-proof-audit/data/analytic-identity-audit.json
```

**Exit:** 0. Primary source packet SHA-256 `655d481d638f8b6fba0f95d01a4bab45079d905fbc6cb4f3e822571729d4d7c1`; tested source `scripts/audit_suzuki_math_closure.py` SHA-256 `369531ec58196d5939d2fa6d4facc93d45aa18992d4821c0dc15140f20c35ad1`. JSON output SHA-256 `2727d45bc3080d16a850bb65e9ee06b27d73579942b7485c6abfbfa504e7ece4`.

### Independent results

| Check | Outcome | Mathematical status |
|---|---|---|
| Separate binomial endpoint-polynomial integration \(\int_{-1}^1 |x-y|^dy^kdy\), \(0\le d,k\le8\) | **81/81 exact rational polynomial equalities PASS** | Exact algebraic test; general formula justified by binomial expansion |
| Whole-interval \(\int x^nv(x)dx\), \(n=0,2,20,190\) | **4/4 high-precision references PASS** | Numerical diagnostic; full identity proved by differentiating a beta integral |
| Whole-interval \(\int x^nv(x)^2dx\), same \(n\) | **4/4 high-precision references PASS** | Numerical diagnostic; full identity proved by second beta derivative |
| Packet shape and active-term header | **PASS:** exactly \(2\times192\times193/2=37,056\) scalar interval slots; active \(m=2,3\) | Metadata/completeness, NOT verification of each analytic value |
| Original rational input/witness | **Preserved unchanged** | Existing independent rational Schur positivity holds relative to source inputs |

Eight nonproof numerical errors range from exact-at-displayed-precision zero to about \(4.14536\times10^{-76}\), at 75 digits of `mpmath` precision. These numerical comparisons **cannot** verify every \(N=192\) transcendental interval. The prior SYS-4 distinct low-form, \(VP\), \(PR_K\), complement, residual, projected-tail, and exact rational tests remain as-run evidence; no full-size experiment was repeated.

### Scope and closure

The source of \(V,V^2\) moments is mathematically accounted for by differentiating \(B(n+\frac12,s+1)\); the residual polynomials follow from exact split \(|x-y|\)-power integrals, and the existing source audit accounts for translation-cell moments and full Suzuki residual error. The complete packet and exact rational matrix theorem consequence remain intact.

**The independently closed all-entry analytical enclosure proof is still absent.** The verifier reads the generator's endpoint intervals rather than independently reproducing and certifying every transcendental entry. Therefore **no new finite-support theorem is admitted**, and the candidate retains `POSITIVE_CANDIDATE`, PRE-THEOREM. The precise mathematical trust boundary and proof statement are in F-20261017-014.
