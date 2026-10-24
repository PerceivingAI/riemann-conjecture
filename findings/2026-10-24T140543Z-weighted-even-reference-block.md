# Exact positive even reference block; odd assessment remains unresolved

- **Finding ID:** `F-20261024-002`
- **Created:** `2026-10-24T14:05:43Z`
- **Last updated:** `2026-10-24T14:05:43Z`
- **Type:** `DERIVED_RESULT` with retained exact finite-matrix verification and independent analytical input acceptance
- **Status:** `VERIFIED` for the even low reference block under the stated source premises; odd and whole-space positivity unresolved

## Statement

C-0083 establishes a uniform positive lower on the **96-dimensional even low block** of the harmonic reference at unchanged T=3/5,N=192,K=32, active terms [2,3] and the original exact rational mu.

Let E index degrees 0,2,...,190, and let

\[
D_E=\operatorname{diag}_{j=0}^{95}\frac2{4j+1}.
\]

At the finite evaluation boundary m=316, the independently accepted complete source inputs and the C-0082 construction give a rational symmetric lower L_E and exact invertible rational W with

\[
S_{0,E}\succeq L_E,\qquad
W L_E W^{\mathsf T}\succeq\eta I,\quad \eta>0.
\]

Writing

\[
t=\operatorname{tr}(W D_E W^{\mathsf T}),\qquad g=\eta/t>0,
\]

one obtains

\[
\boxed{S_{0,E}\succeq L_E\succeq gD_E.}
\]

The exact rational g is retained in `data/even-gap.stdout.txt` in [X-20261024-002](../computations/2026-10-24T124142Z-weighted-low-space/record.md). Its decimal **display** is approximately **1.577381523629527e-9**. This is a mass-normalized uniform lower, not a floating minimum or the congruence margin itself.

C-0072 also gives \(S_{\mathrm{true},E}\succeq S_{0,E}\). This transfer does not evaluate the true inverse. It does **not** establish positivity of the odd block, the whole reference, or the complete Weil smooth-test class at this support. No production theorem is admitted.

## Complete analytical and exact inputs

The source packet at m=316 contains:

| Analytical input | Independently accepted slots |
| --- | ---: |
| Raw A_K upper triangle | 18,528 |
| Complete Q192 mixed G_K upper triangle | 18,528 |
| Rectangular V/P/R32 pairings | 71,424 |
| Full residual and complement scalars | 2 |
| Total | 108,482 |

Every stored interval contains a separately reconstructed rigorous interval, with outward reference receipts. Opposite-parity entries are justified exact zeros after consistency checks, not omitted unexamined slots. Symmetry supplies the lower triangles. All 192 exact residual images agree by signature; source geometry and the original chosen mu are checked independently.

The generator uses 1024-bit full low/Gram construction and 1792-bit head construction. The reference uses 2048 and 3584 bits respectively. Publication is outward 352-bit dyadic; independent receipts are outward 512-bit dyadic. These inputs concern the **newly generated complete matrices**, not a claim that an earlier unstored historical matrix was independently replayed.

The exact source packet SHA-256 is `6e47790be55809d55b08df478f6dbb11a3975b30da2688d0c80229ae1e866ad9`; the independent acceptance artifact is separately byte-bound. The original source/trial packet remains SHA-256 `44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b`.

## Weighted matrix and full error proof

Use the complete signed source W_K=V+P+R32. The raw high pairings r_k have ordinary-Legendre coordinates; normalized rank-one contributions are

\[
t_k^*t_k=r_k^*r_k/d_k,\qquad d_k=2/(2k+1).
\]

The implementation retains every same-parity cross-direction term in

\[
U_m=w_mG_K+\sum_{192\le k<m}(w_k-w_m)t_k^*t_k.
\]

It does not replace the correlated final matrix by a scalar trace bound. The complete omitted infinite tail, interval Loewner error and full residual cross effects are paid through C-0082:

\[
L=A^--U^+-rD,\quad
r\ge\delta+2\delta\sqrt{\operatorname{tr}(D^{-1}U^+)/\mu}+\delta^2/\mu.
\]

At m=316 the global tail-loss trace upper displays 24.832113801605544, whereas r displays about 7.48e-13 and interval overestimates are much smaller. A large trace allowance is not itself a matrix eigenvalue. Retaining the correlated matrix permits an even-block proof despite that coarse scalar diagnostic.

An exact lower-triangular dyadic W has nonzero diagonal. Native zero-float rational congruence evaluates every Gershgorin row margin; their minimum eta is strictly positive, with display 0.999999985300644. Separate replay reconstructs the complete bounds and checks the witness, margins, source bindings, scalar allowances and original-trial consequences without using floating proposal success as evidence.

