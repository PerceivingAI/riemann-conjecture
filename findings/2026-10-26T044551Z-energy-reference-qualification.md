# F-20261026-004: exact energy decomposition and stronger scalar-floor obstruction

- **Created:** `2026-10-26T04:45:51Z`
- **Last updated:** `2026-10-26T05:00:39Z`
- **Type:** Derived identities, conditional reference bound and rejected closure
- **Status:** VERIFIED within stated source premises; no new complete positivity result
- **Claims:** C-0107, C-0108, C-0109

## Positive mathematical results

With complete arithmetic P and signed pole K_pole, the exact identity is

    P+K_pole=L_T-D_E,
    L_T(u,v)=exp(-|u-v|/2),
    D_E=integral exp(-l/2)(U_l+U_-l)d[psi(exp(l))-exp(l)+1].

L_T is positive and compact. The discrepancy D_E is a compact correction of -P, not generally compact itself. The shifted archimedean form d_A=q_A+(1-A(0))||f||² is positive, has an explicit complete Legendre-tail lower, and yields a conditional outside criterion if a useful one-sided logarithmic-energy discrepancy bound is proved. This changes the outside estimate rather than merely reordering the same finite Schur blocks, but supplies no new complete low/cross sign.

A separate modulation/compactness proof establishes

    bI+P_T+C>=mu I implies b>=mu+a_*(T)

for every fixed T>0 and compact self-adjoint C. At T>=7/2, C-0102 gives a_*>(3/20)exp(T). The same floor remains after removing any finite-dimensional low space. Consequently nonnegative bounded Fourier H0 itself requires a>=a_*, without separately assuming positive aI+P. Adding the pole, retaining another finite band or rearranging finite Schur blocks cannot remove that cost.

This strengthens the earlier scalar-reference obstruction. It does not imply Weil negativity or exclude an unbounded energy-based argument; logarithmic energy grows along the modulations used in the proof.

## Rejected bounding argument

Absolute Stieltjes integration gives

    |d_E[f]|<=B(T)[2||f|| ||f'||+||f||²].

For smooth modulations the derivative norm grows linearly while logarithmic energy grows at most logarithmically. This majorant therefore cannot be absorbed into that energy with fixed finite linear constants when B>0. The actual D_E remains bounded on L². Failure of the H1 majorant is not failure of its actual relative boundedness.

No useful energy-relative constants or new complete positivity criterion are established. The scalar/norm-only alternatives also retain the compact-floor obstruction. The qualification rejects this particular closure rather than asserting a new general no-go or promoting a reformulation into a proof mechanism.

## Evidence

[X-20261026-004](../computations/2026-10-26T044551Z-energy-reference-qualification/record.md) retains both full proofs, independent review, declared controls and captured-code replay. Four fresh P/pole scalar normalizations fit the original accepted T3/4 source intervals; exact overlap, complete Stieltjes/continuum, logarithmic-tail and non-Weil modulation/compact controls pass. Captured-code output is byte-identical. Sixteen earlier seals and965 members remain unchanged.

No new support matrix, Weil-sign test, certificate, working-precision law, outside package or production admission is added. Existing finite positivity and RH unresolved remain unchanged. No literature-originality claim is made.
