# Independent physical-tail qualification

- Created: `2026-10-25T14:38:58Z`
- Last updated: `2026-10-25T14:38:58Z`
- Status: independently derived analytical bounds for the complete real residual at every finite `T > 0`. No numerical execution, implementation, new positivity result, or theorem admission.

## Result

The proposed constants, cusp sign, powers of `T`, and rank-two factors are correct. The argument gives a concrete global residual inequality in the existing physical representation. It bounds the one-sided residual tail as well as its double compression, without a Taylor truncation or an unknown differentiated remainder.

For `N >= 1`, let `Pi_N` retain Legendre degrees `0,...,N-1` on `L²(-1,1)` and `Q_N=I-Pi_N`. Define

\[
C(T)=\frac{11T^2}{24}+\frac{23T^3}{144},
\]

\[
E_N(c)=\frac{(2N+1)c^{2N}}{((2N+1)!!)^2}
\frac1{1-c^2/((2N+1)(2N+3))},
\tag{1}
\]

where the last expression is used only when `c² < (2N+1)(2N+3)`. For the complete Suzuki residual operator `R_T`, with scaled kernel `-T r''(T(x-y))`, the qualified bounds are

\[
\boxed{\ \|Q_NR_TQ_N\|
\le\frac{C(T)}{N(N+1)}+4T e^T E_N(T/2).\ }
\tag{2}
\]

\[
\boxed{\ \|Q_NR_T\|
\le\frac{C(T)}{N(N+1)}
+4\sqrt{T e^T\sinh(T)E_N(T/2)}.\ }
\tag{3}
\]

In particular, (3) also bounds `Q_N R_T Pi_N`. Unlike removal of even polynomial kernels after two projections, it does not assume that a low-to-tail block vanishes. Neither bound is asserted sharper than C-0088 at the previously assessed local parameters.

## 1. Public sources and complete real kernel

