# One-prime support continuation from T=7/20

- **Attempt ID:** `A-20260826-001`
- **Created:** `2026-08-26T17:14:00Z`
- **Last updated:** `2026-08-26T17:28:53Z`
- **Status:** `PROMISING`
- **Success target:** Extend the independently verified localized Weil positivity basepoint `T=7/20` to larger support values inside the one-prime window, while preserving the exact-prime Legendre-Schur trust chain and identifying the first genuine obstruction.

## Question / goal

`C-0050` proves strict localized Weil positivity at

```text
T=7/20=0.35
```

using the exact `p=2` translation, Suzuki residual, Legendre complement coercivity, a finite component tail-Gram Schur reduction, and an independent Rust certificate verifier.

The next question is whether this mechanism has nontrivial continuation range in

```text
(1/2)log 2 < T < (1/2)log 3,
```

or whether `T=0.35` is essentially an isolated point for the present certificate architecture.

This attempt deliberately does **not** generalize the `exact_prime_legendre_schur` certificate profile at the outset. The verified `C-0050` profile remains locked to `T=7/20`, `N=32`. New support values are reconnaissance/candidates until independently verified under a new closed contract.

## Parameterized exact assembly

The reusable `scripts/cert/legendre_schur.py` assembler was generalized from fixed `T=7/20` to an exact rational support `T=num/den` inside the one-prime window.

The following objects are now assembled at arbitrary rational one-prime support without changing the theorem-specific certificate wrapper:

```text
A_N(T),
G_V(T),
G_2(T),
G_R(T),
mu_N(T)=H_N-c_T(T)-c_2-rho_R(T).
```

The proof-bearing `scripts.cert.exact_prime_schur_certificate` continues to use the default `7/20`; `docs/contracts/rh-weil-certificate-v1.json` remains locked to the proved `C-0050` semantics.

For reconnaissance past the point where `mu_N` may become nonpositive, the assembler has an explicit `require_positive_mu=False` mode. The default remains `True`, so certificate-generation failure semantics are unchanged.

## N=32 support map

`X-20260826-001` first reuses the rigorous exact-polynomial/Arb assembly at `N=32`, then converts only matrix midpoints to NumPy for reconnaissance eigenvalues.

The broad scan gives:

```text
T       mu_32        finite A_32 min      Schur midpoint min
0.350   0.8709101    1.19384e-3           +1.18092e-3
0.375   0.6905203    4.92986e-4           -1.11403e-2
0.400   0.5112543    1.81727e-4           -1.74087
0.425   0.3323465    5.87178e-5           -5.20043
0.450   0.1531210    1.62324e-5           -16.6429
0.475  -0.0270278    3.88653e-6            unavailable
0.500  -0.2086514    9.40392e-7            unavailable
0.525  -0.3922588    2.73029e-7            unavailable
0.540  -0.5035744    1.07699e-7            unavailable
```

A finer scan shows the `N=32` full-tail Schur midpoint remains positive through the tested `T=0.37`:

```text
T=0.355   +9.90160e-4
T=0.360   +8.32376e-4
T=0.365   +6.90647e-4
T=0.370   +5.48438e-4
T=0.375   -1.11403e-2.
```

The low finite block and `mu_32` are still positive at `0.375`. Thus the first failure of the fixed `N=32` architecture is the full-tail Schur correction, not observed negativity of the low localized operator and not loss of complement coercivity.

## Dimension diagnosis

A stable orthonormal-Legendre Gauss-quadrature scout was parameterized in `T` to diagnose whether increasing `N` should repair the tail correction. Its tail Grams are finitely truncated, so this remains reconnaissance only.

At `T=3/8`, it predicts recovery from about `N=32` upward. At `T=2/5`, it predicts recovery from about `N=40` upward. At `T=17/40`, recovery is suggested from about `N=48`; at `T=9/20`, from about `N=56`.

The key full-tail checks were then rerun with the rigorous assembler at high enough precision to avoid high-degree monomial cancellation:

```text
T=3/8,  N=40:  Schur midpoint min ~ +4.83388e-4
T=2/5,  N=40:  Schur midpoint min ~ +1.70302e-4
T=17/40,N=40:  Schur midpoint min ~ -1.28340
T=9/20, N=40:  Schur midpoint min ~ -4.23493.
```

Therefore increasing the Legendre cutoff genuinely repairs the full-tail bound at least through `T=0.4`; the `N=32` failure is a resolution/tail-control issue rather than an observed operator obstruction.

### Precision guard

Exploratory `N=40/48` exact-polynomial midpoint runs at only 104-bit Arb precision produced catastrophic cancellation artifacts because high-degree Legendre polynomials are represented in the monomial basis. Those outputs were not retained as evidence. The relevant `N=40` full-tail runs were repeated at 256 bits, where the normalized finite and Schur values agree with the stable orthonormal-Legendre scout at the expected scale.

## Selected next rigorous target: T=2/5, N=40

`T=0.4` is a meaningful continuation from `0.35` while retaining substantially more margin than the later tested supports.

A generator-side exact candidate check was performed using:

- rigorous Arb/exact-polynomial `A_40`, `G_V`, `G_2`, `G_R`;
- 72-bit outward dyadic rational matrix intervals;
- exact rational `mu_40` derived from upper scalar endpoints;
- 40-bit dyadic rational congruence witnesses generated from exact rational midpoint `LDL^T`;
- exact rational interval congruence and Gershgorin evaluation on the Python side.

It gives

```text
mu_40 > 0.7313021813837909,
even Gershgorin margin > 0.004176569432300938,
odd  Gershgorin margin > 0.013120531611009081.
```

All three exact rational margins are positive.

This is **not yet a theorem**. The current independent Rust `exact_prime_legendre_schur` profile is intentionally locked to `T=7/20`, `N=32`. The candidate establishes that no new analytic mechanism is presently needed before attempting independent verification at `T=2/5,N=40`.

## Circularity check

No RH input is used.

The target remains finite-support Weil positivity at one fixed support value. Even a successful theorem at `T=2/5` would not imply RH. Floating midpoint scans and truncated-tail dimension scouts are never promoted to theorem status. The generator-side exact candidate is also not promoted until an independent closed verifier profile checks it.

## Current result

`A-20260826-001` is `PROMISING`.

Established as reconnaissance/candidate evidence:

1. the exact-prime Legendre-Schur assembler can be parameterized in rational `T` without weakening the existing `C-0050` contract;
2. fixed `N=32` remains healthy through the tested `T=0.37` but its full-tail Schur bound fails at `T=0.375` while the low block and complement remain positive;
3. increasing to `N=40` restores the rigorous full-tail midpoint Schur margin at `T=0.375` and `T=0.4`;
4. the natural required dimension grows with support in floating reconnaissance (`~48` at `0.425`, `~56` at `0.45`);
5. `T=2/5,N=40` survives generator-side exact rational outward rounding and congruence/Gershgorin checks with comfortable positive margins.

## Next action

Extend the independent certificate contract **only for the single target**

```text
T=2/5,
N=40,
```

or define a closed versioned profile whose allowed `(T,N)` pairs are explicitly enumerated and verifier-derived. Rust must independently reconstruct `mu_40`, the factor-3 Schur matrix, parity blocks, and exact congruence/Gershgorin margins. Only after that replay passes should a new localized-Weil positivity claim at `T=2/5` be registered as `VERIFIED`.
