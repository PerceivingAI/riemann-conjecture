# One-prime support continuation from T=7/20

- **Attempt ID:** `A-20260826-001`
- **Created:** `2026-08-26T17:14:00Z`
- **Last updated:** `2026-09-24T18:37:15Z`
- **Status:** `PROMISING`
- **Success target:** Extend the independently verified localized Weil positivity basepoint `T=7/20` to larger support values inside the one-prime window, while preserving the exact-prime Legendre-Schur trust chain and identifying the first genuine obstruction.

## Question / goal

`C-0050` proves strict localized Weil positivity at

```text
T=7/20=0.35
```

using the exact `p=2` translation, Suzuki residual, Legendre complement coercivity, a finite component tail-Gram Schur reduction, and an independent Rust certificate verifier.

The next question is whether this mechanism has nontrivial continuation range in

```text
(1/2)log 2 < T < (1/2)log 3,
```

or whether `T=0.35` is essentially an isolated point for the present certificate architecture.

At the outset this attempt deliberately did **not** generalize the `exact_prime_legendre_schur` certificate profile: the then-verified `C-0050` profile was locked to `T=7/20,N=32`. The architecture remains closed and enumerated rather than parameter-open. Since then, separate human-reviewed admissions and independent replays have added `(2/5,40)`, `(17/40,48)`, and `(9/20,56)`. Any new support/dimension pair remains pre-theorem candidate evidence until a separate admission decision changes the closed contract and a fresh independent replay succeeds.

## Parameterized exact assembly

The reusable `scripts/cert/legendre_schur.py` assembler was generalized from fixed `T=7/20` to an exact rational support `T=num/den` inside the one-prime window.

The following objects are now assembled at arbitrary rational one-prime support without changing the theorem-specific certificate wrapper:

```text
A_N(T),
G_V(T),
G_2(T),
G_R(T),
mu_N(T)=H_N-c_T(T)-c_2-rho_R(T).
```

The reusable assembler is parameterized, but the proof-bearing `scripts.cert.exact_prime_schur_certificate` remains fail-closed: it exports only explicitly admitted support/dimension pairs. The current closed theorem whitelist is `(7/20,32)`, `(2/5,40)`, `(17/40,48)`, and `(9/20,56)`; continuation machinery does not edit that admission set.

For reconnaissance past the point where `mu_N` may become nonpositive, the assembler has an explicit `require_positive_mu=False` mode. The default remains `True`, so certificate-generation failure semantics are unchanged.

## N=32 support map

`X-20260826-001` first reuses the rigorous exact-polynomial/Arb assembly at `N=32`, then converts only matrix midpoints to NumPy for reconnaissance eigenvalues.

The broad scan gives:

```text
T       mu_32        finite A_32 min      Schur midpoint min
0.350   0.8709101    1.19384e-3           +1.18092e-3
0.375   0.6905203    4.92986e-4           -1.11403e-2
0.400   0.5112543    1.81727e-4           -1.74087
0.425   0.3323465    5.87178e-5           -5.20043
0.450   0.1531210    1.62324e-5           -16.6429
0.475  -0.0270278    3.88653e-6            unavailable
0.500  -0.2086514    9.40392e-7            unavailable
0.525  -0.3922588    2.73029e-7            unavailable
0.540  -0.5035744    1.07699e-7            unavailable
```

A finer scan shows the `N=32` full-tail Schur midpoint remains positive through the tested `T=0.37`:

```text
T=0.355   +9.90160e-4
T=0.360   +8.32376e-4
T=0.365   +6.90647e-4
T=0.370   +5.48438e-4
T=0.375   -1.11403e-2.
```

The low finite block and `mu_32` are still positive at `0.375`. Thus the first failure of the fixed `N=32` architecture is the full-tail Schur correction, not observed negativity of the low localized operator and not loss of complement coercivity.

## Dimension diagnosis

