# Variable-parameter quadrature and source-enclosure map

- **Created:** `2026-10-26T02:04:35Z`
- **Last updated:** `2026-10-26T02:21:56Z`
- **Scope:** derived variable analytic bounds and conditional numerical-width requirements, not a new source implementation

This note gives sufficient analytic error bounds for the bounded Fourier band and the signed rank-two pole. It does not select a support, compute a low matrix, determine a matrix sign, or give a runtime, memory, or minimal-complexity claim. No support or matrix cases were executed for this note. Existing source and certificate records are unchanged.

## 1. Parameters, basis and source routines

Let $T>0$, $a\geq0$, and $\Omega>0$ be specified exactly. In the surrounding bounded-minorant construction, assume separately that the complete exterior is nonnegative, that $p$ bounds the complete arithmetic operator norm, and that $m=a-p>0$. None of the quadrature estimates below proves those premises. Write $c=T\Omega$ and retain degrees $0,\ldots,N-1$, where $N\geq1$.

Use $f(u)=T^{-1/2}v(u/T)$ and ordinary Legendre polynomials on $[-1,1]$. Their physical mass matrix is

$$D=\operatorname{diag}(D_j),\qquad D_j=\frac{2}{2j+1}.$$

The frequency-integrand operator $F(z)$ on $L^2(-1,1)$ has kernel

$$F(z;x,y)=\frac{T}{\pi}\,[A_{\mathbb C}(z)-a]\cos(Tz(x-y)),$$

$$A_{\mathbb C}(z)=\frac{\psi(1/4+iz/2)+\psi(1/4-iz/2)}2-\log\pi.$$

The band operator is $K_{\rm band}=\int_0^\Omega F(t)\,dt$. For real $t$, $A_{\mathbb C}(t)=\operatorname{Re}\psi(1/4+it/2)-\log\pi$. Taking the real part is valid on this real integration path. It is not the holomorphic definition at complex $z$.

The source patterns are the following existing routines.

- `scripts/weil_m4_fourier_matrix.py`: `panels`, `operator_error`, `band`, `bessel_vector`, `pole`, and `outward`.
- `scripts/verify_m4_fourier_matrix.py`: `gauss_rule`, `finite_hypergeometric`, `transform_vector`, `operator_error`, `band_matrix`, `pole_matrix`, `analytic_grid_radius`, and `numerical_order_loss`.

They use exact panel endpoints, enclosed Gauss nodes and weights, two entire-function anchors followed by downward recurrence, direct positive-argument pole transforms, and outward rational publication. The verifier's finite series includes indices $0$ through `terms`, inclusive. Its first omitted index is therefore `terms + 1`. Its present strict guard is $0<w<192$; the producer only requires $w>0$. These are descriptions of the current files, not a variable-range implementation contract. Their fixed panel table, multiplier envelope, orders, publication grid and working precision are not universal constants. This note changes none of those routines.

## 2. Pole exclusion and an explicit digamma envelope

The possible poles of $A_{\mathbb C}$ are

$$z=\pm i(2k+1/2),\qquad k=0,1,\ldots.$$

Thus the open strip $|\operatorname{Im}z|<1/2$ is pole-free. Fix any exact rational

$$0<\rho\leq\frac14.$$

All the panel disks below lie in the rectangle

$$-\rho\leq\operatorname{Re}z\leq\Omega+\rho,
\qquad |\operatorname{Im}z|\leq\rho.$$

For either $s=1/4\pm iz/2$, put

$$\delta=\frac14-\frac\rho2\geq\frac18,
\qquad L=\frac34+\frac\Omega2+\rho.$$

Then $\operatorname{Re}s\geq\delta$ and $|s-1|\leq L$. In particular no digamma denominator meets a pole, including at the leftmost panel near frequency zero.

