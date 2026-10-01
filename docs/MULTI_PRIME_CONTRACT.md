# Multi-prime mathematical contract

- **Created:** `2026-10-01T10:14:40Z`
- **Last updated:** `2026-10-01T11:02:29Z`
- **Status:** Authoritative pre-implementation mathematical contract

This document freezes the mathematics that future multi-prime tooling must implement. It does **not** admit a new theorem profile, change `rh-weil-certificate-v1`, or create a theorem claim beyond the already retained one-prime results `C-0050..C-0057`.

## 1. Active arithmetic terms

For support `T>0`, the active arithmetic set is

```text
A(T) = { m=p^k : log(m) < 2T },
```

where `m` ranges over prime powers and the inequality is strict. For every active `m`, define

```text
tau_m = log(m)/T,
c_m   = Lambda(m)/sqrt(m),
```

with `Lambda` the von Mangoldt function.

On the scaled interval `[-1,1]`, let `S_m` denote the self-adjoint compressed translation at shift `tau_m`. The signed arithmetic operator contributed by `m` is

```text
P_m = -c_m S_m,
```

and the total signed arithmetic operator is

```text
P = sum_{m in A(T)} P_m.
```

The arithmetic terms are grouped into **one** operator `P`. Individual prime-power operators are not separate Schur components in this contract.

## 2. Immediate structural window

For

```text
(log 3)/2 < T < (log 4)/2 = log 2,
```

one has

```text
A(T) = {2,3}.
```

Indeed `log 2 < 2T` and `log 3 < 2T`, while `2T < log 4`, so `m=4` and every larger prime power are excluded. Therefore

```text
P = P_2 + P_3,
c_2 = log(2)/sqrt(2),
c_3 = log(3)/sqrt(3).
```

For both active shifts, `1 < tau_m < 2`. By the exact compressed-shift norm formula of `C-0040`, the essential translation-chain length is `2`, hence

```text
||S_2|| = ||S_3|| = 1.
```

Thus the rigorous norm bounds in this immediate window are exactly

```text
b_2=b_3=1.
```

## 3. Generic complement rule

Let `Pi_N` be the orthogonal projection onto the first `N` Legendre modes and `Q_N=I-Pi_N`. Let the full localized operator have the same analytic decomposition used by the retained one-prime proof path:

```text
J - c_T I + V + P + R,
```

where `J` is the Legendre-diagonal jump operator, `V>=0`, `P` is the total signed arithmetic operator above, and `R` is the mandatory Suzuki residual.

For every active `m`, let `b_m` be a rigorous bound satisfying

```text
||S_m|| <= b_m.
```

Then

```text
P_m >= -c_m b_m I,
```

and therefore

```text
P >= -sum_m c_m b_m I.
```

Combining `J(q)>=H_N||q||^2`, `V(q)>=0`, and `R>=-rho_R I` gives the frozen complement lower bound

```text
C_N >= mu_N I,

mu_N = H_N - c_T - sum_{m in A(T)} c_m b_m - rho_R.
```

The proof path must require `mu_N>0` before applying the Schur reduction.

In the immediate `{2,3}` window, `b_2=b_3=1`, so

```text
mu_N = H_N - c_T - c_2 - c_3 - rho_R.
```

This is the expected `c2+c3` complement loss. It is a rigorous sufficient lower bound; future tooling may use sharper rigorously proved bounds only through a separately documented contract revision.

## 4. Three-component Schur reduction

Relative to `Pi_N+Q_N`, write the full operator as

```text
[ A_N   B_N  ]
[ B_N*  C_N  ].
```

The Legendre-diagonal part `J-c_T I` creates no cross block. Group the remaining cross block into exactly three components:

```text
B_N = B_V + B_P + B_R,
```

where `B_P` is the cross block of the **combined** arithmetic operator `P`, not a sum treated as separate Schur components after the estimate.

Assume `C_N>=mu_N I` with `mu_N>0`. Completing the square gives

