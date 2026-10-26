# Variable compact complement, truncation and representation work

- **Created:** `2026-10-26T02:04:35Z`
- **Last updated:** `2026-10-26T02:21:56Z`
- **Scope:** sufficient error requirements for the existing positive arithmetic-reference construction, not a new finite sign or an all-support positivity proof

## 1. Full reference and compact operator

Fix T>0 and a>=0. Include every prime power with log(m)<2T, with one-sided coefficient d_m=Lambda(m)/sqrt(m). Let P=-sum d_m(U_log(m)+U_-log(m)) on zero-extended L²(-T,T). Choose a proved norm upper p>=||P|| and m=a-p>0. Per-support m is allowed. Let Omega have A(Omega)>=a, where A(t)=Re psi(1/4+it/2)-log pi. C-0103 implies Omega>4 for this exterior target.

The qualified smooth-source identity is Q_W[f]=<f,H0 f> plus the complete exterior integral of (A-a)|hat f|²/(2pi). Here H0=aI+P+K; K contains both signed rank-two pole sectors and the entire finite band. Retain the negative odd pole. No pole constraints or omitted arithmetic terms may be used to reduce this reference. The smooth identity remains the Suzuki source premise. No equality of all canonical closed operator domains is asserted.

Set c=T Omega, beta=2T Omega/pi, H=4T exp(T), and

    W=max(|A(0)-a|, |A(Omega)-a|).

Monotonicity of A makes W a bound on the entire real band. It is a variable quantity, not the old constant9. Write C0=|A(0)|. Since Omega>4, C-0103 gives W<=a+C0+log(Omega)+1/8. Thus W=O(a+log Omega+1), but actual finite calculations should use the sharper endpoint bound.

For N>=1 retain ordinary Legendre degrees0,...,N-1, with physical mass D_j=2/(2j+1). Let Pi be the orthogonal projection and Q=I-Pi. Define

    E_N(z)=(2N+1)z^(2N)/[(2N+1)!!]^2
           /[1-z²/((2N+1)(2N+3))].

Require both geometric ratios below1. The Rodrigues entire plane-wave bound and exact signed-pole argument used in C-0094/C-0098 apply at every finite T with these variables. No local Taylor-kernel cutoff is being extended. They give the full bounds

    kappa=W beta E_N(c)+H E_N(T/2),
    eta=W sqrt(beta E_N(c))+H sqrt(E_N(T/2)),
    ||QKQ||<=kappa,  ||QK||<=eta.

The second estimate is one-sided. Its H bound treats each pole rank-one term with the correct sign before taking absolute norms; it does not remove the odd negative term. The absolute pole envelopes hold for every finite T, not just the old bounded window.

For completeness, Rodrigues gives |integral_-1^1 exp(izx)P_n(x)dx|<=2|z|^n/(2n+1)!! for real z. The physical tail mass is consequently at most2T times the sum of (2n+1)|z|^(2n)/[(2n+1)!!]^2. Successive terms have ratio z²/[(2n+1)(2n+3)], decreasing in n; summing the geometric majorant proves the displayed E_N. For complex exponential exp(su), the same integration-by-parts proof introduces exp(T|Re s|), so the squared tail bound is2T exp(2T|Re s|)E_N(T|s|).

Plancherel gives ||F_Omega||<=1, while integrating the complete real plane-wave tail gives ||F_Omega Q||²<=||F_Omega Q||_HS²<=beta E_N(c). These prove the double and one-sided band bounds separately. For h_c=cosh(u/2), h_s=sinh(u/2), the actual pole is2 h_c h_c* -2 h_s h_s*. The parallelogram identity on exp(±u/2) bounds the sum of the two squared tail norms by2T exp(T)E_N(T/2), and the sum of their full squared norms by2T exp(T). The signed rank-one triangle and Cauchy inequalities then give H E_N(T/2) and H sqrt(E_N(T/2)). Thus both signs and the full infinite complement remain accounted for.

## 2. Denominator, combined mixed Gram and actual source uncertainty

If d=m-kappa>0, then QH0Q>=dI. The combined arithmetic tail Gram GP=Pi P Q P Pi includes every mixed prime-power product. The complete Gram satisfies

    Pi(P+K)Q(P+K)Pi <= GP+epsilon I,
    epsilon=2p eta+eta².

