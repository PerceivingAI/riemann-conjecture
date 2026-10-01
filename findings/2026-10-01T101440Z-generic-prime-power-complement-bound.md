# Generic prime-power Legendre complement bound

- **Finding ID:** `F-20261001-001`
- **Created:** `2026-10-01T10:14:40Z`
- **Last updated:** `2026-10-01T10:14:40Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For support `T>0`, let

```text
A(T)={m=p^k : log(m)<2T},
tau_m=log(m)/T,
c_m=Lambda(m)/sqrt(m),
P_m=-c_m S_m,
P=sum_{m in A(T)} P_m,
```

where `S_m` is the self-adjoint compressed translation at shift `tau_m`. If `b_m` is any rigorous bound with `||S_m||<=b_m`, then on the Legendre complement `Q_N` the localized Weil operator obeys

```text
C_N >= mu_N I,
mu_N = H_N-c_T-sum_{m in A(T)} c_m b_m-rho_R.
```

In the immediate window

```text
(log 3)/2 < T < (log 4)/2,
```

one has exactly `A(T)={2,3}` and the exact compressed-shift norm formula gives `b_2=b_3=1`. Hence

```text
mu_N=H_N-c_T-c_2-c_3-rho_R.
```

## Evidence / derivation

`C-0039` gives the strict threshold rule `log(m)<2T`, so the open interval between the `m=3` and `m=4` thresholds contains exactly the active prime powers `2` and `3`.

For every active `m`, self-adjointness and the norm bound give

```text
P_m >= -||P_m||I >= -c_m b_m I.
```

Summing over the finite active set gives

```text
P >= -sum_m c_m b_m I.
```

On the high Legendre complement, `C-0045` gives `J>=H_N I`; the endpoint potential `V` is nonnegative and may be dropped in a lower bound; and the Suzuki residual is bounded below by `-rho_R I` as in the existing `C-0047` proof. Adding the bounds proves the displayed `mu_N` formula.

For `m=2,3` in the immediate window, `1<tau_m<2`. The general compressed-shift norm formula in `C-0040` therefore has essential chain length `2`, so each `||S_m||=2cos(pi/3)=1`.

## Dependencies

- `C-0039` — prime powers enter at strict half-log support thresholds;
- `C-0040` — exact norm of a compressed translation;
- `C-0044` — mandatory Suzuki residual;
- `C-0045` — Legendre jump coercivity;
- `C-0047` — historical one-prime complement argument being generalized;
- `docs/MULTI_PRIME_CONTRACT.md`.

## Significance for RH research

This closes the complement-side mathematical generalization needed before the first two-prime structural window can be implemented. The complement loss depends on the sum of rigorous norm losses of active prime powers rather than a hard-coded `c_2` term.

## Limits

This is a sufficient complement lower bound only. It does not prove positivity at any support above `(log 3)/2`, does not choose a Legendre dimension, and does not create a theorem certificate or theorem admission.

## Verification

The derivation is an elementary operator lower-bound argument from already verified repository claims. The `{2,3}` active-set and `b_2=b_3=1` corollary were checked directly from the strict support inequalities and the exact path-graph norm formula; no numerical approximation is a proof premise.

## Timestamped addenda / corrections

None.
