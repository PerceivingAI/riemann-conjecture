# Complete T4/5 reference and target parameter qualification

- **Computation ID:** `X-20261027-002`
- **Created:** `2026-10-27T05:07:43Z`
- **Last updated:** `2026-10-27T05:57:02Z`
- **Status:** `COMPLETE`

## Objective and actual scope

Qualify one complete supported weighted-Gram first attempt at T=4/5 without
constructing the target low/coupling matrices or asserting their sign. Measure
the accepted T3/4 budget, independently prove the new all-frequency reference,
derive residual/error and numerical controls, and freeze an auditable declaration.
No target positive gap, external numerical claim or support-covering law is assumed.

## Environment and inputs

[Environment](data/environment-v1.json) records native Windows x64,
Python3.14.0, python-flint0.9.0 and the actual NumPy/SciPy versions. Exact budget
verification uses FLINT fmpq matrices without float. Numerical eigensystems
only propose exact congruences. Scalar source/audit use512/768 bits; the residual
and control declaration use768-bit scalar generation and independent512/1024-bit
checks. Shared FLINT/Arb is an explicit trust premise.

The starting accepted proof is C-0118 at T3/4,N312. Its root seal is
`ecea29f03fd75664e2a39371b47e43fe1f565c4415986d9549c95555d5fb4b66`.
Its actual source matrices, proposal and exact sign are SHA-bound before use.
The older C-0100 transform supplies coordinates only. No old reference proxy
or T3/4 operator interval is silently used as a T4/5 matrix.

The [scalar input](qualification-inputs-v1.json),
[control-budget input](control-budget-inputs-v1.json), and
[parameter policy](parameter-selection-inputs-v1.json) declare fixed choices
before their respective executions. Earlier method versions remain unchanged.
New work is uncommitted and based on commit2a65306; no clean-production provenance
or new certificate/admission claim is made.

## Mathematical operation

[Reference contract](reference-contract-v1.md) gives the complete signed symbol,
physical source identity, unbounded logarithmic form domain, finite/analytic
frequency cover, complete Legendre leakage and inverse-weight comparison.
[Source/error contract](target-source-error-contract-v1.md) gives actual low/cross
requirements, full signed residual polynomial, canonical regular/polar remainder,
model perturbation, whole physical output and frequency infinity.