```text
2 Re <B_N q,u>
>= -mu_N ||q||^2 - mu_N^(-1)||B_N* u||^2.
```

For every low vector `u`, Cauchy-Schwarz in the three-component direct sum gives

```text
||(B_V*+B_P*+B_R*)u||^2
<= 3( ||B_V*u||^2 + ||B_P*u||^2 + ||B_R*u||^2 ).
```

Define

```text
G_X = B_X B_X* = Pi_N X Q_N X Pi_N,
```

for `X in {V,P,R}`. Therefore the existing factor-3 reduction remains valid in the multi-prime setting:

```text
S_N = A_N - (3/mu_N)(G_V+G_P+G_R).
```

Strict positivity of `S_N` is sufficient for strict positivity of the full operator.

The coefficient `3` counts the three **grouped cross-block components** `V,P,R`; it does not count active prime powers. No positivity, commutativity, or sign assumption on `P_2` and `P_3` is used in this derivation.

## 5. Combined arithmetic tail Gram

The arithmetic tail Gram must be formed from the combined operator before the Schur estimate:

```text
G_P = B_P B_P*
    = Pi_N P Q_N P Pi_N
    = Pi_N P^2 Pi_N - Pi_N P Pi_N P Pi_N.
```

In the unnormalized Legendre basis let

```text
D = diag(||P_0||_2^2, ..., ||P_{N-1}||_2^2)
```

be the low-space Gram matrix. Let `P` denote the low matrix of the arithmetic operator and let repository shorthand `P^2` denote the low matrix of the **operator square**. Then the frozen matrix identity is

```text
G_P = P^2 - P D^{-1} P.
```

Here the first `P^2` is not ordinary matrix multiplication. It is the matrix of the operator square `P^2` projected to the low space; the second term uses the low-space composition rule in the nonorthonormal Legendre basis.

For the immediate window,

```text
P=P_2+P_3,
```

so the operator square necessarily contains

```text
P^2 = P_2^2 + P_2 P_3 + P_3 P_2 + P_3^2.
```

Consequently `G_P` contains the mixed `2/3` tail cross terms. The implementation must **not** replace `G_P` by `G_2+G_3`; doing so drops those mixed terms and is not the frozen mathematical contract.

## 6. P2 generic operator implementation

The first production implementation of this mathematical core is `scripts/cert/prime_power_terms.py`. It is intentionally separate from the frozen one-prime `first_prime_matrices()` implementation.

The P2 module provides all of the following without using ordinary floating-point arithmetic in proof-path quantities:

- exact integer recognition/factorization of `m=p^k`, including primes as exponent `1`;
- rigorous Arb enclosures for `log(m)`, `tau_m`, `Lambda(m)=log(p)`, and `c_m=Lambda(m)/sqrt(m)`;
- exact active-set enumeration from the strict rule `log(m)<2T`, with a fail-closed `ThresholdIndeterminateError` when the requested Arb precision cannot establish which side of a prime-power threshold contains the exact rational support;
- a global piecewise partition of `[-1,1]` using every active left/right translation breakpoint;
- explicit polynomial images for both translated pieces `f(x+tau_m)` and `f(x-tau_m)` on their actual compressed supports;
- summation of every active signed `P_m` on each partition cell before matrix integration;
- direct assembly of the combined low matrix `P` and operator-square matrix `P^2=<P phi_i,P phi_j>` from those combined piecewise images;
- construction of `G_P=P^2-PD^{-1}P` for an exact orthogonal polynomial basis.

Because `P^2` is formed from the already combined images, the mixed terms such as `P_2P_3+P_3P_2` are present by construction and cannot be accidentally omitted through a separate cross-term shortcut.

The piecewise construction does not assume `1<tau_m<2`. Focused acceptance explicitly exercises `T=7/10`, where the active set is `{2,3,4}` and `tau_2<1`; the same implementation remains valid without an `m=4` operator rewrite. Breakpoint ordering itself is rigorous: if Arb cannot certify the ordering needed for a partition at the requested precision, the module fails closed rather than selecting an approximate topology.

