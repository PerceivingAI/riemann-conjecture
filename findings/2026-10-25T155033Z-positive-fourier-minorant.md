# Complete Fourier bounded minorant positive at the matched support

- **Finding ID:** `F-20261025-006`
- **Created:** `2026-10-25T15:50:33Z`
- **Last updated:** `2026-10-25T18:25:39Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED` fresh independent Arb source acceptance and exact rational research proof; not production admission

## Statement

At T=1353/2048,a=7/2,Omega256,N312, the complete C-0094 bounded Fourier minorant H0 is strictly positive on L²(-T,T), conditional on the documented Suzuki source identity and Arb/FLINT correctness premises. This supplies a new reference proof at a support where smooth-test positivity was already known from C-0087. It is not a new support result.

In ordinary unnormalized Legendre coordinates, D_j=2/(2j+1), let A312 be the actual low form matrix and GP the combined arithmetic tail Gram. Fresh source enclosures and exact rational congruences prove both complete156-dimensional parity blocks of

\[
S_-=A_- -\frac{(GP)_++3\cdot10^{-40}D}{19/8-10^{-82}}
\]

strictly positive. Here A_- and (GP)_+ are complete Loewner enclosures of the actual matrices, not entrywise endpoints incorrectly treated as matrix order.

| Finite sufficient block | Certified mass-normalized lower display |
| --- | --- |
| Even | 1.3995633634664128e-11 |
| Odd | 8.213611938461616e-9 |

The displays are backed by exact rationals in the proof and independent receipt. They bound the finite sufficient blocks, not the spectral minimum of H0 or the full Weil form. C-0094's complete outside block and mixed-Gram allowance then imply H0>0 on the whole Hilbert space. Its nonnegative Fourier exterior gives the original nonzero smooth-test Weil positivity. No complete operator-domain identification is assumed.

## Evidence and derivation

[X-20261025-006](../computations/2026-10-25T155033Z-fourier-minorant-sign/record.md) retains the entire experiment, actual controls, original defect and corrected source versions.

The [complete enclosure argument](../computations/2026-10-25T155033Z-fourier-minorant-sign/matrix-enclosure-derivation-v1.md) supplies a rigorous whole-band Gauss remainder in operator norm. On every declared complex panel rectangle, DLMF's digamma series gives abs(A(z)-a)<4096. Cauchy estimates and exact positive Gauss quadrature give the full panel error8hM2^(-2q), summed over the entire band. The producer's total operator-error upper displays4.329079351385665e-21. Entry enclosures pay E sqrt(D_i D_j); no quadrature samples replace the integral and no error is dropped.

The source independently generates P,P²,GP,pole,band and A. P² retains the2/3 mixed products; GP=P²-PD^-1P. The pole's odd sign remains negative. Arithmetic is integrated exactly as a polynomial on the strict shift partition. Entire Fourier vectors are evaluated without a removable-zero division at any integration node.

The independent source audit rebuilds all six triangular matrices, **292968 entries in total**, at Arb768 using arithmetic Gauss313 rather than312 and band Gauss64 rather than48. It uses direct signed-shift intersections, separately derived Gauss weights, finite hypergeometric anchors with explicit tails and interval recurrence propagation. Each complete fresh enclosure must be contained in the published interval. The auditor separately reconstructs the exact sufficient lower, verifies nonsingular rational congruences, strict Gershgorin margins and the physical mass normalization.

The proof's authority does not include the earlier positive K312 witness or weighted-tail analytical packet. The only inherited numerical premise is the SHA-bound C-0094 scalar complement record. Existing arithmetic and exact-proof code is reused as code, not as a substituted positive conclusion.

## Dependencies

- C-0094's source split, full exterior, compact one-sided/double-tail bounds and mixed-Gram inequality.
- `R-0028`, [Suzuki arXiv2606.09096v3](https://arxiv.org/html/2606.09096v3), and `R-0030`, [DLMF5.7.6](https://dlmf.nist.gov/5.7.E6).
- Exact Legendre orthogonality, entire spherical-Bessel identity, polynomial Gauss exactness, operator-valued Cauchy bounds and bounded block square completion.
- Python-flint/FLINT transcendental and rigorous Legendre-root correctness. Producer and auditor share these library premises; they are not independent arithmetic libraries.

## Verification

- Corrected fresh source generation and exact positive proof exit0.
- Complete independent source reconstruction and exact verification exit0.
- Separate exact-only replay exits0 and is explicitly not fresh analytic acceptance.
- Isolated captured-source regeneration, proof and exact receipt are byte-identical to the originals.
- Four focused normalization/entire-transform/pole regressions pass.
- Five actual altered proof/source-binding reports are rejected without success outputs. These are binding/consequence controls, not five fresh analytic reconstructions.
- The original defective source and its failed proof remain reproducible in their original source closure.

## Implementation correction preserved

The first producer divided `PrimePowerTerm.coefficient` by two even though the existing API already supplies the coefficient of each one-sided shift. This halved P and quartered P². The original packet and failed proof attempt are invalid for the intended H0; they are not mathematical negative evidence.

A minimized real arithmetic control compares the constant trial with its exact overlap formula and combined operator-square formula. It detects both scaling errors before the fix and passes after the fix. Version2 removes the extra consumer factor. Frozen arithmetic implementations and earlier records were not changed. The entire defective method, source packet, failure and corrected rerun are retained separately.

## Significance and limits

The quantitative complement is now joined to a complete positive finite predicate. This is a demonstrated fixed-support whole-space bounded-reference capability, not merely positive sampled directions or qualitative compactness. It avoids inheriting the old positive physical reference as its authority.

It does not establish a positive unbounded support-covering family, a new support frontier, superiority to external work, novelty, a controlled larger-support cost law or a matched end-to-end speedup. Arithmetic and exterior constants change with support. The4 transition was not tested. No Rust/Lean verification, production certificate export, new admission or RH conclusion occurred. Admissions remain8v1/0v2/1v3; RH is unresolved.

## Timestamped addenda / corrections

None to this finding. The initial implementation correction is recorded above and in the separate versioned computation evidence; no earlier mathematical finding was silently rewritten.

### Primary identity cross-check, 2026-10-25T18:25:39Z

`R-0037` records direct inspection of [DLMF10.54.2](https://dlmf.nist.gov/10.54.E2) and [DLMF3.5(v)](https://dlmf.nist.gov/3.5#v). They confirm the Legendre Fourier phase/normalization, positive Gaussian weights and exactness through degree2q-1 used above. The complete operator remainder and source/error accounting remain the repository's stated derivation.
