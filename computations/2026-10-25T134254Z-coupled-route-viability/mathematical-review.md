# Mathematical review of the finite coupled-tail route

- Created: `2026-10-25T13:44:05Z`, from the runtime UTC clock.
- Scope: an independent written qualification of the fixed finite coupled-tail comparison, not a new numerical assessment or production theorem admission.
- Sources: [C-0063, C-0072, C-0087, C-0091 and C-0092](../../docs/CLAIMS.md); [the C-0092 finding](../../findings/2026-10-25T130058Z-coupled-tail-comparison.md); [`load_context` and `responses`](../../scripts/weil_coupled_tail_comparison.py); [the accepted weighted-support extension record](../2026-10-24T191616Z-weighted-support-extension/record.md).

## Conclusion

The proposed equivalence is correct under the domain, positivity and common-reference conditions stated below. For one fixed outside reference and identical retained data, moving a finite block from the named low space into a coupled tail is an elimination order, not a stronger exact positivity criterion. The positivity of that coupled tail is part of the criterion and cannot be discarded.

This conclusion does not invalidate C-0092. That result establishes a real, avoidable loss in the particular diagonal P20 reference on two fixed directions. It does not establish that the demonstrated dense rearrangement is a distinct or worthwhile primary continuation mechanism. Its complete positivity authority already comes from the accepted larger P312 construction. The warranted recommendation is to retain this concrete rearrangement as a diagnostic and interpretation tool. New analytical or computational structure remains open, but the present evidence does not demonstrate it.

## Domains and the fixed reference

Work under the conditional local closed-form hypotheses of C-0063 and C-0072. Let

\[
\mathcal H=L\oplus E\oplus F,\qquad
L=P_N\mathcal H,\quad E=(P_M-P_N)\mathcal H,\quad F=Q_M\mathcal H.
\]

Here the notation denotes finite Legendre projections, not polynomial basis elements. C-0063 places the finite modes in the operator domain, makes the low-to-F cross maps bounded, and makes these projections preserve the true form domain. Thus the latter splits as the finite spaces L and E plus its restriction to F. No use of a bounded global logarithmic multiplication operator is justified or needed.

Write the true form as

\[
q(x,z)=\langle x,A_Mx\rangle
       +2\operatorname{Re}\langle B_Mx,z\rangle+c_F[z],
\qquad x\in L\oplus E.
\]

Use the same self-adjoint outside reference \(D=D_{F,0}\) for both methods. A sufficient set of assumptions is

\[
D\ge dI_F\quad(d>0),\qquad
D(c_F)\subseteq D(D^{1/2}),\qquad
c_F[z]\ge\|D^{1/2}z\|^2\quad(z\in D(c_F)).
\]

The actual cross map \(B_M:L\oplus E\to F\) is bounded. These assumptions hold for a valid uniformly positive harmonic reference of the stated kind. Merely saying that D is positive on each nonzero vector is insufficient in general: without a uniform lower bound its inverse can be unbounded, and one must separately establish the required energy-dual bounds and inverse domains. No such weaker generalization is claimed here.

Define the reference form on the possibly larger domain

\[
D(q_0)=(L\oplus E)\oplus D(D^{1/2})
\]

by replacing only \(c_F\) with \(\|D^{1/2}z\|^2\). All finite blocks and both actual F cross maps remain unchanged. This is a lower reference on the true domain. Equality of the two domains is not required. All comparisons with the true form are one-sided; positivity of the reference suffices for true positivity, but is not necessary for it.

In orthonormal coordinates the following formulas use ordinary adjoints. In ordinary Legendre coordinates they mean the corresponding quadratic-form matrices with their physical masses retained, or their mass-normalized congruences. Omitting the mass conversion would not preserve these formulas as operator-coordinate statements.

## Exact elimination and its necessary hypothesis

Square completion gives

\[
q_0(x,z)=\langle x,H_Mx\rangle+
 \|D^{1/2}(z+D^{-1}B_Mx)\|^2,
\qquad H_M=A_M-B_M^*D^{-1}B_M.
\]

Since \(D^{-1}B_Mx\in D(D)\), this minimum is attained in the reference form domain. When D is the chosen harmonic reference outside M, \(H_M\) is exactly the ordinary larger-projection harmonic reference at M, before outward finite enclosures. For a different valid D the same algebra holds, but calling it that particular harmonic reference would be inaccurate.

