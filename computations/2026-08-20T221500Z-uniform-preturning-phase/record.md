# Uniform pre-turning stationary-phase diagnostics

- **Computation ID:** `X-20260820-007`
- **Created:** `2026-08-20T22:15:00Z`
- **Last updated:** `2026-08-20T22:15:00Z`
- **Status:** `COMPLETE`

## Objective

Numerically evaluate the exact uniform pre-turning stationary map derived in `A-20260820-005`, compare it with the earlier small-`u` approximation, and check the analytic critical-line phase and stationary-normalization identities on representative zeta-zero ordinates.

## Mathematical quantity tested

For

```text
A=2s0-1,
```

the script evaluates

```text
u_uniform=A^2/(A^2+4gamma^2),
u_small=A^2/(4gamma^2),
log x_gamma / n = 4A/(A^2+4gamma^2),
```

and compares

```text
4[gamma*u_uniform/A-xi(u_uniform)]
```

with the critical Cayley phase per coefficient

```text
-2 atan(A/(2gamma)).
```

It also evaluates the leading stationary normalization

```text
1/2 u^(-3/4)(1-u)^(-1/4)/sqrt(-xi''(u)),
```

which is analytically equal to `1` at the stationary point.

## Environment

- CPython `3.14.0`
- `mpmath 1.3.0`
- `matplotlib 3.11.1`
- project environment resolved by `uv.lock`
- zero ordinates: numerical evaluations from `mpmath.zetazero`, **not certificates**
- working precision for zero evaluation: `40` decimal digits
- script: `scripts/uniform_phase_diagnostics.py`
- script SHA-256: `23eb29c38566feb05ea3ce88155cd12fa14d506d1becde284b240785c02f86f5`

## Inputs and parameters

Three generalized centers were retained:

```text
s0=2, 3, 4
```

For each center, the first `8` numerically evaluated positive zeta-zero ordinates were used.

## Reproduction procedure

```text
.venv\Scripts\python.exe scripts\uniform_phase_diagnostics.py --s0 2 --zeros 8 --dps 40 --output-json computations\2026-08-20T221500Z-uniform-preturning-phase\data\s0-2.json

.venv\Scripts\python.exe scripts\uniform_phase_diagnostics.py --s0 3 --zeros 8 --dps 40 --output-json computations\2026-08-20T221500Z-uniform-preturning-phase\data\s0-3.json --plot computations\2026-08-20T221500Z-uniform-preturning-phase\plots\stationary-map-s0-3.svg

.venv\Scripts\python.exe scripts\uniform_phase_diagnostics.py --s0 4 --zeros 8 --dps 40 --output-json computations\2026-08-20T221500Z-uniform-preturning-phase\data\s0-4.json
```

## Output

At `s0=3`, for the first numerical ordinate

```text
gamma=14.134725141735...
```

the retained output is

```text
u_uniform = 0.03033384878268...
u_small   = 0.03128277577246...
relative small-u error = +0.03128277... = 3.128277...%
log_x_per_n = 0.02426707902614...
phase residual = 0 at displayed precision
stationary normalization = 1.000000000000
```

Across all `24` retained rows (`8` ordinates at each of three centers):

- phase residuals were at binary roundoff scale (`0` to roughly `5.6e-17`);
- stationary normalization printed as `1.000000000000`;
- the small-`u` relative error decreased monotonically with increasing `gamma` within each retained center.

Representative first-zero relative errors:

```text
s0=2: 1.12618...%
s0=3: 3.12828...%
s0=4: 6.13142...%
```

Artifacts:

- `data/s0-2.json` SHA-256 `31bbb29bc4aacba2c8427b08829b03fa2755b9174b8e87d69cc8c719ddf63eaf`
- `data/s0-3.json` SHA-256 `61eec27dff6c4cab3878590dd08cf839ddca8020fcee2bb9932f4d54988a456b`
- `data/s0-4.json` SHA-256 `27d6b05dfa2514e7bf674126d0fa1a2c3323c2bb63222b12ab6857c8b2f8d897`
- `plots/stationary-map-s0-3.svg` SHA-256 `65ab890ddaaaedb81d7da66cca254a1735bd2c5b08e2b81fd54be7a55bd4774a`

## Interpretation

The computation corroborates the analytic identities and quantifies how quickly the previous small-`u` formula approaches the uniform map for actual low numerical zero ordinates.

It also confirms that moving `s0` changes the finite-`gamma` error of the small-`u` approximation, making the uniform formula preferable even when the approximation is numerically close.

## Limitations

- The zero ordinates are numerical evaluations, not certified zero data.
- Numerical agreement does not prove the DLMF-derived formulas; those formulas are established analytically in `A-005`.
- Only eight ordinates and three centers are plotted/tabulated.
- The experiment does not address the joint high-frequency regime `gamma~n`.
- Nothing in this computation proves RH or provides evidence that an off-critical zero cannot exist.

## Related claims / attempts / findings

- `A-20260820-005`
- `F-20260820-017`
- `F-20260820-018`
- `C-0021`
- `C-0022`

## Timestamped addenda / corrections

None.