A stable orthonormal-Legendre Gauss-quadrature scout was parameterized in `T` to diagnose whether increasing `N` should repair the tail correction. Its tail Grams are finitely truncated, so this remains reconnaissance only.

At `T=3/8`, it predicts recovery from about `N=32` upward. At `T=2/5`, it predicts recovery from about `N=40` upward. At `T=17/40`, recovery is suggested from about `N=48`; at `T=9/20`, from about `N=56`.

The key full-tail checks were then rerun with the rigorous assembler at high enough precision to avoid high-degree monomial cancellation:

```text
T=3/8,  N=40:  Schur midpoint min ~ +4.83388e-4
T=2/5,  N=40:  Schur midpoint min ~ +1.70302e-4
T=17/40,N=40:  Schur midpoint min ~ -1.28340
T=9/20, N=40:  Schur midpoint min ~ -4.23493.
```

Therefore increasing the Legendre cutoff genuinely repairs the full-tail bound at least through `T=0.4`; the `N=32` failure is a resolution/tail-control issue rather than an observed operator obstruction.

### Precision guard

Exploratory `N=40/48` exact-polynomial midpoint runs at only 104-bit Arb precision produced catastrophic cancellation artifacts because high-degree Legendre polynomials are represented in the monomial basis. Those outputs were not retained as evidence. The relevant `N=40` full-tail runs were repeated at 256 bits, where the normalized finite and Schur values agree with the stable orthonormal-Legendre scout at the expected scale.

## Selected next rigorous target: T=2/5, N=40

`T=0.4` is a meaningful continuation from `0.35` while retaining substantially more margin than the later tested supports.

A generator-side exact candidate check was performed using:

- rigorous Arb/exact-polynomial `A_40`, `G_V`, `G_2`, `G_R`;
- 72-bit outward dyadic rational matrix intervals;
- exact rational `mu_40` derived from upper scalar endpoints;
- 40-bit dyadic rational congruence witnesses generated from exact rational midpoint `LDL^T`;
- exact rational interval congruence and Gershgorin evaluation on the Python side.

It gives

```text
mu_40 > 0.7313021813837909,
even Gershgorin margin > 0.004176569432300938,
odd  Gershgorin margin > 0.013120531611009081.
```

All three exact rational margins are positive.

At that stage this was **not yet a theorem**: the independent Rust profile had not yet admitted `T=2/5,N=40`. The candidate established that no new analytic mechanism was needed before attempting independent verification at that support.

## Independent certification at T=2/5

The selected `T=2/5,N=40` candidate has now crossed the independent-verifier boundary.

The current v1 `exact_prime_legendre_schur` contract remains closed rather than parameter-open: it explicitly whitelists exactly

```text
(T,N)=(7/20,32)
(T,N)=(2/5,40)
(T,N)=(17/40,48)
(T,N)=(9/20,56).
```

The full `T=2/5,N=40` proof object was generated with 256-bit Arb assembly, 72-bit outward dyadic matrix endpoints, residual order `32`, and 40-bit dyadic exact rational congruence witnesses. Rust independently derives the complement bound and Schur matrix and returns

```text
passed=true
verified_scope=localized_weil_positivity_T_2_5.
```

The retained exact lower quantities are

```text
mu_40 > 0.7313021813837909
even margin > 0.004176569432300938
odd  margin > 0.013120531611009081.
```

A real-certificate adversarial replay rejects a wrong factor as a contract error (`exit 2`) and reports theorem failure for a contract-valid negative matrix perturbation (`exit 1`).

This establishes `F-20260826-002` / `C-0051`: strict localized Weil positivity at `T=2/5`.

## Independent certification at T=17/40

The next selected support `T=17/40` was tested at `N=48` with 384-bit Arb precision to defeat the known high-degree monomial-conditioning problem.

The rigorous full-tail assembly gives reconnaissance midpoints