The normalized gap follows because \(W D_E W^{\mathsf T}\) is PSD and bounded above by its trace times I. Thus

\[
W L_E W^{\mathsf T}\succeq\eta I
\succeq(\eta/t)W D_E W^{\mathsf T}.
\]

Invertible congruence proves the boxed inequality. The mass uses the **actual even degrees**, not the positions 0,...,95 treated as consecutive Legendre degrees.

## What happened in the odd block

Both parity blocks were assessed, not only favorable basis vectors. At m=316, an exact odd vector has

\[
z^*L_{\mathrm{odd}}z<0,
\]

with decimal display **-0.1574622207633184**. The conservative lower is therefore not positive definite. A separately residual-restored directional **upper for the actual S0 value** on this vector displays **+0.44991346418918476**.

A positive upper does not establish the actual reference value is positive. The negative lower does not establish it is negative. The actual odd-reference sign remains unresolved; no negative true-Schur or Weil direction is inferred.

The preserved original odd trial remains positive by C-0081. On that same trial, the new uniform lower and finite-head upper display [0.2031276216162931,1.0077559508789693], containing the earlier accepted bracket [0.6257295744306691,0.8504608367268481]. The lower proof margin is about 0.4226019528 weaker. This quantifies the more conservative matrix tail allowance; it is not disagreement with the earlier directional calculation.

## Accuracy-driven refinement and actual execution limit

The starting boundary 224 follows from the residual image degree bound 223. Its two lower-block tests were inconclusive. C-0082's predeclared uniform error rule selected m=316, the smallest even index satisfying w_m<=w_224/2. The successful even proof above was obtained there.

The same rule selected m=626 before further source evaluation. The source child exceeded its reserved **30-second** window and was killed and reaped; no m=626 source packet was produced. Consequently no m=626 matrix or analytical acceptance is claimed. The remaining contracted source-plus-independent-validation reservation did not fit the balance. This is a measured resource limit on this execution path, not a mathematical obstruction at m=626 or a no-go for the method.

The numerical ledger carries 97.41939420008566 prior seconds and charges **432.87469699967187 new seconds**, including failures and the timeout, for **530.2940911997575/600 seconds**. Unspent balance is **69.70590880024247 seconds**. The cumulative ceiling was **not exhausted**; the failed next reservation could not simply be restarted with all independent checks still reserved. No allowance was reset or enlarged.

## Implementation corrections and controls

The first full independent audit rejected R32[192,0]. The source computed the exact rational zero, but monomial ball contractions did not impose the **individual residual image's** polynomial-degree orthogonality. Increasing precision was not the cause-based fix.

The corrected auditor proves k>degree(R32 P_j) from independently reconstructed exact polynomials, requires the computed ball to contain zero, then imposes the exact zero. A regression failed before and passed after; the nonzero degree edge remains checked. All failed source versions, stderr and corrected outputs are retained separately.

Native integer center/radius matrix products retain signed off-diagonal terms and pay cross radii, radius products and weight uncertainty before Loewner inflation. They may change last-bit enclosure widths relative to the earlier entry-loop method; earlier implementations/results remain reproducible from their snapshots. Seven behavioral controls pass, including noncentered interval uncertainty, physical mass, full residual cross error, conservative-lower versus actual-sign distinction, residual-degree zeros, and pinned-input invalidation/forgery.

The optional low-input reuse path pins both exact accepted ancestor bytes and requires unchanged low matrices, scalars, source definitions, original mu and residual signature. It rechecks copied receipt containment and freshly reconstructs the exact residual images and every head. Its receipt distinguishes inherited low evidence from fresh heads. An actual m=224 reuse audit passed; no uncompleted m=626 reuse audit is represented as a result.

Altered exact witness margins and changed reference mu were rejected by actual CLIs without publishing a passing output. Independent read-only review accepted the implementation, native denominator/radius proof, cache provenance constraints and normalized gap implication; the reviewer ran no numerical work.

## Dependencies and limits

Dependencies: C-0063 through C-0065, C-0072, C-0082, and the complete analytical/exact records in X-20261024-002. C-0081 supplies the preserved-trial comparison, not the even-block positivity argument. Shared Suzuki identities, Arb, exact polynomial algebra and the local 2T<pi source premises remain trust assumptions; no Lean verification of those identities is claimed.

There is no full odd or whole-space positive reference result, true-inverse evaluation, complete Weil positivity result at T=3/5, unbounded support-covering family, new certificate profile, admission change or RH proof. Admissions remain eight frozen v1, zero v2 and one retained v3 C-0067. The unresolved odd assessment is not closure of the broader method.
