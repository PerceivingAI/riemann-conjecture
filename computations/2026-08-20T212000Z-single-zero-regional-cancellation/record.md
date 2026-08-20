# Regional cancellation in an exact single-zero Laguerre mode

- **Computation ID:** `X-20260820-006`
- **Created:** `2026-08-20T21:20:00Z`
- **Last updated:** `2026-08-20T21:20:00Z`
- **Status:** `COMPLETE`

## Objective

Numerically split the exact phase-aware mode

```text
-integral_0^infinity e^(-p_rho t)L_(n-1)^(1)(t)dt
= z_rho^(-n)-1
```

into bins of `u=t/(4n)` to test whether region-by-region estimates preserve or destroy important cancellation.

## Mathematical quantity tested

Synthetic modes `rho=beta+i gamma` at `s0=3`, including a critical-line control (`beta=0.5`) and off-line diagnostics (`beta=0.6`).

## Environment

- software/runtime: Python `3.14.0`
- dependencies: Python standard library only
- numeric precision: binary64 complex Simpson integration
- script: `scripts/zero_mode_bins.py`
- script SHA-256: `0646bd5c8da6aea12409ba6adf1181c3cc4d039a01146802fdf3cb5b16d96bf5`

## Inputs and parameters

Main retained runs:

```text
s0=3, beta=0.6, gamma=15, n=8,16,32, 4000 Simpson steps/bin
s0=3, beta=0.5, gamma=15, n=8,16,32, 4000 Simpson steps/bin
s0=3, beta=0.6, gamma=5,  n=16,32,64, 5000 Simpson steps/bin
```

Bins:

```text
0,0.25,0.5,0.75,1,1.25,1.5,2,2.5
```

## Reproduction procedure

```text
python scripts/zero_mode_bins.py --s0 3 --beta 0.6 --gamma 15 --n 8,16,32 --steps-per-bin 4000
python scripts/zero_mode_bins.py --s0 3 --beta 0.5 --gamma 15 --n 8,16,32 --steps-per-bin 4000
python scripts/zero_mode_bins.py --s0 3 --beta 0.6 --gamma 5 --n 16,32,64 --steps-per-bin 5000
```

## Selected output

For `beta=0.6`, `gamma=5`, `n=64`:

```text
u range       |piece|
0.75-1.00     6.666312668
1.00-1.25     5.913524852

exact full magnitude      3.736248542
truncated integral        3.736342603
absolute numerical error  1.05e-4
```

For `beta=0.6`, `gamma=15`, the retained `n=8,16,32` runs matched the exact transform to between roughly `1e-8` and `1e-6` absolute error.

The critical-line control `beta=0.5`, `gamma=15` likewise matched the exact bounded transform.

## Interpretation

The exact transform is reproduced numerically, validating the sign/index convention. Individual regional pieces can exceed the final full-transform magnitude and cancel materially. Therefore independent absolute bounds on regions can lose precisely the phase cancellation that controls the exact coefficient.

## Limitations

The `beta=0.6` modes are synthetic diagnostics, not asserted zeta zeros. Finite quadrature says nothing about RH. The omitted tail is included in the reported numerical error.

## Related claims / attempts / findings

`A-20260820-004`, `F-20260820-015`.

## Timestamped addenda / corrections

None.
