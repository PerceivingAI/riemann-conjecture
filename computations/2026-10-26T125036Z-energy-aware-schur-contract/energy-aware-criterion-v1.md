# Complete logarithmic-energy Schur criterion

- **Created:** `2026-10-26T12:50:36Z`
- **Last updated:** `2026-10-26T13:09:30Z`
- **Scope:** conditional full low/cross/outside criterion, explicit weighted finite contraction and complete enclosure requirements. No new Weil matrix or positivity sign.

## 1. Source, space and domains

Use C-0107's exact source on H_T=L²(-T,T), T>0, zero extension E_T and unitary Fourier transform with measure dt/(2pi). Let J=F E_T. Put

    A(t)=Re psi(1/4+it/2)-log pi,
    A0=A(0), w(t)=A(t)-A0+1>=1,
    d[f]=integral w(t)|Jf(t)|² dt/(2pi).

The form domain V consists of f in H_T with d[f]<infinity. This form is closed: a Cauchy sequence in its graph norm converges in H_T, its transforms converge in the closed range of J, and multiplication by sqrt(w) is closed. Smooth compactly supported functions lie in V and make it dense. This defines the Fourier-form extension used here, not an identification with every canonical Suzuki operator domain.

Let V_T=P_T+K_pole be the complete bounded signed operator at this fixed support. Include every strict active prime power and the negative odd pole. C-0107 gives on this domain

    q[f]=d[f]+(A0-1)||f||²+<f,L_T f>-d_E[f], L_T>=0.

The original smooth-test source is q_A+<.,V_T .>. No external zero-free or cancellation assumption is added.

Take normalized real Legendre p_j(u)=sqrt((2j+1)/(2T))P_j(u/T),0<=j<N. Write Pi for their orthogonal projection and Q=I-Pi. Each zero-extended p_j is bounded variation. Hence |Jp_j(t)|=O(1/|t|), and C-0103 gives w(t)=O(1+log(1+|t|)). Thus w Jp_j is square integrable. Consequently p_j belongs to the operator domain of D=J* w J, not merely its form domain. Pi preserves V and QV is a closed subspace in the form norm.

Set W=D+(A0-1)I+V_T on these low vectors. The exact finite low and true cross are

    A_low,ij=<p_i,Wp_j>, B e_j=QWp_j.

B is bounded because its domain is finite dimensional and each column is in H_T. Its boundedness is proved here, not inferred from a truncated matrix. For f=p_x+y, p_x=sum x_j p_j,y in QV,

    q[f]=x* A_low x+2Re<y,Bx>+q[y].

A previous bounded-minorant Schur matrix is not A_low or B for this formula. Individual old source components are reusable only after checking identical operator, basis, mass normalization and full error meaning.

## 2. The energy-aware outside reference and its true inverse

Assume a proved all-frequency form inequality at this particular support,

    d_E[f]<=alpha d[f]+beta||f||², 0<=alpha<1,beta>=0.

Let gamma=1-alpha, s=1+beta-A0, and g(t)=gamma w(t)-s. The closed outside reference on QV is

    c[y]=integral g(t)|Jy(t)|²dt/(2pi), q[y]>=c[y].

Suppose c>=delta I with delta>0. Its associated positive self-adjoint operator C on QH_T has bounded inverse. Completing its form square gives

    q[p_x+y]>=x*(A_low-B*C^-1 B)x
                 +||C^(1/2)y+C^(-1/2)Bx||².

This is a sufficient reference criterion. Equality with the actual Weil Schur requires the actual tail, not just this lower reference. Strict positivity of its finite Schur implies positivity on the full form domain. It also gives a positive norm gap, since B is bounded and delta>0. No common gap across supports is required.

Compression cannot be omitted: C is the form compression of the unbounded multiplier g to zero-extended functions supported in time and orthogonal to the low space. It is not multiplication by g on the whole Fourier line, and g is negative at low frequencies in the qualified control. Neither 1/g nor a finite section's inverse may be substituted for C^-1.

## 3. A positive full-frequency weight without solving C

Choose exact m>0 and R>0 with g(R)>=m. Let lambda be a rigorous full low-band leakage upper for Q,

    integral_(|t|<=R)|Jy|²dt/(2pi)<=lambda||y||², 0<=lambda<=1.

C-0104/C-0107 supply lambda=min(1,(2TR/pi)E_N(TR)) when their complete geometric ratio is valid. Define

    h(t)=max(m,g(t)),
    d0=max(0,m-g(0)), epsilon=d0 lambda,
    eta=1-epsilon/m.

