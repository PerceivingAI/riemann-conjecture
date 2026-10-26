# Complete supported weighted-penalty comparison

- **Created:** 2026-10-26T17:17:55Z
- **Last updated:** 2026-10-26T17:17:55Z
- **Scope:** Existing physical T3/4, Q312, actual constant/first-odd source. No full low-space sign.

## 1. Identical physical source and different references

Reuse C-0114's independently accepted full supported source approximants Z_j and errors e_j. Their complete arithmetic2/3/4, negative odd pole, endpoint logs and infinite residual remain paid. No old bounded-minorant array is a new actual Weil source. Let f_j=Wp_j, B_j=Q312 f_j and A_j=<p_j,f_j>. C-0112/C-0114 give the true reference-penalty upper eta^-1 integral |J B_j|²/h, with h=max(1/3,g), gamma3/4, beta873/1024 and eta>=1-9e-49. This uses supported B_j, not A(t)Jp_j on the whole line.

C-0099/C-0100 imply the actual Weil tail is at least d_old=63/32-4e-49 on Q312, since the omitted exterior is nonnegative. Thus ||B_j||²/d_old is a valid matched scalar comparator for the SAME actual W and B. It is a consequence of the old tail theorem, not a replay of the old bounded-minorant low matrix or GP. C-0113's all-low-subtraction whole-line failure remains a reused theorem, not recomputed source. No ordering of exact inverses follows from ordering these particular reported allowances.

## 2. Actual low subtraction and uniform-time error

Use unnormalized phi_n(u)=P_n(u/T), with mass L/(2n+1), L=2T. The exact projection coefficients of Z are b_n=(2n+1)/L integral Z phi_n. Full cell moments use integral P_n=(P_(n+1)-P_(n-1))/(2n+1), or the constant moment at n0. Round to exact dyadic c_n on a64-bit grid. A proved coefficient enclosure yields epsilon_projection²=sum L/(2n+1)|b_n-c_n|². The physical polynomial p=sum c_n phi_n needs no unexplained normalized mass conversion.

On65536 uniform physical cells let UZ be the EXACT cell-average projection of Z. Its full error epsilon_Z²=||Z||²-||UZ||² is exact rational, including cap zeros and every cell intersection. Approximate p on each cell by its midpoint value and round UZ-p(mid) to a48-bit dyadic. All midpoint evaluation/rounding is paid by epsilon_round from full coefficient intervals. Let Delta=L/65536. Cauchy-Schwarz on each half-cell proves ||p-p_mid||<=Delta/2 ||p'||. The exact derivative Gram is integral phi_n'phi_k'=min(n,k)(min(n,k)+1)/T for equal parity, zero otherwise. Hence the full uniform step q satisfies

    ||B_j-q_j||<=delta_j=e_j+epsilon_projection+epsilon_Z
                          +Delta/2 ||p_j'||+epsilon_round.

The source e term survives orthogonal Q with norm1. The remaining terms compare QZ with q; q need not be exactly orthogonal. All quantities are physical L² norms. Exact parity is enforced by reflection. The complete two-column weighted Gram and low matrix are diagonal by parity, not by deleting off-diagonal entries.

## 3. Interval FFT samples and ALL aliases

Zero-pad the65536 uniform cell coefficients to M=16*65536. Set P=16L, omega=2pi/P. With an unnormalized DFT D_k,

    |Jq(k omega)|²=Delta² sinc(pi k/M)² |D_k|².

The omitted phase has unit modulus. sinc0=1. These are exact Fourier samples of the uniform STEP FUNCTION, not samples of an unquantified point approximation. Interval FLINT DFT enclosures pay all arithmetic. Direct nonzero sample controls verify normalization/phase and compare source and consumer organizations.

The complete unweighted infinite lattice has exact Parseval mass

    omega/(2pi) sum_(k in Z) |Jq(k omega)|²=||q||².

Proof: group k by residue modulo M and use sum_l sinc(pi(x+l))²=1, including integer limits. Finite DFT Parseval then gives Delta/M sum |D_k|²=Delta sum |q_i|². Equivalently time translates by P have disjoint support. This equality is for the INFINITE frequency lattice, not the finite DFT prefix.