```text
finite A_48 minimum ~ 5.86139746887575e-5
Schur minimum       ~ 5.52986775504016e-5,
```

while the exact rational candidate survives 88-bit outward dyadic matrix rounding and 48-bit exact rational congruence witnesses.

The closed v1 whitelist was then extended by **only** `(T,N)=(17/40,48)`. The full retained certificate is independently accepted by Rust with

```text
passed=true
verified_scope=localized_weil_positivity_T_17_40
mu_48 > 0.7326484380944506
even margin > 0.0028958690673761525
odd  margin > 0.010715413283695166.
```

The real-certificate adversarial replay again distinguishes malformed proof data (`exit 2`) from a contract-valid theorem failure (`exit 1`).

This establishes `F-20260826-003` / `C-0052`: strict localized Weil positivity at `T=17/40`.

## Independent certification at T=9/20

The next selected support `T=9/20` was tested at `N=56` with 512-bit Arb precision to control the increasing high-degree monomial conditioning.

The rigorous full-tail assembly gives reconnaissance midpoints

```text
finite A_56 minimum ~ 1.61824684632997e-5
Schur minimum       ~ 1.50101270255024e-5,
```

while the exact rational candidate survives 104-bit outward dyadic matrix rounding and 56-bit exact rational congruence witnesses.

The closed v1 whitelist was then extended by **only** `(T,N)=(9/20,56)`. The full retained certificate is independently accepted by Rust with

```text
passed=true
verified_scope=localized_weil_positivity_T_9_20
mu_56 > 0.7060951994695617
even margin > 0.003888027441177187
odd  margin > 0.004366893328949625.
```

The real-certificate adversarial replay again distinguishes malformed proof data (`exit 2`) from a contract-valid theorem failure (`exit 1`).

This establishes `F-20260826-004` / `C-0053`: strict localized Weil positivity at `T=9/20`.

## Canonical continuation at T=19/40

**Addendum — `2026-08-27T12:06:30Z`.** The canonical pre-theorem driver was run at

```text
T=19/40=0.475
N=48,52,56,60,64,68,72,76,80.
```

The three-resolution floating scout classifies `N=48,52,56` as negative, `N=60` as unstable, and `N=64,68,72,76,80` as stable-positive. Per the driver contract, `N=64` became the primary rigorous target and `N=68` the single fallback.

At `N=64`, 128-bit Arb output is catastrophically conditioned and 256 bits recovers the expected finite-block scale, but the Schur midpoint remains negative. The 384- and 512-bit runs agree to displayed precision:

```text
mu_64              ~ +0.6583679342698018
finite A_64 min    ~ +3.8671406454e-6
Schur min          ~ -0.18090174481401158.
```

Because the key signs are stable and interval widths continue to contract, the driver correctly classifies this as `MATHEMATICAL_NEGATIVE`, not `INSUFFICIENT_PRECISION`.

At `N=68`, 128 bits is again conditioning-corrupted, 256 bits restores the positive scale, and 384 bits stabilizes against the prior precision:

```text
mu_68              ~ +0.7185353202932019
finite A_68 min    ~ +3.8668365900e-6
Schur min          ~ +3.6658868513e-6.
```

The exact candidate stage then succeeds with 64-bit outward matrix rationalization and 32-bit rational congruence witnesses. The exact-rational lower margins are positive, approximately

```text
mu lower      > 0.7185353202932019
even margin   > 0.0013831260220094517
odd margin    > 0.006360318287493695.
```

The terminal state is therefore

```text
CANDIDATE_READY
(T,N)=(19/40,68).
```

The retained canonical bundle is `X-20260827-001`. It records clean generator commit `206f5678ca598568c4dfda65218d007f43a292ea` with `git_dirty=false`; all twelve manifest artifact hashes were mechanically checked after completion with no mismatch.