The deficit h-g vanishes for |t|>=R and lies between0 and d0 everywhere. If epsilon<m, then for every y in QV,

    c[y]>=integral h|Jy|²-epsilon||y||²
         >=eta integral h|Jy|².

Thus C>=eta H_Q>0, where H_Q is the form compression of h, and C>=eta m I. This retains h(t) growing like gamma log|t| at infinity. R is a leakage-proof anchor, not an operator cutoff. The strict denominator eta>0 must be proved and paid. No frequency band is discarded.

One can alternatively take m=g(R)>0. Then d0=gamma(w(R)-1), and eta m equals the earlier gamma mu_N(R)-s. The exact rational m formulation avoids pretending an uncertain special-function value is an exact serialized scalar. At the already qualified T3/4,N312,alpha1/4,beta873/1024,R256, the published outside1/3 makes m=1/3 a natural fixed floor to qualify. This changes no support, projection or alpha.

## 4. A complete finite weighted Gram upper

A direct dual representative avoids a time-compression shortcut. Define the whole-line functions

    xi_j(t)=A(t)Jp_j(t)+J(V_T p_j)(t).

For y in QV, <y,Be_j>=integral conj(Jy)xi_j dt/(2pi). Each xi_j is in L² by section1. For any fixed finite matrix K, set

    zeta_j=xi_j-sum_k Jp_k K_kj,
    G(K)_ij=integral conj(zeta_i)zeta_j/h dt/(2pi).

The subtraction is legitimate because Jy is orthogonal to every Jp_k. It is NOT a claim that xi_j equals J(Wp_j): the latter includes time compression of the archimedean multiplier. Outside-time components of xi can make this dual upper conservative. No commutation of restriction, projection, multiplier or inverse is assumed.

Weighted Cauchy or direct square completion now gives

    B*C^-1B <= eta^-1 G(K),
    q[p_x+y]>=x*(A_low-eta^-1G(K))x
        +eta integral h|Jy+eta^-1 h^-1 zeta_x|²dt/(2pi).

The square's center need not be a supported-time vector. Minimizing over an enlarged frequency space gives a sufficient upper penalty, not the true inverse or an equality. Therefore

    A_low-eta^-1 G(K)>0

is a complete finite sufficient positivity criterion on the full form domain, including the entire infinite complement. If its lower is sigma>0, a norm gap is at least

    min(sigma/[1+2||G(K)||/(eta² m)], eta m/2)>0.

Indeed ||y||² is at most twice the shifted-square norm divided by eta m, plus2 x*G(K)x/(eta²m). This provides strict positivity without assuming an unknown full-form spectral gap.

## 5. Choose the low subtraction from the weight

There is no need to guess K or enlarge N to choose this dual projection. Define the complete weighted arrays

    M_ij=integral conj(Jp_i)Jp_j/h,
    R_ij=integral conj(Jp_i)xi_j/h,
    H_ij=integral conj(xi_i)xi_j/h.

All integrals use the full real line and measure dt/(2pi). M is strictly positive: any nonzero finite low vector has nonzero Fourier transform in L², and1/h is positive almost everywhere. Then

    G(K)=H-R*K-K*R+K*MK,
    K_opt=M^-1R,
    G_min=H-R*M^-1R,
    G(K)=G_min+(K-K_opt)*M(K-K_opt).

Stars mean adjoints, including on R in R*K. R need not be Hermitian. This is Loewner optimal only within these finite low subtractions for this h and these dual representatives. It is not optimality among all references, projections or outside-time corrections.

An implementation need not trust an approximate inverse or prove it exact. Store any chosen K as exact rational entries and independently enclose G(K) directly. For residual E=R-MK and verified M>=nu I>0,

    G(K)-nu^-1 E*E <=G_min<=G(K).

This brackets the penalty lost by the approximate projection. It does not permit replacing a proven upper by G_min without separately certifying that lower penalty. Rank, denominator and input uncertainty must be paid, not inferred from a solve's residual alone.

## 6. Explicit complete source tails

The finite contraction is not a finite-frequency assertion. Here are usable full-tail bounds, including all signs and mixed products through the combined xi before squaring.

Let C_i bound the total variation of the zero-extended p_i, and D_i that of zero-extended V_T p_i. Then for t!=0,

    |Jp_i(t)|<=C_i/|t|,
    |J(V_Tp_i)(t)|<=D_i/|t|.

For a compact zero-extended BV function, Stieltjes integration by parts gives Jf(t)=(it)^-1 integral exp(-itu)df(u). The endpoint jumps are included in df, so its total variation gives the two displayed bounds directly.

