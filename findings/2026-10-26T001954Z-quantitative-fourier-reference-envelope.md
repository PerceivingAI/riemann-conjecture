# F-20261026-001 — Intrinsic quantitative growth of the positive arithmetic reference

- **Created:** `2026-10-26T00:19:54Z`
- **Last updated:** `2026-10-26T00:28:18Z`
- **Type:** Derived mathematical bounds with externally sourced unconditional premises
- **Status:** VERIFIED — independently reviewed, scalar/exact controls and isolated replay; no production admission
- **Claims:** C-0102, C-0103

## Result

For the complete prime-power arithmetic P_T on L²(-T,T), put a_*(T)=sup sigma(-P_T). The positive arithmetic reference M_T=aI+P_T requires a>=a_*; requiring M_T>=m(T)I strengthens this to a>=a_*+m(T), without a uniform m.

C-0101's constant trial has rate r(T)=Theta(exp(T)/T), but is not norm-sharp in rate. A normalized vector supported on the two unit boundary caps gives, for T>=7/2,

    (3/20)exp(T) < a_*(T) <= ||P_T|| <= (21/5)exp(T)-21/10.

The upper bound follows from the complete arithmetic norm sum and partial summation; no commutation is assumed. The necessary exponential rate therefore cannot be attributed only to a conservative sufficient norm bound. Explicit finite ranges, constant-trial inequalities and chain-threshold conventions are in [the derivation](../computations/2026-10-26T001954Z-quantitative-reference-cutoff/quantitative-envelope-v1.md).

For A(t)=Re psi(1/4+it/2)-log pi,

    |A(t)-log(t/(2pi))| <=2/t², t>0.

Consequently the unique cutoff solving A(Omega)=b, for b>=0, lies in

    [2pi exp(b-1/8), 2pi exp(b+1/8)].

The upper endpoint is constructively sufficient for the full exterior, not just one frequency. Combining the two inequalities proves a double-exponential necessary cutoff order in support for this globally positive-M/nonnegative-exterior construction. A separate constructive choice attains that order when arithmetic/exterior reserves sum to O(exp(T)); reserves tending to zero do not remove the necessity.

## Evidence and provenance

[X-20261026-001](../computations/2026-10-26T001954Z-quantitative-reference-cutoff/record.md) retains the proof, independent review, exact/scalar calculation, initial failed-control source versions, source snapshot and actual command receipts. Canonical and isolated scalar outputs are byte-identical. The two accepted old cases are consistency checks only; no new support matrix or positivity sign was evaluated.

External premises were checked against the original [Rosser–Schoenfeld1962 paper](https://doi.org/10.1215/ijm/1255631807), printed pp.70–71, and [DLMF5.11(ii)](https://dlmf.nist.gov/5.11#ii); registered as R-0038/R-0039. The published arithmetic finite verification and Arb/FLINT correctness remain trust premises. No external code was imported and no local reproof of those published estimates is claimed.

## Meaning and boundary

This is a quantitative limitation of one positive arithmetic-reference/exterior architecture, not negativity of H0, Weil's form, or a no-go for other references/Fourier methods. It does not establish the unknown low positive gap, a practical work law or global positivity. It does not invalidate the existing finite positives, claim literature originality, or alter the frozen8v1/0v2/1v3 admissions. RH remains unresolved.
