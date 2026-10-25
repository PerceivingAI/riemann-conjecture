# Necessary parameter growth for the present positive arithmetic reference

- **Created:** `2026-10-25T23:23:20Z`
- **Scope:** mathematical limitation of a specific reference construction, not a no-go for Weil positivity or Fourier methods

## 1. A necessary constant-trial bound

For each finite T>0, use the complete active arithmetic set log(m)<2T and d_m=Lambda(m)/sqrt(m). On L²(-T,T), let the zero-extended physical shifts be U_log(m), and define

P_T=-sum_m d_m(U_log(m)+U_-log(m)), M_T=a(T)I+P_T.

Every sum here is finite. The normalized constant vector is u_T=(2T)^(-1/2) on the interval. It belongs to L² and to the domain of the bounded arithmetic reference; no assertion that it belongs to the smooth Weil source domain is needed.

A one-sided shift has overlap2T-log(m), hence

r(T)=-<u_T,P_T u_T>

    =sum_(log(m)<2T) d_m(2-log(m)/T).

If M_T is nonnegative, then a(T)>=r(T). If M_T>=m(T)I with m(T)>0, then a(T)>=r(T)+m(T)>r(T). No common lower bound on m(T) across supports is assumed.

This is a necessary bound, not an exact norm or a sufficient reference-coercivity criterion. In the ordinary scaled Legendre basis it is exactly -P_00/2. The retained corrected C-0096 and C-0100 intervals independently enclose its fresh scalar evaluation in the accompanying comparison calculation.

## 2. The lower bound grows without bound

For every prime p<=exp(T), the term is active and2-log(p)/T>=1, so

r(T)>=sum_(p<=exp(T)) log(p)/sqrt(p).

For completeness, the required divergence uses only unique factorization and elementary positive series, not a prime number theorem, RH or an unproved cancellation estimate.

Suppose sum_p1/p converged. Since -log(1-x)<=2x for0<=x<=1/2, the finite products product_(p<=X)(1-1/p)^(-1) would remain bounded as X grows. Expanding their geometric factors, unique factorization shows each product includes every1/n with n<=X. It therefore dominates sum_(n<=X)1/n, which diverges. This is a contradiction. Thus sum_p1/p diverges.

For p>=2, log(p)/sqrt(p)>=(log2)/p. Therefore the weighted prime sum also diverges, proving r(T)->infinity as T->infinity. Equivalently, one can first fix a finite prime sum larger than any chosen bound and then take T large enough for all its primes to lie below exp(T). No asymptotic rate is established by this argument.

Consequently any family of these globally positive arithmetic references on supports T_j->infinity requires a(T_j)->infinity, even if its positive coercivity constants m(T_j) tend to zero.

## 3. Complete exterior forces the cutoff to grow too

The Fourier exterior used here is A(t)-a(T), with A(t)=Re psi(1/4+it/2)-log pi. It is continuous and finite on every bounded real interval and even/increasing for t>0 by the previously qualified digamma-series argument.

If the complete exterior is nonnegative for abs(t)>Omega(T), continuity at the cutoff requires a(T)<=A(Omega(T)). Thus a(T_j)->infinity forces Omega(T_j)->infinity. In particular a single fixed a and Omega cannot support this globally positive-M construction on an unbounded support family.

This necessity concerns positivity of the full arithmetic M_T plus the nonnegative complete exterior. It does not prove the bounded minorant H0 negative when M_T fails, nor does it rule out a different outside reference, decomposition or proof of Weil positivity. At the two actually accepted finite cases the unchanged a7/2,Omega256 remain valid.

## 4. A separate obligation of the current tail majorant

The present complete Legendre-tail enclosure E_N(c) uses the geometric ratio

c²/[(2N+1)(2N+3)]<1, c=T Omega.

Using this particular formula requires

N>sqrt(c²+1)/2-1.

Therefore along the above unbounded support family, the dimension used by this formula must also tend to infinity. This is only a prerequisite for this sufficient enclosure. It is not a lower bound on the minimum dimension of a positive Weil matrix, a necessary rate for every Fourier method, or a proof that this dimension condition suffices for small error or low positivity.

In particular the proof supplies no usable law for the low positive gap, required accuracy, actual minimal cutoff, numerical conditioning or global computational cost. The two accepted finite cases do not supply such a law either.

## 5. Interpretation and circularity

The successful4 transition demonstrates an implemented, independently checked structural capability at fixed dimension. It does not license holding the same parameters fixed forever or treating successive finite successes as an all-support proof mechanism.

No global Weil positivity, positive minorant family or uniform coercivity is assumed here. The conclusion is a necessary parameter-growth obligation for the current construction. It neither proves efficient continuation nor establishes that continuation is impossible. No new support matrix or numerical sign is computed by this argument.