This follows from the norm of Pi P Q being at most p and of QK being at most eta; no arithmetic/compact cross term is discarded. In ordinary Legendre form coordinates the allowance is epsilon D.

Let A_low=Pi H0 Pi. Suppose genuine one-sided ordered bounds obey

    0<=A_low-A_-<=ell_A D,
    0<=G_+-GP<=ell_G D.

These are complete source/order-loss hypotheses, not just midpoint radii or selected working precisions. Then the actual sufficient finite lower is

    S_-=A_- -(G_++epsilon D)/d.

For the ideal comparison S_star=A_low-GP/m, using 0<=GP<=p²D gives

    0<=S_star-S_-
      <=[ell_A+ell_G/d+epsilon/d+p² kappa/(d m)]D.

S_star itself is not the full inverse Schur and its sign is not presumed. A declared error tolerance in this display is not evidence of a positive low gap. Finite positivity of both complete parity blocks remains a separate obligation.

For GP construction from independently enclosed low P and P², if the physical-mass operator uncertainties before publication/order conversion are u and v, respectively, the product error is at most v+2p u+u². This is the expansion of (P_low+Delta)²-P_low² in mass-normalized coordinates. It needs no commutation and does not replace the full combined square by a sum of separate squares. Final rounding and interval-to-Loewner losses must still be added. See the separate [source map](quadrature-source-map-v1.md) for those budgets and numerical-width limits.

The source map bounds errors about a specified center. Turning a symmetric center error radius r into a Loewner lower or upper generally doubles the worst true-to-ordered loss. For entry radii r_ij, put s_i=sum_j r_ij. The actual row-sum lower is C-diag(s_i); a valid true-to-lower loss in mass units is delta_normrow+delta_row, with the two quantities defined in the source map. For the analytic band radii E sqrt(D_i D_j), this is F_N E, where

    F_N=max_parity[k+max_i sum_(j in parity) sqrt(D_j/D_i)].

This replaces the fixed470 conversion. If the analytic operator correlation is retained outside the entry box, centering and subtracting E D instead gives true-to-lower loss at most2E. Do not compare these differently represented budgets without that factor. For publication grid2^(-b), a sufficient true-to-ordered allowance is k(2N-1)2^(-b), twice the source map's center-radius publication bound. Thus b>=ceil(log2(k(2N-1)/ell_pub)) is sufficient for a declared one-sided publication loss ell_pub. Any extra rounding of separately serialized analytic radii must also be counted.

## 3. An explicit sufficient dimension for a declared compact loss

The geometric prerequisite alone,

    N>sqrt((T Omega)²+1)/2-1,

does not say that the compact error is small. The following policy is sufficient and deliberately coarse.

For z>=0 and integer N>=max(1,3z), use (2N+1)!!>=2^N N!, N!>=(N/e)^N, e<3 and (2N+1)<=2^(N+1). The geometric ratio is at most1/36, hence

    E_N(z)<= (36/35)(2N+1)4^(-N) <3*2^(-N).

Choose a compact Schur-loss tolerance delta>0 and theta in(0,1), without assuming either equals an unknown gap. Set

    R=delta(1-theta)m/2,
    eta0=R/[sqrt(p²+R)+p],
    kappa0=min(theta m, delta(1-theta)m²/(2p²))   if p>0,
    kappa0=theta m                              if p=0,
    L=W beta+H,  J=W sqrt(beta)+H,
    xi=min(kappa0/L, (eta0/J)²).

All denominators here are positive. A sufficient integer choice is

    N>=max(1, ceil(3 max(c,T/2)), ceil(log2(3/xi))).

Use certified upper rational bounds when publishing integer requirements; never infer a boundary decision from an Arb midpoint. This yields kappa<=kappa0, eta<=eta0, d>=(1-theta)m>0 and

    epsilon/d+p² kappa/(d m)<=delta.

For p=0 the second term is zero. The cancellation-free eta0 formula is exactly sqrt(p²+R)-p. The policy supplies a complete compact/mixed target without selecting a new support, making a low matrix or proving positivity. Its conservative factor3 in N is not a necessary dimension.

