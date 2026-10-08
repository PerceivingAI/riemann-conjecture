# OAI-4 — Exact route-by-route impact of OpenAI quasi-RH

- **Recorded:** `2026-10-08T02:38:25Z` (UTC)
- **Status:** `COMPLETE — MATHEMATICAL DEPENDENCY AUDIT`
- **External theorem:** `EXT-0001` — `openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`
- **Existing project consequence:** `C-0060`, `F-20261008-001`
- **Source overlap/context:** `references/external-results/EXT-0001-lean-overlap-audit.md`
- **Scope:** All eleven registered historical research attempts, Li/Laguerre and prime-discrepancy barriers, positivity/Weil continuation, generic multi-prime v2 and its actual rejection evidence. This audits the **mathematical consequences of the exact external theorem**, not the upstream proof internals or new computational/theorem admission.

## 1. Premises and decision rule

The only new external premise granted here is

```text
EXT-0001:  Re(s) > 7/8  =>  zeta(s) != 0.
```

The standard zeta functional-equation symmetry gives, for each nontrivial zero `rho`,

```text
1/8 <= Re(rho) <= 7/8.
```

The strict upstream statement does **not** exclude zeros on `Re(s)=7/8`. It does **not** say `Re(rho)=1/2`, and it does **not** establish nonvanishing of arbitrary Dirichlet `L`-functions without their separate pole hypotheses. Our already verified, external-dependent `C-0060` proves, for **fixed** `s0>1`,

```text
limsup_(n->infinity) |S_n(s0)|^(1/n)
    <= B(s0) := (s0-1/8)/(s0-7/8) > 1.
```

The RH-equivalent `C-0010` target is `<=1`. Letting `s0` vary with `n`, or informally taking `s0->infinity`, is not licensed by this fixed-center bound.

For every route, classify an effect as:

- **ESTABLISHED IMPROVEMENT:** follows from `EXT-0001` and an identified existing result without importing a missing RH-strength premise.
- **CONDITIONAL DIAGNOSTIC:** a hypothetical pointwise/smoothed error estimate is inserted only to calculate its insufficiency, not asserted as a consequence of the half-plane theorem.
- **NO CHANGE TO BLOCKER:** the theorem does not establish the actual missing lemma/certificate or invalidate the existing obstruction.
- **NOT ESTABLISHED:** any claimed direct formula, uniform error term, formal port, or new theorem admission that requires additional proof.

No historical attempt status is rewritten; historical documents describe their original stage, and subsequently resolved/intermediate results must be read together with the current `docs/STATUS.md` and `C-0050..C-0059`.

## 2. Audit of all registered attempts

