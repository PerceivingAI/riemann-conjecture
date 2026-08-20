# Prime-density decomposition in the turning window

- **Computation ID:** `X-20260820-004`
- **Created:** `2026-08-20T21:05:31Z`
- **Last updated:** `2026-08-20T21:05:31Z`
- **Status:** `COMPLETE`

## Objective

Compare the discrete prime-power contribution with the continuous prime-density integral in bins of `u=t/(4n)`, especially near the turning/Airy region.

## Environment

- Python `3.14.0`
- standard library only
- binary64 Laguerre recurrence
- composite Simpson quadrature
- script: `scripts/prime_range_decomposition.py`
- script SHA-256 at retained run: `a09b45ebcd6e0d93d3b4bdd9b954c9d25f16e64f4786266f1c9e64444de0ac97`

## Reproduction procedure

```text
python scripts/prime_range_decomposition.py --s0 3 --n 8,12,16 --max-m 2000000 --u-bins 0,0.25,0.5,0.75,1.0,1.25,1.5 --simpson-steps 800
python scripts/prime_range_decomposition.py --s0 3 --n 16 --max-m 2000000 --u-bins 0,0.25,0.5,0.75,1.0,1.25,1.5 --simpson-steps 1600
```

## Selected output

For `s0=3`, `n=16` at 1600 Simpson steps:

```text
u range      prime sum       density integral   difference
0.50-0.75    +27.10497377    +27.11571325       -0.01073948
0.75-1.00    -325.8458248    -325.8255670       -0.02025776
1.00-1.25    -228.3793946    -228.4233557       +0.04396110
```

The 800-step run agreed in the displayed differences to the reported digits relevant here.

## Interpretation

Near the turning region, the discrete and smooth-density contributions are individually large but locally very close. In the `0.75-1.00` bin the absolute difference is about `2e-2` against a main contribution of about `3.26e2`.

The within-bin `cancellation_ratio` was close to `1` in the largest turning bins, so this small difference is **not** primarily cancellation among positive/negative prime terms inside the bin. It is prime density tracking the continuous main term. That supports working with the discrepancy measure from `A-002` directly.

## Limitations

This is a finite-cutoff, finite-`n` observation. It does not imply an asymptotic error estimate and cannot be extrapolated to RH.

## Related claims / attempts / findings

`A-20260820-003`, `F-20260820-010`, `F-20260820-012`.
