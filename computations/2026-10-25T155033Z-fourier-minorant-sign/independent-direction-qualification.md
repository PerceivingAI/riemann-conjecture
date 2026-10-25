# Independent qualification of the bounded-minorant direction test

Created 2026-10-25. This is a written mathematical qualification, conditional on the public source identity and rigorous Arb/Acb primitive semantics. No numerical experiment, test, build, or formatter was run in preparing it. Numerical acceptance requires the separately executed producer and independent verifier receipts.

## Sources and trust boundary

The source premise is Masatoshi Suzuki, [Weil's quadratic form via the screw function, arXiv:2606.09096v3, 23 September 2026](https://arxiv.org/html/2606.09096v3), especially [Section 1.1](https://arxiv.org/html/2606.09096v3#S1.SS1) for the explicit functional and [Section 2.4](https://arxiv.org/html/2606.09096v3#S2.SS4) for Fourier normalization. The public C-0094 derivation is [bounded-minorant-closure-v1.md](../2026-10-25T142424Z-reference-route-selection/bounded-minorant-closure-v1.md), with its [source qualification](../2026-10-25T142424Z-reference-route-selection/fourier-qualification.md). No private research material is a premise.

The relevant local trust rules are [CONTRACTS.md, Sections 1 and 5](../../docs/CONTRACTS.md) and [PROTOCOL.md, external-source and decoupled-trust rules](../../docs/PROTOCOL.md). An independent formula implemented using the same Python-Flint/FLINT library is not an independent arithmetic library, a Lean proof, a production certificate admission, or a replay of Suzuki's whole paper. A raw-byte hash binds an input image; it does not prove its mathematics.

The unchanged [quadrature wrapper](../../scripts/cert/quadrature.py), specifically `rigorous_integral_1d` and `require_real_enclosure`, may be shared. It supplies exact endpoint/tolerance handling and calls Acb integration. It does not prove that a supplied callback is holomorphic. Its real projection is justified only after mathematical realness is established. The independent evaluator must not import the new producer or use its transform values as mathematical authority.

For the callback contract, see [FLINT Acb integration](https://flintlib.org/doc/acb_calc/index.html), [the integration guide](https://flintlib.org/doc/acb_calc/integrate.html), and [Python-Flint Acb](https://python-flint.readthedocs.io/en/latest/acb.html). These specify complex-ball evaluation, holomorphy requests, and rigorous quadrature enclosures. Failure to reach a requested tolerance does not make a returned valid wide enclosure narrow. The verifier must explicitly reject nonfinite or insufficiently informative results.

## Fixed operator and exact trial

Fix

\[
T=1353/2048,\qquad a=7/2,\qquad \Omega=256,\qquad N=312.
\]

Write an exact rational trial in ordinary unnormalized Legendre polynomials as

\[
p(x)=\sum_{j=0}^{d}z_jP_j(x),\qquad
f(u)=T^{-1/2}p(u/T)\mathbf1_{(-T,T)}(u).
\]

The nonzero coefficient vector is part of the immutable mathematical input, not a floating-point eigenvector. Orthogonality gives the exact positive normalization

\[
D=\|f\|_2^2=\int_{-1}^1p(x)^2\,dx
 =\sum_{j=0}^{d}\frac{2z_j^2}{2j+1}>0.
\]

No factor of T occurs in D. Degree 20 means coefficients through index 20. A trial restricted to the C-0094 low space has degree at most 311, since N=312 counts degrees 0 through 311. The evaluator can also handle degree 312, but that trial then lies outside that specific compression. It remains a legitimate direction of the bounded operator H0.

Use the minus-sign transform

\[
I(w)=\int_{-1}^1p(x)e^{-iwx}\,dx,
\qquad \widehat f(t)=\sqrt T\,I(Tt).
\]

Suzuki's plus-sign convention interchanges t and -t. It does not change the energy below.

## Derivation of every contribution

For real p and real t, I(-Tt) is the conjugate of I(Tt). It follows from Parseval with measure dt/(2pi), the even real multiplier A, and the unitary scaling above that

\[
q_{\rm band}
 =\frac{T}{\pi}\int_0^{256}
 [A(t)-a]I(Tt)I(-Tt)\,dt,
\qquad
A(t)=\Re\psi(1/4+it/2)-\log\pi.
\]

The multiplier here is the exact digamma multiplier. An asymptotic log multiplier or a Bernoulli polynomial is not an interchangeable input. The factor T/pi includes both the Fourier factor 1/(2pi) and doubling the symmetric frequency band.

For a compressed shift of length ell, its quadratic form on a real trial is the overlap of the shifted functions. After u=Tx,

\[
\langle J_\ell f,f\rangle
 =\int_{-1}^{1-\ell/T}p(x)p(x+\ell/T)\,dx.
\]

There is no remaining T factor. At this support the active prime powers are precisely 2 and 3, and Lambda(m)=log(m) for both. Therefore

\[
q_P=-\sum_{m=2,3}\frac{2\log m}{\sqrt m}
 \int_{-1}^{1-\log(m)/T}p(x)p(x+\log(m)/T)\,dx.
\]

The factor 2 is already in c_m=2 log(m)/sqrt(m), not in the overlap integral a second time. The active-set assertion must be independently checked by strict enclosures log(3)<2T<log(4). Any omitted m at this support has zero von Mangoldt weight or disjoint supports. Equality at a support endpoint contributes only a null set.

The polar evaluations of the transform produce the signed product, not two positive squares. Put

\[
C=\int_{-1}^1p(x)\cosh(Tx/2)\,dx,\qquad
S_h=\int_{-1}^1p(x)\sinh(Tx/2)\,dx.
\]

Then

\[
q_{\rm pole}=2T(C^2-S_h^2)
 =2T I(iT/2)I(-iT/2).
\]

Indeed, I(iT/2)=C+S_h and I(-iT/2)=C-S_h. This is positive in the even sector and negative in the odd sector. Replacing it by an absolute square changes the operator.

The actual bounded-minorant energy is exactly

\[
q_0=aD+q_P+q_{\rm pole}+q_{\rm band},\qquad R_0=q_0/D.
\]

No compact-complement, Gram, Schur, or Taylor-residual allowance belongs in this directional identity. Those are obligations of a different sufficient whole-space proof. The complete finite band and every transcendental input to this displayed identity still need rigorous enclosures.

## Analytic continuation required by Acb

Acb integration requests values on complex balls around the real segment. The correct callback is the meromorphic continuation

\[
G(z)=\left[
 \frac{\psi(1/4+iz/2)+\psi(1/4-iz/2)}2
 -\log\pi-a\right]I(Tz)I(-Tz).
\]

Taking the real part of one digamma value, or using the conjugate of I(Tz), gives a nonholomorphic function of z. Those replacements are correct only on the real axis and cannot support analytic quadrature error bounds.

The digamma poles occur at z=+i(2k+1/2) and z=-i(2k+1/2), k a nonnegative integer. The open strip |Im z|<1/2 has no poles and contains the full integration path, including z=0. A sufficient conservative callback policy is to return an indeterminate complex ball on an analytic request unless the entire input rectangle has imaginary interval strictly inside (-1/2,1/2). Acb can then subdivide. This discards some harmless off-strip balls, but never asserts false holomorphy. The ordinary value request must also return a valid enclosure, or a nonfinite failure, never a value obtained by silently projecting its argument onto the real line.

There is no singularity of I at zero. Any inverse-power endpoint formula has only removable singularities there and must not be evaluated on a ball containing zero. The Taylor formula below works on such balls without division. Branching between two valid enclosures of the same entire I does not change the underlying function. The bounds and branch decision must hold on the whole supplied complex rectangle.

G is real on the real path. Hence the exact integral is real. Checking that the final imaginary ball contains zero is a consistency check; it is not the proof of realness. After that check its real projection encloses the desired integral. The T/pi multiplication must itself use rigorous Arb constants.

## A separate transform evaluator

Convert the ordinary Legendre expansion to an exact rational monomial polynomial using

\[
P_0=1,\quad P_1=x,\quad
(j+1)P_{j+1}=(2j+1)xP_j-jP_{j-1}.
\]

No transcendental evaluation occurs in this conversion. Exact moments follow from integrating each monomial, with odd powers integrating to zero. Let

\[
\mu_k=\int_{-1}^1p(x)x^k\,dx,
\qquad L=\sum_j|z_j|.
\]

Since |P_j(x)|<=1 on [-1,1], |mu_k|<=2L. The entire moment Taylor representation is

\[
I(w)=\sum_{k=0}^{M}\frac{\mu_k(-iw)^k}{k!}+E_M(w).
\]

For every point of a complex integration ball satisfying |w|<=r, and M+2>r,

\[
|E_M(w)|\le
\frac{2L\,r^{M+1}}{(M+1)!}
 \frac1{1-r/(M+2)}.
\tag{1}
\]

To prove (1), expand the exponential under the integral. The absolute tail is at most 2L times the tail of sum r^k/k!. The ratio of successive terms after k=M+1 is at most r/(M+2), so the geometric majorant gives (1). Uniform absolute convergence on each compact complex set justifies exchanging integration and summation. The alternative 2L exp(r)r^(M+1)/(M+1)! also works but is weaker. A rigorous upward bound on |w|, not just the midpoint modulus, is required. Add the remainder as a radius in both real and imaginary components, or use a genuine containing complex disk.

For a ball whose modulus lower bound is positive, repeated integration by parts terminates exactly at d and gives

\[
I(w)=\sum_{k=0}^{d}
 \frac{p^{(k)}(-1)e^{iw}-p^{(k)}(1)e^{-iw}}
 {(iw)^{k+1}}.
\tag{2}
\]

Compute the endpoint derivatives exactly. A separate formula check is

\[
P_j^{(k)}(1)=\frac{(j+k)!}{2^k k!(j-k)!},\quad
P_j^{(k)}(-1)=(-1)^{j+k}P_j^{(k)}(1)
\quad(0\le k\le j).
\]

Formula (2) is finite and has no truncation remainder. Arb/Acb arithmetic encloses the cancellation. It is structurally independent of the producer's 0F1 or spherical-Bessel transform. Near zero use (1); away from zero use (2). One practical overlap is Taylor on balls with |w| upper bound at most 16 and the endpoint formula when |w| lower bound is at least 8. A ball meeting neither condition can use a dynamically extended Taylor sum, or return indeterminate to request subdivision. It must never use a near-zero inverse power without a certified denominator bound.

## Precision and practical limits

There is no universally sufficient precision specified by degree alone. Rational coefficients can have arbitrary height and scale, and the requested sign margin can be arbitrarily small. The final exact interval width and sign, not a nominal precision, decide success.

Nevertheless cancellation can be bounded before execution. On a ball with |w|>=r0 and |Im w|<=h, define

\[
B=\frac{2L e^h}{r_0}
 \sum_{k=0}^{d}\frac{(d+k)!}{2^k k!(d-k)!r_0^k}.
\]

The sum of the absolute endpoint terms in (2) is at most B. All its factorials and rational powers are exact, so B gives a concrete coefficient-dependent precision planning bound. The implementation should reserve target absolute bits plus the binary size of B and arithmetic guard bits. Interval dependence on the input rectangle can still force subdivision even at high working precision.

For perspective, at r0=8 the elementary bound

\[
\frac{(d+k)!}{2^k k!(d-k)!8^k}
 \le 2^d(2d/8)^k
\]

follows by bounding a binomial coefficient by 2^(d+k) and (2k)!/k! by (2k)^k. If h<1, this bounds B by 2^85 L for d=20 and by 2^2507 L for d=312. These are deliberately conservative magnitude bounds, not observed losses. The strip policy above gives h<T/2<1 for the band-transform argument. Thus 1024 working bits is a reasonable starting policy for a modest-height degree-20 trial and a 512-bit absolute target. A 4096-bit policy pays a conservative degree-312 endpoint cancellation bound plus that target and guard space for modest L. Neither policy promises convergence or certifies a sign without checking actual output.

Near zero, M=384 and r<=16 give a remainder less than 2^(-1153)L by (1). One may use n!>=(n/e)^n, e<3, and 385/3>128 to check this bound. All moments and factorials can be cached exactly. A requested tighter enclosure needs a larger M; it must not simply relabel the fixed remainder as zero. The polynomial arithmetic and Taylor cost grow with the degree and M, but no degree-squared array of Fourier matrix entries is required for a single direction.

## Full input accounting and report acceptance

An independent directional audit must capture report and trial bytes once and derive its mathematical input from those captured images. It must reject duplicate JSON keys, nonfinite values, ordinary floating proof inputs, zero trials, altered fixed parameters, unexpected basis normalization, unsupported parity/dimension declarations, and changed source or trial identities. Exact rational arithmetic must reconstruct D, aD, every stored sum, normalization, and sign label.

The independent computation must enclose both active arithmetic overlaps, their log/square-root coefficients, the signed polar product, and the entire integral from 0 to 256. Exact polynomial antiderivatives after a shift, or a rigorously normalized unit-interval integral, avoid uncertain integration endpoints. For example, with delta=log(m)/T and length b=2-delta, substitute x=-1+by. The overlap is b times the integral from 0 to 1 of p(-1+by)p(-1+by+delta), whose coefficients are rigorously enclosed. No endpoint uncertainty is discarded.

All segment endpoints must be exact and cover [0,256] without gaps or overlaps. A point sample, a finite quadrature sum without its analytic error, an unproved transform truncation, or an imported producer total fails this obligation. The identity uses the exact full multiplier, so no additional source approximation is allowed unless its explicit entire-band error is included. If the producer uses the same exact multiplier, there is no Suzuki residual-series truncation charge to invent.

For stored energy intervals, mere overlap with fresh independent intervals is too weak to establish honest enclosure. Require fresh rigorous intervals to be contained in stored outward intervals, with exact equality permitted for exact rational quantities. The acceptance policy should bound the admitted report width and pin the captured trial hash separately. A report can honestly be wider than necessary; a broad interval cannot establish a strict sign. A bound with upper endpoint below zero proves negativity. A bound with lower endpoint above zero proves positivity of this direction only. Otherwise the result is inconclusive.

The audit receipt must name the actual independent transform method, working precision, Taylor order/remainder policy, quadrature tolerances and limits, complete segment coverage, number of checked components, captured report/trial hashes, and the remaining shared Suzuki/Python-Flint/FLINT trust premise. Source fingerprints are part of provenance, not a replacement for recomputation. Acceptance does not amend any production theorem whitelist or retained-proof registry.

## Complete matrix integration by an operator remainder

If directional probes are positive, a complete positive certificate needs the whole C-0094 finite criterion. The following alternative to scalar adaptive integration pays the full frequency band in operator norm. It is a written qualification of the procedure, not evidence that its matrix has been computed.

On scaled L2(-1,1), let F(z) have kernel

\[
\frac{T}{\pi}[A(z)-a]\cos(Tz(x-y)).
\]

For a panel [c-h,c+h], choose rho>h such that the closed disk |z-c|<=rho avoids the digamma poles. Schur's integral-kernel bound gives

\[
\sup_{|z-c|=\rho}\|F(z)\|
\le M=\frac{2T}{\pi}e^{2T\rho}
 \sup_{|z-c|=\rho}|A(z)-a|.
\]

The factor 2 is the length of the spatial interval. The exponential follows from |x-y|<=2. A finite complex-ball digamma enclosure on the enclosing rectangle is an admissible upper bound for the circle supremum. If that rectangle contains a pole or gives a nonfinite result, it is not an admissible finite bound.

Operator-valued Cauchy estimates bound the Taylor remainder after degree 2q-1 by M(h/rho)^(2q)/(1-h/rho) on the panel. Exact q-node Gauss-Legendre quadrature integrates that Taylor polynomial exactly. Its exact weights are positive and sum to 2h. The integral remainder and quadrature remainder therefore each have norm at most 2h times that bound. Consequently

\[
\left\|\int_{c-h}^{c+h}F(t)\,dt
 -\sum_{\nu=1}^{q}w_\nu F(t_\nu)\right\|
\le\frac{4hM(h/\rho)^{2q}}{1-h/\rho}.
\tag{3}
\]

The same argument works after finite compression. Summing (3) over panels pays the entire band, with no endpoint samples standing in for an integral. Panels [0,1/4], [1/4,1/2], [1/2,1], [1,2], [2,4], and the width-4 panels from 4 through 256 cover the band exactly. With rho=2h, the first two disks have imaginary radius 1/4<1/2. Every later disk has strictly positive real part, so it cannot contain a digamma pole on the imaginary axis. The enclosing rectangles obey the same exclusion. Formula (3) becomes 8hM times 2^(-2q). The actual outward M bounds and their sum, not a heuristic decay estimate, must appear in the source accounting.

At the exact real Gauss nodes, only real transform arguments are needed. For all degrees 0 through 311, an efficient independently organized reconstruction can start with anchors n=312 and n=313,

\[
j_n(w)=\frac{w^n}{(2n+1)!!}
 \sum_{k=0}^{K}\frac{(-w^2/4)^k}{k!(n+3/2)_k}
 +\text{bounded remainder},
\qquad I_n(w)=2(-i)^n j_n(w).
\]

For a containing real ball |w|<=170, put u=w^2/4 and b=n+3/2. The absolute first omitted hypergeometric term is u^(K+1)/[(K+1)!(b)_(K+1)]. The ratio of following terms is at most u/[(K+2)(b+K+1)]. If that ratio is below 1, dividing the first omitted term by one minus the ratio bounds the whole tail. This bound must be added before multiplying by the prefactor.

For K=384 and n>=312, u/b<24 and the first omitted term is less than 24^385/385!<2^(-770). The remaining ratio is below 1/16, giving a hypergeometric tail less than 2^(-769). This is an absolute bound for the hypergeometric series, not an absolute bound for the final j_n. The prefactor and all subsequent propagation must retain their radii.

The exact recurrence j_(n-1)=(2n+1)j_n/w-j_(n+1) reconstructs lower degrees. Node balls must strictly exclude zero. Interval propagation through the full downward recurrence pays the amplification of both anchor uncertainties. It is not valid to use the raw anchor tail as an unchanged error for each lower degree. Exact monomial moment Taylor evaluation is a possible independent fallback near zero. A verifier using finite series rather than the producer's special-function anchors has a distinct anchor evaluation and quadrature organization, but it still shares the Bessel identity and recurrence. This is weaker formula independence than the endpoint/moment direction evaluator above and must be disclosed.

Rigorous node and weight enclosures require independent root isolation or another proven Gauss construction. The exact roots must be identified completely and uniquely, with positive weights derived from the correct derivative formula. Numerical approximations alone are not a quadrature certificate. Node and weight interval uncertainty belongs in every resulting matrix enclosure in addition to the operator remainder (3).

If E is the total operator-norm integration remainder, its quadratic allowance in ordinary Legendre coordinates is E D, where D is the diagonal matrix with entries 2/(2j+1). It is not E times the coordinate identity. In an orthonormalized basis it becomes E times the identity. A full positive proof must then construct the actual low block A_N, the combined arithmetic Gram G_P including mixed prime terms, and the C-0094 charges

\[
A_N-\frac{G_P+3\cdot10^{-40}I}{19/8-10^{-82}}
\]

in one consistent Hilbert-space normalization. Only a rigorous positive certificate for this complete finite lower, together with C-0094's complement assumptions, establishes positivity of H0. Exact parity blocks can be handled separately because reflection commutes with every operator involved. Positive trial energies alone cannot replace this step.

## What a sign would mean

C-0094 proves a sufficient Schur lower criterion for H0. A negative value of that lower criterion is not a negative value of H0. This experiment instead evaluates the actual H0 identity above, without subtracting Schur charges.

A certified negative upper bound q0<0 on one nonzero rational polynomial proves that the chosen bounded minorant H0 is not positive semidefinite at these parameters. H0 is bounded on all L2(-T,T), so this conclusion does not require the discontinuous zero-extended polynomial to lie in a particular unbounded operator domain. Its normalized value has the same sign because D>0. Density also transfers the negative H0 value to nearby smooth compactly supported directions.

This does not prove negative Weil energy. The public source split is

\[
Q_W(f)=\langle H_0f,f\rangle+
 \frac1{2\pi}\int_{|t|>256}(A(t)-7/2)|\widehat f(t)|^2\,dt.
\]

C-0094 certifies that exterior multiplier nonnegative. Dropping it gives a lower bound, and the omitted energy can restore positivity. Conversely, positive energies on finitely many trials prove neither positivity of H0 on its whole space nor the sufficient Schur criterion. No result of this directional experiment proves or disproves RH, all-support Weil positivity, or superiority of this Fourier reference over another route.
