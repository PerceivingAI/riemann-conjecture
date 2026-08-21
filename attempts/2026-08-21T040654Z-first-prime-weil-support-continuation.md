# First-prime Weil support continuation: exact absorption, residual structure, and certificate audit

- **Attempt ID:** `A-20260821-003`
- **Created:** `2026-08-21T04:06:54Z`
- **Last updated:** `2026-08-21T04:06:54Z`
- **Status:** `COMPLETE`
- **Success target:** Fix the exact first-prime Weil normalization, obtain at least one rigorous continuation inequality beyond the first prime threshold, determine what remains after that inequality, and audit whether any existing public FP-0.35 certificate can be accepted as a proof dependency.

## Question / goal

`A-20260821-002` isolated the first-prime support window

```text
(1/2)log 2 < T < (1/2)log 3,
```

where the only arithmetic atom is `m=2` and the compressed symmetrized shift has exact operator norm `1`.

This attempt asks:

1. what the exact finite-support Weil form is in the current Suzuki normalization;
2. whether the `p=2` term admits a rigorous local absorption mechanism rather than a crude global norm bound;
3. whether a finite value, specifically `T=7/20`, can be advanced by exact arithmetic;
4. whether the public `weil-first-prime` FP-0.35 certificate is sufficiently rigorous and internally consistent to use as a theorem;
5. what residual operator remains if that external claim is not accepted.

No statement in this attempt is allowed to count a finite-support positivity result as RH.

## Dependencies and literature

Repository claims used:

- `C-0039` — prime powers enter as thresholded compressed translations;
- `C-0040` — exact compressed-shift norm in the first-prime window;
- `C-0041` — restricted-support Weil positivity has an unconditional base regime.

External sources:

- `R-0024` — Bombieri's variational Weil-functional framework;
- `R-0025` — Connes-Consani archimedean positivity framework;
- `R-0028` — Suzuki 2026, exact finite-support quadratic-form formulas;
- `R-0029` — Connes-Consani 2023 numerical prime-threshold behavior;
- `R-0030` — NIST DLMF digamma representation used for the positive-kernel decomposition;
- `R-0031` — pinned public `weil-first-prime` source tree, treated only as an external proof candidate and source-audit target.

Computation:

- `X-20260821-003` — exact rational endpoint certificate and 256-bit Arb enclosures of first-prime transcendental constants.

## Step 1 — exact finite-support formula and a normalization guard

Suzuki's finite-support formula has three structurally distinct pieces. In Fourier variables it contains

```text
(1/2pi) integral
  [ Re psi(1/4+i xi/2) - log pi ] |fhat(xi)|^2 dxi
```

minus the finite prime-power symbol

```text
(1/2pi) integral
  |fhat(xi)|^2
  sum_(m<=exp(2T)) [Lambda(m)/sqrt(m)] 2 cos(xi log m)
  dxi,
```

and **also** a finite-support residual term involving the Fourier transform of `r''_(0,T)`.

Equivalently, after scaling to `[-1,1]`, Suzuki equation (4.5) writes the Rayleigh quotient as

```text
-log T -(2A+1)
+ kinetic/logarithmic form
- prime translation overlaps
- T * double-integral residual kernel.
```

Therefore the tempting operator

```text
digamma Fourier multiplier - prime translations
```

is not by itself the full finite-support Weil operator.

### Discarded reconnaissance

An initial sine-basis Galerkin scout was built for the multiplier-plus-`p=2` operator. During the normalization audit two issues were caught before registration:

1. the mixed-parity version initially imposed only one of the two pole constraints;
2. more importantly, Suzuki's exact finite-support residual kernel was absent.

The script and its floating data were deleted before this attempt was recorded. No eigenvalue from that scout is retained as evidence for full Weil positivity.

This correction is important because Connes-Consani's published numerical first-prime compensation concerns their full semi-local form, not the incomplete multiplier truncation.

## Step 2 — exact endpoint geometry at `T=7/20`

Fix

