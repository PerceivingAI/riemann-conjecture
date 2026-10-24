# Controlled weighted continuation is positive at T=1353/2048

- **Finding ID:** `F-20261024-006`
- **Created:** `2026-10-24T20:28:55Z`
- **Last updated:** `2026-10-24T20:37:47Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED` source-conditional research positivity by fresh analytical acceptance and exact rational witnesses/replay; not production theorem admission
- **Claim:** C-0087
- **Evidence:** [X-20261024-004](../computations/2026-10-24T191616Z-weighted-support-extension/record.md)

## Statement

At T=1353/2048=0.66064453125,N=312,K=38,m=1018, active arithmetic[2,3] and the original exact positive reference mu from C-0084, both156-dimensional parity lower matrices are strictly positive for

\[
S_0=A-B^*C_0^{-1}B,\qquad
C_0 e_k=(\mu+H_k-H_{312})e_k.
\]

Let D_jj=2/(2j+1) be the ordinary Legendre mass. Exact positive rationals satisfy S0_even>=g_even D_even and S0_odd>=g_odd D_odd. Their decimal displays are:

| Parity | Dimension | Certified mass-normalized reference lower |
| --- | ---: | ---: |
| Even |156|1.4153700144298843e-11|
| Odd |156|8.376781192230801e-9|

The exact rationals and their congruence witnesses are in `data/extension-assessment-v1.json` of X-20261024-004. These are conservative reference lower bounds, not the full operator's minimum eigenvalue or optimal constants.

Under C-0072's stronger harmonic tail domination, C-0063's closed-form/source premises and C-0082/C-0085's complete errors, this gives strict positivity of the constructed full closed form and the source-conditional Suzuki admissible smooth-test implication at this support. Both parity sectors and nonzero complex tests are included. Restriction then covers smaller physical test supports; it does not certify every smaller-support S0 matrix or admit additional parameter pairs.

## Why this support was tested

[F-20261024-004](2026-10-24T193421Z-cross-cut-norm-controlled-continuation.md) proves a uniform cross-cut potential bound and complete dimension-independent residual charge. The selector ran before any new matrix sign and nearly doubled the prime3 translation overlap. It retained the original exact mu, bounded the new full residual charge by the old accepted charge, and matched the omitted inverse-weight cap.

The actual overlap ratio is about1.9946789613. The first certified scalar choices are N=312,K=38,m=1018. They are not a matrix-sign search or claims of minimum useful dimensions. Matching the weight cap did not assume matching omitted source mass or error.

Strict arithmetic activation,1<tau2<tau3<2, signed-cell order and2T<pi were freshly certified. The m=4 and tau2=1 structural transition was not crossed.

## Complete analytical acceptance

| Input | Accepted slots | Provenance |
| --- | ---: | --- |
| Raw A_K and complete Q312 mixed G_K upper triangles |97,656|Fresh source and independent reconstruction|
| Rectangular signed V/P/RK heads |660,816|Fresh source and independent reconstruction|
| Complement, full residual and uniform cross-norm upper |3|Fresh independent bounds|
| Total |758,475|No inherited analytical arrays|

Source low/head precisions are1792/4608 bits; independent global-moment/Taylor reconstruction uses3584/9216. Publication/reference receipts use352/512 bits. All312 exact residual images and their degree/parity signature are reconstructed afresh; individual source-column zeros are justified, not inferred only from a global cutoff. The separately accepted cross-norm bound includes the full residual norm allowance.

Packet SHA256 is `c9790a7b129aae0d410670830e8a472d639105d01884a041165fc119e627671e`. Independent audit SHA256 is `e23fa00b66d5ebe5ccc261e23b886c10e2e4fdd3f816d9a8a3dcbca38282408e`. Assessment SHA256 is `d7569a7037021fc729987b27851e64648f8f8f1eead8123dbd3391c4ce27cb8d`.

## Exact finite proof and full error

The lower is Aminus-Uplus-rD, with the complete mixed signed source and C-0085 uniform residual allowance. Exact rational lower-triangular48-bit witnesses W have nonzero diagonals and strictly positive exact Gershgorin margins eta for W L Wtranspose. Setting g=eta/trace(W D Wtranspose) gives the displayed mass-normalized bounds. A separate CLI process recomputed the full consequence and reported EXACT_REPLAY_PASS on the same source/audit/result bytes.

The full residual allowance displays1.9466091170e-13. The alternative trace allowance displays1.4220444040e-13, but was not substituted to obtain this result. Matrix interval one-sided errors display5.2969292919e-102 for A and2.4494112230e-100 for U.

For the retained weak even proposal, all values below are exact mass-normalized directional enclosures, displayed approximately:

| Contribution | Display |
| --- | ---: |
| Raw low-form lower |1.4659316584e-11|
| Correlated weighted inverse-energy upper |3.1083485402e-13|
| Omitted weighted allowance within that upper |2.1707995854e-14|
| Full residual charge |1.9466091170e-13|
| Resulting directional matrix lower |1.4153820818e-11|

This proposal is not claimed to be an exact minimum eigenvector. The separate whole-block congruences certify all directions. The global tail-trace diagnostic increases to about12.0496430 despite the positive correlated lower. It is not the actual penalty in every direction. Replacing its correlated tail treatment by a scalar12.05D penalty would give a different, potentially much weaker ordinary-coordinate criterion.

## What the continuation establishes about the method

The distribution-sensitive weighted mechanism survives a substantial controlled support change, a nearly doubled prime3 overlap and an enlarged low space. This is evidence of an implemented within-window extension mechanism, not only another serialization of the old result.

The certified even reference lower is about112 times smaller than at the old baseline, and the odd lower about68 times smaller. Those comparisons concern certified reference bounds with the same normalization; they are not measurements of the full operator's actual spectral-gap ratio.

The existing scalar scout separates cost growth. Its conservative cost rises from5.6523929575 to6.1352925716. The c_T increase is about0.0962863 and the full-residual norm-majorant increase about0.3866133. The arithmetic norm budget is unchanged in this window. Thus about80% of the scalar cost increase comes from that residual norm majorant. This does not prove comparable growth of the true tail-restricted residual norm. The full norm allowance is also distinct from the small truncation error controlled by K.

Interval width is not the observed limiting loss. Full residual and omitted-tail allowances remain below the new even lower, but smaller certified margins make error control more demanding. One successful continuation supplies no general growth law, feasible all-support family or reason to accumulate arbitrary support records.

## Verification, versions and limits

The complete actual frozen selection, all budget/provenance fields and source bytes were checked before acceptance. A prospective partial-selection guard defect was separately found and reproduced. The correctly selected actual data were intact. All numerical generation, analytical audit, matrix assessment and first replay used preserved source-version2; the later complete-selection/byte-binding correction is version3, not a relabeled producer of this proof. X-20261024-004 records the correction and its actual regression/CLI evidence.

Changing the odd witness margin or reencoding the source bytes while retaining the old audit caused actual replay rejection and no success output. Separate mathematical review accepted the conditional implication but performed no independent numerical execution. Source truth remains conditional on the documented Suzuki identity, Arb arithmetic, exact polynomial formulas and form-domain premises.

After the live guard correction, an isolated restore of the exact numerical source-version2 also passed the actual retained replay. This checks historical reproducibility across the source-version cutover without rewriting earlier bytes or pretending that a current-source guard produced the old arrays.

This result is not a clean committed production certificate, new Rust/Lean source validation, production theorem admission, full operator-domain equality, a priority or efficiency claim, an unbounded support-covering proof or RH. Production inventory stays eight frozen v1, zero v2 and one v3 C-0067. All old research and proof artifacts remain preserved.
