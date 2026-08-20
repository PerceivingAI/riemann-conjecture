# Li coefficients, generalized centers, and the Laguerre-weighted prime trace

- **Attempt ID:** `A-20260820-001`
- **Created:** `2026-08-20T20:37:00Z`
- **Last updated:** `2026-08-20T20:49:00Z`
- **Status:** `BLOCKED`
- **Success target:** Prove an unconditional subexponential bound for the standard Li coefficients, or an equivalent generalized-Li bound, from an explicit prime-side representation without assuming an estimate already equivalent to RH.

## Question / goal

Can the Riemann Hypothesis be attacked by transforming nontrivial zeros to the unit circle, expressing the corresponding Li coefficients through primes, and then proving that the prime-side coefficients cannot contain the exponentially growing oscillatory behavior forced by an off-critical zero?

A secondary question is whether moving the Li generating-function center from the boundary point `s=1` to a point `s0>1`, where the Euler product converges absolutely, genuinely weakens the required prime-side estimate.

## Motivation

The Li criterion converts RH into positivity of a real sequence. Under the Möbius transform underlying that criterion, the critical line becomes the unit circle. An off-critical zero therefore maps to a point with modulus different from one, suggesting exponential behavior in high powers.

The prime-side expression for the Li coefficients contains Laguerre polynomials. At the standard center `s=1`, the Euler product is on its convergence boundary. The natural attempted improvement is therefore to use the generalized Li criterion at `s0>1`, where the prime Dirichlet series is absolutely convergent for each fixed coefficient.

## Dependencies and known results

- `C-0001` — Li criterion.
- `C-0002` — generalized Li criterion and generating function at a center `s0>1`.
- `C-0003` — Voros asymptotic dichotomy for Li coefficients.
- `C-0004` — RH equivalence with the square-root-scale Chebyshev-psi error bound.
- `C-0005` — Laguerre generating function and fixed-argument large-degree asymptotic.
- `C-0006` — exact generalized prime-Laguerre component.
- `C-0007` — zero-orbit contribution formula and critical-line pair correction.
- `C-0008` — fixed-prime `m^{-1/2}` envelope cancellation for generalized centers.

Primary literature/source registry entries used: `R-0001` through `R-0009` as applicable.

## Mathematical setup

Define the completed Riemann xi function

```text
xi(s) = (1/2) s(s-1) pi^(-s/2) Gamma(s/2) zeta(s).
```

Its nontrivial zeros are the nontrivial zeros of `zeta`, and the functional equation gives

```text
xi(s) = xi(1-s).
```

The zero set is also invariant under complex conjugation.

### 1. Standard Li map

For a nontrivial zero `rho`, define

```text
w(rho) = (rho - 1)/rho = 1 - 1/rho.
```

Then

```text
|w(rho)| = 1
```

if and only if

```text
|rho-1| = |rho|,
```

which is equivalent to

```text
Re(rho) = 1/2.
```

Thus the standard Li Möbius map sends the critical line exactly to the unit circle.

The standard Li coefficients are

```text
lambda_n = sum_rho [1 - (1 - 1/rho)^n],
```

with the zero sum interpreted in the standard symmetric sense described by Li and Bombieri-Lagarias.

### 2. Generalized center in the Euler-product half-plane

Fix

```text
s0 > 1
A  = 2 s0 - 1 > 1.
```

Define the Möbius map

```text
s(z) = s0 + A z/(1-z).
```

Its inverse is

```text
z(s) = (s-s0)/(s+s0-1).
```

The points `s0` and `1-s0` are reflections across the critical line. Therefore

```text
|z(s)| = 1  <=>  Re(s) = 1/2.
```

Sekatskii's generalized-Li generating function specializes to

```text
log xi(s(z)) = log xi(s0) + sum_{n>=1} ell_n(s0) z^n/n.
```

At `s0=1`, this reduces to the standard Li generating function and `ell_n(1)=lambda_n`.

For `s0>1`, nonnegativity of all generalized coefficients `ell_n(s0)` is an RH-equivalent criterion (with the conventional zero pairing specified in the source).

## Derivation / argument

### Step 1 — zero symmetry and orbit contributions

Suppose first that `rho` is genuinely off the critical line and is not real. Its symmetry orbit consists of four distinct zeros

```text
rho, conjugate(rho), 1-rho, 1-conjugate(rho).
```

Write

```text
w(rho) = r exp(i theta).
```

The four standard-Li transformed values are

```text
w, conjugate(w), 1/w, 1/conjugate(w).
```

Their combined contribution to `lambda_n` is

```text
C_n(off) = 4 - [w^n + conjugate(w)^n + w^(-n) + conjugate(w)^(-n)]
         = 4 - 2(r^n + r^(-n)) cos(n theta).
```

This is an exact algebraic identity for a four-element off-line orbit.

#### Critical correction to the original informal derivation

On the critical line, `1-rho = conjugate(rho)`. The symmetry orbit has only two distinct zeros, not four. If

```text
w = exp(i theta),
```

then the actual pair contribution is

```text
C_n(on) = 2 - w^n - conjugate(w)^n
        = 2 - 2 cos(n theta)
        = 4 sin^2(n theta/2) >= 0.
```

