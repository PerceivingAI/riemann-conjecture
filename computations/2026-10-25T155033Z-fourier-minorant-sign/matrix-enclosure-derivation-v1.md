# Complete fixed-minorant source enclosure

- **Created:** `2026-10-25T15:50:33Z`
- **Status:** analytical source contract; numerical acceptance is a separate gate
- **Scope:** fixed T=1353/2048,a=7/2,Omega256,N312 in ordinary unnormalized Legendre coordinates

## Source and arithmetic normalization

Use C-0094's original Suzuki Fourier identity and complete exterior/complement inequalities. With scaled time x in[-1,1], the mass is D_j=2/(2j+1). The existing generic arithmetic API stores d_m=Lambda(m)/sqrt(m), the coefficient of EACH one-sided shift. In the notation P=-sum c_m J_m of C-0094, c_m=2d_m and J_m=(S_m+S_m*)/2. Thus P=-sum d_m(S_m+S_m*). There is no further factor1/2 when consuming `PrimePowerTerm.coefficient`.

Both2 and3 are active, and T<log2<log3<2T. The generic strict global breakpoint partition is reused unchanged. On each cell, every translated polynomial is either zero or a fixed polynomial of degree at most311. Gauss-Legendre order312 integrates every product of two such polynomials exactly. Node, weight, log and coefficient uncertainty is retained in Arb. The producer integrates the combined images to obtain P and P², including both mixed prime products. The auditor independently integrates each signed-shift overlap and every nonempty ordered shift-pair intersection with order313.

The combined arithmetic Gram is GP=P²-P D^-1P. These are quadratic-form matrices in the ordinary Legendre basis, not coordinate matrices with identity mass.

## Entire Fourier vectors and the signed pole

For w=Tt,

\[
I_j(w)=\int_{-1}^1P_j(x)e^{-iwx}dx=2(-i)^j j_j(w),
\]
\[
j_j(w)=\frac{w^j}{(2j+1)!!}\,{}_0F_1(j+3/2;-w^2/4).
\]

Within each parity, the products I_i(w)I_j(-w) equal the outer product of real values2(-1)^floor(j/2)j_j(w). The low-band form is T/pi times their integral with weight A(t)-a over[0,256]. Both parity blocks are included.

The producer uses two exact special-function anchors j312,j313 and the exact downward recurrence. The auditor uses384 finite hypergeometric terms, an explicit geometric bound on the omitted tail, and interval propagation through that recurrence. Its quadrature order64 differs from the producer's48. Both share Arb's transcendental and rigorous Legendre-root primitives; they are not independent numerical libraries. Node intervals are strictly ordered inside(-1,1); weights are positive. The auditor derives weights separately from the Legendre derivative relation. Native root-enclosure correctness remains an explicit FLINT trust premise.

The polar form is2T(cc* - ss*), where c_j=int P_j(x)cosh(Tx/2)dx and s_j=int P_j(x)sinh(Tx/2)dx. Its odd block is negative. The producer evaluates the entire imaginary-wave formula; the auditor uses a finite positive hypergeometric series with an explicit tail.

## A complete frequency quadrature remainder

The analytic operator has kernel

\[
F_z(x,y)=\frac{T}{\pi}(\mathcal A(z)-a)\cos(Tz(x-y)),
\quad\mathcal A(z)=\tfrac12[\psi(1/4+iz/2)+\psi(1/4-iz/2)]-\log\pi.
\]

Use panels[0,1/4],[1/4,1/2],[1/2,1],[1,2],[2,4], then width4 panels through256. For center c and halfwidth h, take rho=2h. The first two disks lie in abs(Im z)<=1/4. Every later disk has strictly positive real part, so all avoid the digamma poles z=+-i(2n+1/2).

A uniform bound abs(A(z)-a)<4096 holds on every containing rectangle. To see this directly from DLMF5.7.6, put v=1/4+-iz/2 and split its digamma series after256 terms. In the first two rectangles Re(v)>=1/8. In every other rectangle abs(Im(v))>=1/8. Hence abs(k+v)>=1/8 for all k>=0. The finite absolute sum is at most256(1+8)=2304. Across all rectangles Re(v)>=-7/4 and abs(v-1)<132. The remaining sum of (v-1)/[(k+1)(k+v)] is bounded in absolute value by

`132/(255-7/4) < 1`.

Together with gamma<1,log(pi)<2 and a=7/2 this is strictly below4096. No unverified digamma asymptotic envelope or finite frequency sample is substituted for this analytic bound.

Schur's kernel estimate gives M=(2T/pi)exp(2T rho)*4096 on the circle. Operator-valued Cauchy estimates bound the Taylor remainder after degree2q-1 on the panel by M(h/rho)^(2q)/(1-h/rho). Positive exact Gauss weights sum to2h and integrate that Taylor polynomial exactly. Integral and quadrature remainders each cost at most2h times the uniform remainder, so

\[
\left\|\int F(t)dt-\sum w_k F(t_k)\right\|
\le\frac{4hM(h/\rho)^{2q}}{1-h/\rho}
=8hM\,2^{-2q}.
\]

Summing every panel bounds the COMPLETE band. This operator allowance is E D in ordinary Legendre quadratic coordinates. An entrywise enclosure may conservatively add E sqrt(D_i D_j) to each entry. The producer uses an outward rational upper for E, not its midpoint. The auditor rebuilds at q64 and requires its entire fresh input enclosure to be contained in the published source interval, not merely overlap.

## Exact sufficient matrix and proof meaning

Set A312=aD+P+pole+band. Every published matrix entry is outward rounded to a dyadic interval at128 fractional bits. For a symmetric interval triangle, its midpoint minus the diagonal of absolute radius row sums is a Loewner lower; plus that diagonal is an upper. These ordered bounds give the complete exact finite lower

\[
S_-=A_- -\frac{(GP)_++3\cdot10^{-40}D}{19/8-10^{-82}}.
\]

For each156-dimensional parity block, a nonsingular rational congruence C with strictly positive exact Gershgorin margin for C* S_- C proves S_->0. Its mass-normalized lower is margin divided by sum_(i,j) D_i C_ij², a Frobenius bound. A floating Cholesky inverse supplies only a proposal; all positivity and margins are checked with exact rational arithmetic.

With the inherited C-0094 complement, two positive blocks imply H0>0 on the entire L² space and hence the original smooth-test positivity. A negative sufficient matrix is not H0 negativity. No unbounded support family, new support, novelty, closed operator-domain identification or production admission is inferred.

## Version integrity

The first producer incorrectly halved the already one-sided arithmetic coefficient. Its packet and source closure are retained as version1 and are invalid for the intended H0. A minimized real arithmetic control detects half P and quarter P². Version2 removes that consumer factor and receives separate generation, verification and results. No old generic arithmetic implementation, historical test or theorem artifact is modified.

## Primary-source cross-check, 2026-10-25T18:25:39Z

[DLMF10.54.2](https://dlmf.nist.gov/10.54.E2), after x=cos(theta), gives the stated entire Fourier integral and its phase. [DLMF3.5(v)](https://dlmf.nist.gov/3.5#v) gives positive Gaussian weights and exactness through degree2q-1. These sources are registered as R-0037. They do not supply the complete operator remainder or assert our positive result.
