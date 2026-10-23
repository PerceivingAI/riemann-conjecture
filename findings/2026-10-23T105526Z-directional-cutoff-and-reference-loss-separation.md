# Finite cutoff loss and diagonal-reference loss are different quantities

- **Finding ID:** `F-20261023-001`
- **Created:** `2026-10-23T10:55:26Z`
- **Last updated:** `2026-10-23T10:55:26Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`, separately reviewed written spectral identities and exact retained-data bounds, conditional on the stated source premises. Not an admitted positivity theorem or Lean proof.
- **Claim:** `C-0074`

## Statement and setup

In C-0072's setting, fix the original odd trial at `T=3/5,N=192` and the already evaluated prefix ending before `M0=211`. Write `a=<u,Au>`, `t_k=<e_k,Bu>`, `w_k=(mu+H_k-H_192)^-1`, and

\[
P=\sum_{192\le k<211}w_k|t_k|^2,\quad
Q=\sum_{192\le k<211}|t_k|^2,\quad
R=\sum_{k\ge211}|t_k|^2,\quad
J=\sum_{k\ge211}w_k|t_k|^2.
\]

Even terms in the known prefix vanish by exact odd parity. Here P and Q are scalar prefix energies, not the signed arithmetic operator. The full combined Gram on this trial is `G(u)=||Bu||^2=Q+R`.

The finite sufficient directional value and exact diagonal-reference value are

\[
s_U=a-P-w_{211}R,\qquad
s_0=a-P-J.
\]

Consequently the cutoff loss is

\[
\Delta_{\rm cut}=s_0-s_U
=w_{211}R-J
=\sum_{k\ge211}(w_{211}-w_k)|t_k|^2\ge0.
\]

This is distinct from the inverse-reference loss

\[
\Delta_{\rm ref}
=\langle Bu,(C_0^{-1}-C^{-1})Bu\rangle\ge0,
\qquad
s_C=s_U+\Delta_{\rm cut}+\Delta_{\rm ref}.
\]

A negative finite sufficient value does not determine either nonnegative gain or the sign of either larger reference/true Schur value.

## Bounds available from the retained intervals

For the nine accepted full-source intervals `I_k`, define

\[
q_k^-=\operatorname{dist}(0,I_k)^2,\qquad
q_k^+=\max_{x\in I_k}|x|^2.
\]

Then `Q_- = sum q_k^- <= Q <= sum q_k^+ = Q_+` and `P_- = sum w_k q_k^- <= P <= sum w_k q_k^+ = P_+`. The correct implications of the original one-sided `a<=a_up`, `G(u)>=g_low` are

\[
s_0\le a_{\rm up}-P_-,\qquad
R\ge R_-:=\max(0,g_{\rm low}-Q_+).
\]

Subtracting `Q_-` instead would give the wrong direction for a physical omitted-mass lower bound. Although the algebraic expression `a_up-P_--w_M(g_low-Q_-)` is a valid finite-majorant upper when all prefix weights are ordered appropriately, `g_low-Q_-` is not itself such a mass bound.

The executed [retained-data audit](../computations/2026-10-23T105408Z-directional-loss-review/record.md) gives the following decimal displays. Exact endpoints are in its JSON artifact.

| Quantity | Value |
| --- | ---: |
| Known mass lower Q_- | 0.9635928360509430 |
| Known mass upper Q_+ | 0.9635928360511430 |
| Known inverse cost lower P_- | 4.744783306913747 |
| Known inverse cost upper P_+ | 4.744783306914679 |
| Original low-form upper a_up | 6.407116781359653 |
| Prefix-only exact-reference upper a_up-P_- | 1.662333474445906 |
| Actual omitted mass lower R_- | 0.7987791726070741 |
| Finite charge lower w_211 R_- | 2.862508772853621 |

Thus the known prefix alone does **not** force negativity of the exact diagonal reference. Its positive upper is not positive evidence. The omitted mass is substantial, but a mass lower bound is not an upper bound on its inverse-weighted cost J. The width `P_+-P_-` is exactly below `10^-12`; the missing spectral distribution cannot be supplied by narrowing these same nine intervals.

The separated bound `a_up-P_--w_211 R_-` is still negative. This explains which terms in the finite allowance exceed the available upper headroom, without equating the allowance with the actual cutoff loss. The latter also depends on the unknown J.

## What the retained scalar inequalities do not determine

