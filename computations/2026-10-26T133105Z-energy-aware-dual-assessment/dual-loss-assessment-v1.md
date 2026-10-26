# Outside-time loss in the whole-line dual criterion

- **Created:** `2026-10-26T13:31:05Z`
- **Last updated:** `2026-10-26T13:43:38Z`
- **Scope:** an actual low-mode necessary condition for C-0112's whole-line dual Gram, parameter/cost laws, and a declared existing-case qualification. No full Weil matrix or new support.

## 1. A coupling direction invisible to every low subtraction

Use exactly C-0112's physical space, source and Fourier normalization. Put L=2T, and define two unit vectors on the full time line,

    p(u)=L^(-1/2) 1_(-T,T)(u),
    r(u)=L^(-1/2) 1_(T,3T)(u).

The first is the normalized low Legendre mode p0. The second is a dual witness outside the physical interval, not a proposed Weil test on H_T. Their supports are disjoint up to a null endpoint. They are BV and have finite logarithmic energy. Since r is a translate of p, their Fourier magnitudes agree.

For every low dimension N>=1 and every finite low subtraction K in C-0112,

    zeta_0=A(t)Jp+J(V_Tp)-sum_(j<N)Jp_j K_j0.

Both latter terms are transforms of functions supported in[-T,T]. Therefore

    <Fr,zeta_0>=<Fr,A Jp>.

This component is independent of K, N and the optimal weighted projection. Even allowing any supported-time low subtraction cannot remove it. Weighted Cauchy gives the necessary penalty lower

    G(K)_00 >= |<Fr,A Jp>|² / integral h|Fr|² dt/(2pi).

This is a lower on the actually defined complete Gram, not an upper inferred from a finite-frequency sample. It remains present because the chosen xi is a whole-line representative rather than J(Wp).

## 2. Exact archimedean coupling and physical low entry

Let a_k=k+1/4 and b_k=2a_k=2k+1/2. The positive digamma-difference series used in C-0110/C-0112 is

    A(t)-A0=sum_(k>=0) t²/[a_k(t²+4a_k²)].

Each summand's time operator is a_k^-1 I minus convolution by exp(-b_k|u|), because the Fourier transform of that exponential is2b_k/(t²+b_k²). On the disjoint supports the identity term is zero. Integration of the two adjacent boxes gives

    <Fr,A Jp>=-I(T),
    I(T)=L^-1 sum_(k>=0) (1-exp(-b_k L))²/b_k² >0.

The series is absolutely convergent. Equivalently the off-diagonal archimedean kernel is -exp(-|u-v|/2)/(1-exp(-2|u-v|)). The shared corner singularity is integrable in the double integral. The series proof avoids treating a distributional diagonal as an ordinary kernel. Partial multiplier sums converge on p in L² because |partial(A-A0)|<=A-A0 and (A-A0)Jp is square integrable. This justifies the pairings and limit, not merely a formal kernel identity.

For the physical source q=q_A+P+K_pole the exact constant low entry is

    a(T)=q[p]
        =A0+(2/L)sum_(k>=0)(1-exp(-b_k L))/b_k²
          +32sinh²(T/2)/L
          -2sum_active d_m*(1-log(m)/L), d_m=Lambda(m)/sqrt(m).

Every strict active prime power is present. The odd pole is exactly zero on this even p, not omitted from a general operator. The even pole coefficient follows from integral cosh(u/2)du=4sinh(T/2). No finite bounded-minorant low entry is substituted for this full Fourier-form entry.

For any truncation M>=1, the omitted positive sums obey

    0<=I-I_M<=1/[L(4M-3)],
    0<=q_A-q_A,M<=2/[L(4M-3)].

Indeed sum_(k>=M)b_k^-2<=integral_(M-1)^infinity (2x+1/2)^-2 dx=1/(4M-3). Thus the actual low entry and cross coupling have complete deterministic enclosures.

A separate audit can sharpen both tails from below using sum_(k>=M)b_k^-2>=1/(4M+1), multiplying by the endpoint factors1-exp(-b_M L), squared for I. This is not required by the producer and gives independent narrower source enclosures.

## 3. A uniform upper for the dual witness energy

C-0112's g simplifies exactly to

    g=A-alpha w-beta<=A,
    h=max(m,g)<=max(m,A), 0<=alpha<1,beta>=0,m>0.

This bound holds for every allowed relative-bound pair, not just alpha1/4. C-0103 proves A(4)<0 and A is even/increasing. Thus h=m on |t|<=4. For t>=4,

    0<=h(t)-m<=A(t)-A(4)
       <=log(t/4)+2/t²+2/16
       <=log(t/4)+1/4.

The first equality h=m on the band follows from g<=A<0<m. The elementary box transform obeys |Fr(t)|²<=4/(L t²). Including both frequency tails with dt/(2pi) gives

    integral h|Fr|² <= m+C(T),
    C(T)=5/(4pi L)=5/(8pi T).

