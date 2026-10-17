# Source audit: rigorous mixed-Gram primitives and the subinterval logarithmic-moment gap

- **Finding ID:** F-20261017-008
- **Created:** 2026-10-17T14:02:16Z
- **Last updated:** 2026-10-17T14:04:10Z
- **Type:** OPEN_REQUIREMENT / source-grounded mathematical and interval-computation feasibility audit
- **Status:** VERIFIED source capabilities and elementary analytical reduction; **NOT IMPLEMENTED OR BENCHMARKED** as a complete mixed-Gram evaluator
- **Research source revision:** `a18746e437b52cdd0a3f0d4af1654df116be28de`, with the earlier `F-20261017-007` documentation uncommitted and preserved
- **Scope:** Audit existing mathematical primitives and precise validity/conditioning boundaries. No production, certificate, Rust, Lean, support sweep, theorem admission, or private plan changes.

## Executive finding

The conditional combined low-to-tail criterion and exact image-Gram identity are established in `C-0063..C-0066`; `F-20261017-007` shows that a **rigorous cancellation-sensitive upper bound** on the *combined* Gram (or an equivalent directly justified Schur lower bound) would be useful, without establishing that a complete exact mixed-Gram evaluator is necessary.

Inspection of the current source resolves the three **truncated-residual** cross terms differently:

| Pairing | Mathematical calculation available from existing primitives | Current complete rigorous mixed-matrix interface | Main qualification |
|---|---|---|---|
| `V × R_K` | **YES**: `R_K P_j` is an exact rational polynomial; `_potential_matrices` supplies grouped exact full-interval \(v(x)\) polynomial-product moments for arbitrary exact input polynomials | **NO** preassembled mixed matrix | Conversion, cross-argument extraction and conditioning at large degrees not yet verified |
| `P × R_K` | **YES**: arithmetic `P P_i` is a rigorously represented piecewise local-Legendre polynomial; `R_K P_j` is exact polynomial, so cellwise local-Legendre pairing reduces to existing orthogonal polynomial inner products | **NO** preassembled mixed matrix | Existing assembly routines assume symmetric same-operator matrices; an **ordered mixed** \(M_{PR_K}\) must not be incorrectly symmetrized |
| `V × P` | **ANALYTICAL REDUCTION EXISTS**, but the existing `_potential_matrices` is **whole-interval**, whereas \(P P_j\) is polynomial only *on translated subintervals* | **NO** | Certified **subinterval logarithmic polynomial moments**, particularly at exact \(x=\pm1\) endpoints and Arb-enclosed moving interior breakpoints, are not supplied by the current source |

The full \(R_T\) is **not** \(R_K\). Its rigorous remainder can be handled by the **existing** \(\delta_K\) operator norm and the previously proved Young inequality once an enclosure for the *combined truncated* Gram is available. No additional analytic representation of the full residual is required merely to obtain a conservative upper enclosure.

**No current source demonstrates a complete cancellation-sensitive combined-Gram matrix upper enclosure, or its stability at \(N=192/196\).** The available building blocks do not prove that new integration *infrastructure* is necessary; they identify a **narrow missing weighted cell-moment capability** if the full mixed-Gram route is deliberately selected.

## 1. Exact calculation and normalization to preserve

