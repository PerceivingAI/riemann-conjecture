# Research Log

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T21:05:31Z`
- **Policy:** Append-only

This is the chronological master log. Add newest entries at the top, immediately below this introduction. Existing entries must not be silently altered.

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