This is **not** a theorem admission. The closed v1 theorem contract still admits only `(7/20,32)`, `(2/5,40)`, `(17/40,48)`, and `(9/20,56)`. No theorem certificate, independent Rust theorem replay, new `C-xxxx`, or theorem finding was created by this continuation run.

## Circularity check

No RH input is used.

The target remains finite-support Weil positivity at one fixed support value. Even a successful finite-support theorem does not imply RH. Floating midpoint scans and truncated-tail dimension scouts are never promoted to theorem status. `CANDIDATE_READY` is also not promoted automatically: the canonical continuation driver stops there, a separate human/research decision must admit the exact pair to the closed theorem contract, and only then may a fresh independent verifier replay establish theorem status.

## Current result

`A-20260826-001` remains `PROMISING`.

Current results:

1. the exact-prime Legendre-Schur assembler is parameterized in rational `T` while theorem admission remains closed and enumerated;
2. `C-0051`, `C-0052`, and `C-0053` independently verify strict localized Weil positivity at `T=2/5,N=40`, `T=17/40,N=48`, and `T=9/20,N=56` respectively;
3. the canonical driver now resolves the next support slice at `T=19/40`: the previous `N=56` cutoff is inadequate, `N=60` is scout-unstable, and `N=64` is rigorously stable-negative under the present Schur reduction;
4. `N=68` survives the rigorous precision ladder at 384 bits and exact rational candidate construction with positive `mu`, even, and odd margins;
5. `(T,N)=(19/40,68)` is therefore `CANDIDATE_READY`, but is not whitelisted, independently verified, or theorem-bearing;
6. the P12 conditioning guard is functioning as intended: low-precision catastrophic values at both `N=64` and `N=68` are not mistaken for mathematical decisions;
7. the hard pre-theorem boundary remains intact: this run did not edit the closed contract, generate a theorem claim/finding, or invoke the independent verifier.

## Next action

Stop at the `CANDIDATE_READY` boundary and make the required separate human/research decision on whether to admit exactly

```text
(T,N)=(19/40,68)
```

to the closed theorem contract.

If admission is approved, the subsequent slice should modify only the closed configuration set needed for this pair, generate a fresh proof certificate under the admitted contract, perform a fresh independent Rust replay plus adversarial checks, and promote theorem status only if that independent path passes. Until that admission decision is made, no theorem-facing files should change.

## Admission and independent theorem replay at T=19/40

**Addendum — `2026-08-27T13:16:15Z`.** The required separate admission decision was affirmative for exactly

```text
(T,N)=(19/40,68).
```

The closed Python exporter/validator, JSON Schema, and Rust verifier were extended only by that enumerated configuration. Admission testing exposed and corrected two stale shared dimension guards that still stopped at `56`; mixed `19/40` dimensions remain rejected.

A fresh theorem certificate was then assembled from scratch at

```text
Arb precision = 384 bits
matrix bits   = 64
witness bits  = 32.
```

The independent zero-float Rust replay returns

```text
passed=true
verified_scope=localized_weil_positivity_T_19_40
mu_68       > 0.7185353202932019
even margin > 0.0013831260220094517
odd margin  > 0.006360318287493695.
```

The real-certificate adversarial replays preserve the trust boundary: wrong Schur factor gives contract failure (`exit 2`), while a contract-valid negative diagonal perturbation gives theorem failure (`exit 1`); the retained unchanged certificate returns `exit 0`.

The full current verification snapshot passes: default Python suite `409 passed, 2 deselected`, the real `N=68` slow-acceptance generator regression passes separately, all `rh_cert` Rust targets pass, strict clippy passes, and `lake build` succeeds.

This establishes `F-20260827-001` / `C-0054`: strict localized Weil positivity at `T=19/40`. The pre-theorem `X-20260827-001` remains a historical candidate bundle; the proof-bearing theorem run is the separate `X-20260827-002`.

