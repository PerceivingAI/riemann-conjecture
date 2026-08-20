# Regionwise absolute-bound barrier

- **Finding ID:** `F-20260820-014`
- **Created:** `2026-08-20T21:20:00Z`
- **Last updated:** `2026-08-20T21:20:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

Let `Phi_A(u)` be the post-turning smooth-density exponent from `A-003`. There is a unique `u_0(A)>u_*` with `Phi_A(u_0)=0`.

- On every fixed region `u>=u_0+delta`, the discrepancy integral is exponentially suppressed using the uniform Laguerre expansion and only the ordinary PNT `E(x)=o(x)`.
- In every fixed pre-turning region with `u>0`, an absolute-value estimate using the current unconditional Vinogradov-Korobov-scale PNT error retains positive root rate `exp(2u/A)>1`; the relative PNT error contributes only `exp[-o(n)]` at `log x ~ c n`.

Therefore the complement of a narrow post-turning saddle window cannot be discarded by absolute estimates. Pre-turning/oscillatory contributions require phase-sensitive cancellation.

## Evidence / derivation

`Phi_A` decreases strictly after `u_*` and tends to `-infinity`, giving a unique zero. Below the turning point, the DLMF Bessel representation leaves exponential envelope `exp[nu u/(2A)]`. Johnston's current PNT-error form gives a relative factor with exponent `o(n)` on the moving exponential-in-`n` prime scale.

## Dependencies

- `A-20260820-004`
- `R-0011`
- `R-0015`
- `X-20260820-005`

## Significance for RH research

This closes the far post-turning tail but invalidates the strategy of reducing the proof to independent absolute control of a single narrow Airy/saddle window.

## Limits

It does not rule out oscillatory or signed cancellation in the pre-turning region; it shows only that known absolute-error inputs cannot supply the required root bound.

## Verification

Analytic rate signs checked directly; `window_diagnostics.py` reports the positive pre-turning root rates and the numerical `u_0(A)` values.

## Timestamped addenda / corrections

None.
