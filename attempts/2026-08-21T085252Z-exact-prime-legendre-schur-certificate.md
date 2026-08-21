# Exact-prime Legendre-Schur certificate at T=7/20

- **Attempt ID:** `A-20260821-004`
- **Created:** `2026-08-21T08:52:52Z`
- **Last updated:** `2026-08-21T13:52:37Z`
- **Status:** `COMPLETE`
- **Success target:** Prove strict positivity of the full localized Weil quadratic form at `T=7/20` by retaining the exact `p=2` compressed translation, using Legendre harmonic-number coercivity on the infinite complement, and reducing the remaining problem to a finite rigorous Schur certificate.

## Question / goal

`A-20260821-003` proved the unconditional operator inequality

```text
V + P_2 >= (69/100)V >= 0,
```

where

```text
V(x)=-(1/2)log(1-x^2).
```

The initial plan for this attempt was to insert that bound globally and certify positivity of

```text
jump + (69/100)V + Suzuki residual - c_T I.
```

This attempt first tests whether that target is actually true. If not, it asks whether retaining the exact first-prime translation makes a rigorous finite-plus-complement Schur reduction possible.

Even success at `T=7/20` would be a finite-support Weil theorem only and would not imply RH.

## Dependencies and known results

Repository claims used:

- `C-0039` — prime powers enter the localized Weil form as thresholded compressed translations;
- `C-0040` — the first-prime compressed symmetrized shift has norm `1` in the first-prime support window;
- `C-0042` — exact endpoint absorption `V+P_2 >= (69/100)V`;
- `C-0044` — Suzuki's finite-support residual kernel is mandatory.

External inputs:

- `R-0028` — Suzuki 2026, authoritative scaled localized Weil form;
- `R-0032` — Gerontogiannis-Mesland, modern statement of Tuck's Legendre identity;
- `R-0033` — Tuck 1964, original identity source.

Computation:

- `X-20260821-004` — proof-path Arb obstruction/complement certificate plus explicitly non-rigorous Schur-dimension reconnaissance.

## Mathematical setup

Fix

```text
T=7/20.
```

In Suzuki's scaled normalization on `[-1,1]`, define

```text
J(w)
= (1/4) int int |w(x)-w(y)|^2/|x-y| dx dy,

V(w)
= -(1/2) int log(1-x^2)|w(x)|^2 dx,

R_T(w)
= -T int int r''(T(x-y)) w(y) conjugate(w(x)) dx dy,

c_T
= log(2*pi*T)+EulerGamma.
```

At this support only `m=2` is active. Let `P_2` denote the exact first-prime compressed-translation quadratic form. The exact first-prime target is

```text
Q_T(w)=J(w)+V(w)+P_2(w)+R_T(w)-c_T||w||_2^2.
```

Let `P_N` denote orthogonal projection onto the first `N` Legendre modes `P_0,...,P_(N-1)` and `Q_N=I-P_N`.

## Step 1 — quantitative Legendre diagonalization of the jump term

Tuck's identity, in the normalization used by Gerontogiannis-Mesland, is

```text
int_{-1}^1 [P_n(x)-P_n(y)]/|x-y| dy
= 2 H_n P_n(x),
```

where

```text
H_n=sum_(k=1)^n 1/k,
H_0=0.
```

By symmetrization of the jump quadratic form,

```text
J(P_n)=H_n ||P_n||_2^2.
```

Hence, for every `q` orthogonal to `P_0,...,P_(N-1)`,

```text
J(q)>=H_N ||q||_2^2.
```

This is the required quantitative replacement for the merely qualitative compact-embedding argument: `H_N~log N` forces coercivity in high Legendre modes.

## Step 2 — the global 69-percent absorbed target is false

Take the explicit polynomial

```text
w=P_0-P_2=(3/2)(1-x^2).
```

This belongs to `H_0^1(-1,1)` and is an admissible regular test function for the scaled form.

Exactly,

```text
||w||_2^2 = 12/5,
J(w)       = 3/5,
V(w)       = 47/25 - (12/5)log 2.
```

