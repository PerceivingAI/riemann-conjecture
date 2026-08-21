# Public FP-0.35 certificate claim is not verified by this repository

- **Finding ID:** `F-20260821-015`
- **Created:** `2026-08-21T04:06:54Z`
- **Last updated:** `2026-08-21T04:06:54Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

At pinned external commit

```text
e66f467bc4447c5b2491577cbb6c3ae0e721fb43
```

of `R-0031`, the public repository claims strict finite-scale Weil positivity at `T=7/20`, but the available checker/replay paths inspected during `A-20260821-003` do not provide a single internally consistent trusted full-`c_T` proof chain that this repository can accept as rigorous.

This is a source-audit conclusion, not a claim that FP-0.35 is false.

## Specific audit findings

1. `scripts/reproduce_fp035.py` builds `tau` from a rational approximation to binary-float `log(2)` and injects `c_2` from a binary float into Arb as a point value. The exact `tau` error of the retained rational point is about `1.924e-9`; smallness alone is not an enclosure proof.
2. `checker/fp035/recompute_schur.py` uses the real `c_T` formula but floating `tau`, floating `c_2`, and a numerical LDL pivot.
3. `checker/first_prime/exact_split.py` uses rational log2 bounds for its prime layer but sets `c_L=0`, so it is the easier O1-B gate, not the full FP-0.35 form with `c_T≈1.36527`.
4. Lower-level source comments distinguish interim mpmath interval LDL from the still-intended full exact/Fraction certification.
5. The external repository itself documents earlier certificate defects and currently contains status text saying both that FP-0.35 holds and that parts of the trusted replay/release chain remain in progress.

## Repository policy consequence

`FP-0.35` remains **unverified external work** here until independently replayed with:

- exact interval transcendental constants;
- certified primitive enclosures;
- a rigorous infinite-dimensional complement bound;
- and interval/exact positive-definiteness certification of the full `c_T` form.

## Dependencies

- `R-0031`
- `A-20260821-003`
- `X-20260821-003`
