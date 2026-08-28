# Canonical pre-theorem continuation at T=21/40

- **Computation ID:** `X-20260827-005`
- **Created:** `2026-08-27T23:48:12Z`
- **Last updated:** `2026-08-28T01:25:03Z`
- **Type:** `PRE-THEOREM CONTINUATION / RIGOROUS FULL-TAIL SCREEN / EXACT CANDIDATE`
- **Supports:** `A-20260826-001`, later `F-20260828-001`, `C-0056`
- **Status:** `HISTORICAL PRE-THEOREM EVIDENCE`

## Objective

Continue the one-prime localized Weil / Legendre-Schur mechanism above the verified `T=1/2` frontier while remaining strictly below the structural threshold `(1/2)log 3`. The canonical driver was required to stop at `CANDIDATE_READY`; this computation did not admit a theorem pair, generate a theorem certificate, edit the verifier whitelist, or invoke the independent theorem verifier.

## First canonical pass

The first run used

```text
T=21/40
N=72,76,...,128
```

with the canonical `continuation-driver-p15-v1` workflow. Floating reconnaissance became stable-positive from `N=88` upward, but rigorous full-tail precision escalation overturned the first two scout positives:

```text
N=88 -> MATHEMATICAL_NEGATIVE
N=92 -> MATHEMATICAL_NEGATIVE
```

At converged 512-bit precision the full Schur minima were approximately

```text
N=88: -0.5482556100498948
N=92: -0.12127824455981323.
```

This demonstrated that the truncated floating scout can materially overstate positivity at this larger support; the rigorous full-tail penalty remains decisive.

## Second canonical pass

Because the negative margin improved sharply from `N=88` to `N=92`, the canonical driver was rerun only over the unresolved higher range

```text
N=96,100,...,128.
```

All nine dimensions were floating stable-positive. Rigorous screening of the primary/fallback pair then gave

```text
N=96  PRECISION_STABLE at 512 bits
N=100 PRECISION_STABLE at 512 bits.
```

For the selected smallest successful dimension `N=96`, the converged full-tail values were approximately

```text
mu_96                    = 0.6960091338406399
finite block min         = 2.71647006832036e-7
full Schur min           = 2.6312924612533194e-7.
```

Exact outward rounding succeeded at 64 matrix bits with 32-bit exact witnesses. The resulting exact rational quantities were all positive. Fixed-parameter reassembly from 512 to 640 Arb bits left the exact `mu`, even margin, and odd margin unchanged while working interval widths contracted. The driver therefore ended at

```text
CANDIDATE_READY
selected (T,N)=(21/40,96)
classification=CANDIDATE_STABLE
confirmed precision=640 bits.
```

`N=100` also reached generator-side exact candidate readiness, but the driver selected the smaller `N=96`; `N=100` was not automatically admitted and remains outside the theorem whitelist.

## Bundle structure

The retained data are under

```text
data/continuation-T021-040/
data/continuation-T021-040-N096-128/
```

The second-pass summary SHA-256 is

```text
fcd359d77d31da198fa74021ab037e35d0aba15d307aae92fa9190a15560eb17
```

and the selected exact-candidate artifact SHA-256 is

```text
9e9d11197a97283f08f669056c1ef2f85ed920fa3acad8e5d8841221feb53444.
```

## Later theorem promotion

This record remains pre-theorem. A later separate research decision explicitly admitted only `(T,N)=(21/40,96)` and fresh proof-bearing `X-20260828-001` independently established `C-0056`. The fresh theorem certificate is not this candidate artifact.

## Limit

This computation does not prove RH and does not establish positivity beyond `T=21/40`. The entry of the `p=3` compressed translation at `(1/2)log 3` remains a separate structural phase.