Using the canonical Suzuki residual kernel with 224-bit Arb enclosures, `X-20260821-004` proves

```text
Q_0.69(w)
:= J(w)+(69/100)V(w)+R_T(w)-c_T||w||_2^2
< 0.
```

The retained enclosure is centered near

```text
-0.05275381732676
```

with an error far below the distance to zero; its upper endpoint is strictly negative.

Therefore the proposed route

```text
replace V+P_2 globally by 0.69V
then prove the residual lower operator positive
```

is impossible.

This does **not** refute `C-0042`. That inequality remains correct. It shows only that the inequality is too lossy to be used wholesale in a proof of full first-prime positivity.

For this same test function, the critical scalar fraction required merely to avoid negativity is rigorously between `0.93` and `0.94`, approximately

```text
alpha_crit = 0.9337265205748...
```

so the gap from `0.69` is structural rather than a tiny numerical margin.

## Step 3 — retaining the exact prime term repairs the test direction

For the same polynomial, the first-prime overlap is explicitly integrable. With

```text
tau=log(2)/T,
c_2=log(2)/sqrt(2),
```

the exact real prime contribution is

```text
P_2(w)
= -2 c_2 int_{-1}^{1-tau} w(t)w(t+tau) dt.
```

Arb interval evaluation gives

```text
-P_2(w)/V(w) ~ 5.05e-5,
(V(w)+P_2(w))/V(w) ~ 0.9999495.
```

Thus the uniform `31%` loss from `C-0042` is enormously pessimistic on this low smooth direction.

More importantly, the full exact-prime value on this test function is rigorously positive:

```text
Q_T(w) > 0,
```

with retained value near

```text
0.0143337515668.
```

This establishes the mechanism pivot: the prime translation must be retained with substantially more geometry than its global endpoint norm bound.

## Step 4 — rigorous crude high-mode complement bound

On `Q_N L^2`, keep only the jump term for positive coercivity and bound the two nonlocal negative-capable pieces by operator norms.

The endpoint multiplication `V` is nonnegative and may be dropped in a lower bound.

The exact first-prime term satisfies

```text
P_2 >= -c_2 I,
```

because the compressed symmetrized shift has norm `1`.

For the residual operator with kernel

```text
K_R(x,y)=-T r''(T(x-y)),
```

the Schur test gives

```text
||R_T|| <= rho_R,
rho_R=2T sup_{|u|<=2T}|r''(u)|.
```

The proof-path script bounds `r''` by its exact Bernoulli/Taylor coefficients plus the rigorous series remainder already used by `scripts.cert.residual_kernel`. At `T=7/20`, it certifies

```text
sup |r''(u)| <= 1.90312199054349...,
rho_R <= 1.33218539338044....
```

Therefore

```text
Q_T(q)
>= [H_N-c_T-c_2-rho_R] ||q||_2^2
=: mu_N ||q||_2^2
```

for every `q` in the Legendre complement.

The first certified positive crude complement bound is already

```text
N=14,
mu_14 > 0,
```

with `mu_14` near `0.0639772546354`.

Thus the infinite-dimensional tail is not the fundamental obstruction once the Legendre jump structure is used.

## Step 5 — exact-prime finite Schur reduction

Write the full operator relative to `P_N+Q_N` as

```text
[ A_N   B_N  ]
[ B_N*  C_N  ].
```

The previous step proves

```text
C_N >= mu_N I.
```

For `u=P_N w`, `q=Q_N w`, Cauchy-Schwarz gives

```text
2 Re <B_N q,u>
>= -mu_N ||q||^2 - mu_N^(-1)||B_N* u||^2.
```

Hence the sufficient finite condition is

```text
A_N - mu_N^(-1) B_N B_N* > 0.
```

The diagonal operator `J-c_T I` creates no cross block. Decompose

```text
B_N=B_V+B_2+B_R
```

for endpoint multiplication, exact prime translation, and residual kernel. For every low vector `u`,

```text
||(B_V*+B_2*+B_R*)u||^2
<= 3( ||B_V*u||^2 + ||B_2*u||^2 + ||B_R*u||^2 ).
```