These constants are computable without a derivative norm for the unknown test. For p_i=sum a_k u^k one safe C_i is2|a_0|+4sum_(k>=1)|a_k|T^k. It bounds both endpoint jumps and integral derivative. Interval truncation of a translated compact BV function does not increase total variation: removed variation reaches each new boundary trace and pays its introduced jump. Thus every compressed shift has variation at most C_i. With hc=cosh(u/2),hs=sinh(u/2), one sufficient complete bound is

    D_i=2sum_active d_m C_i
        +2|<hc,p_i>|[4cosh(T/2)-2]
        +2|<hs,p_i>|[4sinh(T/2)].

The signed pole remains exact in xi; the absolute values here bound only omitted Fourier integrals. All mixed arithmetic/pole/archimedean terms remain in H or G(K). Replacing the combined square by a sum of independent term squares is invalid.

For U>=1 put cA=2+log(2pi). C-0103 implies |A(t)|<=log|t|+cA for |t|>=U. Define

    I0=1/U,
    I1=(log U+cA+1)/U,
    I2=[(log U+cA)^2+2(log U+cA)+2]/U.

These are the exact integrals of1,log t+cA,and(log t+cA)^2 against dt/t² over[U,infinity). Both frequency tails, including their1/(2pi) normalization, satisfy entrywise

    |A_low,ij^out| <= C_i(C_j I1+D_j I0)/pi,
    |M_ij^out| <= C_i C_j I0/(pi m),
    |R_ij^out| <= C_i(C_j I1+D_j I0)/(pi m),
    |H_ij^out| <= [C_i C_j I2+(C_i D_j+D_i C_j)I1+D_i D_j I0]/(pi m).

For G(K) directly replace D_i by D_i+sum_k C_k|K_ki| in the H formula. These complete but possibly costly tails do not assert favorable scaling. The bounds tend to zero for each fixed finite N,T,K, so they furnish a genuine finite enclosure operation for any declared positive entry accuracy.

On[-U,U], finite interval enclosures of the integral definitions give convergent Riemann upper/lower sums. The functions are continuous, h>=m, and digamma has no pole on Re z=1/4. A kink in max(m,g) is handled by interval bounds or a certified split, not unsupported analytic quadrature. Exponential polynomial integrals at t0 are entire integrals with removable divided formulas; their zero values must not be evaluated by an interval containing a division by zero. Both analytic tails and interval/quadrature error must enter each source array.

## 7. One-sided finite acceptance and uncertainty

For fixed exact K, suppose complete Hermitian sources give

    ||A_low-A_bar||<=e_A,
    ||G(K)-G_bar||<=e_G,
    eta>=eta_low>0.

Entrywise errors can be converted to operator bounds with a Hermitian row-sum majorant. Then the complete sufficient matrix lower is

    S_lower=A_bar-eta_low^-1 G_bar
                    -(e_A+eta_low^-1 e_G)I.

The factor replacement is valid because the exact G(K) is positive semidefinite. Do not scale an indefinite nominal Gram as though it were exact positive data. Independent exact congruence/Gershgorin or another qualified finite proof of S_lower>0 completes this conditional criterion. Input, quadrature, analytic infinity, outward rounding and physical-mass conversion errors all belong in e_A/e_G. A chosen adaptive quadrature order, a finite inverse or a precision setting is not an error bound.

This contract specifies a complete mathematical acceptance operation, not an implemented research matrix generator or production verifier. No full A_low,M,R,H,G(K) array or S_lower sign is supplied by the present qualification.

## 8. Equivalence, comparison and circularity

The exact finite Schur algebra is the same algebra as C-0093. Reordering identical finite blocks with identical infinite reference cannot strengthen it. The actual change here is the unbounded outside lower c and its positive full-frequency weighted dual upper. Keeping only eta m I would discard that change and return to a scalar inverse penalty.

The scalar-plus-compact theorem C-0108 does not apply to c or h because they grow logarithmically in frequency. This establishes applicability outside that obstruction's premises, not a favorable support law. No estimates for unknown-support alpha,beta, coupling, source cost or working precision have been proved.

A smaller scalar minimum does not determine the weighted penalty. It may be worse on low-frequency coupling and better on sufficiently high-frequency coupling. Extra loss may also enter through the dual representative's outside-time component, finite subtraction or full-tail enclosure. The complete G(K), errors and same-source comparison decide that, not the scalar floor alone. There is no dominance assertion against the older criterion.

Every hypothesis concerns explicit fixed-support source bounds and a finite sufficient sign. Neither all-support Weil positivity nor an RH-level cancellation estimate is assumed. Proving these conditions for an unbounded support-covering family would be an additional mathematical result; it is not supplied here. The present claim is the conditional criterion and its complete enclosure/projection rules, not a new positivity theorem, support extension, cost advantage, literature originality or admission.