The scalar information admits abstract completions of either exact-reference sign. This is an information-limit argument, not a construction of alternative Weil sources.

Fix prefix moments at their interval midpoints. The audit establishes `P_+<a_up` and `g_low>Q_+`, so these choices have `a_up-P>0` and `R_*=g_low-Q>0`. Set the abstract scalar `a=a_up` and total coupling mass `G=g_low` in both completions.

- Put all `R_*` at the odd tail index 211. The audited inequality `P_-+w_211 R_->a_up` makes the abstract diagonal-reference direction negative.
- Put the same finite `R_*` at a sufficiently large odd index K. Since `w_K` tends to zero, an odd K exists for which `w_K R_*<a_up-P`, making the abstract direction positive. No such index or new source moment was numerically evaluated.

Both completions are square-summable and retain the same prefix, a and G while satisfying the serialized scalar inequalities. They are not asserted to satisfy the additional structure of the actual Suzuki source. Therefore even exact knowledge of total mass alone would not determine J from these prefix constraints. In particular, the result does not say that the actual form is uncomputable or that no further analytical consequence can be derived from its source.

With only a lower bound on G, the scalar inequalities also yield no finite numerical upper bound on the cutoff loss. At any fixed odd K greater than 211, arbitrarily large finite additional tail mass makes `(w_211-w_K)R` arbitrarily large while preserving `G>=g_low`. Each individual completion still has finite mass. The actual source is bounded on this low direction, but that upper bound is not supplied by these retained scalar inequalities.

## A two-sided directional sign condition

If valid additional bounds `a_-<=a<=a_+` and `J_-<=J<=J_+` are known, then

\[
a_- -P_+-J_+\le s_0\le a_+-P_--J_-.
\]

A strictly positive lower endpoint or strictly negative upper endpoint decides **this one direction** of the exact diagonal reference. An interval containing zero is inconclusive. Positivity on one direction is not full low-matrix or Weil positivity.

For example, a total-mass upper `G<=G_+` supplies the conservative estimate `J<=w_211(G_+-Q_-)`. This is a sufficient format for tail control, not the only one. It preserves the same worst-weight relaxation, so merely adding opposite scalar endpoints would not generally remove the lost spectral distribution.

The original approved packet serializes `a_full_rayleigh_upper_exact` and `gram_full_rayleigh_lower_exact`, but no corresponding low-form lower or full-Gram upper. The accepted source packet supplies the nine moment intervals, not J. These missing directions of inequality must not be invented from decimal width displays or from a positive upper.

For this fixed prefix the limitation is stronger. Keep the same mu and worst-weight estimate, and suppose valid `a_-<=a<=a_up` and `G<=G_+` are added. Necessarily `a_-<=a_up` and `G_+>=g_low`, so its lower endpoint obeys

\[
a_- -P_+-w_{211}(G_+-Q_-)
\le a_{\rm up}-P_+-w_{211}(g_{\rm low}-Q_-)
=u_{\rm exact}-(P_+-P_-)<0,
\]

where `u_exact<0` is the already established C-0073 upper. The corresponding retained-prefix upper is `a_up-P_->0`. Thus this particular cheap bracket straddles zero even with the best admissible opposite scalar endpoints. Improving those endpoints alone, while keeping the same prefix and worst-tail-weight relaxation, cannot make this bracket decide the reference sign. This is not a no-go for a distribution-sensitive bound on J or a different mathematical inequality.

## Dependencies, verification and limits

- C-0072 and C-0073; original SYS-6.4 trial/A/G premises and existing local Suzuki/Arb trust.
- X-20261022-001 for independent acceptance of the new moments, and X-20261022-002 for the completed finite-majorant screen. Neither earlier record was modified or rerun.
- X-20261023-001 executes a small exact audit on the same immutable packets; no new analytical moments or alternative cutoffs were evaluated.

A separate read-only mathematical review checked the loss identities, inequality orientations, abstract-completion argument and two-sided bracket. Exact audit quantities matched a separately coded Fraction accumulation. No new test suite, source evaluator, matrix/inverse calculation, external fetch, Rust/retained-proof replay or Lean build was performed.

The original A/G analytical inputs retain generator-source-qualified trust. The result establishes the loss separation and limits of the stated scalar inequalities; it proves no sign of the actual exact reference, true Schur complement or Weil form. No other support, dimension, trial or cutoff was qualified. Admissions remain eight v1, zero v2 and one v3; RH unresolved.