Let \(\ell_i=P_i\), \(d_i=2/(2i+1)\), \(D_N=\mathrm{diag}(d_i)\), \(Q_N=I-\Pi_N\), \(P=P_T\), and \(R_K=R_{T,K}\). On each low mode \(i<N\), set
\[
 v_i(x)=v(x)\ell_i(x),\qquad
 p_i(x)=P\ell_i(x),\qquad
 r_{K,i}(x)=R_K\ell_i(x),
 \quad v(x)=-\tfrac12\log(1-x^2).
\]
Define \(W_K=V+P+R_K\), \(K_X(i,j)=\langle\ell_i,X\ell_j\rangle\), \(M_{XY}(i,j)=\langle X\ell_i,Y\ell_j\rangle\). With conjugate-linear first inner-product argument, the *unnormalized coordinate* Gram is
\[
 \boxed{\displaystyle
 G_{K,\mathrm{coord}}
  =\sum_{X,Y\in\{V,P,R_K\}}M_{XY}
     -\Bigl(\sum_XK_X\Bigr)D_N^{-1}
             \Bigl(\sum_YK_Y\Bigr).
 }\tag{1.1}
\]
All six **ordered** off-diagonal \(VP,PV,VR_K,R_KV,PR_K,R_KP\) pairings and their exact projection products must be retained. \(P\) already includes all active signed prime-power terms, including mixed \(2/3\) contributions in the current first window. Exact opposite-parity zeros may be imposed only after the existing parity argument.

Individual mixed \(M_{XY}\) generally are **not symmetric**: \(M_{YX}=M_{XY}^*\). Therefore symmetric assembly of a **single ordered mixed term** by copying its upper triangle is mathematically invalid. Symmetrize only after adding the correctly oriented adjoint pair.

For each matrix entry, \(M_{VP}\), \(M_{VR_K}\) and \(M_{PR_K}\) are ordinary integrals of \(L^2\) images; no global domain assumption for an operator square is needed.

## 2. Cross term `V R_K`: whole-interval grouped moments suffice algebraically

The current `scripts/cert/multi_prime_legendre_schur.py::_residual_truncation_operator` constructs **exact** `fmpq_poly` images \(r_{K,j}=R_K\ell_j\) by applying its `_abs_power_action` to exact monomials. Thus
\[
 (M_{VR_K})_{ij}
  =-\tfrac12\int_{-1}^1
       \log(1-x^2)\ell_i(x)r_{K,j}(x)\,dx.
 \tag{2.1}
\]
Because the integrand is the logarithmic potential multiplied by the product of two exact rational polynomials, the already implemented grouped harmonic-moment contraction in `_potential_matrices` applies *mathematically* to an expanded finite collection containing \(\ell_i\) and \(r_{K,j}\), without developing new integration formulas. The existing routine uses exact rational harmonic contractions **before** converting to Arb, and exact coefficient parity zero checks.

**Audit boundary:** It does not currently produce a rectangular/mixed `VR_K` output or automatically expose all residual images from the public assembler. An arbitrary-polynomial collection/extraction is possible in principle, but the stable behavior of large exact residual polynomials at \(N=192/196\) has not been benchmarked for this cross pairing. Source-level representability is not an executed high-dimensional enclosure.

## 3. Cross term `P R_K`: reuse local Legendre cell pairing, not symmetry shortcuts

`scripts/cert/prime_power_terms.py` provides `PrimePowerOperatorAssembly.images`, a rigorously enclosed family of **combined signed arithmetic** piecewise polynomials in each cell's Legendre coordinate \(t=(x-c)/r\); the breakpoints are ordered and supported by certified Arb comparisons. `_affine_legendre`, `_local_basis` and `_legendre_inner` implement the affine change of basis and exact local Legendre norms (with Arb coefficients).

An exact rational polynomial \(r_{K,j}\) may likewise be evaluated in the same local basis. Therefore
\[
 (M_{PR_K})_{ij}
   =\sum_{\mathrm{cells}\ [a,b]}
       \frac{b-a}{2}\sum_{k\ge0}
          \frac{2}{2k+1}\,
             p_{i,[a,b],k}\,r_{K,j,[a,b],k},
 \tag{3.1}
\]
with implicit zero padding, is the mathematically exact cell-inner-product formula. Arb products and sums can enclose the coefficients, widths and polynomial cell Jacobian *provided the existing strict partition checks succeed*. There is no new transcendental integral in \(PR_K\) apart from the already enclosed translated endpoints/coefficients.

