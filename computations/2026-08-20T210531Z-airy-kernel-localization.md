# Airy-kernel localization scan

- **Computation ID:** `X-20260820-002`
- **Created:** `2026-08-20T21:05:31Z`
- **Last updated:** `2026-08-20T21:05:31Z`
- **Status:** `COMPLETE`

## Objective

Locate the sampled maximum of `|exp(-pt)L_(n-1)^(1)(t)|` in the uniform coordinate `u=t/(4n)` and compare it with the analytic saddle `u_*=A^2/(A^2-1)`.

## Environment

- Python `3.14.0`
- standard library only
- binary64 exploratory recurrence
- script: `scripts/kernel_scan.py`
- script SHA-256 at retained run: `4d73542b930cdb7e52cd358ce6a028baefff5df673170f19010aba7c636c0220`

## Reproduction procedure

```text
python scripts/kernel_scan.py --s0 3 --n 64,128,256 --u-max 1.12 --steps 11200
python scripts/kernel_scan.py --s0 4 --n 128,256 --u-max 1.08 --steps 10800
```

## Output

For `s0=3`, `A=5`:

```text
predicted u_* = 1.04166666667
log|q|       = 0.405465108108

n    sampled u_max   log(max)/n
64   1.0211          0.348709898
128  1.0310          0.374412777
256  1.0362          0.388597201
```

For `s0=4`, `A=7`:

```text
predicted u_* = 1.02083333333
n=128: sampled u_max=1.0080
n=256: sampled u_max=1.0141
```

## Interpretation

The sampled maxima move toward the analytically predicted Airy saddle as `n` grows, and the observed per-`n` log amplitude moves toward `log|q|` from below.

## Limitations

This scan is not a proof of the uniform asymptotic. Binary64 recurrence is used only as reconnaissance. The saddle and rate in `F-20260820-010` are derived analytically from DLMF.

## Related claims / attempts / findings

`A-20260820-003`, `F-20260820-010`.