RH remains unresolved. Before pushing the Legendre dimension substantially farther, optimizing the exact Rust verifier is a justified tooling improvement; any such optimization must preserve zero-float exact semantics and replay the retained theorem/adversarial corpus before continuation resumes.

## T=1/2 continuation, admission, and independent theorem replay

**Addendum — `2026-08-27T17:39:01Z`.** This addendum supersedes the earlier sections only where they describe the then-current whitelist, frontier, or next action; those earlier sections remain preserved as historical state.

After the exact-verifier and continuation-tooling improvements, the canonical pre-theorem driver was run at

```text
T=1/2,
N=56,60,64,...,104.
```

Floating reconnaissance classified `N=56..68` negative, `N=72` unstable, and `N=76..104` stable-positive. The primary rigorous target `N=76` was then shown mathematically negative under the current full-tail Schur reduction. Fallback `N=80` stabilized positive at 512-bit Arb precision. With `T`, `N`, residual order, 64-bit matrix rounding, and 32-bit witness rounding fixed, the exact candidate remained unchanged under 512-to-640-bit reassembly and was classified `CANDIDATE_STABLE`. The pre-theorem bundle remains separate at `computations/2026-08-27T151517Z-t1-2-continuation/` and correctly stopped at `CANDIDATE_READY`.

A separate explicit admission decision then added exactly

```text
(T,N)=(1/2,80)
```

to the closed v1 theorem contract. The independent admission-consistency corpus was expanded to the six admitted pairs and the full off-diagonal `6 x 6` pair grid; `(1/2,76)` remains explicitly forbidden. The consistency gate detected stale shared dimension guards in the JSON Schema and Rust exact-prime validation path before proof generation, and those guards were corrected without centralizing the production whitelist.

Fresh proof-bearing run `X-20260827-004` reassembled the theorem certificate from scratch at

```text
Arb precision = 512 bits
matrix bits   = 64
witness bits  = 32
residual order = 32.
```

The retained certificate SHA-256 is

```text
95dd6c7a497ad605ddc81129a774bade5fbbc769d0f6fdf29172b89da2a57a7d
```

and the independent zero-float Rust verifier returns

```text
passed=true
verified_scope=localized_weil_positivity_T_1_2
mu_80       > 0.6983326376765460
even margin > 0.0006030229450313612
odd margin  > 0.002927388923852846.
```

The Rust replay artifact SHA-256 is

```text
7383c91f48ead83ac9268fcdb154f9372c45ac3510339b9eaac3bd6fd461322a
```

and its exact derived rational `mu`, even margin, and odd margin agree with the generator outputs. Real-certificate adversarial replays preserve the trust boundary: changing the Schur factor from `3` to `2` is rejected as a contract error (`exit 2`), while a contract-valid `A(0,0)=-1` perturbation reaches theorem verification and returns `passed=false` (`exit 1`).

This establishes `F-20260827-002` / `C-0055`: strict localized Weil positivity at `T=1/2`. The proof-bearing theorem run is `X-20260827-004`; the earlier `T=1/2` continuation bundle remains non-proof-bearing historical candidate evidence. The explicit retained-proof registry now contains `C-0050` through `C-0055`, and the canonical current-verifier audit passes

```text
RETAINED PROOF CHAIN: PASS - 6/6.
```

The active one-prime frontier is therefore now strictly above `T=1/2`, still below the structural threshold `(1/2)log 3`. The next continuation slice must use fresh reconnaissance and must not extrapolate `N=80` or automatically promote a candidate. Entry of the `p=3` compressed translation at `(1/2)log 3` remains a separate mathematical/tooling phase. None of these finite-support results proves RH.

## T=21/40 continuation, admission, and independent theorem replay

**Addendum — `2026-08-28T01:48:56Z`.** This addendum supersedes the earlier frontier/next-action statements only; the earlier sections remain preserved as historical state.