```text
T=7/20,
tau=log(2)/T,
epsilon=2-tau.
```

After scaling to `[-1,1]`, the symmetrized first-prime translation couples only the two edge intervals

```text
[-1,-1+epsilon]
and
[1-epsilon,1].
```

Let

```text
V(x)=-(1/2)log(1-x^2).
```

On those edge intervals,

```text
1-x^2 < 2 epsilon,
```

hence

```text
V(x) >= kappa_edge,
kappa_edge=(1/2)log(1/(2 epsilon)).
```

If `C_tau` denotes the symmetrized compressed translation, then Cauchy-Schwarz / `2|ab|<=|a|^2+|b|^2` gives

```text
|<C_tau w,w>|
<= ||w||^2_edge
<= kappa_edge^(-1) <Vw,w>.
```

The first-prime coefficient is

```text
c_2=log(2)/sqrt(2).
```

Thus the prime perturbation satisfies

```text
P_2(w) >= -(c_2/kappa_edge)<Vw,w>.
```

The only remaining task for this step is to make the scalar ratio rigorous without injecting decimal approximations.

## Step 3 — self-contained rational certificate for the absorption constant

`scripts/weil_endpoint_absorption_certificate.py` proves the required logarithmic inequalities with exact `Fraction` arithmetic.

For every rational `x>1`, set

```text
y=(x-1)/(x+1).
```

Then

```text
log x
=2 sum_(k>=0) y^(2k+1)/(2k+1).
```

The positive tail after `N` terms obeys the exact rational bound

```text
R_N
<= 2 y^(2N+1) / [(2N+1)(1-y^2)].
```

Four terms at `x=2` prove

```text
842/1215 < log 2 < 23581/34020.
```

Therefore

```text
epsilon
=2-log(2)/(7/20)
<34/1701.
```

Hence

```text
1/(2 epsilon)>1701/68.
```

The exact integer inequality

```text
(1701/68)^5 > (87/32)^16
```

combined with a five-term rigorous atanh-series lower bound

```text
log(87/32)>1
```

gives

```text
kappa_edge>8/5.
```

Also

```text
sqrt(2)>7/5
```

by squaring, so

```text
c_2
< (23581/34020)/(7/5)
<62/125.
```

Consequently

```text
c_2/kappa_edge
< (62/125)/(8/5)
=31/100.
```

Therefore, rigorously,

```text
boxed:  V + P_2 >= (69/100)V >= 0
```

at `T=7/20`.

This is an unconditional finite-scale inequality and does not use RH.

## Step 4 — exact transcendental balls for the next certificate

`scripts/weil_exact_constants.py` uses python-flint/Arb at 256 bits to enclose the constants that a rigorous full Schur or Ritz certificate must propagate as intervals.

The retained output includes

```text
log2
= [0.693147180559945309417232121458176568075500134360255254120680 +/- 9.51e-63]

tau=log2/(7/20)
= [1.98042051588555802690637748988050448021571466960072929748766 +/- 2.84e-60]

c_2=log2/sqrt2
= [0.490129071734273595856950861817616690645730349549527360521123 +/- 1.24e-61]

c_T=log(2*pi*(7/20))+EulerGamma
= [1.36527060681220065583730073019427666472543738980832338274545 +/- 2.56e-60].
```

The rational value

```text
1355726/993009
```

is confirmed to lie above exact `c_T`; the difference is enclosed around

```text
2.36039629629129348e-14.
```

These balls are not a proof of full positivity. They establish that the transcendental inputs can be handled rigorously without point-float substitutions.

## Step 5 — positive-term decomposition of the archimedean digamma multiplier

Let

```text
a_k=k+1/4,
m_0=psi(1/4)-log pi.
```

From the standard digamma representation,

```text
psi(z)+EulerGamma
=sum_(k>=0) [1/(k+1)-1/(k+z)]
```

for `Re z>0`. Taking `z=1/4+i xi/2` and subtracting the value at `xi=0` gives