| Attempt | Existing goal / decisive result | Exact new consequence | Does it remove the blocker? |
| --- | --- | --- | --- |
| [`A-20260820-001`](../../attempts/2026-08-20T203700Z-li-laguerre-prime-trace-route.md) | Generalized Li/Laguerre; exact prime trace, critical half-weight, RH-strength cancellation required (`C-0001..C-0008`) | Off-line zero orbits can now be restricted to `1/2<beta<=7/8`; the geometric and fixed-prime identities are unchanged | **NO**: Li positivity and the necessary prime-side root bound are not proved |
| [`A-20260820-002`](../../attempts/2026-08-20T204900Z-pole-subtracted-prime-laguerre-route.md) | Exact pole removal and RH-equivalent `S_n` criterion (`C-0009..C-0012`) | **ESTABLISHED:** `C-0060` supplies `limsup |S_n|^(1/n)<=B(s0)>1` for each fixed center | **NO**: strict gap from `1` remains; the exact pole subtraction needs no revision |
| [`A-20260820-003`](../../attempts/2026-08-20T210531Z-airy-saddle-discrepancy-kernel-route.md) | Correct Airy scale and absolute-value barrier (`C-0013..C-0016`); later superseded as active frontier | **CONDITIONAL DIAGNOSTIC:** even if a suitable pointwise `E(x)=O(x^(7/8+eps))` bound is separately justified, its exponent is above `1/2` | **NO**: `C-0016` leaves positive exponential loss under absolute values |
| [`A-20260820-004`](../../attempts/2026-08-20T212000Z-post-turning-phase-aware-discrepancy-route.md) | True saddle classification; exact zero-mode response; rightmost-zero mean-square boundary (`C-0017..C-0020`) | **ESTABLISHED:** zero modes with `beta>7/8` disappear; from retained `C-0020` and `Theta<=7/8`, dyadic `L2` has upper order at most `O(X^(11/4))` (derivation below) | **NO**: `O(X^(2+eps))` for all `eps>0`, which would imply RH via `C-0020`, is not obtained |
| [`A-20260820-005`](../../attempts/2026-08-20T221500Z-uniform-preturning-laguerre-phase-route.md) | Uniform stationary map, critical-mode normalization, high-frequency endpoint limitations, `L2` circularity (`C-0021..C-0025`) | Allowed off-critical real parts narrow, but `u_gamma=A²/(A²+4gamma²)` and zero-height geometry do not change | **NO**: missing uniform arithmetic/endpoint control remains |
| [`A-20260820-006`](../../attempts/2026-08-20T224400Z-prime-side-chirp-dirichlet-reduction.md) | Endpoint closure, microlocal weighted prime-polynomial reduction, length-versus-frequency and zero-sensitivity barriers (`C-0026..C-0030`) | Permissible hypothetical off-line `beta` decreases to at most `7/8`; a matched cell may still respond at `X^(beta-1/2)` | **NO**: generic mean-value `N` term and independent subexponential cell estimate are not supplied |
| [`A-20260821-001`](../../attempts/2026-08-21T020900Z-global-bilinear-vaughan-chirp-route.md) | Rank-one logarithmic Hessian, dyadic phase separability, square-root saving needed (`C-0031..C-0035`) | New zero strip changes neither the Hessian identity nor the fixed-interior exponential scale | **NO**: no new Type I/II cancellation theorem; the recorded *generic phase-only* obstruction stands |
| [`A-20260821-002`](../../attempts/2026-08-21T022600Z-positivity-moment-weil-mechanism-audit.md) | Li Gram/CND is RH-equivalent; natural prime Gram atoms fail PSD; restricted-support Weil foothold (`C-0036..C-0041`) | **ESTABLISHED analytic context:** some hypothetical zero placements are now impossible | **NO**: positivity of all Li Gram matrices or full Weil functional still requires RH, and prime atom signs do not change |
| [`A-20260821-003`](../../attempts/2026-08-21T040654Z-first-prime-weil-support-continuation.md) | First-prime endpoint absorption, mandatory Suzuki residual, digamma decomposition (`C-0042..C-0044`) | No change to `P_2` translation, `V`, `R_T`, or the support threshold | **NO**: these are operator identities and finite-support estimates, not supplied by zero-freeness |
| [`A-20260821-004`](../../attempts/2026-08-21T085252Z-exact-prime-legendre-schur-certificate.md) | `C-0045..C-0048` Legendre/tail-Gram theorem and eventual verified `C-0050` | Nothing additional follows for the exact matrices or positivity margins at `T=7/20` | **NO**, and no need: the original target has already been rigorously certified separately; the old attempt's interim text must not be confused with current theorem status |
| [`A-20260826-001`](../../attempts/2026-08-26T171400Z-one-prime-support-continuation.md) | Continuation with eight admitted `C-0050..C-0057` supports, ending at `T=27/50,N=104`; next `p=3` threshold | No change to `log(m)<2T`, certified tail bounds, or allowed `(T,N)` pairs | **NO**: no ninth theorem, no extension across `(log 3)/2`, no RH claim |

The final three rows intentionally distinguish historically complete research *attempt goals* from the current proof-bearing `C-0050..C-0057` state. A new external zeta theorem cannot retroactively transform a pre-theorem observation into a certificate.

## 3. Quantitative checks and exact remaining gaps

### 3.1 Li/Laguerre coefficients and individual zero modes

From `C-0019`, for `rho=beta+i gamma`,

```text
z_rho=(rho-s0)/(rho+s0-1)

|z_rho|^(-2)
  = ((s0+beta-1)^2+gamma^2)/((s0-beta)^2+gamma^2).
```

For `s0>1` and any `beta>1/2`, the numerator minus denominator is exactly

```text
(2s0-1)(2beta-1) > 0.
```

Hence even the *remaining permitted* zeros `1/2<beta<=7/8` would give `|z_rho|^(-1)>1`. A shrinking range for `beta` reduces possible right-of-line locations but is not the phase cancellation or zero-exclusion needed for `C-0010`.

For fixed `s0`, `B(s0)-1 = (3/4)/(s0-7/8) >0`. This algebraic gap cannot be removed by changing `n` alone or treating `s0` as a moving parameter without a separate uniform argument.

