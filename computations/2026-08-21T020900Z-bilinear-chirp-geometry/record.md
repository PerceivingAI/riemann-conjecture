# Bilinear Laguerre chirp geometry and dyadic separability

- **Computation ID:** `X-20260821-001`
- **Created:** `2026-08-21T02:09:00Z`
- **Last updated:** `2026-08-21T02:09:00Z`
- **Status:** `COMPLETE`

## Objective

Numerically check the deterministic phase geometry used in `A-20260821-001`: dyadic four-corner defects, their `1/n` scaling, the logarithmic width required for `O(1)` bilinear nonseparability, and the total formal pre-turning phase excursion.

## Mathematical quantity tested

For

```text
F(r,s)=Phi_n(r+s),
Phi_n(y)=4n xi(Ay/(4n))-3pi/4,
```

the script computes

```text
Delta F
=F(r+h,s+k)-F(r+h,s)-F(r,s+k)+F(r,s),
```

on logarithmic boxes, compares it with

```text
|Phi_n''| h k,
```

and records

```text
Hcrit=1/sqrt(|Phi_n''|)
```

for the balanced unit-cross-phase scale.

It also computes

```text
4n[xi(1)-xi(0)]/(2pi)=n/2.
```

## Environment

- CPython `3.14.0`
- standard library only
- project environment resolved by `uv.lock`
- script: `scripts/bilinear_chirp_geometry.py`
- script SHA-256: `9f8b6ca30a18e36896249a9936075241496b434ed9fcde87622c546af5f807bd`

## Inputs and parameters

Retained runs:

```text
s0=2,3,4; n=1024
s0=3; n=256,4096
logarithmic box width=log 2
```

Fixed-interior `u` values were selected from

```text
0.05,0.10,0.25,0.50,0.75.
```

## Reproduction procedure

```text
.venv\Scripts\python.exe scripts\bilinear_chirp_geometry.py --s0 2 --n 1024 --output-json computations\2026-08-21T020900Z-bilinear-chirp-geometry\data\s0-2-n1024.json
.venv\Scripts\python.exe scripts\bilinear_chirp_geometry.py --s0 3 --n 1024 --output-json computations\2026-08-21T020900Z-bilinear-chirp-geometry\data\s0-3-n1024.json
.venv\Scripts\python.exe scripts\bilinear_chirp_geometry.py --s0 4 --n 1024 --output-json computations\2026-08-21T020900Z-bilinear-chirp-geometry\data\s0-4-n1024.json
.venv\Scripts\python.exe scripts\bilinear_chirp_geometry.py --s0 3 --n 256 --u 0.1,0.25,0.5 --output-json computations\2026-08-21T020900Z-bilinear-chirp-geometry\data\s0-3-n256.json
.venv\Scripts\python.exe scripts\bilinear_chirp_geometry.py --s0 3 --n 4096 --u 0.1,0.25,0.5 --output-json computations\2026-08-21T020900Z-bilinear-chirp-geometry\data\s0-3-n4096.json
```

## Output

At `s0=3`, `u=0.25`, the dyadic cross defect is

```text
n=256   -> 2.7090215e-2
n=1024  -> 6.7722305e-3
n=4096  -> 1.6930526e-3,
```

which scales as `1/n`.

At `s0=3`, `n=1024`, the balanced unit-cross-phase widths are approximately

```text
u=0.10 -> Hcrit/sqrt(n)=0.138564...
u=0.25 -> Hcrit/sqrt(n)=0.263215...
u=0.50 -> Hcrit/sqrt(n)=0.400000...
```

and the script returns

```text
total_preturning_cycles=512
```

as predicted by `n/2`.

## Interpretation

The diagnostics support the analytic conclusions that standard dyadic Type-II boxes become phase-separable as `n` grows and that nontrivial bilinear phase coupling first appears on `sqrt(n)` logarithmic scales.

## Limitations

This computation tests deterministic phase geometry only. It does not evaluate Vaughan coefficients, primes, or any arithmetic cancellation theorem, and it cannot prove RH.

## Related claims / attempts / findings

- `A-20260821-001`
- `F-20260821-001`
- `F-20260821-002`
- `F-20260821-003`

## Timestamped addenda / corrections

None.
