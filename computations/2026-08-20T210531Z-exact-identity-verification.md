# Exact identity verification for A-002/A-003

- **Computation ID:** `X-20260820-001`
- **Created:** `2026-08-20T21:05:31Z`
- **Last updated:** `2026-08-20T21:05:31Z`
- **Status:** `COMPLETE`

## Objective

Falsify indexing/sign errors in the Laguerre contiguous identity, pole integral, and pole-annihilating shift filter before using them in later asymptotics.

## Environment

- Python `3.14.0`
- standard library only
- exact arithmetic: `fractions.Fraction`
- script: `scripts/verify_identities.py`
- script SHA-256 at run: `272601e282fb321644b6712b13fb7ea0316ac56d9c3217dcfd270e99cbe5e55d`

## Reproduction procedure

```text
python scripts/verify_identities.py --max-n 40
```

## Output

```text
PASS
Laguerre contiguous identity: exact for n=1..40
s0=2:   pole integral and filter exact; q=-2
s0=3:   pole integral and filter exact; q=-3/2
s0=5/2: pole integral and filter exact; q=-5/3
s0=4:   pole integral and filter exact; q=-4/3
```

## Interpretation

No finite-case algebraic counterexample was found, and the tested statements were evaluated exactly rather than in floating point.

## Limitations

Finite verification is not a proof for all `n`. The general identities are proved analytically in `A-002` and sourced where appropriate.

## Related claims / attempts / findings

`A-20260820-002`, `A-20260820-003`, `C-0011`, `C-0012`.