### 3.2 Pointwise and smoothed prime discrepancy

The `C-0016`/ `C-0034` obstacle is a threshold: a bound of the form

```text
|psi(X)-X| <= X^(theta+o(1))
```

inserted **absolutely** into a fixed-interior Laguerre/microlocal estimate leaves a critical-half-weight factor of order

```text
X^(theta-1/2+o(1)).
```

At the *illustrative* value `theta=7/8`, this is `X^(3/8+o(1))`, not `X^o(1)`; since `X=exp(cn)` for fixed `c>0`, it still means exponential-in-`n` loss. In `C-0034` notation, `delta=1-theta=1/8`, while the direct method requires `delta>=1/2`.

**Important boundary:** `EXT-0001` directly proves zero-freeness, **not** the displayed pointwise prime-error estimate with an exact exponent or any particular log factor. A correctly scoped explicit-formula/contour proof (including zeros, pole, truncation, uniformity, boundary, and error terms) is separate OAI-5 work. The hypothetical `theta=7/8` substitution above is an *insufficiency test*, not a theorem newly admitted here.

### 3.3 Dyadic mean-square input from an already recorded theorem

`C-0020` records an established result, with `Theta = sup Re(rho)`:

```text
If Theta = 1/2:   integral_X^(2X) (psi(x)-x)^2 dx  ~asymp X^2.
If Theta > 1/2:   integral_X^(2X) (psi(x)-x)^2 dx  << X^(2Theta+1),
                  with a related lower order X^(2Theta+1-eps).
```

Combine **the claimed `C-0020` upper theorem** with `C-0060`'s `Theta<=7/8`:

```text
integral_X^(2X) (psi(x)-x)^2 dx = O(X^(11/4)).
```

Arithmetic is exact: `2(7/8)+1=11/4`. This conclusion is a *dependency-level corollary of the retained `C-0020` statement*; OAI-4 did not independently revisit the underlying Zhao source or re-prove its asymptotic hypotheses, and does not register a new claim ID. It still misses the `O_eps(X^(2+eps))`-for-every-`eps` bound that `C-0020` says would force `Theta=1/2`. It therefore cannot be used as a noncircular substitute for the RH-scale mean-square estimate.

### 3.4 Li Gram, conditional-negative-definite, and Weil forms

`C-0036` and `C-0037` are already **equivalent** to RH: all-`N` Li Gram PSD or global conditional negative definiteness implies Li positivity. The externally established strip does not give those all-index positivity statements. Likewise, the Weil criterion requires full test-class positivity, whereas our `C-0050..C-0057` theorems certify only finite supports. No implication from `EXT-0001` to a new full localized operator lower bound was established.

## 4. Current main route: one-prime v1 vs generic multi-prime v2

### 4.1 Frozen one-prime exact certificates

The independently verified one-prime `exact_prime_legendre_schur` contract retains exactly eight pairs:

```text
(7/20,32), (2/5,40), (17/40,48), (9/20,56),
(19/40,68), (1/2,80), (21/40,96), (27/50,104).
```

The condition `log(m)<2T`, mandatory Suzuki residual, `C-0048` complement/Schur proof, and independent Rust exact-replay contract are unaffected by a new theorem about possible global zeta-zero locations.

**Decision:** Keep the eight v1 theorem statements and their existing verified evidence unchanged. No ninth pair can be inferred, and neither the full test class nor RH is established.

### 4.2 Generic multi-prime structure

`C-0058` and `C-0059` establish, in the window `(log3)/2<T<(log4)/2`, that the arithmetic active set is `{2,3}`, the combined operator is `P=P_2+P_3`, the complement loss includes `c_2+c_3`, and the sufficient factor-`3` Schur matrix involves combined `G_P` with mixed `P_2P_3+P_3P_2` terms. These are *support geometry / operator-algebraic* facts. The global zeta-zero strip does not alter them.

The current multi-prime v2 theorem admission grid remains **empty**. The actual frozen-target `T=11/20`, `N=192/196` calculations have exact, independently checked negative directions in the **specific sufficient factor-3 Schur matrices** after stable enclosure; even the higher-precision/stronger witness-bit tests do not make those matrices positive. See `docs/STATUS.md`, `docs/LOG.md`, and `X-20261001-001`.