Therefore it suffices to prove

```text
S_N
:= A_N
 - (3/mu_N)(G_V+G_2+G_R)
>0,
```

where

```text
G_X=B_X B_X* = P_N X Q_N X P_N.
```

Each `G_X` can be reduced without representing infinitely many tail modes:

```text
G_X
= P_N X^2 P_N - (P_N X P_N)^2.
```

For `V`, this requires compact-support polynomial integrals against `log^2(1-x^2)`. For the prime shift, it requires explicit integrals on the small overlap intervals. For the residual, the convergent `|x-y|^m` expansion plus an operator tail bound gives a finite rigorous route.

This is the core theorem architecture for the next phase.

## Step 6 — floating Schur reconnaissance

`scripts/weil_legendre_schur_scout.py` uses normalized Legendre polynomials and floating Gauss-Legendre quadrature. It is explicitly **not** a proof tool.

With `max_mode=120`, the finite exact-prime Ritz matrix has lowest sampled eigenvalue approximately

```text
0.00119357.
```

Using the crude `mu_N` and the factor-3 separate-component Schur surrogate, but truncating the component tail Grams at mode `120`, the scout gives negative values through `N=24` and positive values from the tested `N=28` onward:

```text
N=28  ~ +0.00117081
N=32  ~ +0.00118485
N=40  ~ +0.00118955
N=50  ~ +0.00119178.
```

These numbers are only dimension-selection evidence because the scout truncates the infinite tail. They do not certify positivity.

The natural rigorous target is therefore `N=32` rather than the smallest numerically positive dimension, leaving some room for interval and tail-enclosure losses.

## Checks performed

- **Algebraic checks:** exact `P_0-P_2` norm, jump energy, endpoint integral, and prime-overlap antiderivative.
- **Analytic/domain checks:** `P_0-P_2=(3/2)(1-x^2)` lies in `H_0^1`; Legendre jump identity gives exact complement coercivity; Schur and factor-3 reductions are ordinary Hilbert-space inequalities.
- **Rigorous computation:** 224-bit Arb test-function obstruction, exact-prime value, residual sup bound, and `mu_N` table in `X-20260821-004`.
- **Reconnaissance only:** floating normalized-Legendre Ritz/Schur dimension scan, explicitly separated from proof data.
- **Literature cross-check:** Suzuki scaled form and Tuck/Legendre jump identity checked against `R-0028`, `R-0032`, and `R-0033`.

## Circularity check

No RH input is used.

The target is positivity of one fixed finite-support localized Weil form. Even a complete proof at `T=7/20` does not imply full Weil positivity and therefore does not imply RH.

No positive finite Galerkin matrix is treated as a theorem. The required infinite-dimensional complement bound is explicit and the remaining Schur tail Grams must be enclosed rigorously before finite-scale positivity can be recorded as verified.

## Result

This attempt is `PROMISING`, not complete.

Established:

1. the Legendre jump component is diagonal with harmonic-number eigenvalues and yields explicit high-mode coercivity;
2. the globally absorbed `0.69V` residual target is rigorously **not** positive;
3. retaining the exact prime translation restores positivity on the explicit obstructing polynomial;
4. a rigorous crude complement bound is positive from `N=14` onward;
5. the infinite-dimensional problem reduces to finite low-mode matrices plus finite tail Gram matrices `G_V,G_2,G_R`;
6. floating reconnaissance suggests a rigorous target around `N=32` with a roughly `10^-3` finite Schur margin.

No full `T=7/20` positivity theorem has yet been proved.

## Obstruction / unresolved step

The remaining blocker is to produce rigorous enclosures for

```text
G_V=P_N V Q_N V P_N,
G_2=P_N P_2 Q_N P_2 P_N,
G_R=P_N R_T Q_N R_T P_N
```

at a selected dimension, preferably `N=32`, and then certify

```text
A_N-(3/mu_N)(G_V+G_2+G_R)>0
```

with Arb-generated exact rational intervals and the independent Rust verifier.

