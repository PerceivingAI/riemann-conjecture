# Reusing the exact harmonic cancellation and full residual range

- **Created:** 2026-10-26T17:42:37Z
- **Last updated:** 2026-10-26T17:42:37Z
- **Scope:** Existing T3/4,N312. Consequence of existing source/domain theorems, not a new residual method or positivity claim.

C-0063 gives W=J+V+P+R-c_T I after the unitary physical scaling. J is the Legendre harmonic-number diagonal and V(u)=-log(1-(u/T)²)/2. R includes the full even real kernel AND the signed polar rank two, as in C-0095. It is not permissible to add the pole twice. Polynomial source/domain membership is already proved there. Since both J and c_TI preserve the finite low space,

    Q_N W Pi_N=Q_N(V+P+R)Pi_N.

This exact identity removes the degree-growing regular-difference evaluation from the cross construction. It does not remove V's logarithmic endpoints, any active arithmetic term or the low R block. The original direct source formula stays valid; its uniform-derivative remainder floor is not a necessary source cost.

C-0095 supplies a FULL ONE-SIDED operator bound, not an evaluated column or double-tail bound. At T3/4, C(T)=333/1024, N(N+1)=97656 and z=T/2=3/8. The geometric ratio z²/((2N+1)(2N+3)) is below1/2. Even dropping the positive double-factorial denominator gives

    E_N(z)<1250*(3/8)^624<10^-250.

The elementary bounds exp(3/4)<3 and sinh(3/4)<2 imply4sqrt(T exp(T)sinh(T))<16. Thus the entire signed-pole one-sided charge is below10^-120, and

    ||Q312 R||<=333/(1024*312*313)+10^-120<1/300000.

Consequently the true FULL finite-to-infinite map B differs from Q312(V+P)Pi312 by operator norm less than1/300000, simultaneously on every low vector. There is no sqrt312 multiplication because this is an operator norm. Its weighted source-map error is below sqrt3/300000 at floor1/3. This is an already justified reuse bound, not freshly reconstructed residual matrices.

What remains is useful complete weighted V/P coupling on the entire low space, its source/projection/error work, and the actual low Weil block including R. The old bounded-minorant A/GP arrays cannot substitute for them. No full source is generated here and no ordering between complete sufficient criteria, global efficiency, extension or new full positivity follows. The companion exact control executes the rational thresholds and elementary prefactors; the full operator theorem remains the registered C-0095 premise.
