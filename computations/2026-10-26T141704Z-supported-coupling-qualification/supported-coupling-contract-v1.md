# Supported source action and a complete energy-weighted coupling bound

- **Created:** `2026-10-26T14:17:04Z`
- **Last updated:** `2026-10-26T14:17:04Z`
- **Scope:** explicit time-supported polynomial source, complete L² approximation error, energy-weighted inverse penalty and finite/infinite acceptance rules. No full positivity matrix or new support.

## 1. Keep the physical source before taking a Fourier dual

Use C-0107/C-0112's H_T, zero extension E_T, J=F E_T, physical measure du and Fourier measure dt/(2pi). Write V_T=P_T+K_pole and W=A_T+V_T, where A_T=J* A(t)J on the low polynomial vectors. The full shifted logarithmic reference, its form domain and positive Q-tail lower C>=eta H_Q are exactly those qualified in C-0112. At the existing control their premises are C-0110/C-0111; none is promoted to a support-uniform assertion.

The genuine low source columns are f_j=Wp_j in H_T, with true cross B e_j=Qf_j. Low Legendre vectors belong to the operator domain by C-0112's BV/Fourier argument. Thus Jf_j is an actual transform of supported output. It is not A(t)Jp_j+J(V_Tp_j), which also retains outside-time archimedean output.

For every finite matrix K set

    z_j=f_j-sum_k p_k K_kj,
    G_s(K)_ij=integral conj(Jz_i)Jz_j/h dt/(2pi).

Orthogonality of Q to the low space and the same weighted square completion give

    B*C^-1B<=eta^-1G_s(K),
    A_low-eta^-1G_s(K)>0 implies full Fourier-form positivity.

This changes the dual representative, not the finite Schur algebra. No compression, projection or inverse is interchanged. C-0093's matched-reference equivalence remains valid.

The outside-time witness in C-0113 pairs to zero with every Jz_j because z_j really is supported. This removes that specific lower-bound mechanism. It proves neither positivity of the new sufficient matrix nor a better total penalty; weighted Fourier norms do not obey an assumed monotonicity under time restriction.

## 2. Explicit supported archimedean action on polynomials

Let L=2T, b_k=2k+1/2, and

    k(r)=exp(-r/2)/(1-exp(-2r)), r>0,
    F(r)=sum_(k>=0)exp(-b_k r)/b_k
        =atanh(exp(-r/2))+atan(exp(-r/2)).

The last equality follows by adding the elementary atanh/atan power series: their sum is2sum z^(4k+1)/(4k+1). No new external formula is presumed. The C-0113 digamma-resolvent identity gives, for every polynomial p and almost every -T<u<T,

    A_Tp(u)=p(u)[A0+F(T+u)+F(T-u)]+R_p(u),
    R_p(u)=integral_(-T,T) k(|u-v|)[p(u)-p(v)]dv.       (1)

Each finite resolvent term equals its boundary exponential contribution plus the difference integral. The latter is integrable at u=v because |p(u)-p(v)|<=D|u-v|, D>=||p'||_infinity. The boundary terms are logarithmic and square integrable. Convergence from the full multiplier in L² identifies(1) with the time-compressed source rather than a different finite-part convention. No delta or endpoint term is dropped.

For M>=1 let R_p,M use only rates b_0 through b_(M-1). Positive kernel tails give

    |R_p-R_p,M|<=2D/(4M-3).                         (2)

Indeed each side of the difference integral is bounded by D integral_0^infinity r exp(-b_k r)dr=D/b_k², and sum_(k>=M)b_k^-2<=1/(4M-3). This is an all-interior-point upper, not an observed contraction. For the constant polynomial D=0, the boundary-log formula is exact without any residual sum.

For higher polynomials the difference is a finite sum of powers of r on the two sides. Each term is explicitly computable through

    integral_0^d r^ell exp(-b r)dr
      =ell! b^(-ell-1)[1-exp(-bd)sum_(q=0)^ell (bd)^q/q!].

The formula at zero is its entire integral limit. At high degree it can be poorly conditioned; no cheap target-scale operation is inferred from its existence.