The earlier informal value `8 sin^2(n theta/2)` was a factor-of-two error caused by counting the same critical-line pair twice as though the four symmetry images were distinct. This repository uses the corrected pair formula.

The quartet formula by itself is not used to claim a global asymptotic for `lambda_n`; cancellation among different zeros must be handled globally. For the rigorous global growth dichotomy, this attempt relies on Voros (`C-0003`).

### Step 2 — a weaker target than positivity

Voros proves a sharp large-`n` alternative: on RH the Li coefficients have tame `n log n` growth, whereas failure of RH produces a non-tempered oscillatory form with exponentially growing amplitude.

Therefore a proof of

```text
lambda_n = exp(o(n))
```

would already imply RH. Any fixed polynomial bound, for example

```text
|lambda_n| <= n^100
```

for all sufficiently large `n`, would be far stronger than necessary for this purpose.

This is useful because it replaces the sign problem `lambda_n >= 0 for every n` by a growth problem.

### Step 3 — exact prime-Laguerre kernel at `s0>1`

Differentiate the generalized generating function:

```text
d/dz log xi(s(z))
  = A/(1-z)^2 * xi'(s(z))/xi(s(z))
  = sum_{n>=1} ell_n(s0) z^(n-1).
```

For `Re(s)>1`,

```text
zeta'(s)/zeta(s) = - sum_{m>=2} Lambda(m) m^(-s),
```

where `Lambda` is the von Mangoldt function.

Also

```text
m^(-s(z))
 = m^(-s0) exp[-A log(m) z/(1-z)].
```

The Laguerre generating identity

```text
(1-z)^(-2) exp[-x z/(1-z)]
 = sum_{k>=0} L_k^(1)(x) z^k
```

therefore gives the prime component of `ell_n(s0)` as

```text
-P_n(s0),

P_n(s0)
 = A sum_{m>=2} [Lambda(m)/m^s0] L_(n-1)^(1)(A log m).
```

The remaining pieces of `ell_n(s0)` come explicitly from `s(s-1)`, `pi^(-s/2)`, and `Gamma(s/2)` in `xi`.

For every fixed `n` and every `s0>1`, `L_(n-1)^(1)(A log m)` is a polynomial in `log m`, so the prime series above converges absolutely. This genuinely removes the boundary-convergence nuisance present at `s0=1`.

### Step 4 — test whether the improved Dirichlet weight changes the critical scale

For fixed `x>0` and fixed Laguerre parameter `alpha`, DLMF 18.15.14 gives the large-degree asymptotic

```text
L_n^(alpha)(x)
 = [n^(alpha/2-1/4) e^(x/2)]
   / [sqrt(pi) x^(alpha/2+1/4)]
   * (oscillatory factor + lower-order terms).
```

Set

```text
alpha = 1,
x = A log m.
```

For each fixed prime power `m`, as `n -> infinity`, the exponential part of the kernel contributes

```text
e^(A log(m)/2) = m^(A/2).
```

The Dirichlet weight in `P_n(s0)` is `m^(-s0)`, so the product of these two exponential-in-`log m` factors is

```text
m^(-s0) * m^(A/2)
 = m^[-s0 + (2s0-1)/2]
 = m^(-1/2).
```

Thus the apparent improvement from moving `s0` farther to the right is exactly cancelled in the fixed-`m`, large-`n` Laguerre envelope.

This observation is **local in `m`**. DLMF 18.15.14 is uniform only for `x` in compact subsets of `(0,infinity)`, so it does **not** justify replacing the entire infinite prime sum by an `m^(-1/2)`-weighted sum. No interchange of the `n -> infinity` limit with the infinite `m`-sum is made here.

What it does establish is narrower but important: moving the center to `s0>1` does not produce a simple per-prime exponential-envelope gain that becomes stronger as `s0` increases.

### Step 5 — attempt to obtain the needed cancellation from prime-counting error bounds

Let

```text
psi(x) = sum_{m<=x} Lambda(m).
```

A natural approach is to use partial summation and an error estimate for `psi(x)-x` against the oscillatory Laguerre kernel.

However, the standard square-root-scale estimate

```text
psi(x) = x + O(x^(1/2+epsilon))
```

for every `epsilon>0` is itself equivalent to RH. Therefore any proof of the required prime-trace bound that simply inserts this estimate is circular.

We would need an unconditional cancellation mechanism tailored to the Laguerre kernel that is materially weaker than an RH-equivalent pointwise bound for `psi(x)-x`.

## Checks performed

- **Algebraic checks:**
  - verified `|rho-1|=|rho| <=> Re(rho)=1/2`;
  - verified the four-element off-line orbit transforms to `w, conjugate(w), 1/w, 1/conjugate(w)`;
  - corrected the critical-line orbit from four counted images to two distinct zeros;
  - verified the critical pair contribution `4 sin^2(n theta/2)`;
  - verified `s(z)=s0+A z/(1-z)` has inverse `(s-s0)/(s+s0-1)` and sends the critical line to `|z|=1`.