Canonical pre-theorem `X-20260827-005` ran at `T=21/40=0.525`. Floating reconnaissance first reported stable-positive behavior from `N=88`, but rigorous full-tail precision escalation showed `N=88` and `N=92` to be stable mathematical negatives, with converged Schur values approximately `-0.5482556100498948` and `-0.12127824455981323`. Continuing over the unresolved higher range found `N=96` and `N=100` rigorously stable-positive at 512 bits. The driver selected the smaller `N=96` and produced an exact 64-bit-matrix / 32-bit-witness candidate whose exact `mu`, even margin, and odd margin remained unchanged under fixed 512-to-640-bit reassembly while Arb widths contracted. The pre-theorem workflow correctly stopped at `CANDIDATE_READY`.

A separate explicit admission decision then added exactly `(T,N)=(21/40,96)` to the closed v1 theorem contract. The larger generator-side `(21/40,100)` point remains forbidden. The seven-pair admission-consistency corpus covers the full off-diagonal `7 x 7` grid and explicit nearby outsiders including `(21/40,92)` and `(21/40,100)`. During admission, the consistency checks exposed stale independent dimension guards in the JSON Schema and Rust validation path before theorem generation; both were corrected without centralizing production authority.

Fresh proof-bearing run `X-20260828-001` reassembled the certificate from scratch at 512-bit Arb precision with 64-bit outward matrix endpoints and 32-bit exact witnesses. The retained certificate SHA-256 is `a455dcb995a56f6d387e79b199cfc6f18ba6fca108fcfe3c00987e1c47b44824`. The independent zero-float Rust verifier returns `passed=true`, `verified_scope=localized_weil_positivity_T_21_40`, and exact lower bounds corresponding approximately to `mu_96>0.69600913384063989`, even margin `>0.00090134267068206139`, and odd margin `>0.0037494074424420441`. The retained Rust replay SHA-256 is `9530b53b00c1e96a1be82b2127adc7d1424e63af444803f169be8434f51d2e83`.

Real-certificate adversarial replay preserves the trust boundary: changing the Schur factor from `3` to `2` is rejected as a contract error (`exit 2`), while a contract-valid `A(0,0)=-1` perturbation reaches theorem verification and returns `passed=false` (`exit 1`). Focused retained-proof tests pass `67/67`, the exact-prime Rust integration target passes `19/19`, strict Clippy passes, and the canonical retained-proof gate reports `RETAINED PROOF CHAIN: PASS - 7/7`.

This establishes `F-20260828-001` / `C-0056`: strict localized Weil positivity at `T=21/40`. The proof-bearing theorem run is `X-20260828-001`; `X-20260827-005` remains historical pre-theorem evidence only. The active one-prime frontier is now above `T=21/40` and still below `(1/2)log 3`. The next canonical pre-theorem slice is `T=27/50=0.54`, with the dimension selected by the driver rather than extrapolated from `N=96`. Entry of the `p=3` compressed translation at `(1/2)log 3` remains a separate mathematical/tooling phase. None of these finite-support results proves RH.

## Pre-run declaration for T=27/50

**Addendum — `2026-09-23T23:46:41Z`.** The next clean canonical pre-theorem computation is registered as `X-20260923-001`. Before observing its canonical results, fix the exact support and dimension range as

```text
T=27/50
N=80,84,88,...,144.
```

The range intentionally overlaps the previous transition region, contains the earlier `N=96` frontier dimension, and leaves substantial headroom without assuming where the new transition occurs. It was selected before the p17 diagnostic tooling work and is not changed by that dirty-tree diagnostic. Canonical `continuation-driver-p17-v1` must choose the smallest stable-positive scout target and next fallback, subject both to rigorous full-tail screening, and stop at `CANDIDATE_READY` or another fail-closed terminal state. If no candidate survives, or useful behavior appears only at the upper range boundary, do not infer mathematical failure without a separately predeclared extension. No automatic theorem admission is authorized.

## T=27/50 canonical pre-theorem result

