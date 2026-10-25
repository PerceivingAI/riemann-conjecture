# Finite coupled-tail elimination and the larger-projection criterion

- **Finding ID:** `F-20261025-004`
- **Created:** `2026-10-25T13:42:54Z`
- **Last updated:** `2026-10-25T13:42:54Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `PROVISIONAL`, independently qualified algebra; retained accounting not yet executed
- **Proposed claim:** C-0093
- **Computation:** X-20261025-004

## Question

Does the demonstrated finite coupled-tail rearrangement provide an exact positivity criterion or demonstrated practical leverage beyond the ordinary larger-projection method? This is an assessment of that concrete construction, not a search for another positive result at the existing support.

## Matched-reference equivalence

Use the C-0063 closed form and finite splitting L=P_N, E=P_M-P_N, F=Q_M. Fix the **same** uniformly positive outside reference D>=dI, with the domain inclusion and form domination required by C-0072. Retain the same actual bounded finite-to-F cross maps and finite blocks. Replacing only the F form by D yields a valid lower reference on its possibly larger form domain.

Eliminating F gives the ordinary larger-projection reference

\[
H_M=A_M-B_M^*D^{-1}B_M.
\]

If G=(H_M)_EE is positive, eliminating E gives

\[
S_N^{coupled}=(H_M)_LL-(H_M)_LE G^{-1}(H_M)_EL.
\]

This is also the result of eliminating the coupled tail E plus F at once. Square completion therefore gives

\[
H_M>0\quad\Longleftrightarrow\quad G>0\ \hbox{and}\ S_N^{coupled}>0.
\]

A positive formal low Schur expression with an indefinite E block is insufficient. The same finite equivalence holds for a fixed complete Loewner lower K_M. It does not identify K_M with the exact reference or the true Schur. Different outward bounds and conditioning can change practical certificate success, not the exact common-reference identity.

The actual historical N20 and M312 references have different chosen reserves. They are not silently identified here. The equivalence concerns a fair comparison with the outside reference held fixed.

## Dense accounting

For each parity let m=M/2, n=N/2 and e=m-n. A dense block-Cholesky leading model satisfies

\[
e^3/3+e^2n+en^2+n^3/3=m^3/3.
\]

Its full triangular-factor parameter count satisfies

\[
e(e+1)/2+en+n(n+1)/2=m(m+1)/2.
\]

These are accounting identities, not universal complexity lower bounds, actual certificate sizes or measured wall-time predictions. They exclude omitting the retained tail/cross work while counting only the final low block as the complete dense calculation. Structured algorithms and alternative certified bounds are not excluded.

## Scope at creation

The independent written qualification is retained in the new computation bundle. The executed check will account for actual source slots and recorded workloads, not generate another positivity matrix. C-0092's quantitative loss diagnosis remains valid. No decision about all coupled-tail methods, new support, optimal dimension, external priority, production admission or RH follows from this initial record.