**Audit boundary:** The current `_low_matrix_from_images` and `_operator_square_matrix_from_images` write symmetric same-family matrices, so directly misusing them to generate an **ordered** \(PR_K\) matrix would be invalid. A narrowly scoped cross-family evaluation/combination is needed if that computation is selected; it is **not** a new mathematical integration primitive. No new code or full-dimensional stability verification is performed here.

## 4. Cross term `V P`: the distinct subinterval logarithmic moment

For each existing certified arithmetic cell \([a,b]\), \(p_j(x)=P\ell_j(x)\) is a polynomial in \(x\) on that cell with coefficient intervals inherited from the active shift geometry. Therefore
\[
  (M_{VP})_{ij}
    =-\tfrac12\sum_{\mathrm{cells}\ [a,b]}
       \int_a^b \log(1-x^2)\,\ell_i(x)p_j(x)\,dx.
 \tag{4.1}
\]
The **whole-interval** moment \(\int_{-1}^1x^nv(x)dx\), as implemented by `_potential_matrices`, cannot generally recover each truncated cell moment. In particular, the moving interior cell boundaries depend on \(\tau_m=\log(m)/T\), and the full-interval parity/harmonic expressions do not encode these boundary terms.

### An exact elementary mathematical reduction

For every integer \(n\ge0\), let
\[
 F_n^-(x)=
  \frac{(x^{n+1}-1)\log(1-x)
          -\displaystyle\sum_{j=1}^{n+1}\frac{x^j}{j}}
       {n+1},\quad -1\le x<1,
\]
\[
 F_n^+(x)=
  \frac{(x^{n+1}-(-1)^{n+1})\log(1+x)
          -\displaystyle\sum_{k=0}^{n}
                  \frac{(-1)^kx^{n-k+1}}{n-k+1}}
       {n+1},\quad -1<x\le1.
\tag{4.2}
\]
Polynomial division/integration by parts verifies, on \((-1,1)\),
\[
 (F_n^-)'=x^n\log(1-x),\qquad
 (F_n^+)'=x^n\log(1+x).
\]
Thus the weighted cell monomial moments have the **closed elementary form**
\[
 \boxed{\displaystyle
 \int_a^b x^nv(x)\,dx
  =-\tfrac12\bigl[
      F_n^-(b)-F_n^-(a)
      +F_n^+(b)-F_n^+(a)
     \bigr].
 }\tag{4.3}
\]
Where \(b=1\), use the analytic removable limit
\[
 F_n^-(1)=-\frac{H_{n+1}}{n+1};
\]
where \(a=-1\), use the analogous **finite polynomial** limit of \(F_n^+(-1)\). **Do not naively evaluate a zero factor multiplied by \(\log0\)** using an Arb endpoint interval. At strictly interior Arb-enclosed breakpoints, every log argument must be proved positive throughout its enclosure; otherwise reject the evaluation, do not guess a branch or midpoint.

The formulas prove **analytical representability** using rational operations, harmonic numbers and the already installed Arb \(\log\) / \(\log1p\). They do **not** by themselves prove a high-degree, well-conditioned implementation: converting hundreds of local Legendre coefficients into a global monomial basis could cause catastrophic cancellation. Correctness requires verified coefficient dependence, exact endpoint limits, and outward enclosures under inexact shift breakpoints.

### Local API and small independent overlap check

The installed locked environment reports `python-flint 0.9.0`, `acb.integral` available, and `arb.integral` unavailable. Official python-flint documentation warns that `acb.integral` callbacks must explicitly enforce analyticity when logarithmic branches are involved; it is **not** a license to integrate through \(x=\pm1\) singularities without a separate analytic endpoint treatment.

A **limited, non-persistent** Arb smoke check evaluated the \(n=0\) antiderivative at the rational interior split \(x=1/3\), using the correct removable limits at \(x=\pm1\), and compared the combined split integral against the independent existing `_potential_matrices([[1]])` whole-interval enclosure. The bounds overlapped (both enclosed approximately `0.613705638880109...`, consistent with \(2-2\log2\)). This checks **only low-degree normalization and a rational interior split**; it does not establish correctness for uncertain moving breakpoints, arbitrary polynomial degree, or target 192/196 conditioning.

