# T=1 execution allocation and contraction contract

- **Created:** 2026-10-29T01:39:29Z
- **Scope:** Specified dense-layout resource analysis and restricted execution probes; no full analytical matrix, width gate, coupled sign or positivity acceptance.

## Fixed mathematical declaration

[C-0126](../2026-10-29T004611Z-t1-direct-reference/reference-contract-v1.md) supplies T=1, N=5564, M=11128, K=132, beta2981/1024, R4060, Rc8120, alpha1/4, m1/3, eta1-2^-128, accuracy2^-78 and starting source25600/audit34304/publication256 bits. Active prime powers are2,3,4,5,7. These controls are not reduced to claim an execution improvement.

The existing source and independent audit remain fixed to T=.81,N826,M1652,K86 with dimension413. Their main/input/provenance/active-set guards are unchanged. No generic T=1 proof runner exists in this computation. Applying their allocation strategy to the accepted declaration is a precisely identified comparison, not an executed full-target adaptation.

## Allocation graph

Let d=N/2=2782 and q=(M-N)/2=2782. The following are shape deductions from the retained implementation, not measured total target peaks.

| Retained operation | Shape at the new declaration | Evidence |
| --- | --- | --- |
| Source global exact Legendre polynomials | M polynomials through degree M-1; only low-input polynomial rows are subsequently indexed in source() | [producer:169](../2026-10-28T034134Z-t081-resource-execution/build-whole-source-v4.py), source():113-150 |
| Source combined signed square | two d-by-d accumulators; per cell both parity row/weighted-row lists and native copies | producer:85-111; 11 target cells, not the frozen nine-cell claim |
| Source translated low/tail evaluations | three Gauss-row lists plus weighted Y, held with previous loop-local matrix variables until rebound | producer:124-136 |
| Source logarithmic moment matrix | N-by-N dense table; C and shifted matrices are d-by-N | producer:132-136 |
| Source VV, head and exterior construction | many simultaneous d-by-d or q-by-d matrices plus transient products/transposes | producer:139-150 |
| Audit globals | M exact Rodrigues polynomials, N residual output polynomials, harmonic tables, BOTH q-by-q frequency kernels and N Gauss nodes | [consumer:681-692](../2026-10-28T034134Z-t081-resource-execution/verify-whole-source-v2.py) |
| Audit residual conversion | selected parity power count at most d+K/2=2848; coefficient matrix at most2848-by-d and low/tail moment matrices d-by2848 or q-by2848 | consumer:162-212; degree bound, not measured exact support of every output |
| Audit arithmetic coefficient matrices | d-by-d low and q-by-N tail | consumer:264-270 |
| Audit each signed-window moment tables | d-by-N low/log tables and **N-by-N tail table**, plus N-by-d shifted transpose | consumer:285-302 |
| Audit each window images | d-by-d low/log and N-by-d tail; accumulators d-by-d or q-by-d | consumer:300-305 |
| Audit signed square per cell | N-by-d row and weighted-row lists, their native copies/product and d-by-d accumulator | consumer:310-354 |
| Audit reconstruction | mass diagonals, V/P/R low and tail, several complete Gram/intermediate matrices; three outputs returned together | consumer:432-479 |
| Publication/checking | source materializes full upper-triangle Python lists/JSON/gzip; consumer retains compressed and expanded bytes plus parsed pairs | producer:181-186; consumer:507-547 |

Python locals survive loop bodies. For example the previous tail_moments remains live while the next assignment constructs its replacement. Likewise the previous parity's returned three-matrix dictionary remains bound while the next source()/reconstruct() RHS executes. Sequential parity ordering therefore does NOT imply release of the previous parity before reconstruction. These are explicit lifetime risks, not a numerical sum of an unmeasured peak.

Producer and consumer retain different arithmetic/normalization constructions; an execution change must not make the analytical consumer import producer mathematics. The old checker also has fixed32MiB JSON/compression caps and fixed dimensions/pins/counts; a larger target cannot be admitted by merely changing N.

## Full-length moment-vector census

The audit's power table is

`H[k,j]=moments[2k+p+j]`, k,j=0..N-1, p=0 or1,

where moments[s]=integral_a^b x^s dx. For each active m and both starting precisions, the probe executes the unchanged lower-level power_window_moments on the ACTUAL T=1 window[-1,1-log(m)] through degree3N-2. It explicitly checks exact ball reflection against the opposite window; this storage symmetry is not used to omit either signed P/VP window in a proof.

For each of the16691 moments, an exact hexadecimal midpoint/radius dump is loaded into an opaque independently owned native Arb scalar. Native bits must equal Python bits. A FRESH arb_set copy supplies native heap bytes; retained capacity is cleared before each measurement. Native _arb_vec_allocated_bytes independently checks the scalar-sum account on4096 copied entries for every case. No Python/Cython object-layout casts are used.

The multiplicity of each moment in H is computed both by an integer endpoint formula and by an independent row-interval prefix sum; each sums to N^2=30958096. Summing copied heap bytes with these multiplicities and the measured native48-byte ball body gives the dense-copy account. This is neither a scaled old RAM observation nor an actual target-matrix allocation. It excludes allocator overhead, row pointers, Python objects and every other live matrix. The explicit midpoint limb payload alone is also reported as a lower bound for this uncompressed independent-entry representation.

FLINT documents [arb_allocated_bytes and vector accounting](https://flintlib.org/doc/arb/index.html#memory): scalar heap excludes sizeof(arb_struct), whereas vector accounting includes its body. The installed DLL is SHA-bound separately. These are software allocation premises, not new mathematical literature assumptions.

## Equivalent execution identities

For a low input mode n, let B[j,n] be the complete monomial coefficients of P_n(x+tau), padded to all N powers. The selected tail-power contraction is

`Y[k,n]=sum(j=0..N-1) moments[2k+p+j]*B[j,n]`.

Row blocking changes only which output rows coexist; every inner power remains. A structured alternative uses M(z)=sum moments[s] z^s and B_rev(z)=sum B[j,n] z^(N-1-j):

`Y[k,n]=coefficient(z^(N-1+2k+p), M(z)*B_rev(z))`.

This identity eliminates the N-by-N Hankel table. Interval operation grouping may change radii; a full-target integration would still have to prove every native containment and transformed numerical-error goal. It does not permit dropping a term or trusting matching floating output.

The restricted probes use four actual high modes5557,5559,5561,5563, twelve selected power rows including5563, the full5564 inner powers, parity1, T=1,m2 and34304 bits. They do NOT represent all prime terms, both parities, the complete source, a target width goal or the final coupled matrix.

For every selected output, an independent native polynomial composition and endpoint antiderivative must fit the contraction's outward256-bit interval. A deliberately omitted nonzero highest-power contribution must fail that containment. All algorithms retain this independent check. Native full-precision endpoints need not be byte-identical after reassociation; selected published dyadic pairs are compared explicitly.

## Admission boundary

A specified dense-layout native storage account above observed host/system capacity rejects that execution configuration. It does not prove the host is incapable of a differently represented workload, require a larger machine, or imply a negative mathematical sign. A successful selected contraction does not qualify the unimplemented complete target producer, analytical consumer, exact witness path or retained acceptance. No full T=1 run is admitted by these measurements.
