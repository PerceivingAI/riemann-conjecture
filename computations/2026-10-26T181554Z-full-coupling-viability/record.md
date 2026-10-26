# Whole-low-space residual-completion obstruction

- **Computation ID:** X-20261026-010
- **Created:** 2026-10-26T18:15:54Z
- **Last updated:** 2026-10-26T18:55:12Z
- **Status:** COMPLETE, independently verified rejection of the specified isotropic residual completion on WHOLE312
- **Claim / finding:** C-0116 / F-20261026-010
- **Assessment:** STOP the norm-only isotropic completion. The exact supported energy criterion remains UNRESOLVED, not rejected.

## Complete criterion and necessary whole-space test

At existing T3/4,N312, C-0063/C-0115 give B=Q(V+P+R)Pi. The actual low A retains the full residual and both signed pole sectors. The existing alpha1/4,beta873/1024,m1/3 reference and full one-sided r=1/300000 residual allowance are reused. Their mathematical validity is not questioned.

Let C=Q(V+P)Pi, E=QR Pi and G_C be the COMPLETE supported Gram weighted by1/h. It retains the signed V/P mixed terms. C-0114's norm error completion gives

    G_B<=G_C+[2rho r/sqrt(m)+r²/m]I,
    rho>=sqrt(||G_C||).

Even with actual A, exact G_C and no arithmetic error, the completed sufficient lower obeys

    S_norm=A-eta^-1 G_C
           -eta^-1[2rho r/sqrt(m)+r²/m]I
           <=A-(1/30000000000)I.

This is an optimistic UPPER for a rejection, not a replacement of G_C by zero for positivity. An actual low Rayleigh upper below this floor rejects the WHOLE312 completion without generating its V/P Gram. Unknown low gaps and favorable cancellation laws are not assumed.

## Declared coupled screen and its limits

[Initial contract](coupled-witness-contract-v1.md) and [inputs](assessment-inputs-v1.json) use both complete parity blocks of low degrees156..311 and one auxiliary tail shell312..623. The projection remains312. A certified negative physical coupled witness could reject the entire sufficient matrix. A favorable finite block proves nothing about its full positivity.

The [floating screen](data/proposal-v1.json) gives minima about0.668302/0.669749. These are explicitly NON_PROOF; neither block is certified positive and no global exclusion of negative directions is inferred. Canonical combined2/3/4 arithmetic and every proposed coefficient remain retained. No generator or extension follows from this screen.

## Actual low source and full exterior

[The necessary floor contract](residual-completion-contract-v1.md) uses ALL degree<=311 polynomials with four endpoint zeros at both ends,304 dimensions split into152 per parity. This is not a pair of isolated Legendre modes. Coefficients are quantized on the declared40-bit grid.

The SHA-pinned C-0100 packet is a two-sided enclosure of bounded H0 low A, NOT actual full Weil A. Its original quadrature inflations remain present. The actual source upper uses

    q_W[f]=q_H0[f]+integral_(|t|>256)[A(t)-7/2]|Jf_phys(t)|² dt/(2pi).

All active2/3/4 arithmetic, signed poles and bounded Fourier terms stay in q_H0. The ENTIRE positive exterior is paid separately, so old bounded or conservative lower matrices are never substituted as new full-source uppers.

The exact endpoint jets put the physical zero extension in H4. C-0103's complete digamma envelope gives A(t)-7/2<=log(t/256)+1/2 outside256, with the endpoint scalar checked afresh. Full-line Plancherel bounds BOTH tails by the squared fourth-derivative norm divided by2(T*256)^8. [The terminating polynomial endpoint expansion](polynomial-exterior-completion-v1.md) gives a second complete bound. Both are published and their minimum is paid. No frequency grid replaces infinity.

The first Jacobi8 proposal minimizes H0 alone. Its complete actual-source uppers, about1.01e-5/0.007884, are valid and independently audited but do not reject the floor. These programs/results are preserved. [The second proposal](complete-form-proposal-v2.md) minimizes the COMPLETE Sobolev source upper minus the SAME fixed floor in the SAME endpoint-constrained space. The Jacobi4 fourth-derivative Gram is diagonal; mass-plus-exterior preconditioning preserves deficit sign. No support, projection, frequency anchor, precision, coefficient grid or target is increased. Floating signs only propose exact witnesses.

## Certified result

Exact endpoints and full witnesses are in [source2](data/floor-assessment-v2.json) and [independent audit2](data/independent-floor-audit-v2.json). Displays below are outward rounded.

| Parity witness | Actual full Weil Rayleigh upper | Whole norm-completion Rayleigh upper |
| --- | --- | --- |
| Even, degree310 | 5.804e-14 | -3.3275e-11 |
| Odd, degree311 | 7.239e-12 | -2.6094e-11 |

