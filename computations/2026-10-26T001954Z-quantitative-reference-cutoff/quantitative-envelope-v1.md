# Quantitative arithmetic-reference and exterior-cutoff envelopes

- **Created:** `2026-10-26T00:19:54Z`
- **Last updated:** `2026-10-26T00:19:54Z`
- **Scope:** the complete positive arithmetic reference and nonnegative Fourier exterior; not a general obstruction to Weil positivity

## 1. Setup and external premises

On L²(-T,T), extend functions by zero and let U_l denote the compressed physical translation by l. Set d_m=Lambda(m)/sqrt(m), with all prime powers satisfying log(m)<2T included, C_T=sum d_m(U_log(m)+U_-log(m)), P_T=-C_T and M_T=aI-C_T. These are finite bounded self-adjoint sums at every finite T. Write a_*(T)=sup sigma(C_T). Then M_T>=mI precisely when a>=a_*+m. Here m=m(T)>0 may depend on support; no uniform lower bound is assumed.

Rosser–Schoenfeld (1962), Theorem4 (3.14), p.70, gives theta(x)>x[1-1/(2 log x)] for x>=563. Theorem12 (3.35), p.71, gives psi(x)<1.03883x for x>0. Thus, with c=9/10, C=21/20 and x0=563,

    psi(x)>=c x  (x>=x0),   psi(x)<=C x  (x>0).

Indeed log563>5, and theta<=psi. These unconditional published inequalities are external premises; our scalar checks are not a local reproof of the paper's numerical verification. The original scanned pages were visually inspected. Publisher DOI: https://doi.org/10.1215/ijm/1255631807 ; inspected facsimile: http://denise.vella.chemla.free.fr/Rosser-Schoenfeld-1962.pdf .

For the digamma remainder we use NIST DLMF5.11.2 and5.11(ii): after retaining log z-1/(2z), the remainder has modulus at most (12|z|²)^(-1) sec³(arg(z)/2), in the stated cut-plane sector. Our z=1/4+it/2 has |arg z|<pi/2. Sources: https://dlmf.nist.gov/5.11.E2 ; https://dlmf.nist.gov/5.11#ii .

## 2. The constant-trial bound has a quantitative rate, but misses the norm rate

C-0101's normalized constant trial gives

    r(T)=sum_(log(m)<2T) d_m(2-log(m)/T) <= a_*(T).

Put X=exp(2T). Stieltjes partial summation, including the zero weight at X, gives exactly

    r(T)=(1/T) integral_1^X psi(x) x^(-3/2)[1+(1/2)log(X/x)] dx.

This formula remains valid if X is a prime power: the endpoint atom has zero weight. Consequently, for every T>0,

    r(T) <= (C/T)[4exp(T)-2T-4].

For T>=(log563)/2 it also gives

    r(T) >= (c/T){4exp(T)-sqrt(563)[4+2T-log563]}.

The latter expression is zero at its left endpoint and nonnegative afterward. Hence r(T)=Theta(exp(T)/T). These are bounds on the constant trial, not an exact arithmetic operator norm. The finite sums in the two previously accepted cases remain available and are sharper than the global envelopes there.

## 3. A boundary-cap trial proves the stronger necessary rate

For T>=7/2, let f_T=1/sqrt(2) on [-T,-T+1] union [T-1,T], and zero elsewhere. Its L² norm is1; the two caps are disjoint. If l=2T-delta with delta in[1/2,3/2], the overlap between the translated left cap and right cap is

    w(l)=1-|delta-1| >=1/2.

The two signed translations together contribute w(l) to <f_T,(U_l+U_-l)f_T>: each individual overlap carries the normalization factor1/2. Contributions from every other translation are nonnegative and can be discarded for a lower bound.

Take L=exp(2T-3/2), U=exp(2T-1/2). All prime powers L<m<=U are strictly active. Since 1/sqrt(m)>=exp(-T),

    a_*(T) >= <f_T,C_T f_T>
            >= (1/2) exp(-T)[psi(U)-psi(L)]
            >= (1/2)[c exp(-1/2)-C exp(-3/2)] exp(T)
            > (3/20) exp(T).

The published lower bound applies because U>=exp(13/2)>563. The upper bound at L has no lower-range restriction. This proves a necessary exponential reference scale on T>=7/2, without testing a new Weil matrix or presuming the caps belong to the smooth source domain: they are legitimate vectors of the bounded arithmetic reference only.

## 4. Sufficient norm bounds and their losses

