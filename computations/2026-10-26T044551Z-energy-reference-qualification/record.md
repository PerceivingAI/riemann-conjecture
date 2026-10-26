# X-20261026-004: energy reference and discrepancy closure qualification

- **Created:** `2026-10-26T04:45:51Z`
- **Last updated:** `2026-10-26T05:00:39Z`
- **Status:** COMPLETE qualification. Exact decomposition/reference bounds proved; proposed derivative closure rejected; no useful replacement positivity criterion established.
- **Claims:** C-0107, C-0108, C-0109

## Question and actual outcome

Qualify a reference retaining logarithmic archimedean energy rather than demanding global positivity of a scalar arithmetic reference before treating the archimedean term. Do not mistake an exact reformulation, compact addition or finite Schur rearrangement for an improvement.

The [energy/discrepancy derivation](energy-discrepancy-reference-v1.md) establishes

    P+K_pole=L_T-D_E,
    E(l)=psi(exp(l))-exp(l)+1,
    D_E=integral exp(-l/2)(U_l+U_-l)dE(l),
    L_T(u,v)=exp(-|u-v|/2)>=0 as an operator.

Both pole signs, the complete prime-power sum and endpoint conventions remain intact. The positive logarithmic reference d_A=q_A+(1-A(0))||f||² has a genuine full Legendre-tail lower mu_N(R). A proved one-sided discrepancy bound d_E<=alpha d_A+b||f||², alpha<1, would imply an explicit outside lower. No useful such alpha,b is supplied by the attempted closure.

