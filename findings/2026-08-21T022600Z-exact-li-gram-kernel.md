# Exact Li Gram kernel

- **Finding ID:** `F-20260821-006`
- **Created:** `2026-08-21T02:26:00Z`
- **Last updated:** `2026-08-21T02:26:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

With `lambda_0=0`, define

```text
K_jk=lambda_j+lambda_k-lambda_|j-k|.
```

Under RH,

```text
K_jk=sum_rho (1-w_rho^j)(1-conj(w_rho^k)),
```

so every finite `K^(N)` is PSD. Conversely `K_nn=2lambda_n`, hence PSD of all finite matrices implies Li positivity and RH.

Therefore

```text
RH <=> K^(N) is PSD for every N.
```

## Evidence / derivation

Direct expansion using `|w_rho|=1` and zero conjugation; converse is the diagonal plus Li's criterion.

## Dependencies

- `A-20260821-002`
- `C-0001`
- `R-0001`, `R-0002`

## Significance for RH research

Provides an exact regularization-free finite Gram kernel for the Li sequence.

## Limits

It is not a weaker criterion: the original Li inequalities occur on the diagonal.

## Verification

Algebraic derivation and synthetic unit-circle numerical check in `X-20260821-002`.

## Timestamped addenda / corrections

None.