For one compressed shift pair, let L_m=ceil(2T/log(m)). The exact essential chain norm is

    ||U_log(m)+U_-log(m)||=2cos(pi/(L_m+1)).

When 2T/log(m) is an integer, the longer endpoint-only chain has measure zero and must not increase L_m. Thus

    ||P_T|| <= p_chain(T)=sum_active d_m 2cos(pi/(L_m+1))
             <= 2 sum_active d_m.

At an unresolved activation or ceiling boundary, a numerical implementation must fail closed or prove the equality symbolically; it must not select an integer from a midpoint. This is a sum of norms, not an assumption that the compressed translations commute.

Partial summation yields sum_(m<=X) Lambda(m)/sqrt(m)<=C(2sqrt(X)-1). Including a possibly inactive endpoint only enlarges this upper bound. Therefore, for every T>0,

    ||P_T|| <= p_global(T)=(21/5)exp(T)-21/10.

Choosing a=p_global+m guarantees M_T>=mI. On T>=7/2 the upper/lower envelope ratio is less than28. Thus a_*(T)=Theta(exp(T)); this stronger necessary rate is not an artifact of using the sufficient norm sum. The constants do not determine the exact norm, and an error of a constant factor in a still produces an exponentially large cutoff uncertainty.

In the already qualified first post4 window log2<T<log5/2, replace the separate2/4 chain contributions by their proved joint bound:

    p_joint24=log2(1+sqrt17)/4 + log3/sqrt3 <49/32.

The proof of that bound uses three-point2-fibers and the combined4 coupling. It must not be extended beyond its window. At the older active{2,3} case the ordinary chain sum remains the applicable sufficient bound. The scalar comparison checks these two existing cases only; no new support positivity is inferred.

## 5. Explicit digamma error and invertible cutoff bracket

Let A(t)=Re psi(1/4+it/2)-log pi. It is even and strictly increasing for t>0 by the already established convergent digamma series. For t>0, DLMF's remainder gives

    psi(z)=log z-1/(2z)+R(z),  |R(z)|<=sqrt2/(6|z|²)<1/(4|z|²).

Since |z|²=(t²+1/4)/4,

    A(t)=log(t/(2pi)) +(1/2)log(1+1/(4t²))
         -1/[2(t²+1/4)] + Re R(z),
    |Re R(z)| <1/(t²+1/4).

Using log(1+x)<=x gives the simple rigorous bound

    |A(t)-log(t/(2pi))| <=2/t²,  t>0.

There is no midpoint inversion or asymptotic expression used as an inequality without a remainder. In particular A(4)<=log(2/pi)+1/8<0. Therefore, for every target b=a+e>=0, the unique solution A(Omega_b)=b lies above4, and

    2pi exp(b-1/8) <= Omega_b <= 2pi exp(b+1/8).

The right endpoint is a constructive sufficient cutoff: A(t)>=a+e for every |t|>=2pi exp(a+e+1/8). The left endpoint is necessary for any complete exterior reserve e>=0. These two explicit cutoffs differ by exp(1/4), for a fixed target b, not by an unknown inverse-digamma estimate. The stronger frequency-dependent error2/t² remains available for sharper finite brackets.

## 6. Combined tradeoff and limitations

For T>=7/2, any M_T>=m(T)I and complete exterior A(t)-a>=e(T)>=0 require

    a > (3/20)exp(T)+m(T),
    Omega >=2pi exp((3/20)exp(T)+m(T)+e(T)-1/8).

Conversely, setting

    a=(21/5)exp(T)-21/10+m(T),
    Omega=2pi exp(a+e(T)+1/8)

constructs these two positive reference/exterior bounds at every finite support. If m(T)+e(T)=O(exp(T)), this construction has log Omega=O(exp(T)); the necessary bound has log Omega=Omega(exp(T)). Thus the minimal achievable cutoff order for this architecture is double exponential in T. Taking the reserves toward zero does not remove the necessary rate.

This does NOT establish positivity of H0, the finite Schur matrix, or Weil's form. Nor does it prove a practical work law. Existing tail and mixed-error bounds must still be evaluated with variable parameters, particularly c=T Omega, and compared with an actually proved positive low gap. C-0101's dimension condition for its particular geometric Legendre enclosure remains a condition on that sufficient formula, not a general minimum positivity dimension.

The new conclusions refine C-0101; they do not rewrite it, confer production admission, or claim originality relative to the mathematical literature. The earlier finite results and their exact bytes remain unchanged. No RH-equivalent positivity is used in any of the bounds above.