The derived absolute Stieltjes majorant is

    |d_E[f]|<=B(T)[2||f|| ||f'||+||f||²],
    B(T)=integral_0^(2T) exp(-l/2)|E(l)|dl.

This has the wrong energy order for direct absorption. Smooth modulations have derivative norm of linear frequency growth, but logarithmic reference energy at most logarithmic growth. Hence no fixed finite linear energy-plus-mass bound can absorb this H1 majorant when B>0. This rejects this specific bounding argument, not the actual discrepancy form, which is bounded on L².

The independent [compact-correction theorem](compact-correction-obstruction-v1.md) proves a stronger limitation than the earlier positive-M condition:

    bI+P_T+C>=mu I, C compact self-adjoint
      implies b>=mu+a_*(T), for every fixed T>0;
    a_*(T)>(3/20)exp(T), for T>=7/2.

The proof uses elementary simultaneous phase recurrence, weakly null modulations and compactness. The floor persists after removing finitely many modes. In particular bounded Fourier H0=aI+P+K_pole+K_band cannot be nonnegative with a<a_*, even if positivity of aI+P is not separately demanded. A scalar one-sided bound for D_E has the same floor. Thus moving compact pieces or changing finite elimination blocks cannot remove the cost.

These new conclusions extend the earlier obstruction and do not rewrite its historical proof or limitations. They do not give Weil negative directions: the omitted unbounded archimedean/exterior energy grows on the modulations and can repair the bounded minorant. A genuinely energy-dependent estimate is not excluded by the compact theorem.

## Circularity and equivalence audit

The candidate changes the outside energy estimate; it is not merely C-0093's matched finite Schur elimination. Nevertheless no dominance over an old complete positivity criterion is proved. The discrepancy-relative interface alone is not an RH assertion: every bounded D_E has the trivial alpha0,b>=||D_E|| bound without implying full-form positivity. A useful smaller b/energy tradeoff and the independent low/cross sign are the missing quantitative content. They cannot be replaced by assuming all-support positivity.

No new zero-free theorem, conditional prime-error estimate or outside implementation is used. The source identity is the already qualified Suzuki convention, with the previously accepted digamma and Fourier-tail inputs. All new recurrence, compactness, Laplace-transform, Stieltjes and modulation arguments are included in full. No literature originality is claimed.

## Independent verification

[Independent qualification review](independent-qualification-review.md) approved both derivations without findings. It specifically checked signs and origin/endpoints, the reference domain and full tail, all compact-floor quantifiers, the bounded H0 consequence, the failed H1 absorption and the distinction between that majorant and the actual bounded operator.

[input-pins.json](input-pins.json) declares the finite controls before execution. Only the existing T3/4 source is used. No new support matrix, low Schur sign, eigenvector, witness or certificate is computed.

Actual controls in [controls-v1.json](data/controls-v1.json):

- The complete active set is2,3,4. Four fresh scalar P/pole diagonal normalizations for modes0/1 fit the original128-bit physical-mass source intervals. The odd pole is explicitly negative. This is not a fresh audit of all292968 source slots.
- Four exact rational overlap controls derive the even/odd autocorrelation normalizations independently.
- Piecewise integration proves all relevant post-jump E values negative at this fixed support and evaluates B about0.5843331895709215. A separate closed prime-sum formula agrees. B is a coefficient multiplying an H1 expression, not an operator-norm bound of size0.584.
- Closed physical pole values, discrete prime sums, continuous shift moments, positive Laplace moments and Stieltjes integration by parts agree for both parity modes. The two low discrepancy values are negative, but no global discrepancy sign follows.
- At existing N312 and the analytically derived R416/3, the reference-only tail lower is about9.466377157461127. It is not a complete Weil-tail lower: the missing discrepancy estimate still has to be paid.
- Four declared modulations1,16,256,4096 of a normalized cosine H1_0 function check the derivative/log-energy comparison and the bounded actual discrepancy. The ratio to the logarithmic upper grows from about0.250 to245.4. These finite controls illustrate the proved asymptotic obstruction; the proof uses genuinely smooth test functions, not a numerical extrapolation or a Weil-sign evaluation.
- Three commensurate-shift toys check exact phase recurrence and decay of a rank-one compact form. Their rational shifts/coefficients are not prime arithmetic at a new support. They do not replace the proof for arbitrary finite prime phases.

All controls pass on their first canonical execution. Exact rational enclosures, not rounded display values, are retained. No permanent tests or existing source changes were introduced.

## Executed command and captured-source reproduction

Equivalent repository-root invocation, using a fresh output:

```text
uv run --locked python -B computations/2026-10-26T044551Z-energy-reference-qualification/energy-controls-v1.py --output <new-output.json>
```

The actually exercised locked-environment Python command, stdout/stderr and elapsed time are in [the canonical receipt](data/scalar-exact-controls.run.json). Python3.14, python-flint0.9 and Arb512 are recorded in [environment.json](data/environment.json). No precision ladder or numerical-sign search occurred.

An [eight-file captured code closure](source-v1/manifest.json) preserves the script, pins, four imported project files and pyproject/lock. It deliberately does not duplicate the original accepted source packet. The isolated Python invocation enforces captured project-source origins and uses explicit --input-root for the original SHA-bound retained source data. Source isolation and data location are distinct. [Isolated receipt](data/isolated-scalar-exact-controls.run.json) and [replay summary](data/isolated-replay-summary.json) record the exact command and scope.

Canonical and captured-code outputs are byte-identical, SHA256 `76ecb999551e17a86ab5e800e06e68580abc92a0440be50363d0fb68fe81c8c4`. Bytecode writing is disabled. [Preservation receipt](data/preservation-check.json) verifies16 preceding seals,965 historical members and16 protected public files unchanged. The new root manifest seals this bundle last. Original theorem artifacts, source/checker/test files and historical records retain their bytes.

## Decision boundary

The exact energy-aware representation and reference-tail estimate are proved. The proposed derivative closure is rejected; compact/scalar modifications cannot evade the stronger floor. No useful closing energy-relative estimate, complete new positive reference criterion or replacement implementation is qualified. The already accepted T3/4 result remains intact, as do frozen8v1/0v2/1v3 admissions. RH unresolved.

No generic tool, dependency, cloud operation, source-profile broadening, production-retention or theorem-admission change is made. No full suite, Rust or Lean run, commit or push was performed.
