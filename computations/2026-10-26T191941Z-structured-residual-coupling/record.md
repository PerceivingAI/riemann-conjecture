# Exact structured residual coupling and complete control-case error budget

- **Computation ID:** X-20261026-011
- **Created:** 2026-10-26T19:19:41Z
- **Last updated:** 2026-10-26T19:48:35Z
- **Status:** COMPLETE, independently accepted exact whole-map residual representation and model-error budget
- **Claim / finding:** C-0117 / F-20261026-011
- **Assessment:** QUALIFIED residual-aware operation. No full mixed weighted Gram, new Schur sign or support extension is established.

## Objective and unchanged source

C-0116 rejects treating the full residual cross as an independent isotropic error at existing T3/4,N312. This operation instead RETAINS its signed finite action inside the combined source before forming the energy-weighted Gram. It does not claim that the old residual norm was false, make that stopped completion pass, or establish a new full positivity theorem.

Use the actual C-0063/C-0115 split B=Q(V+P+R)Pi with ordinary Legendre mass D_n=2/(2n+1). R includes both signed pole sectors. V/P/R correlations must be retained. [Inputs](qualification-inputs-v1.json) fix the same support/projection and derive the approximation order from a verified existing-control budget, not from a favorable Schur sign or hardware allowance. Canonical residual helpers are reused UNCHANGED; no root library, CLI, dependency, schema or theorem-admission change.

## Exact whole-low residual representation

[The complete derivation](structured-residual-contract-v1.md) uses the existing exact positive-side Taylor coefficients of the full residual kernel. Even polynomial degrees below N have range below N and vanish from Q R_K Pi. For odd d, the actual integral action is2d! times a(d+1)-fold primitive plus a boundary polynomial of degree<=d. The latter is killed by Q_N, not assumed zero.

For even K with2K<N,

    Q_N R_K Pi_N=P_[N,N+K) R_K P_[N-K,N).

This identity controls ALL low directions, not sampled columns. At the derived K56, input degrees256..311 map only to output degrees312..367. All other low columns and higher outputs vanish exactly for the MODEL. The full residual is NOT asserted to vanish there; the complete operator remainder pays every omitted mode.

The exported matrix contains ordinary polynomial OUTPUT COEFFICIENTS U_mn. Inner products are D_m U_mn, and output norm is sum D_m|sum U_mn x_n|². No hidden normalized mass conversion or column-count factor. All57 kernel coefficients, including even/polar terms required in the actual LOW block, remain serialized. Their disappearance from this cross does not authorize discarding them from A_K.

## Complete infinite remainder and signed-model interface

The canonical full regular-plus-polar tail at2T gives ||R-R_K||<=delta_K=2T*tail_radius(2T,K). This uses2T<pi, satisfied here. No global-support range is claimed, no canonical refusal is weakened and no omitted polar term is set to zero.

Let A_K retain the actual low harmonic,V,P and full R_K terms. Define B_K=Q(V+P+R_K)Pi and its COMPLETE supported weighted Gram G_K. The residual stays inside the signed combined source before multiplication, so V/R_K and P/R_K mixed terms remain mandatory.

C-0085/C-0097/C-0115 give b_K=pi/2+49/32+1/300000+delta>=||B_K||. With m1/3 and eta_low=1-9e-49,

    S_true>=A_K-G_K/eta_low-Lambda I,
    Lambda=delta+(2 b_K delta/m+delta²/m)/eta_low.

This pays both low-block and full infinite coupling approximation errors. It does NOT evaluate A_K or G_K, pay their still-uncomputed numerical integration errors, or prove this sufficient lower positive.

## Genuine full-gap control and derived order

Reuse the SHA-bound accepted C-0100 positive proof only at its ALREADY PROVED support. Its two finite mass-normalized gaps, old tail mu=63/32-4e-49 and bounded-source cross upper49/32+2e-24 yield C-0086's full-gap lower

    ell=min(g/[1+2(b0/mu)^2],mu/2)>1e-15.

The independent consumer reconstructs the physical-mass transform trace and exact gap conversion. The nonnegative complete exterior transfers this known H0 lower to the actual form. Adopt ell0=1e-15. This is NOT the gap of the new energy-reference Schur matrix, a fresh analytical replay of the old proof, or positivity assumed at an unproved support. C-0116's Rayleigh UPPERS are never used as gap lowers.

The predeclared policy chooses the FIRST EVEN K with the complete published remainder<=ell0/1024. Every preceding order is retained and independently checked. The selected K56 obeys2K<N and the full model-error target Lambda<=ell0/16. No projection/support grid, precision ladder or sign-driven adjustment occurs.

