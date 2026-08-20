# Research scripts

- **Created:** `2026-08-20T20:59:00Z`
- **Last updated:** `2026-08-20T21:05:31Z`

These scripts are research instruments for the timestamped RH attempts. They use only the Python standard library so the numerical work does not depend on an unrecorded scientific-Python environment.

## Scripts

### `verify_identities.py`

Exact rational checks of the algebra used by `A-20260820-002`:

- `L_n^(0)=L_n^(1)-L_(n-1)^(1)`;
- the pole/main-density integral equals `1-q^n`;
- `T=(E-1)(E-q)` annihilates `1-q^n`.

Run:

```text
python scripts/verify_identities.py --max-n 40
```

### `prime_trace.py`

High-precision `decimal.Decimal` cutoff study of the prime-Laguerre sequence. It reports `P_n(X)` and the diagnostic `S_n(X)=P_n(X)-(1-q^n)` at several prime-power cutoffs.

Run:

```text
python scripts/prime_trace.py --s0 3 --n-max 16 --cutoffs 10000,100000,1000000 --precision 60
```

`S_n(X)` is **not** the exact infinite `S_n` unless cutoff convergence is established. The script labels it accordingly.

### `kernel_scan.py`

Scans the continuous prime-density kernel

```text
e^(-p t) L_(n-1)^(1)(t),
```

and compares its sampled maximum with the Airy-saddle prediction `u_*=A^2/(A^2-1)` and exponential rate `log|q|`. It uses the DLMF uniform scaling

```text
u = 4n,
u = t/(4n).
```

Run:

```text
python scripts/kernel_scan.py --s0 3 --n 8,16,32,64 --u-max 1.6
```

### `prime_range_decomposition.py`

Breaks the truncated prime-power trace into bins in the uniform variable `u=t/(4n)`. For each bin it compares the discrete prime contribution with the continuous main-density integral and reports their discrepancy and an internal cancellation ratio.

Run:

```text
python scripts/prime_range_decomposition.py --s0 3 --n 8,12,16 --max-m 2000000
```

## Shared implementation

`rh_tools.py` contains the standard-library Laguerre recurrence, prime sieve, von Mangoldt prime-power enumeration, pole parameters, high-precision trace accumulation, Simpson integration, and the turning-scale helper.

## Interpretation rule

These scripts can:

- falsify proposed identities or bounds;
- reveal numerical localization and scaling;
- identify unstable cutoff regimes;
- guide which analytic lemma is worth attempting.

They cannot prove RH by numerical verification. Every retained run belongs in `docs/computations/` with exact parameters and limitations.