Partition \(B_M=(B_L,B_E)\) and \(H_M\) according to L and E. Put

\[
G=H_{EE}=A_{EE}-B_E^*D^{-1}B_E.
\]

If \(G\succ0\), a second square completion gives

\[
\inf_{y\in E}\inf_{z\in D(D^{1/2})}q_0(\ell+y,z)
 =\langle\ell,S_N^{\mathrm{ref}}\ell\rangle,
\qquad
S_N^{\mathrm{ref}}=H_{LL}-H_{LE}G^{-1}H_{EL}.
\]

The same quantity results from eliminating the coupled tail E plus F at once. More explicitly, its tail form has block representation

\[
T_0=\begin{pmatrix}A_{EE}&B_E^*\\ B_E&D\end{pmatrix},
\qquad
S_N^{\mathrm{ref}}
=A_{LL}-
\begin{pmatrix}A_{LE}&B_L^*\end{pmatrix}
T_0^{-1}
\begin{pmatrix}A_{EL}\\B_L\end{pmatrix}.
\]

The infinite block notation here denotes the associated form operator, not an instruction to apply an unbounded operator to arbitrary tail vectors. The bounded triangular square-completion transform proves that \(T_0\) is coercively positive exactly when \(G\succ0\), given \(D\ge dI\). It also justifies the bounded inverse used in this display.

Consequently,

\[
H_M\succ0
\quad\Longleftrightarrow\quad
G\succ0\ \text{and}\ S_N^{\mathrm{ref}}\succ0
\quad\Longleftrightarrow\quad
T_0\text{ coercively positive and }S_N^{\mathrm{ref}}\succ0.
\]

These are strict positivity statements. A positive algebraic Schur expression with an invertible but indefinite E block does not imply positivity of the full matrix. A singular nonnegative E block needs range compatibility and a generalized Schur treatment; it cannot give strict positivity of the full finite matrix. Those cases are outside the asserted equivalence.

Successive infima equal the joint infimum because the admissible domain is a product under this finite splitting. This equality alone does not imply finite infima, attainment or an inverse formula. The uniform F reference and the positive G provide those facts for the reference calculation. For the true form, domain preservation gives the analogous equality of infima; positive restricted tails and bounded cross maps justify square completion where used. Reference minimizers need not belong to the narrower true form domain. Taking an infimum over the larger reference domain still yields a valid lower bound on the true infimum.

The equivalence therefore has no hidden improvement in exact reference sign. It does not assert equality between the reference and the true Schur complement.

## One-sided accepted finite lowers

Let \(K_M\) be one fixed accepted self-adjoint lower matrix for the complete true Schur after eliminating F, or for \(H_M\) when that stronger reference lower is available. It must include all outside-tail and source errors. An entrywise interval choice alone is not a Loewner lower.

For this same matrix,

\[
K_M\succ0\quad\Longleftrightarrow\quad
K_{EE}\succ0\ \text{and}\
\operatorname{Schur}_E(K_M)\succ0.
\]

When \(K_{EE}\succ0\), minimizing its quadratic form over E gives a valid lower on the true N Schur by monotonicity of infima. If \(K_M\preceq H_M\), the same argument also gives

\[
\operatorname{Schur}_E(K_M)\preceq\operatorname{Schur}_E(H_M).
\]

The latter comparison presupposes the positive E blocks; it does not identify either finite lower with the exact true Schur. Failure of a conservative lower does not prove failure of the exact reference or true form.

Different outward enclosures, elimination orders, residual estimates or witnesses can produce different certificate success from the same analytical source. That can matter in practice. It is not a violation of the exact identity and is not evidence that relabeling coordinates strengthens a fixed exact criterion. Any claim of such a certificate advantage must compare the actual bounds and retain the cost of constructing and validating them.

## What the retained comparison establishes

C-0091 proves that the complete fixed P20 harmonic reference has negative directions in both parities. This is stronger than an inconclusive lower bound or a finite omitted-tail majorant failure. More precision or more head rows cannot change the signs of that unchanged exact reference on its retained trials.

C-0092 gives positive lower bounds for the true P20 Schur on those same two trials, using the accepted complete K312 lower. The finding records the following outward-endpoint displays.