```text
Re psi(1/4+i xi/2)-log pi
=m_0
+sum_(k>=0)
 [1/a_k - 4a_k/(xi^2+4a_k^2)].
```

With Fourier convention

```text
fhat(xi)=integral f(t) exp(i xi t) dt,
```

we have

```text
Fourier[e^(-2a|t|)](xi)
=4a/(xi^2+4a^2).
```

Therefore the archimedean multiplier quadratic form can be written as

```text
Q_arch(f)
=m_0 ||f||_2^2
+sum_(k>=0)
 [ (1/a_k)||f||_2^2
   - double_integral e^(-2a_k|t-s|)
       f(t)conj(f(s)) dt ds ].
```

Each bracket is nonnegative because its Fourier multiplier is

```text
xi^2 / [a_k(xi^2+4a_k^2)] >= 0.
```

Hence finite truncations of this series give monotone lower bounds for the pure digamma-multiplier part. This does **not** remove Suzuki's separate finite-support residual kernel, but it gives a clean independent architecture for bounding one major component of the next certificate.

## Step 6 — literature comparison: prime-2 compensation is known numerical behavior

Connes-Consani (2023) numerically observed that their archimedean even matrix loses positivity slightly beyond the first prime threshold and that adding the `p=2` contribution restores positivity through the interval before `p=3`.

Therefore any numerical observation of the same behavior here would not be novel. The goal is a rigorous finite-scale inequality/certificate, not rediscovery of the plot.

## Step 7 — audit of the public FP-0.35 certificate project

A public repository, `R-0031`, claims strict Weil positivity at `T=7/20`. It was cloned only into a temporary directory and inspected at the pinned commit

```text
e66f467bc4447c5b2491577cbb6c3ae0e721fb43
```

(commit timestamp `2026-08-12T22:20:01+08:00`).

The repository is treated here as **unverified external proof code**, not as an authority.

### 7.1 Advertised one-command replay

The advertised `scripts/reproduce_fp035.py` computes

```text
TAU_RAT = Fraction(math.log(2)/(7/20)).limit_denominator(10000)
C2_FLOAT = math.log(2)/math.sqrt(2)
```

and then injects values derived from those approximations into Arb as point balls.

At high precision, the true value and its rational point approximation differ by

```text
|log(2)/(7/20) - 17802/8989|
approx 1.9240495e-9.
```

This error is numerically small compared with the claimed finite matrix margin, but no automatic interval enclosure follows from smallness. A rigorous checker must propagate an explicit `tau` interval through every `J(tau)` and `E(tau)` entry.

The script also uses a binary-float point for `c_2`. Again, Arb then certifies the matrix built from that point unless a separate perturbation enclosure is supplied.

### 7.2 Full-`c_T` recomputation path

`checker/fp035/recompute_schur.py` uses the real `c_T` formula but also uses floating `tau`, floating `c_2`, and an ordinary numerical LDL pivot. It is useful as a recomputation diagnostic, not by itself an exact interval proof.

### 7.3 `checker/first_prime/exact_split.py`

This path improves the prime algebra by using rational bounds for `log2`, but its Schur judge explicitly sets

```text
c_L=0
```

and therefore corresponds to the easier O1-B gate rather than the full FP-0.35 form with `c_T≈1.36527`.

Its source also labels the high-precision mpmath interval LDL as an interim method and notes that a full exact/Fraction certification was still intended.

### 7.4 Repository-internal status mismatch

The source tree contains both:

- README/status text claiming FP-0.35 holds; and
- lower-level assembly/checker comments stating that the full Arb LDL certification remained pending or that trusted replay was still in progress.

The repository also documents earlier certificate defects, including an incomplete second-moment term and a copy-generated reproduction path, later said to be corrected.

### Audit conclusion

This project does **not** conclude that the external theorem is false. It concludes only:

```text
The public FP-0.35 claim is not accepted as VERIFIED here.
```

The finite theorem remains an open requirement until either:

