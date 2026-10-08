# OpenAI quasi-RH: zero strip and pole-subtracted Cayley coefficient bound

- **Finding ID:** `F-20261008-001`
- **Created:** `2026-10-08T01:42:58Z`
- **Last updated:** `2026-10-08T01:42:58Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`
- **Source dependency:** `EXT-0001` (OpenAI, `openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`)
- **Repository dependencies:** `C-0010`, `C-0019`
- **Claim:** `C-0060`

## Exact external input and trust boundary

Use only the externally sourced theorem

```text
For every complex s, Re(s) > 7/8 implies zeta(s) != 0.
```

Its pinned Lean declaration is `OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re` in
`lean/OAI/NumberTheory/DirichletL/Nonvanishing.lean`, recorded in
`references/external-results/EXT-0001-openai-quasi-rh.md`.

OpenAI's theorem is an **external mathematical dependency**, not a theorem proved or independently replayed in this repository. The argument below verifies **the deductions** given that external statement. It does not certify the upstream formal proof, and it does not prove RH.

## Consequence 1: nontrivial-zero strip

Every nontrivial Riemann-zeta zero `rho` has

```text
1/8 <= Re(rho) <= 7/8.
```

**Proof.** The external statement excludes `Re(rho)>7/8`. The standard functional-equation zero symmetry sends each nontrivial zero `rho` to the nontrivial zero `1-rho`. Applying the external statement to `1-rho` excludes `Re(rho)<1/8`. Neither step excludes zeros on either boundary. In particular the region `1/2<Re(rho)<=7/8` remains possible.

For `Theta=sup{Re(rho): rho a nontrivial zero}`, this gives `1/2<=Theta<=7/8`, using the standard critical-line symmetry and existence of nontrivial zeros.

## Consequence 2: quantitative Cayley coefficient root bound

Fix `s0>1` and retain the repository's conventions (`A-20260820-002`, `C-0010`):

```text
s(z) = [s0+(s0-1)z]/(1-z)
     = 1/2+(s0-1/2)(1+z)/(1-z),

Z_*(s)=(s-1)zeta(s),

G(z)=d/dz log Z_*(s(z))
    =-sum_(n>=1) S_n(s0) z^(n-1).
```

Set

```text
r0=(s0-7/8)/(s0-1/8),       0<r0<1.
```

For `|z|<r0`,

```text
Re[(1+z)/(1-z)] > (1-r0)/(1+r0),
Re s(z) > 1/2+(s0-1/2)(1-r0)/(1+r0) = 7/8.
```

The external theorem makes zeta zero-free in this image. The pole of zeta at `s=1` is removable in `Z_*`, whose value there is nonzero. Thus `G` is holomorphic throughout `|z|<r0`. By the Cauchy-Hadamard formula,

```text
limsup_(n->infinity) |S_n(s0)|^(1/n)
    <= 1/r0
     = (s0-1/8)/(s0-7/8).
```

This is **not** the `<=1` criterion required by `C-0010`, because the displayed bound is strictly greater than `1` at every fixed `s0>1`. Taking `s0->infinity` in the bound cannot establish RH: `C-0010` fixes `s0` before the `n->infinity` limit, and no needed uniform-in-`s0` estimate is supplied.

## Consequence 3: compatibility with exact single-zero amplification

For `rho=beta+i gamma`, `C-0019` gives the exact mode `z_rho^(-n)-1` where

```text
z_rho=(rho-s0)/(rho+s0-1),

|z_rho|^(-1)
 = sqrt(((s0+beta-1)^2+gamma^2)/((s0-beta)^2+gamma^2)).
```

If `1/2<beta<=7/8`, the ratio is still strictly greater than `1`. Thus the external theorem restricts which off-critical modes can occur but does not remove the exponential-growth obstruction detected by the original Laguerre route.

## Preliminary impact assessment (not a replacement for the full OAI-4 audits)

| Existing route / requirement | What EXT-0001 provides | What remains |
| --- | --- | --- |
| `C-0010` pole-subtracted Laguerre | Quantitative fixed-center upper root rate above | Missing RH-equivalent root rate `<=1` |
| `C-0016` and `C-0018` absolute discrepancy barriers | A zero-free region with exponent `7/8` | A `theta>1/2` pointwise bound still leaves an exponential loss under absolute values |
| `C-0019`, `C-0021`, `C-0025` zero-mode/stationary analysis | Excludes `beta>7/8` | Off-line modes `1/2<beta<=7/8` and high-frequency endpoint uniformity remain |
| `C-0028`, `C-0030`, `C-0034`, `C-0035` prime-side chirp | Narrows hypothetical zero modes | Does not yield subexponential microlocal control or square-root saving; even a hypothetical `X^(7/8+o(1))` discrepancy leaves `X^(3/8+o(1))` after critical half-weighting |
| Prime-counting error estimates | Supplies a new zero-location input for classical explicit-formula methods | A precise unconditional error theorem, logarithmic factors, and hypotheses require a separate derivation/audit |
| Localized Weil v1/v2 machinery | Provides external analytic context | No new support positivity, Schur bound, v2 admission or RH claim |

## Verification and circularity checks

1. The strip uses only the strict external half-plane and the standard zero symmetry; it makes no boundary-exclusion claim.
2. The Cayley inverse and `r0` boundary identity are exact algebraic equalities; for every `|z|<r0`, the mapped real part is strictly greater than `7/8`.
3. The coefficient bound uses existing `C-0010` generating-function normalization, removal of the zeta pole, and Cauchy-Hadamard. It does not assume any RH-equivalent estimate.
4. It distinguishes fixed `s0` from a varying center, and a source theorem from an independently replayed proof.
5. No inference about the numerical Weil certificates, generic `{2,3}` Schur target, or PNT logarithmic factors is made.

No source code from OpenAI has been copied. Independent Comparator replay remains optional, and this finding contains no private execution-environment information.