For the first odd mode p1(u)=c u,c=sqrt(3/L)/T, the finite difference term simplifies to

    R_p1,M(u)=c sum_(k<M)
       [(1+b_k(T-u))exp(-b_k(T-u))
        -(1+b_k(T+u))exp(-b_k(T+u))]/b_k².           (3)

The independent reconstruction may instead subtract the two positive incomplete moments from the integral formula. Both have the same complete remainder(2).

## 3. Arithmetic, pole and physical normalization

Use normalized p0=1/sqrt(L),p1=sqrt(3/L)u/T, and the established Legendre normalization for general low modes. Every active prime power with log(m)<L contributes

    P_Tp(u)=-sum d_m[p(u-log m)1_I(u-log m)
                        +p(u+log m)1_I(u+log m)].

This is the full signed combined operator, including Lambda(4)=log2 in the current2/3/4 window. A cell overlapping an uncertain shift endpoint must include both possible values or pay a certified uncertainty-slab error; endpoints cannot be rounded into a chosen branch silently.

Retain K_pole p=2hc<hc,p>-2hs<hs,p>. In particular

    K_pole p0=2hc *4sinh(T/2)/sqrt(L),
    K_pole p1=-2hs*c[4T cosh(T/2)-8sinh(T/2)].

The negative odd pole is evaluated explicitly, not discarded. Both source sectors are real with the parity of p_j, since every source component commutes with reflection. Symmetry may reduce work only after that identity is established.

## 4. Complete endpoint error, without falsely assigning BV to f_j

The true columns usually have logarithmic endpoint singularities. Do not apply the old BV source-tail bound to them.

For0<r<=L define H(r)=integral_0^1 exp(-rs/2)ds. Then

    F(r)+(1/2)log r
      =(1/2)log[2(1+exp(-r/2))/H(r)]+atan(exp(-r/2))
      <=B_L=log2+L/4+pi/4.

The identity has a removable limit at zero, log2+pi/4. The upper follows from H>=exp(-L/2),1+exp(-r/2)<=2 and atan<=pi/4. At small r the singular piece remains explicit; finite divided formulas must not evaluate through an interval containing zero.

Take P>=||p||_infinity,D>=||p'||_infinity and V>=||V_Tp||_infinity. One fully explicit V is

    V=2P sum_active d_m
       +2cosh(T/2)|<hc,p>|+2sinh(T/2)|<hs,p>|.

Since k(r)<=exp(3L/2)/(2r) for r<=L,

    ||R_p||_infinity<=D L exp(3L/2).

For an endpoint cap of width0<delta<=min(1,L/2), r is distance to its endpoint. Hence

    |Wp(u)|<=a log(1/r)+b,
    a=P/2,
    b=P[|A0|+B_L+F(L/2)]+D L exp(3L/2)+V.

Approximating the source by zero on both caps has squared L² error at most

    E_cap=2delta[a²(ell²+2ell+2)+2ab(ell+1)+b²],
    ell=log(1/delta).                                (4)

This includes both endpoints and tends to zero. It is a source approximation charge, not deletion of the physical test domain.

## 5. Constructive supported approximation on the remaining interval

Choose a finite exact-rational partition of[-T+delta,T-delta]. Evaluate(1) with R_p,M, complete arithmetic and pole on each closed cell by interval arithmetic, including every jump uncertainty. Store an exact rational coefficient q on each cell. If the interval value differs from q by at most r_cell, put

    E_cells=sum width*r_cell²,
    e_p²=E_cap+[sqrt(E_cells)+sqrt(L)*2D/(4M-3)]².     (5)

The separate cap and interior errors are disjoint; the finite resolvent error on the interior is completed by Minkowski. Thus the step function Z_p,zero outside its stored cells, satisfies ||Wp-Z_p||<=e_p on the entire physical interval. Coefficient rounding and Arb input uncertainty belong in r_cell. No sample values are substituted for full-cell ranges.

For columns j use e²=sum_j e_j². Then ||W Pi-Z||<=e as a map from normalized low coefficients into H_T. A polynomial-on-cell approximation has the same argument with its own rigorous range error; step cells already furnish a complete operation. Refining the cap, residual sum and interior cells can reach any fixed positive source accuracy at fixed finite degree. This is not a uniform degree/support cost bound.

