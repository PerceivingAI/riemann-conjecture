# Full real-kernel residual bounds beyond the Taylor radius

- Created: `2026-10-25T14:24:24Z`
- Status at creation: proposed analytical comparison, independent qualification and scalar execution pending
- Scope: full residual operator bounds, not new Weil positivity or production acceptance

## Exact source and real decomposition

Suzuki [arXiv2606.09096v3, §§2.4 and4.2](https://arxiv.org/html/2606.09096v3) gives, on the positive real branch,

\[
r''(t)=-2\cosh(t/2)+g(t),\qquad
g(t)=\frac{e^{-t/2}}{1-e^{-2t}}-\frac1{2t}.
\]

The singularity at0 is removable. The globally defined real residual on the scaled interval is the integral kernel -T r''(T|x-y|). This is the same source used by the existing local Taylor implementation, not a modified source. No Taylor remainder is used in the bound below.

For real t>=0, write

\[
g(t)=e(t)+o(t),\quad e(t)=\frac1{4\cosh(t/2)},\quad
o(t)=\frac1{4\sinh(t/2)}-\frac1{2t}
=t\sum_{k=1}^{\infty}\frac{(-1)^k}{t^2+4\pi^2k^2}.
\]

The last identity follows from [DLMF4.36.5](https://dlmf.nist.gov/4.36.E5). It converges locally uniformly, as do its first two differentiated series. Alternating decrease in k gives |o(t)|<=t/(t²+4pi²)<=1/(4pi), hence |g|<1/3.

## Uniform real derivative bounds

For f(s)=s/(1+s²), |f'(s)|<=1 and |f''(s)|<=3 on the real line. Consequently

\[
|o'|\le\sum(2\pi k)^{-2}=1/24,\quad
|o''|\le3\sum(2\pi k)^{-3}=3\zeta(3)/(8\pi^3)<5/288.
\]

Here zeta(3)<5/4 follows by separating1,1/8 and bounding the remainder with the integral from2 to infinity; pi>3. Direct hyperbolic differentiation gives |e'|<=1/16 and |e''|<=1/16. Therefore

\[
|g'|\le5/48,\qquad |g''|\le23/288.
\]

The removable Taylor limit at0 gives g(0)=1/4 and g'(0)=-1/48. This local derivative evaluation is not a Taylor approximation on the full interval.

## Complete differentiated-kernel bound

Let Rg have kernel k(x,y)=-T g(T|x-y|). The spectral Legendre operator is L=-d/dx[(1-x²)d/dx], with eigenvalues j(j+1). In distributions,

\[
L Rg f=-\frac{T^2}{24}(1-x^2)f(x)
+\int_{-1}^1\left[-2T^2x\,g'(T|x-y|)\operatorname{sgn}(x-y)
+T^3(1-x^2)g''(T|x-y|)\right]f(y)\,dy.
\]

The diagonal term is the cusp contribution; it must not be dropped. Both first and second integral-kernel derivatives are bounded on each finite support. Thus Rg maps L² into H², endpoint flux vanishes, and integration by parts plus Parseval places its range in the spectral domain of L, exactly as in the C-0088 domain argument. Schur row and column bounds yield

\[
\|L Rg\|\le C(T):=\frac{11T^2}{24}+\frac{23T^3}{144}.
\]

For N>=1, Q_N projects onto degrees N and higher. No N-dependent polynomial removal was made, so the estimate is genuinely one-sided:

\[
\|Q_N Rg\|\le C(T)/[N(N+1)].
\]

It therefore also bounds both double-tail and low-to-tail compressions of Rg. This is different from applying C-0088's double-compression polynomial removal to a cross block.

## Exact polar rank and its tail

Put alpha=T/2, c(x)=cosh(alpha x), s(x)=sinh(alpha x). The full polar part of R is

\[
R0=2T(c\otimes c-s\otimes s).
\]

The negative odd component remains present. Let

\[
E_N(z)=\frac{(2N+1)z^{2N}}{((2N+1)!!)^2}
\left(1-\frac{z^2}{(2N+1)(2N+3)}\right)^{-1},
\quad z^2<(2N+1)(2N+3).
\]

Rodrigues' formula and repeated integration by parts imply

\[
\|Q_N e^{\alpha x}\|^2\le2e^T E_N(T/2).
\]

Even and odd projection components are orthogonal. Triangle and rank-one norms then give

\[
\|Q_N R0 Q_N\|\le4T e^T E_N(T/2),
\]

\[
\|Q_N R0\|\le4\sqrt{T e^T\sinh(T)E_N(T/2)}.
\]

The second bound uses ||e^(alpha x)||²=2sinh(T)/T and is not obtained by reusing the smaller double-tail norm.

## Full residual consequence and limits

For every finite T>0 and N>=1 satisfying the displayed geometric-ratio condition,

\[
\boxed{\|Q_N R_T Q_N\|\le\frac{C(T)}{N(N+1)}+4T e^T E_N(T/2)}
\]

and

\[
\boxed{\|Q_N R_T\|\le\frac{C(T)}{N(N+1)}+4\sqrt{T e^T\sinh(T)E_N(T/2)}}.
\]

Neither bound has a2T<pi condition or a fixed-truncation error floor. The ratio condition is explicit and satisfiable at every fixed finite support. These are full real-source bounds, not evaluated high-column samples.

For context, ||R0||<=2T+2sinh(T) and ||Rg||<=2T/3 give the finite global norm ||R_T||<=8T/3+2sinh(T). With the finite active arithmetic sum, this makes the bounded-perturbation form construction meaningful at every fixed finite support under Suzuki's global source identity. It does not establish global positivity, a practical N(T), improved local sharpness, or a new certificate/admission contract. The existing local kernels must keep their historical refusal behavior until a separate implementation is deliberately qualified.