Official API source: https://python-flint.readthedocs.io/en/latest/acb.html (integration, analyticity flag and log-branch handling). The local code capability is grounded in the installed version rather than assuming a future library feature.

## 5. The full Suzuki residual can be bounded without computing full residual cross integrals

As established in `C-0065`, let
\[
 R_T=R_K+E_K,\quad \|E_K\|\le\delta_K,\quad
 B_K=Q_N(V+P+R_K)|_{E_N}.
\]
Then for any **exact** \(\eta>0\),
\[
 \boxed{\displaystyle
 B^*B\preceq(1+\eta)B_K^*B_K+
                   (1+\eta^{-1})\delta_K^2I_{E_N}.}
 \tag{5.1}
\]
The existing `_suzuki_residual_tail_radius` and `_residual_truncation_operator` provide rigorous \(\delta_K\) when \(2T<\pi\). No additional full-kernel double integral is required for this particular conservative enclosure. The parameter \(\eta\) must be **specified and rigorously represented** when applied; varying it without a separate justified comparison is not a proof.

In **unnormalized Legendre coordinate matrices**, (5.1) becomes
\[
 \boxed{\displaystyle
 G_{\mathrm{full,coord}}
   \preceq(1+\eta)G_{K,\mathrm{coord}}
           +(1+\eta^{-1})\delta_K^2D_N.}
 \tag{5.2}
\]
Using \(\delta_K^2 I\) directly on the unnormalized coordinate matrix would be wrong. Similarly the existing low `A` is already a conservative **lower** bound \(\underline A=A_K-\delta_KD_N\), not the exact \(A_{\mathrm{full}}\).

## 6. Matrix-order enclosure: Arb entrywise intervals are not automatically Loewner bounds

The existing exact-rational `scripts/cert/matrices.py::RationalInterval` and `scripts/cert/exact_prime_schur_common.py::coarsen_matrix` can convert each rigorously enclosed Arb entry into exact rational bounds. However, **entrywise inequalities are not themselves matrix-order inequalities**.

For the symmetric coordinate Gram \(G_{K,\mathrm{coord}}\), let \(C_{ij}\in\mathbb Q\) be a **symmetric** midpoint selection and exact \(r_{ij}\in\mathbb Q_{\ge0}\) satisfy
\[
 |(G_{K,\mathrm{coord}}-C)_{ij}|\le r_{ij}=r_{ji}
\]
for every actual possible matrix entry (including correct symmetry). Then for all real or complex coordinate vectors \(z\),
\[
 \begin{aligned}
 |z^*(G_{K,\mathrm{coord}}-C)z|
 &\le\sum_{ij}r_{ij}|z_i||z_j|\\
 &\le\sum_i\Bigl(\sum_jr_{ij}\Bigr)|z_i|^2.
 \end{aligned}
\]
It follows rigorously that
\[
 \boxed{\displaystyle
 G_{K,\mathrm{coord}}\preceq
  C+\operatorname{diag}\left(\sum_jr_{ij}\right).}
 \tag{6.1}
\]
This exact rational diagonal inflation **converts entrywise intervals to a valid Loewner upper bound**, and can be combined with (5.2) and the existing exact finite-matrix positivity routines. It does not require a new proof-certificate format. The diagonal inflation may be **too coarse** to establish positivity; its usefulness depends on actual widths/conditioning, not on its formal validity alone.

Arb matrix results must remain in the **same unnormalized Legendre coordinate convention** for \(\underline A\), \(G_K\), and the \(D_N\)-weighted full residual allowance. Matrix symmetry, sign and parity are mathematical constraints to verify, not things to infer merely because the code copied an upper triangular entry.

## 7. Explicit unresolved implementation/conditioning requirements

The source and mathematics support **feasibility in principle**, not ready-to-use full cancellation-sensitive output.