The certificate schema should be extended only after these mathematical objects and their exact semantics are fixed.

## Findings produced

- [`F-20260821-016`](../findings/2026-08-21T085252Z-legendre-jump-harmonic-coercivity.md)
- [`F-20260821-017`](../findings/2026-08-21T085252Z-uniform-endpoint-absorption-is-too-lossy.md)
- [`F-20260821-018`](../findings/2026-08-21T085252Z-exact-prime-high-mode-complement.md)
- [`F-20260821-019`](../findings/2026-08-21T085252Z-component-tail-gram-schur-reduction.md)
- [`F-20260821-020`](../findings/2026-08-21T085252Z-schur-dimension-scout.md)

## Claims affected

Created `C-0045` through `C-0049`. `C-0042` remains verified; only its proposed use as the final global lower replacement is closed.

## Next action

Build rigorous finite `N=32` matrices for `A_N`, `G_V`, and `G_2`; derive a certified analytic/Taylor tail bound for `G_R`; then evaluate the factor-3 Schur matrix with Arb intervals. Only after that reduction is fixed should `rh-weil-certificate-v1` gain an exact-prime Schur claim profile.

## Timestamped addenda / corrections

### 2026-08-21T13:52:37Z — N=32 exact-prime Schur certificate closes the attempt

The unresolved step above has now been completed without changing the earlier derivation or the recorded failure of the global `0.69V` target.

A rigorous `N=32` implementation was added in `scripts/cert/legendre_schur.py` and `scripts/cert/exact_prime_schur_certificate.py`.

The finite component Grams are no longer truncated reconnaissance objects:

```text
G_V=P_32 V Q_32 V P_32,
G_2=P_32 P_2 Q_32 P_2 P_32,
G_R=P_32 R_T Q_32 R_T P_32
```

are enclosed rigorously by exact polynomial identities plus Arb transcendental/remainder bounds. In particular:

- `G_V` is reduced to closed logarithmic and logarithm-squared moments;
- because `1<tau<2`, the squared first-prime compressed shift reduces to exact edge-interval polynomial overlaps;
- the Suzuki residual uses an order-32 exact-polynomial truncation with a rigorous operator remainder of order `10^-22`.

The retained certificate gives

```text
mu_32 > 0.8709101235096008.
```

The closed `rh-weil-certificate-v1` profile

```text
exact_prime_legendre_schur
```

requires the verifier to derive the complement bound and factor-3 Schur correction from the serialized exact intervals. Rust then reconstructs the even and odd `16 x 16` Schur blocks and applies exact rational congruence witnesses followed by exact interval Gershgorin verification.

A clean-state certificate was regenerated at Git commit

```text
d620aa649a2d0291e407d4c0c8bc7360b67efc38
```

with `git_dirty=false`. The independent Rust verifier returns `passed=true` with exact positive Gershgorin margins approximately

```text
even  > 0.01153505500311919
odd   > 0.04939032559587724.
```

Adversarial replays distinguish malformed-contract failure (exit `2`) from theorem failure after a contract-valid negative perturbation (exit `1`). The retained certificate returns exit `0`.

The normalization was re-audited against Suzuki's pinned v2 equation (4.5): the scalar `c_T=log(2*pi*T)+EulerGamma`, first-prime sign/coefficient, and residual `-T r''(T(x-y))` scaling match the authoritative localized form.

The new Lean file `formal/Cert/Gershgorin.lean` proves the finite-dimensional soundness of strict positive row Gershgorin dominance and invertible congruence transfer. The full formal build completed successfully with `8711` jobs.

Registered closure artifacts:

- `F-20260821-021` — strict first-prime localized Weil positivity at `T=7/20`;
- `C-0050` — verified finite-support positivity theorem;
- `X-20260821-005` — clean exact certificate and independent replay.

**Final outcome:** the success target of `A-20260821-004` is achieved. Suzuki's localized Weil quadratic form is strictly positive at `T=7/20`. This is a finite-support theorem only; RH remains unresolved. The next research frontier is continuation in `T` through the one-prime window toward `(1/2)log 3`.