**Addendum — `2026-09-24T02:32:15Z`.** Clean canonical `X-20260923-001` executed exactly the predeclared `T=27/50`, `N=80,84,...,144` range from committed clean-tree provenance `392aa3d3ae0583dc7a26956bf70295771af1faee`. The p17 scout first became stable-positive at `N=100`; rigorous full-tail screening then rejected `N=100` as `MATHEMATICAL_NEGATIVE` after the full 128/256/384/512-bit ladder, while fallback `N=104` became `PRECISION_STABLE` at 512 bits. Exact 64-bit matrix rounding with a 32-bit witness gave strictly positive exact `mu`, even, and odd margins, and fixed-parameter 640-bit reassembly classified the candidate as `CANDIDATE_STABLE` with unchanged exact margins and contracted Arb enclosures.

The canonical run therefore stops at generator-side `CANDIDATE_READY` for `(T,N)=(27/50,104)`. Its final manifest records `git_dirty=false`, all 19 retained artifact hashes/sizes audit correctly, all five owned pool workers were reaped with `active_children_after_cleanup=0`, and no continuation process remained afterward. This is **pre-theorem evidence only**. The closed theorem contract and retained proof registry still end at `(21/40,96)` / `C-0056`; `(27/50,104)` is not admitted, independently verified, or theorem-bearing. No automatic admission is authorized.

## Admission decision for `(27/50,104)`

**Addendum — `2026-09-24T18:13:34Z`.** A separate research decision now freezes the scope for the next theorem-admission phase. The decision authorizes Phase 2 to extend the closed `exact_prime_legendre_schur` v1 profile by **exactly one** additional support/dimension pair:

```text
(T,N)=(27/50,104)
```

This addendum records the admission **decision and scope only**. It does not itself change any production whitelist, schema, validator, Rust verifier, retained-proof manifest, or theorem status. Until Phase 2 independently updates and verifies those trust layers, the implemented production contract remains the existing seven-pair contract through `(21/40,96)` / `C-0056`.

The intended post-Phase-2 admitted set is exactly

```text
(T,N)=(7/20,32)
(T,N)=(2/5,40)
(T,N)=(17/40,48)
(T,N)=(9/20,56)
(T,N)=(19/40,68)
(T,N)=(1/2,80)
(T,N)=(21/40,96)
(T,N)=(27/50,104)
```

No other pair is authorized by this decision. For the eight-support/eight-dimension consistency grid

```text
supports   = {7/20, 2/5, 17/40, 9/20, 19/40, 1/2, 21/40, 27/50}
dimensions = {32, 40, 48, 56, 68, 80, 96, 104}
```

the eight matched pairs above are the only intended admitted combinations after Phase 2. **All 56 off-diagonal cross-pairs remain forbidden.** In particular, the following controls must remain rejected:

```text
(27/50,96)   forbidden — off-diagonal admitted-grid control
(27/50,100)  forbidden — nearby external control
(27/50,108)  forbidden — nearby external control
(21/40,104)  forbidden — off-diagonal admitted-grid control
```

For support `T=27/50`, every dimension other than `N=104` remains outside the v1 theorem contract unless a later, separately documented admission decision says otherwise.

`X-20260923-001` remains immutable **pre-theorem** generator-side evidence. Its `candidate/candidate.json` and other continuation artifacts must not be renamed, copied, or treated as a theorem certificate. Any proof-bearing theorem computation must be generated afresh from the admitted proof exporter after the admission implementation is committed and clean.

The stable identifier `C-0057` is reserved for the prospective finite-support theorem at `T=27/50`, but is **not** granted theorem status by this reservation. In `docs/CLAIMS.md` it remains a `PROVISIONAL` `OPEN_REQUIREMENT` until a fresh proof-bearing certificate is independently accepted by the zero-float Rust verifier and the later theorem-registration gates are completed.