- **Analytic/domain checks:**
  - the prime Dirichlet series is used only with `s0>1` and sufficiently small `|z|`, where `Re(s(z))>1`;
  - fixed-`n` absolute convergence follows from `s0>1` and polynomial growth in `log m`;
  - the Laguerre large-`n` formula is explicitly restricted to fixed `m` / fixed positive argument and is not interchanged with the infinite prime sum.
- **Numerical/symbolic checks:** none required for this import; no numerical evidence is used as proof.
- **Literature cross-check:** Li (1997), Bombieri-Lagarias (1999), Voros (2006), Sekatskii (2014 and companion preprints), NIST DLMF, and Clay current problem status were checked on `2026-08-20T20:37:00Z`.

## Circularity check

The route is **not complete**.

Two explicit circularity hazards were identified:

1. Replacing the required prime-trace cancellation by the pointwise estimate `psi(x)-x = O(x^(1/2+epsilon))` for all `epsilon>0` simply assumes an RH-equivalent statement (`C-0004`).
2. Treating the fixed-prime Laguerre asymptotic as if it were uniform over the infinite prime sum would be an unjustified interchange and could manufacture a false global bound.

The generalized-center trick removes a convergence nuisance but does not, by itself, supply the missing cancellation theorem.

## Result

This attempt established and documented the following:

1. The Li Möbius geometry gives an exact unit-circle representation of the critical line.
2. The original informal critical-line contribution had a factor-of-two error; the correct distinct-pair contribution is `4 sin^2(n theta/2)`.
3. By Voros's established asymptotic dichotomy, proving any subexponential bound for the standard Li coefficients would imply RH.
4. A generalized Li generating function can be centered at any `s0>1`, where its prime component is an exact absolutely convergent Laguerre-weighted von-Mangoldt series for every fixed `n`.
5. In the fixed-prime, large-`n` Laguerre asymptotic, the improved weight `m^(-s0)` is exactly offset by the Laguerre envelope `m^((2s0-1)/2)`, leaving the critical factor `m^(-1/2)`.
6. This cancellation does not prove a global prime-trace asymptotic because the Laguerre estimate used is not uniform over all prime powers.
7. Standard square-root-scale `psi(x)-x` estimates cannot be used as the missing input without circularity.

No proof of RH was obtained.

## Obstruction / unresolved step

The first genuinely open step for this route is:

> Prove an `n`-uniform subexponential bound for the relevant Li/Laguerre prime trace, or for a rigorously filtered version of it, using unconditional cancellation that does not already imply RH through a standard equivalent criterion.

Absolute convergence at `s0>1` is insufficient because the polynomial degree and oscillation of the Laguerre kernel grow with `n`.

## Findings produced

- [`F-20260820-001`](../findings/2026-08-20T203700Z-critical-line-zero-orbit-contribution.md) — corrected zero-orbit contribution.
- [`F-20260820-002`](../findings/2026-08-20T203700Z-subexponential-li-growth-suffices.md) — subexponential Li growth is sufficient for RH.
- [`F-20260820-003`](../findings/2026-08-20T203700Z-generalized-center-restores-half-weight.md) — generalized center restores the `m^(-1/2)` fixed-prime envelope.
- [`F-20260820-004`](../findings/2026-08-20T203700Z-square-root-psi-bound-is-circular.md) — square-root `psi` input is RH-equivalent and therefore circular here.

## Claims affected

Created and verified `C-0001` through `C-0008` as recorded in `docs/CLAIMS.md`.

## Next action

Formulate a separate attempt around **finite-difference filtering** of the Li/generalized-Li sequence:

1. choose an explicit low-degree polynomial in the shift operator that suppresses the known archimedean `n log n` trend;
2. prove exactly how that filter acts on a hypothetical off-unit-circle zero mode;
3. derive the corresponding filtered prime-Laguerre kernel without heuristic limit interchanges;
4. determine the weakest sufficient bound on that filtered trace;
5. compare that bound against known RH equivalents before trying to prove it.

The key acceptance test for the next route is that its missing estimate must be demonstrably weaker than simply restating RH in another standard form.

## Timestamped addenda / corrections

### 2026-08-20T20:37:00Z — Import correction

The pre-protocol informal discussion stated that a critical-line "quartet" contributes `8 sin^2(n theta/2)`. That wording double-counted the symmetry orbit because on the critical line `1-rho=conjugate(rho)`. The repository record corrects this to the distinct-pair contribution `4 sin^2(n theta/2)`.

### 2026-08-20T20:49:00Z — Raw-prime-trace target corrected

`A-20260820-002` identified a structural issue in this attempt's blocker wording. For `s0>1`, the raw prime-Laguerre sequence `P_n(s0)` contains the deterministic exponential mode `1-q^n`, `q=-s0/(s0-1)`, coming from the known pole of `zeta(s)` at `s=1`. Therefore `P_n=exp(o(n))` is impossible even under RH.

Future references to a subexponential generalized prime trace must mean either the exact pole-subtracted sequence

```text
S_n=P_n-(1-q^n)
```

or an exact pole-annihilated filter such as `(E-1)(E-q)P_n`. The broader raw-trace target is invalidated, while the underlying generalized-center representation remains valid.
