# Research Log

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-21T02:09:00Z`
- **Policy:** Append-only

This is the chronological master log. Add newest entries at the top, immediately below this introduction. Existing entries must not be silently altered.

---

## 2026-08-21T02:09:00Z — Vaughan bilinear phase route closed; mechanism pivot required

**Type:** Research attempt / bilinear geometry / scale barrier / route closure

The UTC date rolled over before execution, so the item previously planned informally as `A-20260820-007` is formally recorded as `A-20260821-001` under the repository ID convention.

Completed `A-20260821-001`.

A Vaughan/Heath-Brown factorization of `Lambda` does not create new independent Laguerre phase directions. For `m=a_1...a_k` and `r_j=log a_j`, the phase is `Phi_n(r_1+...+r_k)` and its logarithmic Hessian is `Phi_n'' 1 1^T`, of rank one. The factor-redistribution directions preserving the product are exactly phase-flat.

On standard dyadic Type-II boxes the four-corner phase defect is `O(1/n)`, so the kernel is asymptotically separable into one-variable phases. `X-20260821-001` verifies the predicted `1/n` scaling. An `O(1)` cross phase first appears when balanced factor log-widths are of order `sqrt(n)`.

The formal full pre-turning Bessel phase has excursion `pi n`, only `n/2` full cycles, while fixed-interior prime scales are `X=exp(cn)`.

Most importantly, an unweighted prime estimate `X^(1-delta+o(1))` becomes `X^(1/2-delta+o(1))` after the critical half-weight. Reaching `exp(o(n))` therefore requires `delta>=1/2`: essentially square-root cancellation. A conventional fixed power saving below square-root remains exponentially too large.

Recorded `F-20260821-001` through `F-20260821-005`, `C-0031` through `C-0035`, computation `X-20260821-001`, and references `R-0021` through `R-0023`.

**Outcome:** RH remains unresolved. The direct Li/Laguerre prime-cancellation branch is blocked at an RH-scale arithmetic boundary; the next research action is a mechanism pivot to positivity/moment-matrix formulations rather than another finite divisor decomposition.

---

## 2026-08-20T22:44:00Z — Microlocal Dirichlet reduction completed; global bilinear structure becomes frontier

**Type:** Research attempt / endpoint closure / mean-value barrier / circularity check

Completed `A-20260820-006`.

The below-first-prime segment was closed exactly using DLMF 18.14.8:

```text
|S_n^[1,2)| <= 2A(sqrt(2)-1)n.
```

More generally, every shrinking endpoint `u<=eta_n=o(1)` is `exp(o(n))` by the same global Laguerre inequality and trivial `Lambda(m)<=log m`.

Actual prime atoms begin at `m=2`, so their maximal local Mellin frequency is

```text
gamma_2(n)
= A/2 sqrt(4n/(A log 2)-1)
~ sqrt(A n/log 2).
```

Thus the discrete prime side carries only `O(sqrt(n))` frequencies; the formal `gamma~n` endpoint from `A-005` lies below the first prime and is not the primary prime-sum obstruction.

On a fixed interior chirp cell, Taylor expansion in `y=log x` gives `Phi_n''(y)=O(1/n)`, so windows `H=o(sqrt(n))` linearize to smooth prime Dirichlet polynomials with coefficients `Lambda(m)m^(-1/2+i gamma_0)`.

The classical Montgomery-Vaughan mean-value theorem was then tested at the exact exponential scale. A cell centered at `u_0` has length `N=exp(4n u_0/A+o(n))`; because the available frequency range is only subexponential, the `O(N)` length term dominates and leaves RMS scale `exp(2n u_0/A+o(n))`, root base `exp(2u_0/A)>1`. Generic one-dimensional large-sieve/Dirichlet-polynomial `L2` machinery therefore does not close the route (`R-0020`).

A second guard was recorded: a matched smooth local cell is itself zero-sensitive through the Mellin explicit formula. Demanding `exp(o(n))` control independently for every such cell can reconstruct a zero-free statement window-by-window, consistent with the smooth-weighted PNT converse literature.

Created `F-20260820-022` through `F-20260820-026`, `C-0026` through `C-0030`, computation `X-20260820-008`, source `R-0019` for the DLMF Laguerre inequality, and `R-0020` for Montgomery-Vaughan.

**Outcome:** RH remains unresolved. The active target is now global arithmetic cancellation that preserves cross-cell structure, beginning with a Vaughan/Heath-Brown bilinear decomposition of the nonlinear chirp.

## 2026-08-20T22:15:00Z — Uniform pre-turning phase derived; arithmetic chirp becomes frontier

**Type:** Research attempt / asymptotic derivation / computation / circularity check

Completed `A-20260820-005`.

DLMF's uniform Laguerre Bessel expansion gives, for `L_(n-1)^(1)(4n*u)`, the phase

```text
4n xi(u)-3pi/4,
xi(u)=1/2[sqrt(u-u^2)+asin(sqrt(u))].
```

The exact frequency derivative is

```text
xi'(u)=1/2 sqrt((1-u)/u),
```

so a Mellin frequency `gamma>0` is matched at

```text
u_gamma=A^2/(A^2+4gamma^2),
A=2s0-1.
```

The earlier `A^2/(4gamma^2)` helper is exactly the large-`gamma` / small-`u` approximation of this uniform map.

For a fixed critical-line mode, the stationary phase equals the exact Cayley phase `n arg(z_rho^(-1))`, and the leading stationary amplitude simplifies exactly to `1`. This gives a local asymptotic mechanism for the `z_rho^(-n)` term in the exact zero response `z_rho^(-n)-1`.

On the prime side, the pre-turning kernel becomes an explicit nonlinear Mellin chirp acting on the critical-half-weight signed measure

```text
exp(-y/2)d(psi(e^y)-e^y).
```

A new limitation was also isolated: the relative stationary width is

```text
sigma_u/u_gamma=sqrt(2gamma/(A n)),
```

so high zero frequencies coalesce with the `u=0` endpoint when `gamma` is of order `n`; fixed-frequency stationary formulas cannot simply be summed over the entire zero spectrum.

Finally, if `M_N=sum_(n=N)^(2N)|S_n|^2`, then `limsup M_N^(1/(2N))<=1` is itself equivalent to RH. Generic coefficient-space Parseval/`L2` control is therefore a circular reformulation unless an independent arithmetic prime-side estimate is proved.

Created `F-20260820-017` through `F-20260820-021`, `C-0021` through `C-0025`, and computation `X-20260820-007`. Added `R-0016` through `R-0018` for Lagarias, Arias de Reyna, and the DLMF Bessel/stationary-phase sources.

Automated verification after the phase-tooling changes: Python `276/276` tests passed and the Rust workspace passed `15/15` tests.

**Outcome:** RH remains unresolved. The active target is now an unconditional arithmetic cancellation theorem for the critical-half-weight nonlinear prime chirp, together with a valid high-frequency endpoint treatment.

---

## 2026-08-20T22:10:00Z — Research environment and phase-helper contract hardened

**Type:** Research infrastructure / reproducibility / correctness guard

Verified the project `.venv` on CPython 3.14.0 with the pinned scientific stack, including `mpmath`, SciPy, NumPy, SymPy, Matplotlib, python-flint/Arb, GMPY2, pytest, and Hypothesis. The Python test suite and Rust workspace tests were passing before this cleanup.

Corrected the maintained environment contract to Python `>=3.12`, aligned repository documentation with the scientific environment and native `crates/rh_engine` CLI, and added `uv.lock` as the resolver lockfile.

Removed the unregistered hard-coded zeta-zero fallback from `scripts/rh_tools.py`; zero ordinates are now explicitly numerical values produced by the pinned `mpmath` dependency, not described as certified data.

Hard-cut the provisional phase API from generic `stationary_*` names to `small_u_stationary_*`. These formulas only encode the small-`u` approximation obtained from the phase `2 sqrt(n t)` and are not accepted as the uniform pre-turning stationary map. `A-20260820-005` remains responsible for deriving the genuine uniform Bessel phase before any broader phase helper is introduced.

Historical computation records that truthfully used only the standard library were left unchanged.

Post-change verification: `uv sync --extra test --locked` completed without environment changes, all research scripts compiled, the Python suite passed `273/273`, and the Rust workspace passed `13/13` tests.

**Outcome:** infrastructure corrected without changing any RH claim or research conclusion.

---

## 2026-08-20T21:20:00Z — Airy-window plan refined to phase-aware full transform

**Type:** Research attempt / correction / computation / literature boundary check

Completed `A-20260820-004`.

The planned narrow Airy-window strategy was tested rather than assumed. The smooth-density maximum from `A-003` is separated from the true Airy turning transition by a fixed distance in `u`; its Gaussian width is `O(n^(-1/2))`, while the Airy transition itself has width `O(n^(-2/3))`. It is therefore more accurately a post-turning Laplace saddle represented by the uniform Airy formula.

The sufficiently far post-turning tail can be suppressed unconditionally. However, the pre-turning region retains positive absolute-envelope root growth under current unconditional PNT errors, so it cannot be discarded by absolute-value estimates.

A new exact identity was derived for one explicit-formula zero mode:

```text
S_(n,rho)=z_rho^(-n)-1,
z_rho=(rho-s0)/(rho+s0-1).
```

This shows directly that the complex phase is essential. `X-005` quantifies the gap between beta-only envelopes and exact Cayley rates, while `X-006` numerically reproduces the exact complex Laplace transform and shows cancellation across `u` regions.

A literature check also closed the generic mean-square shortcut: Zhao's published Lemma 8 shows that the dyadic mean-square exponent of `psi(x)-x` changes with `Theta=sup Re(rho)`, so RH-scale `L^2` control already forces the RH boundary. Han's smooth-weighted-PNT converse results provide a parallel circularity warning for strong smoothed error estimates.

Recorded `F-20260820-013` through `F-20260820-016`, `C-0017` through `C-0020`, `X-20260820-005` through `X-20260820-006`, and sources `R-0013` through `R-0015`.

`A-003` is preserved but marked `SUPERSEDED` as the active frontier, with a timestamped terminology/strategy addendum.

**Outcome:** RH remains unresolved. The next route must preserve phase in the full Laguerre transform rather than reduce the problem to absolute local discrepancy norms.

---

## 2026-08-20T21:05:31Z — Research tooling added; Airy saddle identified

**Type:** Research attempt / computation / derived asymptotic structure

Created `A-20260820-003` and a dependency-free Python research toolkit under `scripts/`.

The tooling includes exact rational identity verification, high-precision prime-trace cutoff studies, uniform-scale kernel scans, and prime-versus-density range decomposition. Four reproducible computation records were created as `X-20260820-001` through `X-20260820-004`.

### Analytic findings

The pole-subtracted discrepancy transform was integrated by parts exactly:

```text
S_n=A n-A integral E(x)f_n'(x)dx,
E(x)=psi(x)-x.
```

Only the ordinary prime number theorem `E(x)=o(x)` is needed to close the upper boundary for fixed `n`.

Using DLMF's uniform Laguerre scaling, `L_(n-1)^(1)` has

```text
nu=4n,
u=t/(4n).
```

The smooth prime-density Airy envelope has its unique exponential saddle at

```text
u_*=A^2/(A^2-1).
```

Its exponential rate simplifies exactly to

```text
[s0/(s0-1)]^n=|q|^n.
```

Thus the deterministic zeta-pole mode removed algebraically in `A-002` is also the dominant smooth-density saddle of the uniform Laguerre asymptotics.

A generalized-center tradeoff was derived: increasing `s0` lowers the moving prime scale but proportionally weakens the Cayley amplification of a hypothetical off-line zero. No free asymptotic gain appears.

Finally, `A-003` shows that a direct absolute-value estimate using any fixed pointwise exponent `|psi(x)-x|=O(x^theta)` with `theta>1/2` still leaves positive exponential growth. The next route must use signed/averaged cancellation in the Airy window rather than a pointwise estimate alone.

### Computation highlights

- exact core identities passed through `n=40` at `s0=2,3,5/2,4`;
- for `s0=3`, the sampled kernel maximum moved from `u=1.0211` at `n=64` to `u=1.0362` at `n=256`, toward the predicted `25/24`;
- a turning-region bin at `s0=3`, `n=16` had prime and smooth-density contributions around `-325.8` differing by about `-0.0203`; doubling Simpson resolution preserved the discrepancy;
- cutoff studies confirmed that the necessary prime range moves rapidly with `n` and that larger `s0` improves numerical reach without changing the underlying analytic difficulty.

Recorded `F-20260820-009` through `F-20260820-012`, `C-0013` through `C-0016`, and sources `R-0011` through `R-0012`.

**Outcome:** RH remains unresolved. The active target is now localized to prime-counting discrepancy in a uniform Airy window.

---

## 2026-08-20T20:49:00Z — Raw prime target corrected; pole-subtracted criterion derived

**Type:** Research attempt / correction / derived criterion

Completed `A-20260820-002`.

The planned finite-difference analysis exposed a more basic issue: for every generalized center `s0>1`, the raw prime-Laguerre sequence contains the deterministic exponential mode

```text
1-q^n,
q=-s0/(s0-1),
```

coming from the known pole of `zeta(s)` at `s=1`. Therefore the previous broad target "prove the generalized prime trace subexponential" is impossible even under RH.

A timestamped correction was appended to `A-20260820-001`; its historical derivation was not silently rewritten.

The hard-cut replacement is

```text
S_n=P_n-(1-q^n).
```

This subtraction is exact: `-S_n` is the Taylor coefficient sequence of

```text
d/dz log[(s(z)-1)zeta(s(z))].
```

Consequently, for every fixed `s0>1`,

```text
RH <=> limsup |S_n|^(1/n) <= 1.
```

The same sequence has the exact prime-discrepancy representation

```text
S_n
= A integral x^(-s0)L_(n-1)^(1)(A log x) d(psi(x)-x).
```

The degree-two shift filter `(E-1)(E-q)` was also derived; it annihilates the pole sequence exactly and converts the prime kernel to an order-zero Laguerre combination.

Recorded `F-20260820-005` through `F-20260820-008`, `C-0009` through `C-0012`, and `R-0010`.

**Outcome:** no proof of RH. The research target is now the pole-subtracted discrepancy kernel, not the raw prime density.

---

## 2026-08-20T20:37:00Z — First RH attempt imported and source-verified

**Type:** Research attempt / literature verification / correction

Created `A-20260820-001`, documenting the Li-coefficient / generalized-center / Laguerre-weighted prime-trace route explored before the repository protocol was initialized.

Recorded `F-20260820-001` through `F-20260820-004`, `C-0001` through `C-0008`, and `R-0001` through `R-0009`.

The pre-protocol critical-line "quartet" value `8 sin^2(n theta/2)` was corrected to the distinct-pair contribution `4 sin^2(n theta/2)`; the historical error remains explicitly documented.

**Outcome:** the generalized center is analytically useful but does not give a simple escape from the critical `1/2` scale. The raw-prime-trace part of this attempt was later corrected by `A-002`.

---

## 2026-08-20T20:33:00Z — Documentation system initialized

**Type:** Repository governance / research infrastructure

Created the authoritative timestamped documentation structure, claim ledger, bibliography, templates, and README navigation instructions.

No mathematical proof claim was created by this initialization.
