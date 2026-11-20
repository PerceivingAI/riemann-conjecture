# T=81/100 supported reference and complete-error contract

- **Created:** `2026-10-27T13:22:36Z`
- **Last updated:** `2026-10-27T13:42:00Z`
- **Scope:** fixed-support reference/error qualification, not a target positivity result

## 1. Source, domain and exact activation

Use C-0063/C-0107's common Suzuki smooth/form domain and ordinary physical L2 mass. Under the unitary map f(t)=T^(-1/2)u(t/T), the mapped basis is the ordinary Legendre basis with D_n=2/(2n+1). Keep all pole, endpoint and low even residual terms. No equality of entire operator domains is asserted.

At exact T=81/100, strict log(5)<81/50<log(7) and 81/50<pi hold. Exact prime-power recognition therefore gives precisely 2,3,4,5. The von Mangoldt coefficients c_m=Lambda(m)/sqrt(m) are log(2)/sqrt(2), log(3)/sqrt(3), log(2)/2 and log(5)/sqrt(5). Integer 6 is not a prime power. The canonical residual proof remains within 2T<pi.

Let I_T=(-T,T), U_l be the one-sided translation compressed to I_T, and S_l=U_l+U_l*. Arithmetic is the ONE signed operator

`P=-sum_m c_m S_(log m)`.

Square its complete signed image before projecting. Thus P^2 includes c_i*c_j*(S_i*S_j+S_j*S_i) for every distinct pair, including every pair with 5. The ordered mixed products VP and PV remain separate adjoint orientations; they cannot be replaced by one symmetrized orientation before forming the complete Gram.

## 2. Fresh full-line discrepancy bound

Write A(t)=Re psi(1/4+it/2)-log(pi), A0=A(0), w(t)=A(t)-A0+1. With Fourier measure dt/(2pi), q_w is nonnegative. C-0107's source identity supplies

`l_T[f]=q_AF[f]+<f,L_T f>-d_E,T[f]`,

where L_T has kernel exp(-|u-v|/2) and is positive. Its positivity does not discard or reverse the original pole: together with the signed continuum in d_E it reconstructs the original source.

The full-line signed discrepancy multiplier is

`rho_T(t)=2 sum_m c_m cos(t log m)-2 Re[(exp((1/2+it)2T)-1)/(1/2+it)]`.

The fresh producer covers [0,256] by 1563 adaptive interval leaves and controls all larger frequencies analytically; evenness covers negative frequencies. An independent consumer uses a real quotient, a positive 128-term digamma prefix with a 64-order Binet remainder, a sharper Lipschitz bound and an independent analytic infinite tail. Native intervals, not overlaps between rounded reports, must fit inside publications.

The published full-line bound is rho_T<=w/4+1933/1024. Its finite witness exceeds 1.745716 in rho_T-w/4, while the conservative infinite-tail cap is about 1.887002. Moving the finite proof boundary alone cannot make this pointwise bound as small as the supported bound below. The global bound gives first reference anchor R1038 and sufficient scalar cutoff N1188.

## 3. Support-aware transfer removes part of the activation loss

C-0119 independently proves the OLD multiplier inequality rho_(4/5)<=w/4+859/1024 on the WHOLE frequency line. That multiplier statement applies to any L2 input in its form domain, not just functions supported in the old interval. Applying this bound to an input supported in I_(81/100) does not transport old Weil positivity, an old low matrix, a tail cutoff or an old spectral gap.

The new discrepancy differs from that old multiplier operator, compressed to the NEW interval, by

`c_5 S_(log 5) - integral_[8/5,81/50] exp(l/2) S_l dl`.

For T<l<2T, U_l has disjoint domain and range, U_l^2=0, and S_l^2 is the projection onto the two edge intervals. Therefore ||S_l||=1, rather than the whole-line norm 2. The endpoint l=2T is zero almost everywhere and causes no integral difficulty. Strictly T<log(5)<2T, and every l in the added continuum strip satisfies l>T. Consequently

`d_E,T[f] <= q_w[f]/4 + (859/1024 + c_5 + 2(exp(81/100)-exp(4/5))) ||f||^2`.

The new prime charge is about 0.719762516; the added continuum charge is about 0.0447341164. Their sum is bounded above by about 0.764496632. Directed publication of the unrounded beta about 1.603363820 on the 1/1024 grid yields

`beta=821/512`.

This is a SUPPORTED FORM inequality, not a pointwise bound for rho_T. Indeed the fresh global finite witness is larger than this beta. The consumer reexecutes the old independent full-line scalar checker on the exact pinned old inputs before accepting the transfer, then independently checks the new shift geometry and every new enclosure. The new source retains the fresh global proof as a comparison and explicitly distinguishes both bound types.

The new physical edge width is 2T-log(5), about 0.0105620876. Small overlap measure does NOT make ||S_(log 5)|| small: it equals 1 for every strictly positive overlap in this disjoint regime. These estimates quantify a conservative isotropic activation cost, not a discontinuity of the true Weil positivity margin or a no-go for a sharper energy-aware estimate.