- **Supported mathematical operations already present:** exact residual polynomial images; grouped whole-interval potential moments; combined signed arithmetic with rigorous cell topology; local Legendre polynomial inner products; Arb transcendental enclosures; residual operator error; outward exact-rational entry intervals and independent finite-matrix arithmetic.
- **Distinct gap for the full-Gram route:** rigorous **cell-restricted weighted logarithmic moments** coupled to existing Arb-enclosed moving arithmetic boundaries. Closed-form antiderivatives (4.2)–(4.3) show these moments are elementary, but the project has no inspected validated routine producing them at arbitrary cell degree/precision.
- **Small integration/assembly glue:** existing primitives are not yet connected into **ordered** \(VR_K/PR_K/VP\) matrices with their conjugate adjoints and complete \(K D_N^{-1}K\) subtraction. A careless same-family symmetric routine would omit needed orientations.
- **Mathematical soundness control:** rigorous endpoint limits, branch positivity for interior breakpoint balls, outward interval arithmetic, parity, exact Legendre norms, retained \(P_2/P_3\) interactions, and a **matrix-order** rather than entrywise bound.
- **Independent validation control:** at minimum a separate reference computation for low-degree cell moments, exact/full-interval overlap controls, parity and adjoint checks, and residual truncation with the full error allowance. The existing small split-integral overlap is a *smoke check*, not a substitute for those controls.
- **Measured conditioning:** **NOT ESTABLISHED** for the new cross-image calculation. Historical stabilization of the standalone arithmetic/potential computations and the four rigorous finite-tail tests does **not** certify stable new mixed-Gram assembly at \(N=192/196\).
- **No assumption of necessity:** another mathematically valid sharp combined-Gram upper bound or direct Schur-form lower bound could answer the specific positivity question without implementing a complete mixed matrix. The current audit does not rank such alternatives experimentally.

## 8. Audited conclusion and boundary

**Source-level mathematical feasibility:** **YES, conditional** — the missing terms have explicit finite integral identities and compatible existing Arb/rational primitives. There is no mathematical need to introduce a new external integration engine or generic computation platform.

**Complete ready-to-use rigorous mixed-Gram evaluator in the current repo:** **NO** — neither source interface nor new full-dimensional enclosures are established.

**Narrowest identified missing primitive (if the complete mixed-Gram route is selected):** certified **logarithmic polynomial moments over Arb-enclosed arithmetic cells**, with exact endpoint limits, stable local-basis handling and independent low-degree references. Ordered cross-family contractions and matrix-order inflation are limited additional integration steps, not proof of a need for a new framework.

**Decision at this audit boundary:** The source supports considering a narrowly scoped implementation **only after** the need for that method is selected; it does not authorize a generalized tooling upgrade or claim a new positivity result. No production code was modified, no new certificate or theorem was admitted, and no support/dimension experiment was executed.

## References

- [Computational necessity assessment, F-20261017-007](2026-10-17T134402Z-combined-gram-computational-necessity-assessment.md).
- [Combined mathematical criterion and exact mixed-Gram, F-20261017-006](2026-10-17T130040Z-sys2-combined-criterion-mathematical-conclusion.md).
- [Exact source mixed-Gram identities, F-20261017-003](2026-10-17T121809Z-exact-mixed-low-tail-gram-identities.md).
- [Rigorously bounded Suzuki residual and complete mixed-error, F-20261017-004](2026-10-17T122838Z-independent-sys2-analytic-validity-audit.md).
- [Current rigorous multi-prime assembler](../scripts/cert/multi_prime_legendre_schur.py), [piecewise combined prime powers](../scripts/cert/prime_power_terms.py), [residual kernel and remainder](../scripts/cert/residual_kernel.py).
- [Exact rational interval matrix tools](../scripts/cert/matrices.py), [outward dyadic and finite-matrix tools](../scripts/cert/exact_prime_schur_common.py).
- [python-flint 0.9.0 complex integration documentation](https://python-flint.readthedocs.io/en/latest/acb.html).
