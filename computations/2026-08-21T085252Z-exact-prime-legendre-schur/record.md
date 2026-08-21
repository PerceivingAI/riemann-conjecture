# Exact-prime Legendre complement and Schur reconnaissance

- **Computation ID:** `X-20260821-004`
- **Created:** `2026-08-21T08:52:52Z`
- **Last updated:** `2026-08-21T08:56:20Z`
- **Status:** `COMPLETE`

## Objective

Test the initially proposed `69%` absorbed residual target rigorously; if it fails, quantify a rigorous high-Legendre-mode complement bound for the exact-prime operator and scout a plausible finite Schur dimension.

## Mathematical quantity tested

At `T=7/20`, the exact scaled first-prime form is

```text
J+V+P_2+R_T-c_T I.
```

The proof-path artifact evaluates the explicit polynomial `w=P_0-P_2`, the absorbed operator `J+0.69V+R_T-c_TI`, the exact-prime value, and

```text
mu_N=H_N-c_T-c_2-rho_R.
```

The separate scout assembles normalized-Legendre finite matrices and truncated component tail Grams for the factor-3 Schur reduction.

## Environment

- software/runtime: CPython 3.14.0 project `.venv`
- rigorous library: python-flint/Arb from the pinned project environment
- reconnaissance libraries: NumPy/SciPy from the pinned project environment
- rigorous precision: 224 bits
- scout arithmetic: ordinary double precision; not proof

## Inputs and parameters

Proof path:

```text
T=7/20
prec=224
max_n=30
residual_order=32
w=P_0-P_2
```

Scout:

```text
max_mode=120
quadrature_order=700
shift_order=350
N=18,20,22,24,28,32,40,50
```

## Reproduction procedure

```text
python -m scripts.weil_exact_prime_complement_certificate \
  --prec 224 \
  --max-n 30 \
  --residual-order 32 \
  --output-json computations/2026-08-21T085252Z-exact-prime-legendre-schur/data/certified-complement.json

python -m scripts.weil_legendre_schur_scout \
  --max-mode 120 \
  --quadrature-order 700 \
  --shift-order 350 \
  --n 18,20,22,24,28,32,40,50 \
  --output-json computations/2026-08-21T085252Z-exact-prime-legendre-schur/data/schur-scout.json
```

Script SHA-256:

```text
weil_exact_prime_complement_certificate.py
dbf041e0266b18938c0fba8e8792aa6f7c7a3afc7627c2f9904c6a10f075cd6b

weil_legendre_schur_scout.py
7772b90a75ef2e1cbf66057fc9e5ab4623826576440d69f796c47a02a8153c36
```

Data SHA-256:

```text
certified-complement.json
a9942313256af6171db6e7d19be44cb4743beb2f2cdf1ecac79b33ee10c618c2

schur-scout.json
4569274137b9869a8bcb5c4adc4b51fc322db762dcbcf6313d6a7ab3e7b9a831
```

## Output

### Rigorous proof-path output

The Arb certificate proves

```text
Q_0.69(P_0-P_2)<0.
```

The value is enclosed near `-0.05275381732676` with strictly negative upper endpoint.

It also proves that the exact-prime value on the same polynomial is positive, near

```text
+0.0143337515668.
```

The retained critical scalar fraction is approximately

```text
alpha_critical=0.9337265205748...
```

and the exact prime loss on this direction is only approximately

```text
-P_2/V=5.04917e-5.
```

For the complement,

```text
rho_R <= 1.33218539338044...
```

and the first certified positive `mu_N` is

```text
N=14,
mu_14 ~ 0.0639772546354 >0.
```

All proof-path JSON numerical values are exact rational interval endpoints; no ordinary float is serialized as a proof premise.

### Floating reconnaissance

The finite `max_mode=120` exact-prime Ritz scout has lowest eigenvalue near

```text
0.00119357.
```

The factor-3 Schur scout becomes positive among the tested dimensions at `N=28` and remains positive for `N=32,40,50`, with values around `1.17e-3` to `1.19e-3`.

## Interpretation

The `69%` global absorption inequality is mathematically valid but too lossy for the desired full first-prime positivity theorem. Retaining the exact first-prime shift produces a viable Legendre-Schur architecture: high modes are rigorously coercive, and the remaining task is a finite tail-Gram certificate.

`N=32` is selected as the first rigorous target rather than `N=28` to leave additional numerical/interval margin.

## Limitations

The scout does not prove positivity. Its tail Grams are truncated at `max_mode=120`, so they are not rigorous infinite-tail bounds. No full Schur matrix has yet been enclosed with Arb and passed through `rh_cert`.

The rigorous artifact proves only the explicit obstruction, the test-function exact-prime positivity, and the crude high-mode complement bound.

## Related claims / attempts / findings

- `A-20260821-004`
- `F-20260821-016` through `F-20260821-020`
- `C-0045` through `C-0049`

## Timestamped addenda / corrections

None.