Take K=floor(16384/omega), verified by exact interval comparisons. Let V_K and E_K be the two-sided weighted and unweighted sums over |k|<=K, including the correct weight at zero. Since h is even increasing, the omitted weighted infinite-grid sum lies in

    [0, (||q||²-E_K)/h((K+1)omega)].

Use outward lower E_K for the upper remainder. No alias, large frequency or continuum integral is declared zero. This exact remaining-mass completion differs from a BV variation envelope and retains the actual frequency weight on every computed sample.

## 4. Continuum quadrature, including the weight kink

For t>=128, A'(t)=sum_(k>=0) 8a_k t/(t²+4a_k²)², a_k=k+1/4. For the positive unimodal summand in a, the unit lattice sum is at most its integral plus twice its maximum. These are1/t and3sqrt(3)/(4t²). Thus A'<=1/125 for t>=128. Termwise differentiation gives |A''|<=3A'/t<=3/16000. The sums and derivatives converge locally uniformly. A is increasing; verify g(128)<1/3. Therefore h varies only at |t|>128.

Set m1/3, gamma3/4, w=1/h. On its smooth pieces,

    w<=1/m, |w'|<=w1=gamma/(125m²),
    |w''|<=w2=2gamma²/(125²m³)+3gamma/(16000m²).

At the two crossing points w is continuous and its derivative has jumps of magnitude at most w1 each. For F=Jq, physical support gives Plancherel derivative bounds ||F'||_nu<=T||q|| and ||F''||_nu<=T²||q||, while |F(t)|²<=L||q||². Thus the total variation of the distributional second derivative of w|F|², with normalized measure nu=dt/(2pi), is at most

    Cq ||q||², Cq=4T²/m+4T w1+w2+L w1/pi.

The last term explicitly pays both kinks. The infinite composite trapezoid Peano kernel is bounded by omega²/8 on every cell. Boundary terms vanish since q is a finite supported step and w decreases. Hence the continuum integral differs from the COMPLETE infinite weighted lattice by at most epsilon_quad=omega² Cq ||q||²/8. This is not an assertion that a point grid itself encloses an integral.

Combining the finite prefix, full alias remainder and quadrature gives lower/upper L_q,U_q for the complete continuum weighted norm. The actual supported coupling satisfies

    G_j >= max(0,sqrt(max(0,L_q))-delta_j/sqrt(m))²,
    G_j <= (sqrt(U_q)+delta_j/sqrt(m))².

The reference penalty upper is G_j_upper/eta_lower. The matched scalar penalty upper is (sqrt(||q||²)+delta_j)²/d_old. Complete source low intervals are <p_j,Z_j> plus/minus e_j, not the old bounded low entries. A positive compressed two-column sufficient lower remains only that compression, not the full312-dimensional Schur criterion.

## 5. Source-rule work floor without a speculative benchmark

For normalized degree n, ||p_n'||_infinity=sqrt((2n+1)/(2T))*n(n+1)/(2T). The positive residual charge in C-0114's published error formula is at least

    r_n(M)=sqrt(2n+1)n(n+1)/(T(4M-3)).

Therefore error1/16 needs r_n(M)<=1/16, even with exact interior cells and zero cap error. Check degree3 at the existing M128 and solve the exact squared inequality at degree311. This is necessary for this PARTICULAR uniform-derivative residual charge, not a mathematical lower bound on the actual source error or on every algorithm. Individual1/16 is not a sufficient whole312-column error policy. No timing is extrapolated from the two-column run. Existing harmonic/residual source structure may permit a different estimate; it is not assumed or implemented here.

## 6. Assessment rule

Report the actual complete matched upper allowances, all error components and analytic work floor. A favorable two-column result removes neither the full-space obligation nor the source-rule work floor. CONTINUE to a full validation requires quantitative support for the whole low space, not a positive sample. RESTRICT or UNRESOLVED must name the source/error operation or estimate still missing. No RH, originality, global advantage, extension or production admission follows.
