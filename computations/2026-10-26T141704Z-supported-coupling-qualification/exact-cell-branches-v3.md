# Exact partition bounds for translated-source branches

- **Created:** `2026-10-26T14:42:35Z`
- **Last updated:** `2026-10-26T14:42:35Z`

Version2 narrows the smooth cell enclosure but still misses the declared odd accuracy. The retained [diagnostic](data/branch-diagnostic-v1.json), produced by [diagnose-branches-v1.py](diagnose-branches-v1.py), finds six cases where exact rational cell/shift bounds prove a cell entirely inside or outside a compressed translation, while its stored Arb ball overlaps the jump.

Arb midpoint/radius storage can widen a cell slightly beyond its exact rational endpoints. Using that widened ball to choose a branch is safe but charges the jump across the entire neighboring cell. Padding the actual arithmetic breakpoint to96bits does not prevent coarser ball-radius rounding of a much wider neighboring cell.

Version3 keeps the same exact partition and chooses the branch from certified exact endpoints. If a shift has enclosure[a_lower,a_upper] and the cell is[left,right], then

    u-shift lies in[left-a_upper,right-a_lower].

These rational bounds determine inside/outside/ambiguous. They do not require the computational ball to be exact. The smooth functions may still be evaluated on an enclosing Arb ball, which is conservative. The midpoint and mean-value path are taken in the actual cell. A truly ambiguous breakpoint slab still gets a complete jump hull and its full measure is paid.

This changes no support, modes, grid, residual sum, working precision or acceptance threshold. It does not discard arithmetic uncertainty or choose a favorable point branch. Versions1/2, their original inputs and unresolved output remain intact. The new source meets the requested accuracy only if independent full-cell and endpoint/residual verification succeeds.
