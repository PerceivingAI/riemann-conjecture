# Post-turning saddle width and phase-loss diagnostics

- **Computation ID:** `X-20260820-005`
- **Created:** `2026-08-20T21:20:00Z`
- **Last updated:** `2026-08-20T21:20:00Z`
- **Status:** `COMPLETE`

## Objective

Numerically check the post-turning saddle width derived in `A-004`, locate the post-turning root-one crossing, quantify pre-turning absolute-envelope rates, and compare beta-only envelope rates with exact Cayley amplification after retaining a complex phase.

## Mathematical quantity tested

For the smooth-density kernel

```text
D_n(t)=exp[-(s0-1)t/A]L_(n-1)^(1)(t),
```

test the saddle `u_*=A^2/(A^2-1)`, curvature

```text
k_A=(A^2-1)^2/(2A^3),
```

and the exact Cayley rate for synthetic `rho=beta+i gamma`.

## Environment

- software/runtime: Python `3.14.0`
- dependencies: Python standard library only
- numeric precision: binary64 exploratory recurrence
- script: `scripts/window_diagnostics.py`
- script SHA-256: `567d993af084c4cfefcd027c4721a6361fdb69736ed9781786c1934797236880`

## Inputs and parameters

Centers `s0=2,3,4`; `n=64,128,256`; beta values `0.5,0.6,0.9,1.0`; gamma values `0,5,15`.

## Reproduction procedure

```text
python scripts/window_diagnostics.py --s0 2 --n 64,128,256 --betas 0.5,0.6,0.9,1.0 --gammas 0,5,15
python scripts/window_diagnostics.py --s0 3 --n 64,128,256 --betas 0.5,0.6,0.9,1.0 --gammas 0,5,15
python scripts/window_diagnostics.py --s0 4 --n 64,128,256 --betas 0.5,0.6,0.9,1.0 --gammas 0,5,15
```

## Selected output

For `s0=3`, `A=5`:

```text
u_*             = 1.04166666667
u_post_root1    = 1.72286415296
k_A             = 2.304

n=64:  delta_u(e^-1)=0.082350981, delta_log_x=4.216370214
n=128: delta_u(e^-1)=0.058230937, delta_log_x=5.962847940
n=256: delta_u(e^-1)=0.041175490, delta_log_x=8.432740427
```

Pre-turning smooth-density root envelopes:

```text
u=0.25 -> 1.105170918
u=0.50 -> 1.221402758
u=0.75 -> 1.349858808
nu=1.00 -> 1.491824698
```

Phase-loss example at `beta=0.6`:

```text
gamma=0:  beta-envelope=1.083333333, exact=1.083333333
gamma=5:  beta-envelope=1.083333333, exact=1.016124871
gamma=15: beta-envelope=1.083333333, exact=1.002164411
```

For `beta=1/2`, the exact rate was `1` for every tested gamma, as required by the critical-line geometry.

## Interpretation

The saddle-width scaling is consistent with the analytic `n^(-1/2)` law. More importantly, discarding the complex phase can grossly overestimate the exponential rate of a mode.

The positive pre-turning absolute-envelope rates confirm that current absolute PNT bounds cannot eliminate that region at root-growth level.

## Limitations

Binary64 recurrence is diagnostic only. The script's beta/gamma pairs are synthetic unless independently known to be zeros. The analytic findings do not depend on these numerical examples.

## Related claims / attempts / findings

`A-20260820-004`, `F-20260820-013`, `F-20260820-014`, `F-20260820-015`.

## Timestamped addenda / corrections

None.