The exact sources inspected were Suzuki [arXiv:2606.09096v3, §1.2 and §2.4](https://arxiv.org/html/2606.09096v3), NIST [DLMF §4.36](https://dlmf.nist.gov/4.36), and the [exact TeX of DLMF 4.36.E5](https://dlmf.nist.gov/4.36.E5.tex). The public proof of [C-0088](../../findings/2026-10-24T224948Z-tail-restricted-residual-bound.md) was read for its spectral-domain and endpoint argument. Its local Taylor remainder is not a premise of (2)-(3).

For `t > 0`, Suzuki gives

\[
r''(t)=-2\cosh(t/2)+g(t),
\qquad
g(t)=\frac{e^{-t/2}}{1-e^{-2t}}-\frac1{2t}.
\tag{4}
\]

This is a real-variable identity, not a license to sum a Bernoulli series beyond its complex convergence radius. Its global real meaning can be checked against the original screw function. In Suzuki (1.3), the nonconstant Lerch term for `t > 0` is

\[
\frac14\sum_{n\ge0}\frac{e^{-(2n+1/2)t}}{(n+1/4)^2}.
\]

Twice differentiating on compact subintervals of `t > 0` gives `e^{-t/2}/(1-e^{-2t})`. Removing the logarithmic reference second derivative `1/(2t)` leaves exactly `g`. Thus the real identity does not depend on analytically continuing the local Taylor bound. Even extension supplies `r''(-t)=r''(t)`.

Use the cancellation-free decomposition

\[
g(t)=e(t)+o(t),\qquad
e(t)=\frac1{4\cosh(t/2)},\qquad
o(t)=\frac1{4\sinh(t/2)}-\frac1{2t}.
\tag{5}
\]

The notation `o` denotes an odd function here, not a little-oh error. DLMF 4.36.E5, after substituting `z=t/2`, gives exactly

\[
o(t)=t\sum_{n\ge1}\frac{(-1)^n}{t^2+4\pi^2n^2}.
\tag{6}
\]

It extends regularly at `t=0`. The function `g` is smooth on the nonnegative real axis, with `g(0)=1/4`. Its even time-difference use is `g(|t|)`, which has a first-derivative cusp at zero. Confusing `g(t)` with a smooth even function would lose the essential diagonal contribution below.

## 2. Independent global derivative bounds

Put `h(s)=s/(1+s²)` and `a_n=2pi n`. The `n`th rational term in (6) is `a_n^(-1) h(t/a_n)`. Direct differentiation gives

\[
h'(s)=\frac{1-s^2}{(1+s^2)^2},\qquad
h''(s)=\frac{2s(s^2-3)}{(1+s^2)^3}.
\]

For every real `s`,

\[
|h'(s)|\le1,\qquad |h''(s)|\le3.
\tag{7}
\]

For the latter, use `|s²-3| <= 3(1+s²)` and `2|s| <= 1+s²`. Consequently the first and second derivative series are absolutely and uniformly convergent on the real line. The original series is locally uniformly convergent, which is enough to identify these derivatives. This yields

\[
|o'(t)|\le\sum_{n\ge1}\frac1{(2\pi n)^2}=\frac1{24},
\]

\[
|o''(t)|\le\frac{3\zeta(3)}{8\pi^3}.
\tag{8}
\]

The identity `sum n^(-2)=pi²/6` also follows by taking the regular coefficient at zero in DLMF 4.36.E3. A sufficient elementary estimate is

\[
\zeta(3)=1+\frac18+\sum_{n\ge3}n^{-3}
<1+\frac18+\int_2^\infty x^{-3}\,dx=\frac54.
\]

For `e`,

\[
e'(t)=-\frac18\operatorname{sech}(t/2)\tanh(t/2),
\]

\[
e''(t)=\frac1{16}\operatorname{sech}(t/2)
\left(2\tanh^2(t/2)-1\right).
\]

Since `sech² + tanh² = 1`, their product in the first formula has absolute value at most `1/2`. Therefore

\[
|e'(t)|\le\frac1{16},\qquad |e''(t)|\le\frac1{16}.
\]

Combining these estimates, and using `pi > 3`, gives the claimed global bounds

\[
\boxed{\ |g'(t)|\le\frac5{48},\qquad
|g''(t)|\le\frac1{16}+\frac{3\zeta(3)}{8\pi^3}
<\frac{23}{288}.\ }
\tag{9}
\]

The endpoint derivative is exact. The elementary expansion `csch(t/2)=2/t-t/12+O(t³)` in (5) gives

\[
g'(0+)=-\frac1{48}.
\tag{10}
\]

Thus the proposed constants do not rely on a guessed digamma envelope or an unproved monotonicity assertion about derivatives.

## 3. Scaling and the diagonal cusp

On `H=L²(-1,1)`, write

\[
R_T=R_0+R_g,
\]

\[
R_0(x,y)=2T\cosh\!\left(\frac{T(x-y)}2\right),
\qquad
R_g(x,y)=-Tg(T|x-y|).
\tag{11}
\]

This sign follows from the physical residual convention `-T r''(T(x-y))`. The pole is not a positive kernel in quadratic-form order merely because its pointwise kernel is positive.

Let `k(s)=-Tg(T|s|)`. Away from zero,

\[
k'(s)=-T^2g'(T|s|)\operatorname{sgn}(s).
\]

Its derivative jump is `-2T² g'(0+) = T²/24`. Distributionally,

\[
k''(s)=-T^3g''(T|s|)+\frac{T^2}{24}\delta_0(s).
\tag{12}
\]

For the auxiliary Legendre operator

\[
L=-\frac d{dx}\left[(1-x^2)\frac d{dx}\right],
\]

this gives, for every `f` in `H`,

\[
\begin{aligned}
(LR_gf)(x)={}&-\frac{T^2}{24}(1-x^2)f(x)\\
&+\int_{-1}^{1}\Big[
-2xT^2g'(T|x-y|)\operatorname{sgn}(x-y)
+(1-x^2)T^3g''(T|x-y|)
\Big]f(y)\,dy.
\end{aligned}
\tag{13}
\]

The proposed negative multiplier `-T²(1-x²)/24` is therefore correct. It is not a positive cusp allowance, though its operator norm contributes positively to an upper norm bound.

## 4. Domain and endpoint verification

For each fixed finite `T`, the kernel and its first weak derivative are bounded on the time square. Formula (12) gives the second weak derivative of `R_g f` as the sum of a bounded integral operator and `T² f/24`. Hence

\[
R_g:H\longrightarrow H^2(-1,1).
\tag{14}
\]

This assertion is for the complete `R_g`, not an unknown remainder obtained after differentiating a norm enclosure.

If `u=R_g f`, one-dimensional Sobolev regularity gives finite endpoint traces of `u` and `u'`. Thus `(1-x²)u'` vanishes at both endpoints. In integration by parts against a Legendre polynomial `P_j`, the other endpoint term also vanishes because `(1-x²)P_j'` is zero there and `u` is bounded. The result is

\[
\langle Lu,P_j\rangle=j(j+1)\langle u,P_j\rangle.
\]

Since the expression (13) is in `L²`, Parseval proves

\[
\sum_{j\ge0}[j(j+1)]^2|\langle u,e_j\rangle|^2<\infty,
\]

where `e_j` are the normalized Legendre polynomials. This places `u` in the domain of the spectral Legendre operator and justifies using its high-mode inverse. It does not require an assumed characterization of every singular-endpoint extension of the differential expression. The auxiliary `L` is not the harmonic jump operator with eigenvalues `H_j`.

## 5. Differentiated norm and range gain

An integral kernel bounded in absolute value by `b` on `(-1,1)²` has row and column integrals at most `2b`, so its operator norm is at most `2b`. Formula (13), with (9), gives

\[
\begin{aligned}
\|LR_g\|
&\le\frac{T^2}{24}
+4T^2\frac5{48}
+2T^3\frac{23}{288}\\
&=\frac{11T^2}{24}+\frac{23T^3}{144}=C(T).
\end{aligned}
\tag{15}
\]

For `N >= 1`, the spectral range statement now gives the one-sided bound

\[
\boxed{\ \|Q_NR_g\|\le\frac{C(T)}{N(N+1)}.\ }
\tag{16}
\]

Applying a contractive projection on the right yields the same bound for `Q_N R_g Q_N`. There is no polynomial-removal step and no need to assume that the input is already high frequency. By self-adjointness, the same bound also holds for `R_g Q_N`.

## 6. Rank-two pole and the exponential tails

Put `h_c(x)=cosh(Tx/2)`, `h_s(x)=sinh(Tx/2)`, and `h_+(x)=exp(Tx/2)`, `h_-(x)=exp(-Tx/2)`. The exact operator identities are

\[
R_0=2T(h_c\otimes h_c-h_s\otimes h_s)
=T(h_+\otimes h_-+h_-\otimes h_+).
\tag{17}
\]

Here `u tensor v` denotes the operator `f -> <f,v>u`. In particular, the odd sector has a negative pole.

The two parity vectors are orthogonal, and

\[
\|h_c\|^2=1+\frac{\sinh T}{T},
\qquad
\|h_s\|^2=\frac{\sinh T}{T}-1.
\]

Thus the nonzero pole eigenvalues are `2T+2sinh(T)` and `2T-2sinh(T)`, and

\[
\boxed{\ \|R_0\|=2T+2\sinh T.\ }
\tag{18}
\]

For completeness, Rodrigues' formula for a complex plane wave gives

\[
\left|\int_{-1}^{1}e^{izx}P_n(x)\,dx\right|
\le\frac{2e^{|\operatorname{Im}z|}|z|^n}{(2n+1)!!}.
\]

The squared normalized Legendre tail is bounded by a geometric majorant with ratio `c²/((2N+1)(2N+3))`. Taking `z=+iT/2` or `z=-iT/2` proves

\[
\|Q_Nh_\pm\|^2\le2e^T E_N(T/2).
\tag{19}
\]

Also `||h_+||²=||h_-||²=2sinh(T)/T`. The two cross rank-one terms in (17) therefore give exactly the proposed upper bounds

\[
\|Q_NR_0Q_N\|
\le 2T\|Q_Nh_+\|\|Q_Nh_-\|
\le4T e^T E_N(T/2),
\tag{20}
\]

\[
\|Q_NR_0\|
\le2T\sqrt{2e^T E_N(T/2)}\sqrt{\frac{2\sinh T}{T}}
=4\sqrt{T e^T\sinh(T)E_N(T/2)}.
\tag{21}
\]

These are conservative inequalities; the exact parity decomposition could give smaller bounds. No factor of `T`, `2`, or `sqrt(T)` is missing. Adding (16) to (20) and (21) proves (2) and (3).

## 7. Full norm and global applicability

For fixed `t > 0`, the positive magnitudes in the alternating series (6) decrease to zero with `n`. Thus

\[
|o(t)|\le\frac{t}{t^2+4\pi^2}\le\frac1{4\pi}.
\]

Together with `|e(t)| <= 1/4`, this proves

\[
|g(t)|\le\frac14+\frac1{4\pi}<\frac13.
\]

The Schur norm bound then gives `||R_g|| <= 2T/3`, and (18) gives

\[
\boxed{\ \|R_T\|\le2T+2\sinh T+\frac{2T}{3}.\ }
\tag{22}
\]

All these operator bounds hold on all `H` for each finite `T > 0`. They have no `2T < pi` condition. Formula (1) still needs its displayed ratio condition, which is met by taking sufficiently large `N` at each fixed `T`. There is no claim of uniform constants as `T` becomes unbounded, no dimension optimality statement, and no demonstrated cost advantage.

## 8. Limits of the source-domain extension

This qualification proves a global bounded residual and explicit smoothing estimates. It does not make the entire Weil operator bounded. The logarithmic boundary multiplication and harmonic jump parts retain their form domains. In particular, `L R_g` being bounded does not justify applying `L` indiscriminately to the unbounded Weil form or changing its domain.

The source identity is available on admissible smooth tests. The complete real residual formula above allows that identity to be used without the local Taylor remainder. The existing physical construction has a support-independent nonnegative base form, the sum of the harmonic jump and boundary multiplication forms, on the intersection of their form domains. For any fixed finite `T`, the arithmetic sum has finitely many bounded shifts and (22) supplies a bounded residual. The bounded-perturbation argument therefore constructs a closed lower-semibounded form on that same intersection at every finite `T`, with the corrected globally defined residual.

This construction must be distinguished from an unproved identification of its entire operator domain with Suzuki's canonical realization. Equality on the smooth core is the relevant source premise for a smooth-test positivity implication. Identifying complete closed realizations additionally requires the appropriate core/closure argument; it does not follow merely from the residual norm bound. No such domain identification is silently added to C-0063 here.

Equations (2)-(3) can supply a valid residual allowance in a new analytical tail or cross-block argument. A smaller residual allowance alone does not prove the low Schur matrix positive. It does not invalidate previously established negative directions in a particular reference matrix, alter historical source/error contracts, or admit a new support theorem.

## Assessment

The proposed inequality survives independent challenge. Its concrete addition is an all-real, complete-residual range-gain bound with the cusp paid explicitly and the pole treated separately at exact rank two. The one-sided estimate is materially different in scope from a bound justified only after two tail projections. It is not established as numerically sharper than the local polynomial-removal estimate, and no positivity consequence has been evaluated.

Only this new qualification file was written for this follow-up. No prior research, code, certificate, or admission was changed.