The independent energy organization uses128 positive digamma-difference terms
and a64-term logarithmic expansion. Primary [DLMF5.9.15](https://dlmf.nist.gov/5.9#E15)
and its [exact TeX](https://dlmf.nist.gov/5.9.E15.tex) were inspected; R-0030 has a
new material-use addendum. Expanding Binet's integral gives the right-half-plane
remainder bound|B_(2p)|/[2p Re(z)^(2p)], not an unsupported use of asymptotics.
No external implementation is imported.

## Observed old-control budget

The source/independent endpoint pair certifies8 whole-space relative caps against
the actual A_model. The combined paid cap is below0.494783 even and0.488511 odd.
The finite weighted head and complete physical exterior are the substantial
charges; canonical residual-model error is below0.004951 even and0.000005347 odd.
Full component cap displays and their distinct mathematical meaning are in the
[finding](../../findings/2026-10-27T050743Z-t080-reference-and-parameter-qualification.md) and exact [source](data/control-budget-v1.json).
Independent component maxima are not added as an equality for the joint budget.

With the accepted nonsingular U, the physical selected-Schur lower is
`margin/tr(U^TDU)`, at least3.4862946e-15. Inverse physical-coordinate Frobenius
and whole conditioning uppers are also computed exactly. These are not exact
eigenvalues or a full-Weil spectral-gap computation.

## Qualified target and frozen first attempt

| Parameter or complete control | Qualified value |
| --- | --- |
| Support | 4/5 |
| Active arithmetic powers | 2,3,4; coefficient4=log2/2 |
| Signed reference | alpha1/4, beta859/1024 |
| Outside floor | 1/3 |
| Reference anchor | R257 |
| Scalar-policy low cutoff | N322, two161-dimensional parities |
| Reference domination | eta=1-2^-128 |
| Residual polynomial | K76; all77 coefficients exact |
| Finite physical output endpoint | M644; Rc514 inverse-tail comparison |
| Inverse-weight frequency anchors | 60 through8224, positive terminal infinity payment |
| Complete inverse-multiplier Q644 upper | below1.147649085 |
| Complete canonical residual discrepancy | below5.674e-23 |
| Full residual-model allowance | below2.969474e-21 |
| Declared model-error accuracy goal | approximately3.324790e-21 |
| Starting source/independent precision | 3072/4096 bits |
| Matrix publication | 256 bits |
| Polynomial arithmetic/square rule orders | 483/322, exact through965/643 |

The source proof bounds all1516 intervals on0..256 plus all frequency infinity.
Strict log4<8/5<log5 and8/5<pi certify the active set and local series domain.
Every preceding eligible integer anchor and six even N policy trials are
accounted for. N322 is a minimum of this declared sufficient policy, not the
minimum dimension for target positivity.

The residual selector pays
`Lambda=delta+(2B_Kdelta+delta^2)/(m eta)`, where
`B_K<=pi/2+2sum c_m+2sum_(d<=K)|c_d(T)|2^d`.
Only the tiny TRUE canonical discrepancy is uncertainty. Full signed R_K remains
in the intended low/coupling source; low even/polar terms remain required.
All37 preceding even degrees are retained and fail the published accuracy policy.
The exact finite cross lies on inputs246..321 and outputs322..397;2K152<N322
andM644>=N+K. No target cross-entry matrix is constructed by this statement.

The [declaration](data/target-declaration-v1.json) and
[first-attempt seal](data/first-attempt-seal-v1.json) bind all controls before
any target matrix/sign execution. The source hash is
`ab63147ed5c77b1f0f1c611d5f72a86219932e41c5d5196cf3511654aaa3a898`.
The accuracy goal is the OLD selected-Schur physical lower divided by2^20. It is
an accuracy choice, NOT a transported target gap. Starting precision bounds
coefficient/recurrence amplification with explicit guards; achieved matrix
widths and target positivity remain unproved. A valid complete physical
numerical-radius upper must later be at most one quarter of that goal.

## Execution, correction and acceptance

| Actual run | Exit | Wall seconds |
| --- | --- | --- |
| Control budget source | 0 | 90.282 |
| Independent exact budget audit | 0 | 112.683 |
| Complete target reference | 0 | 0.718 |
| Independent complete reference audit | 0 | 1.891 |
| Residual/order/precision declaration | 0 | 0.280 |
| Original composition consumer, retained failure | 2 | 0.238 |
| Corrected independent declaration audit | 0 | 2.205 |
| Three mathematical rejection controls | 0 | 6.604 |
| Captured-code/input isolated replay | 0 | 205.740 |

These are different observed workloads, not matched performance comparisons.
All three accepted source/consumer pairs ran real mathematical calculations.
The control budget and reference need no target positivity assumption.

The first declaration consumer rejects with
`reference audited interval mismatch outside_lower_form`. Its executable and
[failed receipt](data/target-declaration-audit-v1.run.json) remain unchanged.
The reference consumer had already checked native independent containment.
Its output then re-rounded audit REPORT intervals; the arbitrary-rational
relative-grid exponent can be coarser than the source's dyadic grid. Report
containment is therefore not a valid substitute for the native check.

New `verify_t080_target_declaration_v2.py` reruns the COMPLETE standalone
reference acceptance, including all cells and infinity, and requires the exact
accepted audit dictionary. It then treats published reports as reports instead
of demanding their containment. No overlap shortcut or exception suppression
is introduced. The [corrected audit](data/target-declaration-audit-v2.json)
passes all coefficients, full error/degree policies and60 inverse weights.
The [independent review](independent-composition-review-v1.md) explicitly
acknowledges that the initial review missed the invalid comparison and approves
the corrected composition. Earlier read-only reports also assessed the budget,
reference and residual-error mathematics; reviewers did not execute checks.

Three actual false mathematical packets reject with exit2 and no success file:
unpaid frequency infinity, an altered signed polar coefficient, and zeroed full
model-error allowance. The [negative-control record](data/negative-controls-v1.json)
retains their self-consistent source packets and observed errors. These are not
hash-only or schema-only attacks.

## Isolated reproduction

The [captured31-file closure](captured-source-v1.json) includes every consumed
project source, all seven source/consumer versions, exact earlier control data,
current inputs/contracts and environment lockfiles. Replay creates a fresh
source/data tree and executes the three pairs, using corrected v2 for final
acceptance. All six scientific JSON outputs and eight exact proof witnesses are
BYTE-IDENTICAL. Its own temporary tree is removed.
[Replay result](data/isolated-replay-v1.json) and
[run receipt](data/isolated-replay-v1.run.json) preserve the actual205.740-second
execution and14 output hashes. The operation reads an existing capture on later
runs and never refreshes it from changed root helpers.

From the root, use a NEW output filename:

```text
.venv/Scripts/python.exe -B -m scripts.weil_t080_qualification_replay --bundle computations/2026-10-27T050743Z-t080-target-qualification --output computations/2026-10-27T050743Z-t080-target-qualification/data/replay-new.json
.venv/Scripts/python.exe -B -m scripts.weil_t080_qualification_replay --bundle computations/2026-10-27T050743Z-t080-target-qualification --negative-controls --output computations/2026-10-27T050743Z-t080-target-qualification/data/negative-new.json
```

For individual operations, use their recorded argv in the native receipts.
The source/consumer pairs are `weil_t080_control_budget` /
`verify_t080_control_budget`, `weil_t080_reference_qualification` /
`verify_t080_reference_qualification`, and `weil_t080_target_declaration` /
`verify_t080_target_declaration_v2`. Fresh output/case directories are mandatory;
negative cases must remain inside this bundle. No command overwrites the old
source, audit, failed implementation or frozen declaration.

## Reuse and intentionally unimplemented target work

[Reuse/gap assessment](data/reuse-and-gap-assessment-v1.json) identifies neutral
frozen helpers and the general finite-band/source/interval arguments. Target
P/P-squared/GP/VP, actual A_K and the complete weighted low/Gram source require
fresh target evaluation and a separately versioned independent matrix consumer.
Those are not implemented or claimed by this parameter-only qualification.
Old T3/4 operator data are not target inputs. The accepted exact coordinate
transform may be padded by identity for five new modes per parity, as coordinates
only. Fresh target matrices must be contracted in high precision before any
floating witness proposal.

## Integrity, limits and related claims

[Historical acceptance](data/historical-preservation-v1.json) verifies25 prior
seals and1456 historical members unchanged, plus16 frozen public source/test/
config files. Every existing method, proof, failure and admission remains intact.
Necessary captured accepted proof inputs are retained even above the raw-data
threshold; they are proof artifacts, not disposable raw data. New sources and
bundle bytes have scoped exact-byte attributes. Root manifest is sealed LAST.

This proves the complete target reference/error qualification and fixes an
executable first attempt. It does not prove target low/coupling positivity,
achieved matrix widths, an optimal target dimension or error law, an external
proof or its reported gap, global viability, a support-covering family or RH.
No target low/coupling source/sign computation, root mathematical-library edit,
production certificate/admission change, full Python suite, Rust/Lean replay,
commit or push was performed. Native scientific source/audit/rejection/replay
runs are the actual exercised acceptance layer.

Claim C-0119; [F-20261027-002](../../findings/2026-10-27T050743Z-t080-reference-and-parameter-qualification.md); related C-0117/C-0118
and R-0030/R-0039. Production inventory8v1/0v2/1v3, RH unresolved.