## 6. Retain the energy weight and pay source error

For exact finite K define tilde_z_j=Z_j-sum p_k K_kj, and let tilde_G be its full Gram with weight1/h. Because h>=m,

    ||h^(-1/2)J(W Pi-Z)||<=e/sqrt(m)=a_err.

For a verified rho>=sqrt(||tilde_G||),

    G_s(K)<=tilde_G+(2rho*a_err+a_err²)I.             (6)

Alternatively any tau>0 gives G_s(K)<=(1+tau)tilde_G+(1+1/tau)e²/m I. The scalar1/m is used only for the controlled source remainder, not to replace the full coupling weight.

If complete finite integration gives ||tilde_G-G_bar||<=e_G, a verified rho can be sqrt(||G_bar||+e_G). The low source A_low can be enclosed from <p_i,Z_j>; Hermitianizing that approximation does not enlarge its error e. Include its coefficient/integration uncertainty in e_A. For eta>=eta_low>0, the full sufficient finite lower is

    S_lower=A_bar-eta_low^-1 G_bar
       -[e_A+eta_low^-1(e_G+2rho e/sqrt(m)+e²/m)]I.    (7)

Scaling uses positivity of the exact Gram before its nominal approximation, as in C-0112. A separately verified positive S_lower gives the full-form implication and norm-gap argument there. No finite Schur sign or inverse is assumed by these error estimates.

Weighted low-subtraction optimization has the same M,R,H identities as C-0112 but uses the supported columns. Their source errors and conditioning must be independently enclosed. An old positive array or an old optimal K is not interchangeable input.

## 7. Full Fourier enclosure of the approximant

The step approximant is BV even though the true column is not. For V_j>=TV(E_T tilde_z_j),

    |J tilde_z_j(t)|<=V_j/|t|.

Since h is even/increasing, both omitted Fourier tails obey the complete matrix upper

    integral_(|t|>U) (J tilde_z)^*(J tilde_z)/h dt/(2pi)
        <=[sum_j V_j²/(pi U h(U))]I.                 (8)

Use a positive lower enclosure for h(U). Low-polynomial subtraction contributes at most sum_k |K_kj|TV(E_Tp_k) to V_j. The full tail is paid, not replaced by zero. Keeping h(U), and h(t) in the finite integrals, retains logarithmic energy.

On[-U,U] each Fourier step transform is an exact finite exponential integral. At zero use its entire moment limit; for an interval containing zero use a convergent entire series with a proved remainder. Interval Riemann/Darboux bounds or qualified quadrature cover every frequency cell and any kink in h. Positivity of h>=m prevents an unsupported denominator crossing. Finite integral, source error(6), Fourier infinity(8), physical mass and outward rounding all enter(7).

A large variation charge or finite-band integration requirement is a genuine cost concern, not a reason to suppress the tail. Formula(8) tends to zero at fixed approximant, so this is an explicit finite acceptance operation rather than an uncomputed compressed inverse.

## 8. Declared qualification and evidence limits

The bounded numerical operation constructs p0 and p1 supported approximants only at existing T3/4. Both parity sectors, exact source jumps, graded endpoint cells, coefficient rounding, cap and residual errors are exercised. The source uses128 residual terms and384bits; a separate512-bit consumer reconstructs all cells and published bounds. The declared individual L² accuracy is1/16. No full low source or Schur positivity matrix is generated.

The finite Fourier controls and complete analytic tail budget check the actual approximant, not a proposed future source. The p0 mean is independently compared with the exact positive-series full physical low entry used in C-0113. Exact non-Weil algebra controls exercise the source-to-Gram error and one-sided acceptance inequalities. None proves a new actual full coupling penalty positive.

The outcome qualifies the explicit operation and its source/error contract if the stated accuracy and independent checks succeed. It does not establish full-matrix usefulness, comparative advantage, a support extension, practical high-degree cost, literature originality or production admission. C-0113 still rejects the old representative. Removing that one witness is not the acceptance condition for this qualification or a claim of all-support positivity.