**Decision:** `EXT-0001` does not turn these negative *sufficient-test* matrices positive, invalidate their rational witnesses, or prove that Suzuki's underlying localized Weil operator is negative. The obstruction is **mathematical rejection of this sufficient criterion at the frozen targets**, not a counterexample to RH. OAI-4 authorizes no change to v2 tests, support/dimension grid, bit ladders, factor-`3` contract, numerical tooling or theorem whitelist.

### 4.3 What would genuinely unblock current continuation?

A proof at new support requires an independently valid positive operator estimate or new sufficiently strong certifying reduction **plus** precise interval/certificate verification and separate theorem admission. Neither a weaker zero-free half-plane nor a more aggressive numerical search is a replacement for those conditions. Changing the sufficient Schur criterion, relaxing precision, or redefining the norm bound requires a separate mathematical research decision.

## 5. Route verdicts and non-dependencies

| Candidate shortcut | Verdict | Reason / related claims |
| --- | --- | --- |
| Treat `EXT-0001` as proof of RH | **REJECTED** | Remaining `1/2<beta<=7/8` is not excluded |
| Replace `C-0010` with `B(s0)>1` | **REJECTED** | Radius/root criterion requires `<=1` |
| Let `s0->infinity` after a fixed-`s0` bound | **REJECTED** | Invalid interchange without uniform control |
| Insert `psi(X)-X=O(X^(7/8))` without proof | **REJECTED** | Not the exact upstream theorem; contour/explicit-formula derivation needed |
| Use hypothetical `7/8` prime error absolutely to finish the chirp | **REJECTED** | Leaves `X^(3/8+o(1))` at fixed interior scales |
| Infer Li Gram/Weil global PSD | **REJECTED** | Equivalent full positivity still unproved |
| Alter `C-0048` / `C-0059` operator algebra or v2 negative witnesses | **REJECTED** | Mathematically independent of the global zeta zero-free strip |
| Register any new one-prime/v2 theorem or claim RH | **REJECTED** | No valid new certificate or proof |
| Use the actual `7/8` theorem as a named analytic dependency in further research | **VALID** | `EXT-0001`, `C-0060` with explicit attribution |

## 6. Priorities after this audit

1. **OAI-5 (optional targeted mathematics):** If a concrete downstream consumer is identified, rigorously derive the `7/8` theorem's `psi`-error or smoothed prime-discrepancy consequences with full hypotheses, epsilon/logarithmic dependencies, boundary and explicit-formula remainders. This must be a standalone proof, not a substitution into `C-0016` without support.
2. **OAI-5 (conditional consequence checks):** Test a *specific* transformed estimate or weighted mechanism against the remaining `beta in (1/2,7/8]` possibility, and show a genuine saving rather than the already known fixed-center upper bound.
3. **OAI-6/7:** Keep the theorem as a pinned cited external input; import into Lean or vendor only when a named new formal consumer justifies its compilation/dependency cost. Comparator replay remains optional and is not falsely claimed as performed.
4. **Independent of OpenAI:** Decide a distinct mathematical direction for the frozen `{2,3}` sufficient-Schur negative: seek a sharper valid inequality or independently justified alternative reduction *without modifying current admission or falsifying the negative witness*.

**Overall OAI-4 conclusion:** `EXT-0001` delivers genuine external mathematical progress (the `7/8` half-plane, hence the strict zero strip and `C-0060` fixed-center root-rate estimate). **None of the existing route blockers is removed by that theorem alone.** Our current exact finite-support successes and multi-prime negative sufficient-Schur diagnostics remain valid and unchanged.

## 7. Evidence and verification scope

Primary sources: `EXT-0001-openai-quasi-rh.md`, `F-20261008-001`, `C-0010`, `C-0016`, `C-0019`, `C-0020`, `C-0021..C-0030`, `C-0034..C-0037`, `C-0039..C-0048`, `C-0050..C-0059`, `C-0060`; the eleven linked `attempts/` files; `docs/STATUS.md`, `docs/MULTI_PRIME_CONTRACT.md`, `X-20261001-001`.

Checks here are source review, dependency mapping, exact algebra and classification; **not** new analytic number-theory proof, numerical recertification, Arb/Rust/Lean retest, complete review of the source behind `C-0020`, or upstream Comparator replay. The diagrammatic `7/8` pointwise error is explicitly labeled hypothetical. No tool outputs, absolute filesystem locations, identities, host details, credential values or raw environment inventory are retained.

This record is an **impact audit**, not a new `C-` theorem, and changes no existing theorem status.