| Qualified quantity | Outward display |
| --- | --- |
| Exact coefficient map | 56 by56,3136 checked entries,812 nonzero |
| Complete $\lVert R-R_{56}\rVert$ upper | 9.152e-19 |
| Complete residual-model error allowance Lambda upper | 1.794913e-17 |
| Adopted known full-form control lower ell0 | 1e-15 |
| Whole-low necessary-budget lower ell0-delta-Lambda | greater than9.81135e-16 |

Consequently A_K-Lambda I>=7ell0 I/8 on the WHOLE low space. This passes the NECESSARY residual-error budget that the earlier isotropic treatment failed. Subtracting G_K/eta_low remains an unresolved obligation. A physical-form lower is not silently substituted for an unknown new-reference Schur gap.

## Retained critical directions

Both actual C-0116 polynomial combinations are SHA-bound inputs. Exact input-strip masses, exact model output coefficients and physical output norms are reconstructed. Including the complete remainder, their unit-normalized actual residual CROSS weighted-image uppers are below2.679e-36 even and7.461e-36 odd. These are diagnostic source-component bounds, not independent positivity allowances or a replacement for mixed V/P/R_K correlation.

The improvement is REPRESENTATIONAL: R_K is included rather than discarded as uncertainty, and only its actual analytic remainder is charged. The original full one-sided residual-cross norm and its stopped isotropic completion remain unchanged and valid within their historical scope.

## Independent verification and actual controls

The source uses the canonical exact Bernoulli coefficients and Legendre primitive walks. The independent consumer imports NO producer/project module. It reconstructs all coefficients through the formal exponential quotient, integrates exact Rodrigues power polynomials, strips high Legendre terms and checks every one of3136 matrix entries, including both parity sectors and812 nonzeros. It independently computes the complete regular/polar tail, derives the inherited mass-gap conversion, checks all prior even orders and reconstructs both critical images and the whole-low budget.

[Independent audit](data/independent-audit-v1.json) passes at768 scalar bits against source512; matrix algebra is exact rational. [Separate read-only proof/code/output review](independent-review.md) approves the representation, normalization, remainder and limited conclusion. Shared FLINT/Arb correctness and the registered source/tail/control premises remain explicit. This is not a second numerical library, formal kernel result or production certificate.

Three actual false mathematical inputs reject with exit1 and NO success output: altered signed band entry, unpaid infinite remainder and forged whole-low error allowance. [Summary](data/rejection-summary.json) binds exact bytes and receipts. Production Rust exit semantics are not changed.

## Reproduction and byte identities

From the repository root, use fresh output paths:

```text
uv run --locked python -B computations/2026-10-26T191941Z-structured-residual-coupling/qualify-structured-v1.py --output <fresh-source.json>
uv run --locked python -B computations/2026-10-26T191941Z-structured-residual-coupling/verify-structured-v1.py <fresh-source.json> --output <fresh-audit.json>
```

The [thirteen-file closure](source-v1/manifest.json) includes both mathematical programs, declarations/runner, all four imported frozen canonical helper files, pyproject/lock, the exact accepted positive proof and critical witness input. The producer enforces project imports under its captured root. Isolated Python with bytecode disabled regenerates source/audit byte-identically. [Replay summary](data/replay-summary.json) records:

- Source SHA256 `afa2a31af3f25fbe1e75aa36633c2be70433fea0479e0d4bea90cd1899f2d01b`.
- Audit SHA256 `97355f8e996d51166b7c1e26c119b0eab5b3d4e079f70a04fca45ee1bd69318e`.

The first source takes0.744s and full independent audit1.190s. These are actual residual-map operations, NOT a matched full-criterion speedup or a full Gram benchmark. No failed mathematical execution, changed source version or parameter retry occurs. Environment is Python3.14.0/python-flint0.9.0; baseline0a10e5aef2ee451d224028f7746c55369002b36f with uncommitted research source, not clean production-certificate provenance.

[Preservation](data/preservation-check.json) validates23 earlier public seals and1282 historical members plus16 protected public source/test/configuration files. Old coefficient/tail helpers, research procedures, tests and artifacts retain their bytes. The new root manifest is written last. No root tool/dependency upgrade, permanent test suite, cloud/GPU operation, full default suite or Rust/Lean acceptance.

## Qualification decision and remaining work

QUALIFIED exact residual-aware operation and whole-low model-error interface at the existing control. The former low-source identity-floor obstruction is removed for this new representation, not retroactively repaired in the stopped completion. This is a complete implemented/audited residual map and paid approximation, not just an asserted formal cancellation.

The actual A_K, complete signed weighted V/P/R_K Gram and their computational enclosures are STILL NEEDED to decide whole-criterion usefulness. No full low/Gram arrays or Schur sign are produced here. No new support, arbitrary N increase, global gap/support law, all-support inference, originality or production admission. Frozen8v1/0v2/1v3 and RH unresolved remain unchanged.
