# Separate source/consumer/sign composition review

- **Created:** 2026-10-27T06:52:49Z
- **Reviewer:** separate reviewer agent T080CompositionReview, not the producer, consumer or sign author
- **Execution limit:** read-only review; actual program receipts are separate
- **Working-tree clarification:** the reviewer comparison remark concerns this new untracked bundle. The repository was not clean: pre-existing C-0119 modifications were preserved.

## Verbatim review

## Findings

No evidence-backed correctness defects found in the reviewed source/consumer/sign composition or numerical refinements.

## Review evidence

- **Ordinary physical normalization.** Producer `source()` and consumer `reconstruct()` use \(d_n=2/(2n+1)\). Low and tail matrices are physical inner products; the head expansion applies \(D_{\mathrm{tail}}^{-1}\) before contraction with the frequency kernel. The exact verifier uses the same masses for model-error subtraction, numerical-radius qualification and physical-gap conversion.

- **Fresh arithmetic and mixed terms.** Producer `combined_square()` sums every active signed translation before forming the Gram. Consumer `complete_arithmetic_squared()` independently does the same on positive overlap cells and doubles the even same-parity products. Its four positive cells cover every positive breakpoint for this support. Both reconstruct powers 2, 3 and 4 with \(c_4=\log(2)/2\). Consumer `arithmetic_blocks()` evaluates both translation windows separately. Both implementations subtract the complete low and tail projections and retain `vp_tail + vp_tail.transpose()`. I found no omitted mixed arithmetic product or VP orientation.

- **Residual and both infinities.** The producer retains exact low residual terms through its helper; the consumer independently constructs both endpoint-normalized polynomial integrals, including even kernel and boundary terms. Its exact degree checks place every residual output below 644. The frequency kernel starts with the terminal weight times physical mass, then adds all band increments, so frequency infinity is paid by Parseval. The omitted physical output uses the complete signed \(Q_{644}(V+P)\) Gram multiplied by the sealed whole-line inverse-multiplier bound. Neither implementation substitutes the inverse of a finite compressed form.

- **Bessel refinement.** In producer `bessel()`, exact midpoint evaluation retains native evaluation uncertainty and adds the full original argument radius. The stated Legendre-integral derivative bound justifies that enlargement for real arguments. Downward recurrence continues on the original argument ball, and the 2048-bit seed guard remains. Consumer `frequency_kernels()` independently starts from elementary sine/cosine formulas and uses upward recurrence.

- **Coordinate refinement.** Proposer v2 forms fresh \(U_0^T(A-\Lambda D)U_0\) before native Cholesky and requires positive pivots. It composes \(W=L^{-T}R\) in Arb after interpreting floating entries of \(R\) as exact binary rationals. It rounds those native composed midpoints directly to 80-bit dyadics. The exact verifier then prepends \(U_0\); there is no double conversion of the composed ill-scaled transform.

- **Exact sign.** `verify-whole-sign-v1.py:60–76` constructs full interval subtraction with positive exact Young coefficients, checks exact nonsingularity, and propagates uncertainty as \(|U|^T R|U|\). Gershgorin subtracts every transformed radius row sum. Its numerical-radius bound is a valid conservative physical-operator bound. Dividing the positive congruence margin by \(\operatorname{tr}(U^TDU)\) gives a valid physical lower bound.

## Recorded outcome and limits

The read artifacts now contain `PASS_COMPLETE_SOURCE` for six matrices and 78,246 triangular entries, and `PASS_COMPLETE_SOURCE_CONDITIONAL_CANDIDATE` with positive complete paid lowers and passing numerical-width goals in both parities. The audit, proposal and exact assessment record the same source SHA-256, `f50d8a194bf4d13ad4cd65ccbcf5762c403d8f5e26d384cbdb38be5ccb807fe6`, and identical input fingerprints.

These are inspected records, not mathematical verification executed by this reviewer. I ran no programs, builds, tests, linters or formatters and made no modifications. The empty working-tree diff means this review addresses the supplied new bundle directly rather than a tracked patch comparison.

The composition still assumes the accepted scalar/reference and canonical contracts, rigorous python-flint/Arb operations, and enclosed Gauss nodes and weights. Exact sign acceptance deliberately does not consume the native audit. Any combined acceptance decision must require the successful audit on identical source bytes and inspect mathematical status rather than process exit alone. Retained replay and adversarial gates remain outside this assignment. The recorded result is a conditional research candidate, not production admission or an independently accepted new theorem.

**Overall correctness:** correct within the assigned research scope.

**Confidence:** 0.88.