**Phase 1 exit gate:** admission intent is now frozen to exactly `(27/50,104)`; the forbidden controls and complete off-diagonal policy are explicit; `X-20260923-001` remains pre-theorem; and `C-0057` is reserved without theorem status. Production trust-layer edits belong to Phase 2 and are not part of this addendum.

## Phase 2 closed-contract admission implementation

**Addendum — `2026-09-24T18:22:49Z`.** The Phase 1 decision has now been implemented independently across every production admission layer required by `exact_prime_legendre_schur` v1. Exactly `(T,N)=(27/50,104)` was added to the Python theorem exporter, the separately maintained Python semantic validator, the raw JSON Schema, and the independent Rust verifier. Rust's separate finite-dimension guard was extended to `104`, while its harmonic-index invariant remains `harmonic_index == dimension`. `docs/CONTRACTS.md` now records the eight-pair closed contract.

The test-only admission corpus was expanded to eight allowed matched pairs, all `56` off-diagonal combinations in the `8 x 8` admitted support/dimension grid, and nine external forbidden controls. The explicitly frozen nearby cases `(27/50,96)`, `(27/50,100)`, `(27/50,108)`, and `(21/40,104)` are all rejected; `(27/50,104)` alone is accepted at the new support.

Focused cross-layer checks pass:

```text
uv run --locked --extra test python -m pytest -q tests/test_admission_consistency.py
6 passed

cargo test -p rh_cert --test test_exact_prime_schur
24 passed
```

The Rust target includes the corpus-wide admission replay plus direct new-pair acceptance and the existing contract/adversarial semantics for wrong factor, cross-parity entries, singular witnesses, nonpositive complement bounds, and theorem-failure-versus-contract-failure distinction.

This closes **admission only**. `computations/retained-proofs.json` is unchanged, `EXPECTED_RETAINED_CLAIMS_V1` remains exactly `C-0050` through `C-0056`, no fresh `(27/50,104)` theorem certificate exists, and no proof-bearing independent Rust replay has been performed. Therefore `C-0057` remains `PROVISIONAL` / `OPEN_REQUIREMENT`, the independently verified theorem frontier remains `(21/40,96)` / `C-0056`, and `X-20260923-001` remains pre-theorem evidence. Phase 3 must freeze, quality-check, and commit this admission implementation from the current working tree before any theorem-certificate generation begins.

## Phase 3 admission freeze and theorem-run predeclaration

**Addendum — `2026-09-24T18:37:15Z`.** The Phase 2 diff was audited directly across the Python theorem generator, Python semantic validator, raw JSON Schema, Rust verifier, and test-only admission corpus. No accidental broadening was found: the production pair admission adds exactly `(27/50,104)`, the schema binds `N=104` to `T=27/50` through the exact-pair branch, all 56 off-diagonal eight-pair combinations remain forbidden, and retained-proof authority still ends at `C-0056`.

The focused Python contract suite passes `15/15`; the complete `cargo test -p rh_cert` package suite passes; `cargo clippy -p rh_cert --all-targets -- -D warnings` passes; `cargo fmt -p rh_cert -- --check` passes; the retained-proof manifest remains valid with seven registrations; and `git diff --check` passes. The admission implementation was then committed cleanly as `f2d284fd85bee8995ef267450e4038768678c3a3` (`Admit T=27/50 N=104 closed contract`), after which `git status --short` was empty.

The fresh proof-bearing run is now predeclared as `X-20260924-001` in `computations/2026-09-24T183715Z-t27-50-schur-certificate/record.md`, with exact parameters `T=27/50`, `N=104`, 512-bit Arb precision, residual order `32`, 64-bit outward matrix endpoints, 32-bit witness entries, and Schur factor `3`. That record fixes the exact generation and independent Rust replay commands and requires an empty working tree before execution. No theorem generation has occurred in Phase 3; `C-0057` remains provisional until the later proof-bearing gates succeed.
