# First-prime Weil continuation: exact absorption and constant enclosures

- **Computation ID:** `X-20260821-003`
- **Created:** `2026-08-21T03:48:25Z`
- **Last updated:** `2026-08-21T04:06:54Z`
- **Status:** `COMPLETE`
- **Type:** exact rational certificate + certified Arb constants

## Objective

Retain only the rigorously reusable computational pieces from `A-20260821-003`:

1. a self-contained exact rational certificate for the first-prime endpoint-absorption constant at `T=7/20`;
2. outward-rounded Arb balls for the exact transcendental constants needed by a future full first-prime interval certificate.

An exploratory sine-basis Galerkin scout was **not retained** because the normalization audit showed that it omitted Suzuki's finite-support residual kernel; its data and script were deleted before this record was created.

## Environment

- CPython `3.14.0`
- exact certificate: Python standard-library `fractions.Fraction`
- constant enclosure: `python-flint 0.9.0`, Arb at `256` bits
- project environment resolved by `uv.lock`

## Retained scripts

### Exact rational absorption

```text
scripts/weil_endpoint_absorption_certificate.py
sha256 229acc6f2eb3f6bb83e5d629e3f9b49b8a6a4c83bbee4af5886e619da8c68780
```

Run:

```text
.venv\Scripts\python.exe scripts\weil_endpoint_absorption_certificate.py \
  --output-json computations\2026-08-21T034825Z-first-prime-weil-continuation\data\endpoint-absorption-rational.json
```

Retained data:

```text
data/endpoint-absorption-rational.json
sha256 b456d1a7dc67ba3f6f90d886f154fd8316a9b8827642c068bca43b14b6dca036
```

The certificate proves, using exact rational atanh-series bounds,

```text
842/1215 < log2 < 23581/34020,
epsilon < 34/1701,
kappa_edge > 8/5,
c_2 < 62/125,
c_2/kappa_edge < 31/100,
```

and concludes

```text
V+P_2 >= (69/100)V >= 0.
```

No floating-point value is used as a proof premise.

### Exact first-prime constants

```text
scripts/weil_exact_constants.py
sha256 226b44ac8bacfab372a2936a44a9763316d25fadfaa7b663435e392dfe048a17
```

Run:

```text
.venv\Scripts\python.exe scripts\weil_exact_constants.py --prec 256 \
  --output-json computations\2026-08-21T034825Z-first-prime-weil-continuation\data\exact-constants-arb.json
```

Retained data:

```text
data/exact-constants-arb.json
sha256 5faf31c126b27d229d6afc0c507ec5609a4d0fd874fc0000a511f88417fdd720
```

Selected balls:

```text
tau=log2/(7/20)
[1.98042051588555802690637748988050448021571466960072929748766 +/- 2.84e-60]

c_2=log2/sqrt2
[0.490129071734273595856950861817616690645730349549527360521123 +/- 1.24e-61]

c_T=log(2*pi*(7/20))+EulerGamma
[1.36527060681220065583730073019427666472543738980832338274545 +/- 2.56e-60]
```

The external rational `1355726/993009` is confirmed to be an upper bound for exact `c_T`; its gap is enclosed around `2.36039629629129348e-14`.

## Interpretation

These retained outputs provide exact/certified scalar inputs only. They do **not** certify the infinite-dimensional first-prime Weil form.

The next computation must combine these constants with:

- the full Suzuki residual kernel;
- a parity-adapted finite block;
- an independently proved complement/tail bound;
- and interval/exact positive-definiteness verification.

## Dependencies

- `A-20260821-003`
- `F-20260821-012`

## Limitations

- Finite-scale only; no RH implication.
- No Galerkin eigenvalue is retained as proof evidence.
- No external FP-0.35 certificate is imported.