[DLMF 5.7.6](https://dlmf.nist.gov/5.7.E6) gives the convergent identity

$$\psi(s)=-\gamma+\sum_{k=0}^{\infty}
\left(\frac1{k+1}-\frac1{k+s}\right)
=-\gamma+\sum_{k=0}^{\infty}\frac{s-1}{(k+1)(k+s)}.$$

For the $k=0$ summand use $L/\delta$. For $k\geq1$ use

$$\left|\frac{s-1}{(k+1)(k+s)}\right|
\leq\frac{L}{k(k+1)}.$$

The latter series telescopes to $L$. Since $0\leq\gamma\leq1$ and $0<\log\pi<2$, the following entirely explicit envelope is valid throughout that rectangle:

$$\boxed{B(a,\Omega,\rho)=a+3+L\left(\frac1\delta+1\right),
\qquad |A_{\mathbb C}(z)-a|\leq B.}$$

The elementary bounds on $\gamma$ follow from harmonic-sum minus logarithm bounds; $\pi<4<e^2$ gives the stated logarithm bound. These loose constants avoid any precision assumption about computing $\gamma$ or $\log\pi$ merely to obtain $B$.

There is also a finite, certified evaluation formula. If the first $K\geq1$ summands, indexed $0,\ldots,K-1$, are evaluated with interval arithmetic, the remaining complex disk has radius at most

$$\boxed{|R_K(s)|\leq\frac{L}{K}.}$$

Indeed, $\sum_{k=K}^{\infty}1/[k(k+1)]=1/K$. To obtain a tail radius at most $\tau_\psi>0$, it suffices to take $K\geq\max(1,\lceil L/\tau_\psi\rceil)$. Any uncertainty in $\gamma$ and the finite sum is separate from this tail. For $A_{\mathbb C}$ the average of the two remainder bounds is still $L/K$, not $2L/K$. This is a proved, if conservative, alternative to a signed asymptotic digamma tail; it does not assume the earlier fixed envelope remains valid.

## 3. Exact panels, complete operator error and a sufficient Gauss order

Set

$$J=\left\lceil\frac\Omega\rho\right\rceil,
\qquad t_j=\frac{j\Omega}{J}\quad(0\leq j\leq J),
\qquad h=\frac\Omega{2J}\leq\frac\rho2.$$

Use the $J$ panels $[t_{j-1},t_j]$, each with center $s_j$ and half-length $h$. The disk $|z-s_j|\leq\rho$ is pole-free and contains its panel with $h/\rho\leq1/2$. This panel count is sufficient only. It is not necessary or optimal. If $\Omega$ and $\rho$ are rational then every endpoint is rational, exactly as in the existing panel representation. For general exact real inputs the same mathematical endpoints apply, but an implementation must enclose their uncertainty and certify the ceiling defining $J$. Approximate floating-point endpoints do not become exact by declaration.

For $|z-s_j|\leq\rho$, the elementary exponential formula for cosine gives

$$|\cos(Tz(x-y))|\leq e^{2T\rho},\qquad -1\leq x,y\leq1.$$

The integral operator norm of a kernel bounded by $C$ on this square is at most $2C$, by the Schur bound. Consequently

$$\boxed{\|F(z)\|\leq M=\frac{2T}{\pi}B(a,\Omega,\rho)e^{2T\rho}.}$$

The operator-valued kernel is holomorphic on a neighborhood of each closed disk. Its Taylor coefficients at $s_j$ have norms at most $M\rho^{-k}$, by Cauchy's coefficient bound. Subtract its Taylor polynomial of degree $2q-1$. The remaining norm anywhere on the panel is at most

$$M\frac{(h/\rho)^{2q}}{1-h/\rho}\leq2M\,2^{-2q}.$$

A $q$-node Gauss-Legendre rule is exact through degree $2q-1$, has positive weights, and its weights on a panel sum to $2h$. These facts are stated in [DLMF 3.5(v), especially 3.5.20_1](https://dlmf.nist.gov/3.5#v). Both the integral and the quadrature sum of the Taylor remainder have norm at most $2h$ times the displayed uniform remainder. Therefore the complete panel-operator error, not just an entry error, obeys

$$E_j\leq8hM\,2^{-2q}.$$

Summing panels proves

$$\boxed{\|K_{\rm band}-Q_q\|\leq E_{\rm quad}
=\frac{8T\Omega}{\pi}B(a,\Omega,\rho)e^{2T\rho}2^{-2q}.}$$

More generally a panel of half-length $h_j<\rho_j$ and disk envelope $M_j$ contributes at most

$$4h_jM_j\frac{(h_j/\rho_j)^{2q_j}}{1-h_j/\rho_j}.$$

For a declared absolute operator tolerance $\epsilon_{\rm quad}>0$, define

$$C_{\rm quad}=\frac{8T\Omega}{\pi}B(a,\Omega,\rho)e^{2T\rho}.$$

An explicit sufficient integer order is

$$\boxed{q\geq\max\left(1,
\left\lceil\frac12\log_2\frac{C_{\rm quad}}{\epsilon_{\rm quad}}\right\rceil\right).}$$

In exact certification it is enough to verify $2^{2q}\epsilon_{\rm quad}\geq\overline C_{\rm quad}$ with an outward upper bound $\overline C_{\rm quad}$. This avoids trusting a rounded logarithm near an integer threshold. The bounds are variable in $T,a,\Omega$; in particular the factor $e^{2T\rho}$ cannot be discarded as $T$ changes. This is an analytic order formula, not a wall-clock or precision formula.

The proof concerns exact Gauss roots and weights. Their computed balls must identify the correct simple roots, remain disjoint, and enclose the positive weights. The existing checker obtains weights from $2/[(1-x^2)P_q'(x)^2]$ with interval denominators excluding zero. Node and weight widths, multiplier evaluation widths and all subsequent arithmetic are paid separately below.

## 4. Full $0F_1$ tails for Fourier and pole transforms

For $n\geq0$ put $b=n+3/2>0$ and $d_n=(2n+1)!!$. The exact transforms used by the source are

$$j_n(w)=\frac{w^n}{d_n}\,{}_0F_1\left(;b;-w^2/4\right),
\qquad \int_{-1}^1P_n(x)e^{-iwx}\,dx=2(-i)^n j_n(w),$$

and, with $\alpha=T/2$,

$$\ell_n(\alpha)=\int_{-1}^1P_n(x)e^{\alpha x}\,dx
=\frac{2\alpha^n}{d_n}\,{}_0F_1\left(;b;+\alpha^2/4\right).$$

These identities also follow directly from Rodrigues' formula and termwise integration of the exponential. The underlying hypergeometric series and its entire convergence are [DLMF 16.2.1 and 16.2(ii)](https://dlmf.nist.gov/16.2#i). No asymptotic or alternating-series cancellation is needed for the bounds below.

For any complex $u$ with $|u|\leq U$, sum the terms indexed $0,\ldots,K$, where $K\geq0$. Set

$$t_k(U,b)=\frac{U^k}{k!(b)_k},\qquad
r_K(U,b)=\frac{U}{(K+2)(b+K+1)}.$$

If $r_K<1$, then

$$\boxed{\left|{}_0F_1(;b;\pm u)-\sum_{k=0}^{K}
\frac{(\pm u)^k}{k!(b)_k}\right|
\leq R_K(U,b)=\frac{t_{K+1}(U,b)}{1-r_K(U,b)}.}$$

The first omitted term is exactly $t_{K+1}$ as a magnitude majorant. Each following ratio is at most $r_K$, since $(k+1)(b+k)$ increases with $k$. The result applies to both signs, all finite $U$, and every integer order $n\geq0$. If $U=0$ the tail is zero. Finite-sum evaluation error is not part of $R_K$.

Here is one closed sufficient truncation policy for any desired $0F_1$ tail $\tau>0$. Choose the first omitted index $L_0=K+1$ to satisfy

$$\boxed{L_0\geq\max\left(1,\left\lceil\frac{6U}{b}\right\rceil,
\left\lceil\log_2\frac2\tau\right\rceil\right).}$$

Indeed, $(b)_{L_0}\geq b^{L_0}$ and $L_0!\geq(L_0/e)^{L_0}$ give $t_{L_0}\leq[3U/(bL_0)]^{L_0}\leq2^{-L_0}$. Also $r_K\leq U/[b(L_0+1)]\leq1/6$, so $R_K\leq(6/5)2^{-L_0}<2^{1-L_0}\leq\tau$. The exact first-omitted test usually permits fewer terms; the closed policy is only sufficient. It proves a finite choice exists rather than instructing the reader merely to choose an unspecified small tail.

For Fourier quadrature, each exact positive node has $0<w=Tt<c$. A certified node enclosure is $W=[w_-,w_+]\subset(0,\infty)$. Use $U=w_+^2/4$, not a node midpoint. For either anchor $n=N,N+1$, its absolute truncation error is at most

$$e_n^{\rm tail}=\frac{w_+^n}{d_n}R_K(w_+^2/4,n+3/2).$$

To require $e_n^{\rm tail}\leq\eta_n$, apply the closed policy with $\tau=\eta_n d_n/w_+^n$. The prefactor and the power must themselves be enclosed when computed. For all nodes simultaneously, $w_+\leq\overline c$ is a sufficient upper argument bound if proved for those enclosures. There is no universal replacement for a fixed argument guard without this check.

For the pole, take an enclosure $0\leq\alpha\leq\alpha_+$ and $U=\alpha_+^2/4$. The direct transform error for every required order is

$$e_n^{\rm pole,tail}\leq\frac{2\alpha_+^n}{d_n}R_K(\alpha_+^2/4,n+3/2).$$

The same formula applies if two high-order pole anchors are used, but the present routines evaluate all pole orders directly. A common sufficient tail bound may use $b\geq3/2$; each prefactor still depends on $n$. No fixed pole-series order is valid for all $T$. The signed pole matrix remains, in each parity block,

$$K_{\rm pole,ij}=2T(-1)^i\ell_i(T/2)\ell_j(T/2),$$

with opposite-parity entries exactly zero. The even sign is positive and the odd sign negative. These truncation bounds change neither that sign nor the exact rank-two operator.

## 5. Downward recurrence with uncertain argument

The exact Fourier recurrence is

$$j_{n-1}(w)=\frac{2n+1}{w}j_n(w)-j_{n+1}(w),
\qquad n=N,N-1,\ldots,1.$$

For $W=[w_-,w_+]\subset(0,\infty)$, form the full coefficient interval

$$A_n=\left[\frac{2n+1}{w_+},\frac{2n+1}{w_-}\right].$$

Given valid anchor balls $J_N,J_{N+1}$, the outward interval operation

$$J_{n-1}=A_nJ_n-J_{n+1}$$

contains the exact result for every $w\in W$. Reusing the same uncertain $w$ creates dependence, but losing that dependence by interval multiplication only widens the enclosure. Replacing the denominator by the midpoint of $W$ without an explicit variation bound is invalid.

A scalar propagation certificate makes the amplification visible. Choose rational representatives $\widehat j_n$ and $\widehat a_n\in A_n$, define

$$a_n^+=\frac{2n+1}{w_-},\qquad
\Delta a_n=\max\{|\inf A_n-\widehat a_n|,|\sup A_n-\widehat a_n|\},$$

$$r_{n-1}=\left|\widehat j_{n-1}-
(\widehat a_n\widehat j_n-\widehat j_{n+1})\right|.$$

Use an outward upper bound for the residual if it is not computed exactly. If $e_n$ encloses $|j_n(w)-\widehat j_n|$ on $W$, then

$$\boxed{e_{n-1}\leq a_n^+e_n+e_{n+1}
+\Delta a_n|\widehat j_n|+r_{n-1}.}$$

All reciprocal bounds use $w_-$ and $w_+$, never a midpoint denominator. For example,

$$\Delta a_n\leq\frac{(2n+1)(w_+-w_-)}{w_-w_+}
\leq\frac{(2n+1)(w_+-w_-)}{w_-^2}.$$

Writing $v_n=(e_n,e_{n+1})^t$ and

$$H_n=\begin{pmatrix}a_n^+&1\\1&0\end{pmatrix},\qquad
 g_n=\Delta a_n|\widehat j_n|+r_{n-1},$$

gives $v_{n-1}\leq H_nv_n+(g_n,0)^t$ componentwise. Thus

$$v_0\leq H_1H_2\cdots H_Nv_N
+\sum_{n=1}^{N}H_1\cdots H_{n-1}(g_n,0)^t,$$

where the product before $g_1$ is the identity. Partial products give the bound at every retained order. This is a computable, finite propagation formula including both anchors, argument uncertainty, and local arithmetic residuals. Even tiny anchor tails can be amplified substantially when $w_-$ is small.

To isolate analytic truncation from working width, compare the exact recurrence from the exact anchors with the exact recurrence from the finite-series anchors at the *same* $w$. Their difference obeys

$$e_{n-1}^{\rm tail}\leq a_n^+e_n^{\rm tail}+e_{n+1}^{\rm tail}.$$

There are no coefficient-variation or rounding sources in this particular comparison. Use the $H_n$ products on the two anchor tail bounds. Separately enclose the finite-series recurrence over $W$ to pay input widths and arithmetic. The Fourier transform components are $v_n=2(-1)^{\lfloor n/2\rfloor}j_n$ within either parity block, so their radii are twice the corresponding $j_n$ radii. It is incorrect to carry the $0F_1$ tail unchanged to all final components.

A Gauss rule has strictly interior exact nodes, so the first panel also has $w>0$. Nevertheless its computed ball must certify $w_->0$. If it does not, refine the input/node enclosure or evaluate the entire series for the required modes directly. At $w=0$, $j_0(0)=1$ and $j_n(0)=0$ for $n>0$; division through an interval containing zero is not a limit argument. Direct entire evaluation uses the same tail bound and needs no recurrence denominator.

## 6. From source radii to matrix radii

For a real same-parity quadrature term write $\beta vv^t$, where

$$\beta=\frac{T}{\pi}h\lambda[A_{\mathbb C}(t)-a],$$

$\lambda$ is a Gauss-Legendre weight on $[-1,1]$, and $v$ is the real signed transform vector just described. Suppose rational centers and certified errors satisfy

$$|\beta-\widehat\beta|\leq d_\beta,
\qquad |v_i-\widehat v_i|\leq d_i.$$

Its entry radius about $\widehat\beta\widehat v_i\widehat v_j$ is bounded by

$$\boxed{|\widehat\beta|
(|\widehat v_i|d_j+|\widehat v_j|d_i+d_id_j)
+d_\beta(|\widehat v_i|+d_i)(|\widehat v_j|+d_j).}$$

Sum over all nodes. This follows by adding and subtracting $\widehat\beta v_iv_j$ and using the product identity; it remains valid for negative band multipliers. It accounts for node, weight, multiplier, $T$, and recurrence uncertainties whenever the stated input radii account for them.

For the analytic finite-series error alone, compare the exact-node finite-prefix vector with the exact vector. Replace $|\widehat\beta|$ by a certified $|\beta|$ bound, $|\widehat v_i|$ by a bound on the exact finite-prefix component, and $d_i$ by its propagated tail radius. There is no coefficient error term in this comparison. The pole uses the same product bound with coefficient $2T(-1)^i$ and direct pole tail radii. Bounds on finite-prefix values may be obtained from their interval evaluations. For an explicit a priori magnitude majorant, $|{}_0F_1(;b;\pm u)|\leq e^{U/b}$ follows from $(b)_k\geq b^k$, so $|j_n(w)|\leq w_+^ne^{U/b}/d_n$; finite prefixes obey the same absolute-sum majorant. These formulas make matrix-tail bounds computable without relying on cancellation.

## 7. Physical-mass interval-to-Loewner conversion

If a self-adjoint operator error has norm at most $E$, its ordinary Legendre form matrix satisfies

$$\boxed{-ED\preceq\Delta\preceq ED.}$$

Indeed $\|\sum x_jP_j\|_{L^2(-1,1)}^2=x^*Dx$. This gives the correct correlated analytic allowance $E_{\rm quad}D$. Cauchy-Schwarz also gives valid individual entry radii $E_{\rm quad}\sqrt{D_iD_j}$, as used by the checker. Those individual radii do not retain the operator correlation if treated as an arbitrary independent interval matrix.

For a symmetric entry-error table $r_{ij}=r_{ji}\geq0$, with $|\Delta_{ij}|\leq r_{ij}$, define

$$s_i=\sum_jr_{ij},\qquad
\delta_{\rm row}=\max_i\frac{s_i}{D_i}.$$

The inequality $2|x_ix_j|\leq|x_i|^2+|x_j|^2$ proves

$$-\operatorname{diag}(s_i)\preceq\Delta\preceq\operatorname{diag}(s_i),
\qquad \boxed{-\delta_{\rm row}D\preceq\Delta\preceq\delta_{\rm row}D.}$$

Another valid choice, sometimes smaller, is

$$\delta_{\rm normrow}=\max_i\sum_j\frac{r_{ij}}{\sqrt{D_iD_j}}.$$

This is the symmetric normalized row-sum bound for $D^{-1/2}\Delta D^{-1/2}$. Use outward square-root bounds if computing it. Either conversion applies separately in each parity block. For arbitrary independent radii $r_{ij}=E\sqrt{D_iD_j}$ in a block of size $k$, the latter bound is $kE$, not $E$. An implementation may retain the proved analytic $ED$ allowance outside the interval table to avoid that artificial loss. If it folds all analytic errors into independent entry intervals, it must instead pay a valid independent-entry conversion.

These are error enclosures about a specified center, not a statement that a matrix of componentwise lower endpoints is a Loewner lower bound.

## 8. Independent accuracy budgets and the precision limitation

Fix a declared total source allowance $\epsilon_{\rm src}>0$ and positive sub-budgets

$$\epsilon_{\rm quad}+\epsilon_{\rm series}
+\epsilon_{\rm work}+\epsilon_{\rm pub}\leq\epsilon_{\rm src}.$$

Keep the four errors distinguishable.

1. Analytic quadrature uses the complete operator bound in section 3. Analytic series truncation uses the first-omitted bounds, recurrence propagation and matrix-product bounds in sections 4 through 6, followed by a valid mass conversion. Require its resulting scalar allowance $\delta_{\rm series}\leq\epsilon_{\rm series}$. If a finite digamma formula from section 2 is used in place of a certified library call, its proved $L/K$ tail must also enter the analytic allowance. It is not free working precision.
2. Arithmetic working width encloses the *finite analytic approximant* before analytic tails and publication expansion. Include finite-series rounding and cancellation, power and prefactor widths, uncertain $w$, all node and derivative-weight widths, digamma-library widths, $\pi$, $\log\pi$, parameter/enclosure endpoints, scalar products, accumulation, and recurrence residuals. Choose rational centers for the resulting finite-approximant intervals, convert their radii using section 7, and require $\delta_{\rm work}\leq\epsilon_{\rm work}$. If $T,a,\Omega$ are nonrational inputs, all supplied input widths and panel-endpoint widths belong here as well. For a variable endpoint an interval-integral enclosure, or the norm bound times its endpoint uncertainty, must cover the change in the integration domain.
3. Publication rounding enlarges those intervals outward to a rational grid $g=2^{-b}$. Each endpoint moves by less than $g$, so an additional radius $g$ about the prepublication center is safe. If opposite-parity zeros remain exact, let $k$ be the largest retained parity-block size. Since $D_i\geq2/(2N-1)$, a sufficient uniform publication allowance is

   $$\boxed{\delta_{\rm pub}\leq\frac{k(2N-1)}2\,2^{-b}.}$$

   In particular it suffices that

   $$b\geq\max\left(0,\left\lceil\log_2\frac{k(2N-1)}{2\epsilon_{\rm pub}}\right\rceil\right).$$

   Outward rounding of separately published analytic radii also costs grid units and must be counted. Publishing a rational scalar analytic allowance outside the entry table avoids pretending these ceilings are exact.

With analytic operator correlation retained, a valid combined enclosure about the chosen finite-approximant center $\widehat Q$ is

$$\boxed{\widehat Q-
(E_{\rm quad}+\delta_{\rm series}+\delta_{\rm work}+\delta_{\rm pub})D
\preceq K_{\rm band}+K_{\rm pole}
\preceq\widehat Q+
(E_{\rm quad}+\delta_{\rm series}+\delta_{\rm work}+\delta_{\rm pub})D.}$$

Here $\widehat Q$ includes the pole and band approximants. Other source matrices require their own enclosures before being added. Analytic truncation, working width, and publication rounding cannot substitute for one another. In particular, increasing working precision does not reduce a fixed analytic Gauss or series remainder, and increasing the publication bit count does not repair a wide working interval.

There is no guaranteed $p_{\rm work}$-bit law in this note. Such a law needs proved quantitative bounds on at least the input enclosure widths, the smallest positive enclosed node argument $w_-$, the products $H_n$, finite-sum cancellation and intermediate magnitudes, the separation and derivative lower bounds used in Gauss-root/weight certification, digamma evaluation error, and accumulation/rounding errors of the actual implementation. Irreducible input width cannot be removed by extra arithmetic bits. A claimed precision sufficient to decide a subsequent positivity predicate would also need a proved positive conditioning or spectral-gap margin for that predicate. No such margin is supplied here.

The formulas give finite analytic choices for every specified finite parameter tuple and positive analytic tolerance. They do not establish low-matrix positivity, a uniform arithmetic working precision, acceptance of a new parameter range by the current scripts, or any runtime or RAM scaling law.