For numerical errors, one may independently prescribe ell_A<=delta_A and ell_G<=(1-theta)m delta_G, yielding total loss at most delta+delta_A+delta_G. Band quadrature and all conversion losses belong in ell_A. Small reserves require smaller errors and can increase N; there is no uniform-reserve assumption.

## 4. Active arithmetic and exact domain counts

Let J_ar(T) count all strictly active prime powers and X=exp(2T). Using C-0102's published psi bounds, for T>=7/2,

    J_ar(T) >= (9/10)exp(2T-1/2)/(2T).

Indeed all m<=exp(2T-1/2) are strictly active and each Lambda(m)<=2T. For an upper bound, split primes at sqrt(X). Larger primes each cost at least T in psi(X); smaller primes number at most sqrt(X). For each proper exponent k>=2 there are at most sqrt(X) candidate bases. There are at most floor(2T/log2)-1 such exponents. Thus

    J_ar(T) <= (21/20)exp(2T)/T +(2T/log2)exp(T),

and J_ar(T)=Theta(exp(2T)/T). This counts actual active arithmetic terms, not a guessed support grid or a prime-only truncation.

There are2J_ar signed single-image domains. For alpha,beta in the signed shifts, their image-product domain is

    I_(alpha,beta)=[-1,1] intersect[-1-alpha,1-alpha] intersect[-1-beta,1-beta].

Its length is max(0,2-[max(0,alpha,beta)-min(0,alpha,beta)]). Every same-sign ordered pair has positive length. A mixed-sign pair is nonempty exactly when log(mn)<2T. Therefore the exact ordered nonempty square-domain count is

    D2=2J_ar²+2#{(m,n) active ordered pairs: log(mn)<2T},
    2J_ar²<=D2<=4J_ar².

Equality of the threshold means a zero-measure domain and is excluded. Actual interval ordering/activation still needs rigorous certified comparisons or symbolic equality handling.

The combined-image partition has at most2J_ar distinct interior breakpoints at ±(1-log(m)/T), and at least J_ar. If J_ar>0, its total strict cell count C_all lies between J_ar+1 and2J_ar+1. The only possible empty-image cell is the central gap when log2/T>1; discard that one for the nonempty-cell count C. In the large-support range T>=7/2 there is no such gap, so C=C_all=Theta(J_ar). The old two cases have C=4/7 and D2=8/20, respectively. These domain formulas describe Gram intersections, not literal shift-composition indices.

## 5. Representation-specific data and dense contraction shapes

Put n_even=ceil(N/2), n_odd=floor(N/2), B2=n_even²+n_odd² and B3=n_even³+n_odd³. Six serialized full triangles, retaining structural parity-zero slots as the existing format does, contain exactly

    6N(N+1)/2=3N(N+1) interval slots.

For arithmetic Gauss order qA>=N, piecewise degree-(N-1) image products have exact mathematical quadrature. The combined-image organization has the classical dense contraction-volume proxy

    V_source=2C B2 qA +B2 L_panels q_frequency+B3.

The direct-image independent organization has

    V_audit=(2J_ar+D2)N² qA_audit +N² L_panels q_frequency_audit+N³.

Choosing qA_audit=N+1 is the old independent policy, not a universal necessary order. These count contraction dimensions only. They exclude translation/polynomial setup, special-function vectors, interval precision, node generation, assembly, publication, serialization, exact witness search/replay and native algorithm details. Pair domains are sequential operations, not equally many simultaneously retained dense matrices. No runtime, peak RAM or bit-complexity law is inferred.

Continuing to use this geometric tail formula forces N>c/2-1. For c>=4 it forces N>c/4, and retaining six full triangles consequently needs more than3c²/16 slots. Together with C-0102/C-0103 this is a double-exponential-in-T dimension and quadratic-payload obligation for this particular enclosure/serialization strategy. It is not a lower bound on the minimum positive Weil dimension, other bases/representations, or an analytical family proof.

The sufficient dimension policy is O(c+logarithmic tolerance/reserve factors) when those logarithmic factors are O(c). No such assumption may be made about an unknown positive low gap. The variable quadrature/anchor requirements and measured numerical-width condition remain separate. No finite-support progression, global positivity, practical speed/RAM forecast, general Fourier no-go, theorem admission or literature-originality claim follows from this accounting.
