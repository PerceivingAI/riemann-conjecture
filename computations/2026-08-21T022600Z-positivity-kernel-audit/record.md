# Positivity kernel and Weil support-operator audit

- **Computation ID:** `X-20260821-002`
- **Created:** `2026-08-21T02:26:00Z`
- **Last updated:** `2026-08-21T02:26:00Z`
- **Status:** `COMPLETE`

## Objective

Check deterministic finite consequences of the positivity audit:

1. finite Li Gram and Schoenberg matrices for synthetic on-line/off-line zero orbits;
2. sign structure of generalized prime-atom Gram contributions;
3. Weil prime-power support thresholds and compressed-shift norms.

## Mathematical quantities tested

Li Gram kernel:

```text
K_jk=lambda_j+lambda_k-lambda_|j-k|.
```

Schoenberg Toeplitz kernel:

```text
Q_jk=exp[-t lambda_|j-k|].
```

Prime atom kernel up to the positive factor `A Lambda(m)m^(-s0)`:

```text
-[B_j(x)+B_k(x)-B_|j-k|(x)],
B_n=L_(n-1)^(1)(x).
```

Weil shift geometry:

```text
T_m=(1/2)log m,
||P_T(U_a+U_a^*)P_T||=2cos(pi/(L+1)),
L=ceil(2T/a).
```

## Environment

- CPython `3.14.0`
- NumPy from the project `uv.lock` environment for finite eigenvalues
- standard library for support geometry
- scripts:
  - `scripts/positivity_kernel_diagnostics.py`
    SHA-256 `4fc32ca79854b26df4fdcaf3133cfe4f0fcb4523a345b5d291cdf62fa2c028ee`
  - `scripts/weil_support_geometry.py`
    SHA-256 `ce685df11f7e1957bb5202bcb02fff9a266a3c94d6b2a3100b6769b58dd90703`

## Inputs and parameters

Kernel diagnostic:

```text
N=8,
theta=0.7,
r=1.2,
Schoenberg t=0.5,
prime-atom x=0,1,5,10.
```

Support diagnostics:

```text
T=0.34,0.45,0.60,
max prime power m=20.
```

## Reproduction procedure

```text
.venv\Scripts\python.exe scripts\positivity_kernel_diagnostics.py --n-dim 8 --theta 0.7 --r 1.2 --search-n 100 --t 0.5 --x 0,1,5,10 --output-json computations\2026-08-21T022600Z-positivity-kernel-audit\data\kernel-diagnostics.json

.venv\Scripts\python.exe scripts\weil_support_geometry.py --T 0.34 --max-m 20 --output-json computations\2026-08-21T022600Z-positivity-kernel-audit\data\support-T034.json
.venv\Scripts\python.exe scripts\weil_support_geometry.py --T 0.45 --max-m 20 --output-json computations\2026-08-21T022600Z-positivity-kernel-audit\data\support-T045.json
.venv\Scripts\python.exe scripts\weil_support_geometry.py --T 0.60 --max-m 20 --output-json computations\2026-08-21T022600Z-positivity-kernel-audit\data\support-T060.json
```

## Output

Synthetic unit-circle pair:

```text
Gram minimum eigenvalue = -1.7417e-15
Schoenberg minimum eigenvalue = 9.7820e-3
```

The tiny negative Gram value is ordinary floating-point roundoff at a theoretically PSD/rank-deficient matrix.

Synthetic off-line quartet:

```text
first negative lambda_n: n=8,
lambda_8=-3.0303263...,
Gram minimum eigenvalue=-12.2257...,
Schoenberg minimum eigenvalue=-3.58215... .
```

Prime-atom samples all have

```text
K_11=-2
```

before the positive common factor.

Support geometry:

```text
0.5 log2 = 0.346573590280...
0.5 log3 = 0.549306144334...
log2/sqrt2 = 0.490129071734...
```

At `T=0.34`, no prime powers are active.

At `T=0.45`, only `m=2` is active and

```text
chain length=2,
shift norm=1,
worst scalar penalty=0.490129071734... .
```

At `T=0.60`, `m=2,3` are active and the crude sum of individual operator-norm penalties is

```text
1.124413172332... .
```

## Interpretation

The finite experiments support the exact algebraic conclusions and isolate the first-prime support window. They do not approximate the full archimedean Weil operator and therefore do not establish positivity beyond the known restricted-support regime.

## Limitations

- synthetic zero orbits are diagnostics, not statements about actual zeta zeros;
- finite matrix eigenvalues do not prove infinite-dimensional positivity;
- the support script computes exact translation geometry only, not the archimedean spectral gap;
- no numerical result here is evidence of RH.

## Related claims / attempts / findings

- `A-20260821-002`
- `F-20260821-006` through `F-20260821-011`
- `C-0036` through `C-0041`

## Timestamped addenda / corrections

None.