`PrimePowerTerm` objects bind their constants to the exact rational support used to construct them. Low-level combined assembly rejects terms from different supports, preventing accidental cross-support operator construction.

This module is operator infrastructure only. It is not yet wired into a multi-prime full Weil assembler, certificate exporter, JSON contract, or Rust verifier, and it creates no theorem admission.

P2 acceptance is green: the focused prime-power/frozen-v1/admission/support target passes `24/24`, and the complete default Python suite passes `567/567`. The historical `scripts/cert/legendre_schur.py` has no diff. `git diff --check` passes, and no repository verification process remains running.

## 7. P3 rigorous multi-prime Schur assembler and v1 bridge

`scripts/cert/multi_prime_legendre_schur.py` now supplies the first full rigorous grouped `V,P,R` assembler through `assemble_multi_prime_schur()`. It reuses the already-rigorous potential and Suzuki residual components but replaces the arithmetic block completely with the P2 generic piecewise prime-power operator. Its canonical output includes `active_terms`, `P`, `P_squared`, `A`, `GV`, `GP`, `GR`, `rho_R`, `mu`, and `schur`, together with the exact support/dimension metadata and rigorous arithmetic norm bounds used in the complement estimate.

The complement arithmetic loss is computed generically from `sum_m c_m b_m`. The shift bound `b_m` is derived from the rigorous compressed-translation chain length `ceil(2/tau_m)` and the exact path-graph norm `2 cos(pi/(L+1))`; unresolved chain thresholds fail closed. The one-prime case uses the exact value `b_2=1`, while the same implementation already handles `tau_2<1` with the next chain norm `sqrt(2)`.

Before accepting any `{2,3}` result, the new assembler was run only in the historical `{2}` region and compared to the frozen `assemble_exact_prime_schur()`/`first_prime_matrices()` path at four existing supports:

```text
T=7/20,  N=16
T=2/5,   N=24
T=17/40, N=28
T=9/20,  N=32
```

At each point, the rigorous Arb enclosures for `P`, operator `P^2`, `GP` versus historical `G2`, `GV`, `GR`, `A`, `rho_R`, `mu`, and the resulting Schur matrix overlap entry-for-entry. The bridge subset passes `4/4` before the `{2,3}` test is executed.

Only after that bridge passes, the immediate multi-prime window is exercised directly. At `T=3/5`, the active set is exactly `{2,3}` and the combined operator-square constant-mode entry is rigorously separated from `P_2^2+P_3^2`; the residual difference is strictly positive. Thus the production assembler demonstrably contains nonzero mixed `P_2P_3+P_3P_2` contributions and is not implementing an additive square shortcut.

The focused P3/P2/frozen-v1 regression target passes `31/31`, and the complete default Python suite passes `574/574` in `375.93 s`. `git diff --check` passes, the frozen `scripts/cert/legendre_schur.py` remains byte-unmodified, and the final process scan is clean. P3 is closed. This is rigorous assembler infrastructure only: it does not add a certificate profile, verifier PASS rule, theorem admission, or retained proof.

## 8. Certification boundary

The analytic factor `3` is now explicitly closed by `C-0059` / `F-20261001-002`, but no theorem certification path has been implemented for this contract yet.

Future multi-prime theorem tooling must therefore satisfy all of the following before any theorem admission:

- use a separate profile/format/verifier path from frozen one-prime v1;
- derive the active prime-power set from the strict support rule;
- use the combined signed arithmetic operator `P`;
- derive the complement loss from `sum_m c_m b_m`;
- compute `G_P` from the combined operator square, including mixed prime-power terms;
- independently reconstruct the factor-3 `V,P,R` Schur matrix in the verifier;
- preserve the existing fresh-generation, adversarial, independent-replay, and explicit-retention boundaries.

No new support/dimension pair is admitted by this document. RH remains unresolved.