| Parity | Fixed P20 reference upper | True P20 Schur lower | Reference-loss lower |
| --- | ---: | ---: | ---: |
| Even | -1.24680669474e-5 | 3.98712016964e-5 | 5.23392686438e-5 |
| Odd | -4.17544391747e-8 | 6.46271561971e-8 | 1.06381595372e-7 |

This certifies avoidable diagonal-reference loss on the two directions. The separately bounded outside-response excess does not leave an unpaid far-tail explanation for the comparison. Positive directional stiffness increments are explanatory probes, not a uniform matrix-order theorem or an additive decomposition of inverse loss. Two positive directional values are not a whole-P20 positivity certificate.

The source dependency is decisive. In `load_context`, lines 91 through 115 reconstruct the full accepted M312 lower, restore the complete residual charge and verify both original parity congruences and gaps. In `responses`, lines 135 through 148 solve an E block of that full lower to propose the coupled minimizer, and a different finite source block to propose the finite response. The exact residual argument certifies the proposal; the floating solve is not its positivity authority. This demonstrates a consequence of accepted M312 positivity, not an independent small-data route to discovering it.

C-0087 had already proved positivity at this support with complete fresh M312 analytical construction and acceptance. Its record reports fresh source generation, independent all-entry audit, exact assessment and separate replay as distinct operations. Cheap inherited-source replay of C-0092 cannot be compared to that fresh-source total as fresh-source acceleration.

The historical P20 and P312 references also use their own chosen reserves. Their outside diagonal restrictions must not be silently treated as the same D. The equivalence proved here deliberately fixes the same D for both competing elimination orders. It does not prove equality of different historical references, or a uniform dominance relation between all such choices. This restriction leaves the fixed-trial reference-loss finding intact.

## Dense accounting and its limits

For one dense real parity block let \(m=M/2\), \(n=N/2\), and \(e=m-n\). In the conventional leading-order Cholesky model, eliminating E first costs

\[
\frac{e^3}{3}+e^2n+en^2+\frac{n^3}{3}
=\frac{(e+n)^3}{3}=\frac{m^3}{3}.
\]

The terms represent the E factorization, cross-block triangular solve, Schur update and final L factorization. This is a leading dense operation model, not an exact instruction count. Lower-order terms, arithmetic type, bit growth, witness construction, source generation and source auditing are not represented.

The number of parameters in the complete block triangular factor is exactly

\[
\frac{e(e+1)}2+en+\frac{n(n+1)}2
=\frac{m(m+1)}2.
\]

This parameter identity describes a full dense triangular factor. It is not a claim that every certificate or implementation must store that factor, nor that all algorithms must incur its cost. Retaining the dense E block and cross block has not made their data disappear. At the demonstrated boundaries, each parity has 146 finite tail coordinates plus 10 low coordinates, still 156 coordinates in total. Naming the final low block P20 does not make the complete dense construction 10-dimensional per parity.

Neither identity is a universal algorithmic lower bound or a measured speedup comparison. They do not include the infinite-F contraction and its accepted source tensors. They do rule out counting only the final n block while omitting the dense eliminated E and cross work in this conventional full-factor calculation.

## Viability judgment and open limits

There is no flaw in the proposed Schur equivalence once its hypotheses are explicit. Its main risks are dropping E positivity, assuming inverse formulas from formal positivity alone, identifying different outside references, or confusing a finite lower with the exact true Schur.

For the demonstrated dense construction, the evidence supports diagnosis of diagonal-reference loss rather than promotion to a primary continuation route. The known success is a rearranged consequence of a larger accepted positive construction. No reduction in fresh analytical data, dense leading factorization work, certificate parameters or support-extension cost has been established by that rearrangement.

This is a restricted assessment, not a global prohibition. Exact sign equivalence leaves room for useful structure, sharper certified bounds, better conditioning, efficient application of an eliminated block, amortized reuse across multiple right-hand sides, or selective directional diagnostics. Such benefits need not await an RH-equivalent global theorem before they merit research. None is demonstrated as a fresh-source continuation advantage by the present two-direction comparison. No replacement construction or prospective implementation plan is selected in this record.

In particular, this assessment proves none of the following: impossibility of coupled-tail methods; optimality or necessity of M312; impossibility of a stronger outside or coupled reference; inability to obtain future local support gains; literature novelty or lack of novelty; a universal complexity barrier; positivity beyond the established support; or RH. It changes no theorem admission, prior source, test or artifact. No numerical job, test, build or formatter was run for this review.
