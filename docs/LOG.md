# Research Log

- **Created:** `2026-08-20T20:33:00Z`
- **Last updated:** `2026-08-20T20:37:00Z`
- **Policy:** Append-only

This is the chronological master log. Add newest entries at the top, immediately below this introduction. Existing entries must not be silently altered.

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

The generalized-center trick is analytically useful because the prime series is absolutely convergent for fixed `n`, but it does not provide a simple asymptotic escape from the critical `1/2` scale. The route is `BLOCKED`, not disproved: the missing object is an unconditional `n`-uniform cancellation bound for a prime-Laguerre trace that is not merely another RH equivalent in disguise.

The next planned attempt is finite-difference filtering of the Li/Laguerre trace.

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
