# Independent quantitative-envelope review

- **Created:** `2026-10-26T00:28:18Z`
- **Last updated:** `2026-10-26T00:28:18Z`
- **Reviewer:** separate read-only mathematical review agent, `QuantitativeEnvelopeReview`
- **Disposition:** APPROVED; no mathematical errors or domain/normalization gaps found

The reviewer independently checked [the derivation](quantitative-envelope-v1.md), rather than using scalar samples as a proof.

1. Differentiating g(x)=x^(-1/2)log(X/x)/T gives the stated positive Stieltjes-integral kernel. The zero endpoint weight handles a prime-power X. Integration with the published Chebyshev bounds gives both constant-trial envelopes and the rate exp(T)/T.
2. The cap vector has total measure2 and amplitude1/sqrt2. Each signed shift contributes half the triangular overlap, so their sum is the overlap, not twice it. The half-open arithmetic interval (L,U] is strictly active. At T>=7/2 its upper endpoint meets the published lower-bound domain. The resulting coefficient is strictly above3/20.
3. The essential chain length is the stated ceiling, including the measure-zero endpoint convention. The norm sum needs no commutativity. Partial summation independently gives the sufficient global bound (21/5)exp(T)-21/10. The joint2/4 bound is restricted to its previously proved window.
4. DLMF's secant-cubed remainder applies along Re(z)=1/4. The real-part normalization gives error at most2/t². Monotonicity, A(4)<0 and divergence give the unique inverse above4 for b>=0, and the bracket2pi exp(b±1/8). Its upper endpoint controls the entire exterior.
5. The necessary positive-M bound and separately constructive sufficient choice establish the stated double-exponential cutoff order when prescribed reserves sum to O(exp(T)). Reserves tending to zero do not remove necessity; larger reserves may force faster growth. No H0/Schur/Weil positivity follows from these two reference bounds alone.

**Review limits:** external Rosser–Schoenfeld domains were supplied from the parent's visual inspection of the original paper; the reviewer checked their use, not the paper's finite verification. The reviewer consulted DLMF's remainder statement. This was written mathematical review, not Lean/Rust acceptance, scalar-code execution, a matrix calculation or a claim of literature originality. No files were modified by the reviewer.