Here integral_4^infinity log(t/4)/t² dt=1/4 and integral_4^infinity (1/4)/t² dt=1/16. The bound contains the entire frequency line; it is not a quadrature approximation. It deliberately uses a conservative uniform upper, so a failure it proves is not caused by optimism about high frequencies.

Consequently, for every K,N containing p0, and every qualified0<eta<=1,

    [A_low-eta^-1G(K)]_00
       <=a(T)-I(T)²/[m+C(T)].                 (1)

A strict negative upper on the right rejects the exact sufficient matrix even at K_opt, zero source error and perfect arithmetic. Projection enlargement at fixed h, more precision and tighter quadrature cannot fix it. This is not a negative direction of the actual Weil form or of the genuine compressed-reference Schur.

If a(T)>0, strict positivity of this particular matrix necessarily requires

    m>I(T)²/a(T)-C(T).                       (2)

If a(T)<=0 it cannot have a strictly positive finite Schur on this vector. No sign of a(T) at unexamined supports is assumed.

## 4. What raising the floor costs in this recipe

Positive-weight qualification requires g(R)>=m. Put gamma=1-alpha and

    b_eff=beta+alpha(1-A0),
    g(t)=gamma A(t)-b_eff.

Therefore A(R)>=(m+b_eff)/gamma. C-0103's inverse bracket yields the necessary

    R>=2pi exp((m+b_eff)/gamma-1/8).          (3)

Since b_eff>=0 and gamma<=1, the universal weaker necessary bound is R>=2pi exp(m-1/8). Its hypotheses hold because A0<1 and m>0. The geometric leakage bound used in C-0112 requires

    (TR)²< (2N+1)(2N+3)<(2N+2)²,
    N>TR/2-1.                               (4)

This is a necessary dimension condition for that geometric recipe, not for all ways to bound leakage or all proof systems. Combining a certified lower from(2) with(3)/(4) quantifies the price of trying to repair this outside-time penalty by a larger positive floor. It is not a hardware timeout or extrapolated matrix benchmark.

A sufficient conditional policy is also explicit. Choose R=2pi exp((m+b_eff)/gamma+1/8), choose a reserve0<theta<1, and set d0=max(0,m-g(0)). For d0>0 take integer

    N>=max(ceil(3TR),4,2ceil(log2(max(1,d0/(theta m))))).

C-0104 gives lambda<=(2N/pi)2^(-N)<=2^(-N/2), so epsilon<=theta m and eta>=1-theta. The middle inequality uses N<=2^(N/2) for integers N>=4 and2/pi<1. If d0=0 no leakage payment is needed. This is a conditional upper policy of order T exp((m+b_eff)/gamma)+log(max(1,d0/(theta m))). Neither useful alpha,beta scaling nor full low positivity at new supports is proved by it.

## 5. Conditioning, full source error and work

C-0112 has a complete but not cost-free finite source operation. For its weighted low mass M, h>=m gives M<=m^-1 I. Let C_j be the qualified BV constants of its basis and S_C=sum C_j². The full high-frequency low-space mass is at most S_C/(pi U). Since h is even/increasing, for S_C/(pi U)<1,

    M >=[1-S_C/(pi U)]/h(U) I.

This follows by Cauchy on sum x_j Jp_j, integrating the complete Fourier tail, then retaining the complementary band with1/h>=1/h(U). It is a sufficient conditioning bound; coarse BV constants can make it poor. The actual condition number is not inferred from a solve or a precision setting.

The source-array omitted tails have the C-0112 I0/I1/I2 bounds, with constants depending on T,N,K and the complete arithmetic/pole operation. The weighted contraction still needs dense finite arrays if implemented in that representation. Their entry count is quadratic in N, and the old finite contraction algebra does not supply a lower-cost theorem. Working precision and useful total errors depend on the actual matrix margins. There is no proved favorable support law for them.

Most importantly, all honest one-sided source errors lower the acceptance matrix. They cannot repair a strict negative exact upper established by(1). The same applies to the optimal finite low subtraction because the witness annihilates every such subtraction. A negative qualification here therefore identifies a representation/coupling loss before error-enclosure or performance investment.

## 6. Declared fixed-case assessment and scope

The separate declared controls evaluate only the already accepted T3/4 source, p0 and this adjacent outside box. No new support, dimension grid, low source array or eigenvector is generated. The producer uses64 positive series terms at384bits; an independent128-term512-bit reconstruction with two-sided tails checks the actual source intervals and published necessary/negative bounds. Their exact inputs and publication rules are retained separately.

The current C-0112 floor m1/3 is tested through(1), and a repair lower through(2) is reported together with universal and fixed alpha1/4,beta873/1024 dimension laws. A negative result would reject this particular whole-line dual contraction, not C-0110's discrepancy inequality, C-0111's positive outside bound, C-0112's conditional theorem, the true compressed energy inverse or every energy-aware method. Those distinctions are part of the conclusion, not a weakened rejection condition.