Both actual low uppers are below the identity charge1/30000000000. Either negative completed upper excludes positivity of the whole completed matrix. These are actual low Rayleigh UPPERS, not merely small conservative positivity margins. Exact eigenvalues and actual signs are not inferred from uppers alone. Existing C-0100 positivity remains unchanged.

Radius publication rounding does not explain the failure. C-0095's regular allowance term is111/33333248; its existing full norm allowance includes an additional nonnegative pole term. Even3*(111/33333248)^2 exceeds both certified low uppers. This is a property of that ALLOWANCE formula, not a lower bound on the actual residual norm.

## Independent verification and historical integrity

The1536-bit source reconstructs exact Jacobi polynomials and ordinary Legendre coefficients. Exact mass and endpoint traces are checked. Its complete H0 interval contraction retains every original analytic radius. Source2 also checks monomial mass against exact Legendre orthogonality.

The2048-bit independent consumer imports no producer or project module. It uses explicit binomial Jacobi polynomials, Rodrigues Legendre polynomials/moments, exact signed rational interval contraction, factorial derivatives and a grouped endpoint-tail sum. It verifies physical mass, all endpoint jets, complete exterior and actual source/floor consequences. Both source variants pass according to their real outcomes: valid nonrejection for1, strict rejection for2. [Independent review](independent-review.md) approves proof, code and recorded signs, without reviewer execution.

A missing fourth-derivative mark in the original proposal display is preserved and corrected by a timestamped addendum. The code and derivative Gram always use the correct identity. No earlier scientific procedure or result is silently altered.

The old complete bounded source is reused as an accepted SHA-pinned premise, not freshly rebuilt here. Shared FLINT/Arb correctness, registered source/domain identities, C-0103's envelope and the prior complete C-0100 source acceptance remain trust assumptions. This is independent exact reconstruction of the new consequences, not a second arithmetic library, formal Rust/Lean proof or production certificate.

## Reproduction and controls

From the repository root, use fresh paths:

```text
uv run --locked python -B computations/2026-10-26T181554Z-full-coupling-viability/propose-low-floor-v2.py --output <fresh-proposal.json>
uv run --locked python -B computations/2026-10-26T181554Z-full-coupling-viability/assess-low-floor-v2.py <fresh-proposal.json> --output <fresh-assessment.json>
uv run --locked python -B computations/2026-10-26T181554Z-full-coupling-viability/verify-low-floor-v1.py <fresh-assessment.json> --output <fresh-audit.json>
```

The [nineteen-file closure](source-v1/manifest.json) captures all new programs/declarations, frozen proposals, canonical arithmetic module/package metadata used only by nonproof reconnaissance, pyproject/lock and the exact compressed accepted source. Both exact sources and both audits run from the captured prefix under isolated Python with bytecode disabled and reproduce canonical bytes. [Replay](data/replay-summary.json) identifies four roles. Floating proposal regeneration is not claimed by that exact replay.

Three actual false mathematical packets reject with exit1 and no success output: false physical mass, unpaid complete exterior and fabricated completion margin. [Rejections](data/rejection-summary.json) bind their bytes/receipts. These are research controls; production verifier exit semantics are unchanged.

The coupled proposal costs5.41s; constrained proposals1.23/1.29s; exact sources17.59/17.33s; independent audits13.97/13.63s. These are actual bounded workloads, not full-Gram benchmarks, speedups or scaling extrapolations. [Environment](data/environment.json) records Python3.14.0/python-flint0.9.0 and uncommitted research provenance from baseline0a10e5aef2ee451d224028f7746c55369002b36f. One heavy owned operation runs at a time.

[Preservation](data/preservation-check.json) validates22 earlier seals and1211 historical members plus16 protected public source/test/configuration files. Every previous method, test and result remains unchanged. The root manifest is written last. No root CLI/library/dependency upgrade, permanent test suite, cloud/GPU work or Rust/Lean acceptance.

## Decision

STOP this isotropic residual-norm completion at the fixed control. It fails even with exact coupled V/P and low arithmetic. More precision or tighter V/P quadrature cannot remove its fixed identity charge. No full generator or extension is justified by it.

The exact supported criterion remains UNRESOLVED. The actual residual is not proved large and no stronger UNIFORM theorem is proved necessary. Availability of a small uniform residual estimate does not establish an adequate proof-error budget. Direction-/matrix-sensitive residual control, or another genuinely qualified complete treatment relative to sensitive low combinations, remains missing. Signed V/P/R correlation and actual low source cannot be replaced by independent positive losses.

No actual Weil negative direction, generic energy-reference no-go, new full positivity, support, originality, global law or admission. Frozen8v1/0v2/1v3 and RH unresolved remain unchanged.
