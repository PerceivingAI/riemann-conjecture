# Research Log

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T20:49:00Z`
- **Policy:** Append-only

This is the chronological master log. Add newest entries at the top, immediately below this introduction. Existing entries must not be silently altered.

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

Recorded:

- `F-20260820-005` — raw trace has deterministic zeta-pole exponential;
- `F-20260820-006` — pole-subtracted RH-equivalent root criterion;
- `F-20260820-007` — exact `d(psi-x)` discrepancy representation;
- `F-20260820-008` — exact pole-annihilating shift filter;
- `C-0009` through `C-0012`;
- `R-0010` — DLMF zeta analytic structure at `s=1`.

**Outcome:** no proof of RH. The research target is now cleaner: estimate the pole-subtracted discrepancy kernel, not the raw prime density.

---

## 2026-08-20T20:37:00Z — First RH attempt imported and source-verified

**Type:** Research attempt / literature verification / correction

Created `A-20260820-001`, documenting the Li-coefficient / generalized-center / Laguerre-weighted prime-trace route explored before the repository protocol was initialized.

Recorded four reusable findings:

- `F-20260820-001` — corrected zero-orbit contribution;
- `F-20260820-002` — subexponential Li growth would imply RH;
- `F-20260820-003` — generalized centers restore the fixed-prime `m^(-1/2)` Laguerre envelope;
- `F-20260820-004` — square-root-scale `psi` input is circular because it is RH-equivalent.

Registered claims `C-0001` through `C-0008` and sources `R-0001` through `R-0009`.

### Correction preserved

The pre-protocol informal argument described a critical-line "quartet" contribution as

```text
8 sin^2(n theta/2).
```

That double-counted the zero orbit. On the critical line `1-rho=conjugate(rho)`, so there are only two distinct zeros in the orbit and the correct contribution is

```text
4 sin^2(n theta/2).
```

The original error is not silently erased; the correction is recorded in the attempt, finding, claim ledger, status file, and this log.

### Outcome

The generalized-center trick is analytically useful because the prime series is absolutely convergent for fixed `n`, but it does not provide a simple asymptotic escape from the critical `1/2` scale. The route is `BLOCKED`, not disproved. The raw-prime-trace part of its blocker is later corrected by `A-20260820-002`.

---

## 2026-08-20T20:33:00Z — Documentation system initialized

**Type:** Repository governance / research infrastructure

Created the authoritative documentation structure for timestamped RH research:

- research protocol;
- current-status snapshot;
- append-only chronological log;
- claim ledger;
- timestamped attempt records;
- timestamped finding records;
- reproducible computation records;
- literature bibliography;
- record templates;
- README navigation instructions.

No mathematical proof claim was created by this initialization.
