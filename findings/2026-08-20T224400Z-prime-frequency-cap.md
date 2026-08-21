# Actual prime-side Mellin frequency is capped at order square-root n

- **Finding ID:** `F-20260820-023`
- **Created:** `2026-08-20T22:44:00Z`
- **Last updated:** `2026-08-20T22:44:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For the pre-turning chirp with `A=2s0-1`, actual prime atoms begin at

```text
u_2=A log 2/(4n).
```

Because the frequency

```text
gamma(u)=A/2 sqrt((1-u)/u)
```

is decreasing, the maximal frequency sampled by a prime atom is

```text
gamma_2(n)
= A/2 sqrt(4n/(A log 2)-1)
~ sqrt(A n/log 2).
```

Thus the discrete prime side carries only `O(sqrt(n))` Mellin frequencies.

## Evidence / derivation

Substitute the first-prime coordinate into the exact stationary-frequency map from `C-0021`.

## Dependencies

- `A-20260820-006`
- `C-0021`
- `F-20260820-022`
- `X-20260820-008`

## Significance for RH research

The `gamma~n` endpoint coalescence identified in `C-0025` occurs below the first prime in the prime-side interpretation. The global prime cancellation problem has exponentially long support but only polynomial Mellin-frequency range.

## Limits

This does not remove the exact high-zero content of the full analytic transform; it identifies where actual prime atoms occur in the chirp geometry.

## Verification

Algebraic derivation and numerical scale checks at `s0=2,3,4`, `n=1024` in `X-008`.

## Timestamped addenda / corrections

None.