1. a trustworthy published proof becomes available; or
2. this repository independently reproduces the full analytic reduction with exact interval constants, certified primitive enclosures, a rigorous complement bound, and an interval positive-definiteness check.

## Step 8 — what remains after endpoint absorption

Using the scaled Suzuki/Bombieri decomposition, the exact endpoint theorem allows the pair

```text
V + P_2
```

to be replaced from below by

```text
(69/100)V.
```

The remaining first-prime problem at `T=7/20` is therefore a residual quadratic-form inequality of the schematic form

```text
kinetic/logarithmic form
+ (69/100)V
+ finite-support residual kernel
- c_T I
> 0,
```

with the exact normalization fixed by Suzuki equation (4.5).

This is a much smaller and better-conditioned target than bounding the first-prime translation by its global operator norm `1`.

The next certificate must still control the infinite-dimensional complement. A positive finite Galerkin matrix alone is not enough.

## Circularity check

No RH-strength input is used in the endpoint absorption proof.

The following are explicitly rejected:

1. treating full finite-support Weil positivity as evidence for RH — finite support does not imply RH;
2. treating a positive finite Galerkin matrix as an infinite-dimensional proof without a complement/tail bound;
3. treating an Arb matrix built from point approximations to `log2` or `sqrt2` as an exact transcendental certificate;
4. importing the external FP-0.35 repository's status flag as a theorem;
5. omitting Suzuki's finite-support residual kernel;
6. assuming Connes-Consani's published numerical positivity plot is a proof of first-prime positivity.

## Result

The stated intermediate target is complete.

Established in this repository:

1. the exact finite-support formula requires the residual kernel in addition to the digamma multiplier and prime terms;
2. at `T=7/20`, the first-prime endpoint perturbation satisfies the rigorous exact-arithmetic inequality
   `V+P_2 >= (69/100)V >= 0`;
3. exact 256-bit Arb balls for `tau`, `c_2`, and `c_T` are available for future interval assembly;
4. the pure digamma multiplier has a monotone sum of nonnegative exponential-kernel corrections;
5. the current public FP-0.35 proof code is not sufficiently self-consistent for this repository to accept its theorem without an independent replay.

No proof of RH has been obtained. Full first-prime positivity at `T=7/20` has **not** been proved in this repository.

## Findings produced

- [`F-20260821-012`](../findings/2026-08-21T040654Z-first-prime-endpoint-absorption.md) — exact rational endpoint absorption at `T=7/20`.
- [`F-20260821-013`](../findings/2026-08-21T040654Z-digamma-positive-kernel-decomposition.md) — monotone nonnegative-kernel decomposition of the archimedean digamma multiplier.
- [`F-20260821-014`](../findings/2026-08-21T040654Z-finite-support-residual-is-mandatory.md) — finite-support Weil form contains a residual kernel that cannot be dropped.
- [`F-20260821-015`](../findings/2026-08-21T040654Z-external-fp035-certificate-not-verified.md) — source audit of the public FP-0.35 certificate claim.

## Claims affected

Created `C-0042` through `C-0044`.

## Next action

Create `A-20260821-004` for an **independent rigorous residual certificate at `T=7/20`**:

1. use Suzuki equation (4.5) as the authoritative scaled form;
2. insert the proven lower bound `V+P_2 >= (69/100)V`;
3. construct a finite Legendre or other parity-adapted block for the residual form;
4. derive the infinite-dimensional complement lower bound independently;
5. evaluate every `tau`, `c_2`, and `c_T` dependency with Arb balls or proven rational intervals;
6. independently enclose the finite-support residual-kernel matrix with explicit quadrature/remainder bounds;
7. prove positive definiteness with interval `LDL^T` or an exact rational Schur criterion;
8. require the lower bound to survive all interval widths before recording finite-scale positivity as `VERIFIED`;
9. keep the result explicitly finite-scale: even a successful `T=7/20` certificate would not imply RH.

## Timestamped addenda / corrections

None yet.
