# High-precision prime-trace cutoff study

- **Computation ID:** `X-20260820-003`
- **Created:** `2026-08-20T21:05:31Z`
- **Last updated:** `2026-08-20T21:05:31Z`
- **Status:** `COMPLETE`

## Objective

Measure how the cutoff required to approximate the prime-Laguerre trace grows with `n`, and test whether moving `s0` right makes larger `n` numerically accessible.

## Environment

- Python `3.14.0`
- standard library only
- `decimal.Decimal`, 60 digits
- exact prime-power enumeration through a bytearray sieve
- script: `scripts/prime_trace.py`
- script SHA-256 at retained run: `0ec8216bce6477391d5214566192339f3cc64043435557e21aed19c717830880`

## Reproduction procedure

```text
python scripts/prime_trace.py --s0 3 --n-max 16 --cutoffs 10000,100000,1000000 --precision 60
python scripts/prime_trace.py --s0 4 --n-max 24 --cutoffs 10000,100000,1000000 --precision 60
```

## Selected output

Change in cutoff diagnostic `S_n(X)` between `X=10^5` and `10^6`:

```text
s0=3:
n=1   +2.47e-10
n=4   -7.22e-6
n=7   +7.48e-3
n=8   -4.89e-2
n=12  -1.57e1
n=16  -3.66e2

s0=4:
n=1   +2.33e-15
n=8   -6.05e-6
n=12  -1.23e-2
n=14  -2.53e-1
n=16  -3.25e0
n=20  -1.31e2
n=24  -5.99e2
```

## Interpretation

A fixed prime cutoff ceases to resolve the trace as `n` rises. Moving from `s0=3` to `s0=4` materially extends the numerically stable range at the same cutoff, consistent with the moving scale `x_*=exp[4nA/(A^2-1)]`.

## Limitations

`S_n(X)=P_n(X)-(1-q^n)` is only a cutoff diagnostic. No row is treated as the infinite `S_n` unless convergence is independently established. These data provide no evidence for or against RH.

## Related claims / attempts / findings

`A-20260820-003`, `F-20260820-011`.