## 4. Complete outside reference and physical inverse

Set alpha=1/4, m=1/3, and

`g(t)=A0+(1-alpha)(w(t)-1)-alpha-beta`,

`h(t)=max(m,g(t))`.

Let Q_N remove the first N ordinary mapped Legendre modes. For c=T*R and r_N=c^2/((2N+1)(2N+3))<1, the COMPLETE Legendre band-leakage estimate is

`lambda_N(R)=(2c/pi) * [(2N+1)c^(2N)/((2N+1)!!)^2] / (1-r_N)`.

It bounds the full low-frequency Fourier mass of every Q_N input, not a finite sample or a truncation of the exterior. Monotonicity of g and Parseval give the complete outside lower

`g(R)-(g(R)-g(0))*lambda_N(R)`.

Also q_h-q_g is at most epsilon_N times physical mass on Q_N, where epsilon_N=(m-g(0))*lambda_N(R). Thus outside>=m and epsilon_N/m<=2^-128 imply q_g>=eta*q_h on Q_N, eta=1-2^-128. This domination is NOT a claim on arbitrary low inputs.

Choose the first integer R>=1 with g(R)>=m+1/64. Verify its predecessor using monotonicity. Then choose the first even N>=2 satisfying both complete inequalities; retain every preceding even trial, including failed geometric ratios. This yields R710,N826. This is a minimum for this published sufficient-bound policy, not the smallest true positivity dimension or an optimized alpha/m choice.

At M=2N=1652 and Rc=2R=1420, independently qualify complete leakage lambda_M(Rc), a=1/g(Rc) and

`kappa=a+(1/m-a)*lambda_M(Rc)<1/m`.

This is a complete physical-output inverse-weight comparison beyond M, not a discarded physical exterior or an inverse of the actual Weil complement. The first-attempt inverse-frequency step majorant has 60 exact anchors: 0,R, positive geometric factors 17/16 strictly below 32R, and 32R. Its terminal positive weight pays ALL higher frequencies; 32R=22720 is not a Fourier cutoff.

## 5. Full canonical residual and numerical controls

Use the canonical C-0117 coefficients c_d(T)=-T^(d+1)k_d, including low even/polar terms and exact endpoint primitives. Independent formal division reconstructs the entire coefficient list and verifies c_1=T^2/48.

For even K and 2T<pi, the complete operator remainder obeys

`delta_K=2T[(2/pi)(2T/pi)^(K+1)/(1-2T/pi) + 2 T^(K+1)/((K+1)!(1-T/(K+2)))]`.

Use the cross bound

`B_K=pi/2 + 2 sum_[m=2,3,4,5] c_m + 2 sum_[d<=K] |c_d(T)|2^d`.

Here pi/2 bounds the V CROSS operator; V itself is unbounded. The true source-model discrepancy is paid by

`Lambda_K=delta_K+(2 B_K delta_K+delta_K^2)/(m eta)`.

The accepted T4/5 selected-low physical Schur bound divided by 2^20 supplies a numerical ACCURACY CHOICE, about 1.50785156e-23. Neither it nor the older full source-norm lower is a T81/100 gap premise. The first qualifying published even order is K86, with Lambda_K below 1.23789121e-23; all 42 preceding even orders fail the same declared accuracy policy.

The exact model cross band has input modes N-K through N-1 and output modes N through N+K-1. Since 2K<N and M>=N+K, the polynomial model has no omitted output beyond M. This does not set the true residual tail to zero: its complete discrepancy remains paid by Lambda_K.

The starting precisions are freshly computed from exact amplification estimates: source4608 bits, independent6144 bits, publication256 bits. They are policies, not proof of achieved target enclosures or a positive sign. The complete physical numerical-radius goal is accuracy/4, below 3.769629e-24. Native all-entry reconstruction and exact transformed-radius checking remain mandatory when full target matrices exist.

Reuse the rigorously paid nonexact-input spherical-Bessel seed rule: evaluate at the EXACT argument midpoint and add its FULL radius using |j_n'|<=1. Keep the native seed guard. Use fresh native actual-A conditioning before float proposals; never make double precision responsible for preserving the original ill-conditioned low spectrum.

## 6. Complete finite criterion and interpretation

With H the complete physical-head weighted Gram and E the complete physical-tail Gram multiplied by kappa, the existing supported completion gives, for any exact theta>0,

`S_K=A_model-[(1+theta)H+(1+1/theta)E]/eta-Lambda_K D`.

Every interval radius and both infinite exteriors must be paid. This follows the already verified C-0118 criterion, with fresh target arithmetic and reference data. Exact positive full-parity congruence of this paid lower, plus new native analytic acceptance, would be sufficient for strict positivity on the common smooth-test domain. Qualification alone checks NONE of these new target signs.

A certified negative direction of this SELECTED conservative lower would reject that lower, not establish Weil negativity. A wide interval or failed numerical goal is not a mathematical negative. No favorable target gap, unbounded support family, external coercivity normalization, production admission or RH conclusion is assumed or obtained here.
