# Chirp-window and Dirichlet-length diagnostics

- **Computation ID:** `X-20260820-008`
- **Created:** `2026-08-20T22:44:00Z`
- **Last updated:** `2026-08-20T22:44:00Z`
- **Status:** `COMPLETE`

## Objective

Quantify the logarithmic scale of fixed-interior chirp cells, the first-prime frequency cap, the local linearization width, and the exponential root scale left by a generic Montgomery-Vaughan Dirichlet-polynomial mean-value estimate.

## Mathematical quantity tested

For `A=2s0-1`, `u in (0,1)`, and `n>=1`:

```text
gamma(u)=A/2 sqrt((1-u)/u),
log X=4n u/A,
Phi_n''(y)=-A^2/[16n u^(3/2)sqrt(1-u)].
```

The diagnostic window `H` is chosen by

```text
(1/2)|Phi_n''(y_0)|H^2=phase_error.
```

The generic Dirichlet-polynomial mean-value length term has logarithmic RMS rate

```text
(log X)/(2n)=2u/A,
```

hence root base `exp(2u/A)`.

The first-prime coordinate and frequency are

```text
u_2=A log 2/(4n),
gamma_2=A/2 sqrt((1-u_2)/u_2).
```

## Environment

- CPython `3.14.0`
- standard library only for this diagnostic
- project environment resolved by `uv.lock`
- script: `scripts/chirp_window_diagnostics.py`
- script SHA-256: `1310296e21ad71b515acae6f4a009403c92ed09f0053252f9d10d8e7298a28e0`
- retained data SHA-256:
  - `s0-2-n1024.json`: `6fa5d90049897f8e49190fd134d6336ad70801ca8e490611f14978fcdeac5f89`
  - `s0-3-n1024.json`: `790ae78b5d1de4cb3c188da349acf395892c0aefb4069d3abd306c3a9d4c07fc`
  - `s0-4-n1024.json`: `dfc5b016ebb1c5bc13a9f3370fa852b2900996d25228a1527dde61035e7e8eea`

## Inputs and parameters

Retained runs:

```text
n=1024
s0=2,3,4
u=0.02,0.05,0.10,0.25,0.50,0.75
phase_error=0.25
```

## Reproduction procedure

```text
.venv\Scripts\python.exe scripts\chirp_window_diagnostics.py --s0 2 --n 1024 --output-json computations\2026-08-20T224400Z-chirp-window-reduction\data\s0-2-n1024.json
.venv\Scripts\python.exe scripts\chirp_window_diagnostics.py --s0 3 --n 1024 --output-json computations\2026-08-20T224400Z-chirp-window-reduction\data\s0-3-n1024.json
.venv\Scripts\python.exe scripts\chirp_window_diagnostics.py --s0 4 --n 1024 --output-json computations\2026-08-20T224400Z-chirp-window-reduction\data\s0-4-n1024.json
```

## Output

At `s0=3`, `A=5`, `n=1024`:

```text
u_2=8.461269293945e-4
gamma_2=85.90895535014
gamma_2/sqrt(n)=2.684654854692
```

The asymptotic constant is

```text
sqrt(A/log 2)=2.685...
```

Selected generic mean-value root bases:

```text
u=0.02 -> 1.008032086
u=0.10 -> 1.040810774
u=0.25 -> 1.105170918
u=0.50 -> 1.221402758
u=0.75 -> 1.349858808
```

These equal `exp(2u/A)` to displayed precision.

## Interpretation

The computation confirms the scale derivations used in `A-006`:

1. the first-prime frequency is `O(sqrt(n))`;
2. local phase-linearization windows are `O(sqrt(n))` in `y=log x`;
3. their centers remain exponentially large in `n` for fixed `u>0`;
4. the generic Montgomery-Vaughan length term preserves a positive exponential root base.

## Limitations

This script does not enumerate primes and does not test an arithmetic cancellation theorem. It only checks the deterministic scales in the analytic reduction.

## Related claims / attempts / findings

`A-20260820-006`, `F-20260820-023`, `F-20260820-024`, `F-20260820-025`.

## Timestamped addenda / corrections

None.
