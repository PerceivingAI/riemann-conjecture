# Critical-line stationary saddle reproduces the Cayley mode

- **Finding ID:** `F-20260820-018`
- **Created:** `2026-08-20T22:15:00Z`
- **Last updated:** `2026-08-20T22:15:00Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

For a fixed critical-line mode

```text
rho=1/2+i gamma,
gamma>0,
```

the stationary point of the uniform pre-turning Laguerre/Bessel phase satisfies

```text
4n[gamma*u_gamma/A-xi(u_gamma)]
= -2n atan(A/(2gamma))
= n arg(z_rho^(-1)).
```

Moreover, the leading stationary-phase amplitude normalizes exactly to `1`:

```text
1/2
* u_gamma^(-3/4)(1-u_gamma)^(-1/4)
/ sqrt(Psi_gamma''(u_gamma))
=1.
```

After the Bessel and stationary-phase constants and the outer sign are included, the localized fixed-`gamma` saddle contributes

```text
z_rho^(-n)
```

to leading order.

## Evidence / derivation

Use `u_gamma=A^2/(A^2+4gamma^2)` and

```text
Psi_gamma(u)=gamma*u/A-xi(u).
```

Direct substitution gives the phase identity and

```text
Psi_gamma''(u_gamma)
=(A^2+4gamma^2)^2/(8A^3gamma).
```

The amplitude simplification is exact. It was independently simplified symbolically with SymPy.

## Dependencies

- `A-20260820-005`
- `F-20260820-017`
- `C-0019`
- `R-0011`
- `R-0018`

## Significance for RH research

This identifies the zero term `z_rho^(-n)` in the exact Li/Laguerre response with a concrete stationary-frequency mechanism of the prime-side kernel. The transform is behaving as a spectral matched filter for Mellin frequency `gamma`.

## Limits

This is a fixed-critical-mode real stationary-phase statement. It does not justify summing the asymptotic over all zeros. For `beta!=1/2`, a natural complex saddle has the exact Cayley exponent algebraically, but a rigorous complex contour deformation is not proved here. The exact full mode remains `z_rho^(-n)-1`; this finding does not assign the remaining `-1` to a single endpoint contribution.

## Verification

Algebraic phase and amplitude identities were checked with SymPy. The phase identity is included in Python property tests and Rust unit tests. `X-007` gives roundoff-level phase residuals and normalization `1` for all retained numerical rows.

## Timestamped addenda / corrections

None.
