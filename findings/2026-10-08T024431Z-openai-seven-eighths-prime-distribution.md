# OAI-5 — Prime-distribution consequences of OpenAI quasi-RH

- **Finding ID:** `F-20261008-002`
- **Created:** `2026-10-08T02:44:31Z`
- **Last updated:** `2026-10-08T02:44:31Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED` (written mathematical derivation, not Lean/Comparator replay)
- **Dependencies:** `EXT-0001`, `C-0060`, `R-0035` (Kiran S. Kedlaya, *An Introduction to Analytic Number Theory*, Chapter 7, https://kskedlaya.org/ant/part-2-4.html)
- **Claims:** `C-0061`, `C-0062`

## Exact theorem and classical inputs

`EXT-0001` states `zeta(s) != 0` for `Re(s)>7/8`. Its functional-equation consequence is `Re(rho)<=7/8` for every nontrivial zero `rho`, including possible zeros **on** the `7/8` boundary.

`R-0035` supplies (i) the truncated von Mangoldt explicit formula (Theorem 7.2) and (ii) the classical count `N(T)=O(Tlog T)` (Theorem 7.6). In its notation, for the half-weighted-at-jumps Chebyshev function `psi_0`,

```text
psi_0(x)-x = -sum_(rho: |Im rho|<T) x^rho/rho
             - zeta'(0)/zeta(0) - (1/2)log(1-x^(-2))
             + O(x log²(xT)/T + log(x) min(1,x/(T d(x)))).
```

Here `d(x)` is distance to the nearest *other* prime power. Ordinary right-continuous `psi(x)=sum_(n<=x)Lambda(n)` differs by at most `Lambda(x)/2<=log(x)/2` at a prime-power jump and agrees elsewhere. From the zero count, summation by parts yields `sum_(|Im rho|<T)1/|rho|=O(log²(2+T))`; finitely many low zeros are harmless. Zeros are counted with multiplicity.

## C-0061 — Chebyshev and ordinary prime-counting errors

For `x>=2`, every zero satisfies `|x^rho|=x^Re(rho)<=x^(7/8)`, so the truncated zero sum is `O(x^(7/8)log²(2+T))`. Set `T=x`: the explicit-formula remainder is `O(log²x)`, since the first term is `x log²(x²)/x` and `min(1,*)<=1` makes the second at most `log x`. The constant and trivial-zero terms are `O(1)` for `x>=2`, and the jump correction is `O(log x)`. Therefore, **uniformly for real `x>=2`**,

```text
psi(x) = x + O(x^(7/8)log²x).                    (C-0061a)
```

This preserves the exponent `7/8` **without an epsilon loss**; the result does not exclude boundary zeros or assert `o(x^(7/8))`.

The classical prime-power comparison `psi(x)-theta(x)=O(sqrt(x)log x)` (also in `R-0035`) gives

```text
theta(x)=sum_(p<=x)log p=x+O(x^(7/8)log²x).     (C-0061b)
```

Stieltjes partial summation gives `pi(x)=theta(x)/log x+integral_[2,x]theta(t)/(t log²t)dt`. With `theta(t)=t+E_theta(t)`, the error is `O(x^(7/8)log x)+O(integral_[2,x]t^(-1/8)dt)=O(x^(7/8)log x)`. The main term differs by an additive constant from `Li_2(x)=integral_[2,x]dt/log t`. Hence

```text
pi(x) = Li_2(x) + O(x^(7/8)log x).               (C-0061c)
```

This is exactly the classical fixed-zero-strip argument of `R-0035` section 7.3 specialized to `c=1/8` from OpenAI's theorem. It does **not** supply a Dirichlet-character arithmetic-progression bound.

## C-0062 — Compact smoothing and critical half-weight

Fix `W∈C_c^1((0,infinity);C)` supported in `[a,b]`, `0<a<b`. Write `E(u)=psi(u)-u`. Stieltjes integration by parts, using vanishing weights at the support boundaries, yields

```text
sum_n Lambda(n)W(n/X) - X integral_0^infinity W(v)dv
  = -integral_0^infinity E(u)W'(u/X)/X du
  = O_W(X^(7/8)log² X).                         (C-0062a)
```

Uniformly for real frequency `tau`, use `h(u)=u^(-1/2+i tau)W(u/X)`, with derivative

```text
h'(u)=(-1/2+i tau)u^(-3/2+i tau)W(u/X)
      +u^(-1/2+i tau)W'(u/X)/X.
```

On `[aX,bX]`, `|u^(i tau)|=1` and `int|h'|du<=C_W(1+|tau|)X^(-1/2)`. Partial summation gives the **uniform-in-tau** result

```text
sum_n Lambda(n)n^(-1/2+i tau)W(n/X)
 - integral_0^infinity u^(-1/2+i tau)W(u/X)du
   = O_W((1+|tau|)X^(3/8)log² X).              (C-0062b)
```

The smooth main-term integral is indispensable. The same bound with `(1+H)` replaces `(1+|tau|)` for a differentiable unit-modulus log phase `exp(i phi(log u))` satisfying `sup|phi'|<=H` on the support. Neither statement is claimed uniform for the full `n`-dependent Laguerre kernel or its endpoint regimes.

## Consequences and boundaries

At `X=exp(cn)` for fixed `c>0`, the remaining `X^(3/8)` loss equals `exp(3cn/8)`; these **upper** estimates cannot establish the `exp(o(n))` bound required by `C-0010`. They do **not** prove the actual sum has a matching exponential lower bound. `C-0034` square-root cancellation remains unproved.

Directly squaring `C-0061a` yields only `O(X^(11/4)log⁴X)` dyadic mean square. The separately retained `C-0020` result gives a stronger `O(X^(11/4))` upper bound under its cited assumptions; it is not superseded.

**Trust:** External OpenAI `EXT-0001` is cited, classical results are `R-0035`, our specializations are documentary proofs, not compiled Lean. No arbitrary character/conductor uniformity, explicit numerical constants, new localized Weil positivity, new v1/v2 admission, RH proof, source vendoring, or private execution-environment data.
