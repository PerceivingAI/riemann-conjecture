# Cancellation-aware source cell enclosure

- **Created:** `2026-10-26T14:38:21Z`
- **Last updated:** `2026-10-26T14:38:21Z`
- **Scope:** versioned interval-evaluation refinement of the same supported source, not changed support, grid, target or physical method

The original v1 run and its inputs/program/output remain unchanged. It certifies squared error uppers91/65536 and615/65536 for degrees0/1. The second exceeds the declared1/16 norm target. Its interior-cell charge dominates, while its endpoint and complete residual charges are small. This is an unresolved requested accuracy, not an invalid source identity or a negative positivity result.

Natural interval evaluation loses correlation in a difference of exponentials and in the sum of source components. Version2 evaluates the smooth source at a midpoint and encloses its actual derivative across the complete cell. It retains the same64 subcells per doubling,128 residual terms,384bits, endpoint caps and target.

Let r_-=T-u,r_+=T+u, B=A0+F(r_-)+F(r_+) and

    k(r)=exp(-r/2)/(1-exp(-2r)),
    k_M(r)=k(r)[1-exp(-2M r)].

The finite geometric sum proves k_M=sum_(k<M)exp(-b_k r). Since F'=-k,

    B'=k(r_-)-k(r_+),
    (A_M p0)'=c0 B',
    (A_M p1)'=c1[B+u B'+r_- k_M(r_-)+r_+ k_M(r_+)].

The p1 identity follows by differentiating the finite residual in equation(3) of the original contract. The derivatives of (1+br)exp(-br)/b² are -r exp(-br); no independent interval variations of its canceling factors are substituted for that identity.

The even and odd pole derivatives are respectively

    hc_coefficient*sinh(u/2),
    -hs_coefficient*cosh(u/2).

A compressed translation that is definitely active on the whole cell contributes its exact affine midpoint value and derivative. A definitely inactive shift contributes zero. Any shift whose endpoint may cross the cell is kept as a separate complete interval hull of zero and its affine image. Its jump is not controlled by a smooth derivative.

For smooth plus definitely active source S, midpoint v and complete interval cell I,

    S(u) lies in S(v)+(I-v)S'(I), u in I.

Adding the ambiguous shift hulls gives a complete cell enclosure of the same finite source A_M+P+K_pole. Equations(2),(4),(5) in [the original contract](supported-coupling-contract-v1.md) still pay the full residual and endpoint source errors. This changes neither the true action nor the accepted error threshold.

A narrower cell range is useful only if the independent consumer verifies the final full L² error. No improved full coupling penalty, positivity sign or practical high-degree cost follows from changing the enclosure organization.
