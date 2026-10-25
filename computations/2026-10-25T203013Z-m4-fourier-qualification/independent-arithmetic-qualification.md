# Independent arithmetic qualification for the first post-m4 Fourier window

- Date: 2026-10-25
- Status: mathematical qualification only. No numerical job, matrix acceptance, test, build or formatter was run for this document.
- Scope: the open interval \(\log 2<T<\tfrac12\log 5\). No particular support, finite dimension, positivity matrix or admission is selected.

## Public premises and normalization

The public inputs are [the multi-prime contract](../../docs/MULTI_PRIME_CONTRACT.md), [C-0040](../../docs/CLAIMS.md#c-0040--exact-compressed-shift-norm-and-first-prime-perturbation), the generic [prime-power implementation](../../scripts/cert/prime_power_terms.py), the [C-0094 Fourier closure](../2026-10-25T142424Z-reference-route-selection/bounded-minorant-closure-v1.md), and the [C-0096 source derivation](../2026-10-25T155033Z-fourier-minorant-sign/matrix-enclosure-derivation-v1.md). The frozen [C-0096 auditor](../2026-10-25T155033Z-fourier-minorant-sign/source-v2/scripts/verify_fourier_minorant_matrix.py), especially its arithmetic reconstruction, supplies a useful comparison, not a valid post-threshold shortcut.

Work on \(H=L^2(-1,1)\) with ordinary Lebesgue mass. Extend functions by zero and define

\[
U_s f(x)=\mathbf1_{[-1,1]}(x+s)f(x+s),\qquad
U_s^*=U_{-s},\qquad J_s=(U_s+U_{-s})/2.
\]

For a prime power \(m=p^k\), put

\[
\ell_m=\log m,\qquad \tau_m=\ell_m/T,\qquad
d_m=\Lambda(m)/\sqrt m=\log p/\sqrt m.
\]

The signed arithmetic operator is

\[
P=-\sum_m d_m(U_{\tau_m}+U_{-\tau_m})
  =-\sum_m2d_mJ_{\tau_m}.
\]

`PrimePowerTerm.coefficient` is \(d_m\), already the coefficient of each one-sided shift. It is not the coefficient of the average \(J\). In particular,

\[
d_2=\frac{\log2}{\sqrt2},\quad
d_3=\frac{\log3}{\sqrt3},\quad
d_4=\frac{\log2}{2}.
\]

The last numerator is \(\Lambda(4)=\log2\), not \(\log4\). There is no additional factor \(1/2\) when consuming the generic coefficient. The original Suzuki source convention used in C-0094 and C-0096 is retained. This document does not independently re-establish Suzuki's Fourier identity or the exterior and compact-tail estimates.

## Strict activation and endpoint conventions

The activation rule is exactly \(\log m<2T\). In the stated interval,

\[
\log4=2\log2<2T<\log5.
\]

Thus 2, 3 and 4 are active. Every larger prime power is at least 5, so none is active. Hence

\[
\mathcal A(T)=\{2,3,4\}.
\]

At \(T=\log2\), 4 is excluded by equality and the active set is \(\{2,3\}\). Its shift would be 2, whose compressed translation is zero almost everywhere. At \(T=\tfrac12\log5\), 5 is still excluded by equality and the active set remains \(\{2,3,4\}\). A shift of exactly 2 touches only an endpoint and contributes no \(L^2\) operator. These facts explain the strict convention; neither endpoint belongs to the window qualified here.

The generic API takes exact rational supports and requires certified strict Arb comparisons. An interval overlapping a threshold is not equality evidence and is not permission to include or exclude a term. `ThresholdIndeterminateError` is a fail-closed precision result. An exact symbolic threshold needs the mathematical equality convention above; the rational API should not be represented as having certified it from overlapping balls.

## Essential fibers and exact single-shift norms

For \(s>0\), write \(x+1=r+ks\), with residue \(0\le r<s\). Fubini's theorem decomposes \(L^2(-1,1)\) into finite chains of points in the interval separated by \(s\). On a chain of length \(n\), \(U_s+U_{-s}\) is the adjacency matrix of the path with \(n\) vertices. Its eigenvalues are

\[
2\cos\frac{j\pi}{n+1},\qquad 1\le j\le n.
\]

Let \(q=2/s\). If \(q\) is not an integer, chains of length \(\lceil q\rceil\) occur on a positive-measure set of residues, and no longer chain occurs almost everywhere. If \(q=k\) is an integer, the essential chain length is \(k\). Including both interval endpoints can give an apparent \(k+1\)-point chain at one residue, but that residue has measure zero. It cannot change an operator norm. Consequently

\[
L=\lceil2/s\rceil,\qquad
\|J_s\|=\cos\frac{\pi}{L+1}.
\]

This also handles \(s\ge2\): the essential chain length is 1 and the norm is zero. With \(s=\log m/T\), the formula is \(L_m=\lceil2T/\log m\rceil\), precisely half the adjacency normalization of C-0040.

For the present window,

\[
2<\frac{2T}{\log2}<\frac{\log5}{\log2}<3,
\]
\[
1<\frac{2T}{\log3}<\frac{\log5}{\log3}<2,\qquad
1<\frac{2T}{\log4}<\frac{\log5}{\log4}<2.
\]

The final inequalities follow respectively from \(5<8\), \(5<9\) and \(5<16\). Therefore

\[
L_2=3,\quad L_3=L_4=2,\qquad
\|J_{\tau_2}\|=1/\sqrt2,\quad
\|J_{\tau_3}\|=\|J_{\tau_4}\|=1/2.
\]

## Preferred joint 2/4 bound

Write \(a=\tau_2\). Then \(\tau_4=2a\), and \(2/3<a<1\). Convexity of the interval gives the exact identity

\[
U_a^2=U_{2a},\qquad U_{-a}^2=U_{-2a}.
\]

Indeed, if both \(x\) and \(x+2a\) lie in the interval, the intermediate point \(x+a\) lies there too. This identity does not extend to arbitrary products with opposite signs: \(U_aU_{-a}\) is a support projection, not the identity.

Let

\[
C_{24}=d_2(U_a+U_{-a})+d_4(U_{2a}+U_{-2a}).
\]

It preserves the same dyadic fibers. The longest fibers have three points and positive residue measure because \(a<1\). On each such fiber its matrix is

\[
(\log2)
\begin{pmatrix}
0&1/\sqrt2&1/2\\
1/\sqrt2&0&1/\sqrt2\\
1/2&1/\sqrt2&0
\end{pmatrix}.
\]

The antisymmetric vector has eigenvalue \(-\log2/2\). Restricting to the reflection-symmetric two-dimensional space gives the other eigenvalues, so the complete list is

\[
(\log2)\left\{-\frac12,\frac{1+\sqrt{17}}4,
                              \frac{1-\sqrt{17}}4\right\}.
\]

A two-point fiber has only the adjacent edge and norm \(d_2\); a one-point fiber contributes zero. The largest absolute eigenvalue above exceeds both shorter-fiber norms. Therefore the exact joint norm is

\[
\boxed{\ \|C_{24}\|=(\log2)\frac{1+\sqrt{17}}4\ }.
\]

A rational similarity model for the three-point matrix divided by \(\log2\) is

\[
R=\begin{pmatrix}0&1&1/2\\1/2&0&1/2\\1/2&1&0\end{pmatrix},
\quad G=\operatorname{diag}(1,2,1),\quad GR=R^tG,
\]
\[
\det(\lambda I-R)=(\lambda+1/2)(\lambda^2-\lambda/2-1).
\]

Specifically \(R=S^{-1}BS\), where \(B\) is the symmetric displayed matrix without \(\log2\) and \(S=\operatorname{diag}(1,\sqrt2,1)\). The correct mass in this rational model is \(G\), not the coordinate identity. The spectrum is not symmetric about zero because the 2/4 fiber contains a triangle. No bipartite symmetry argument is being used.

Since \(P=-C_{24}-d_3(U_{\tau_3}+U_{-\tau_3})\),

\[
\|P\|\le p_*:=(\log2)\frac{1+\sqrt{17}}4+\frac{\log3}{\sqrt3}.
\]

This is a bound for the full norm, not a claim that the full norm equals the sum or that the two operators commute. It controls both signs and hence gives the required lower bound for \(P\).

Here is an elementary rational envelope, with no numerical premise:

\[
\log2<111/160,\quad\log3<11/10,\quad
\sqrt{17}<33/8,\quad\sqrt3>173/100.
\]

For the first logarithm use

\[
\log2=2\sum_{k\ge0}\frac{3^{-(2k+1)}}{2k+1}
 <\frac{842}{1215}+\frac1{6804}=\frac{23581}{34020}<\frac{111}{160}.
\]

The tail estimate starts at \(k=3\) and bounds each denominator below by 7. For the second logarithm, the first six terms of the positive exponential series give

\[
e^{11/10}>\sum_{k=0}^{5}\frac{(11/10)^k}{k!}
=\frac{36015101}{12000000}>3.
\]

The radical bounds follow by squaring positive rationals. Thus

\[
p_*<\frac{4551}{5120}+\frac{110}{173}
=\frac{1350523}{885760}<\frac{49}{32}=:p_0,
\]

where the last gap is exactly \(5797/885760\). For \(M=\tfrac72I+P\),

\[
M\succeq m_0I,\qquad m_0=\frac72-\frac{49}{32}=\frac{63}{32}.
\]

For any orthogonal low projection \(\Pi\), set \(Q=I-\Pi\) and \(G_P=\Pi P QP\Pi\). The crude bounds \(\Pi M\Pi\succeq m_0I\), \(QMQ\succeq m_0I\) and \(G_P\preceq p_0^2I\) imply the scalar sufficient-reference lower

\[
\Pi M\Pi-\frac{G_P}{m_0}
\succeq\left(m_0-\frac{p_0^2}{m_0}\right)I
=\frac79 I.
\]

This is the bare arithmetic-base sufficient Schur lower. It is not a computed sign for the full Fourier minorant \(M+K\), and it is not an assertion that the exact Schur complement has lower bound only \(7/9\). The compact block, its cross terms, the exterior condition and all source errors still require their own accounting. For example, if \(\|QK\Pi\|\le\eta\), the mixed Gram allowance uses \(2p_0\eta+\eta^2\), not the previous window's smaller arithmetic constant.

## Triangle fallback

Without the joint refinement the single-shift norms still give

\[
\|P\|\le r_*:=\frac32\log2+\frac{\log3}{\sqrt3}<\frac{27}{16}=:r_0.
\]

To verify the strict rational comparison, use \(\log2<7/10\), \(\log3<11/10\) and \(\sqrt3>19/11\). The first follows from

\[
e^{7/10}>1+7/10+49/200+343/6000=12013/6000>2.
\]

The others were proved above or follow by squaring. Consequently

\[
r_*<\frac{21}{20}+\frac{121}{190}=\frac{641}{380}
=\frac{27}{16}-\frac1{1520}.
\]

This yields \(M\succeq29I/16\) and the weaker but valid bare sufficient-reference lower

\[
\frac{29}{16}-\frac{(27/16)^2}{29/16}=\frac7{29}.
\]

The preferred \(7/9\) bound and the fallback \(7/29\) bound are mathematical inequalities throughout the window, not finite numerical acceptance results.

## Signed intersections and all 36 products

Put \(a=\tau_2\), \(b=\tau_3\), \(c=\tau_4=2a\). Then

\[
0<a<1<b<c<2,\qquad a+b>2,\qquad a+c>2.
\]

The first mixed inequality follows from \(\log6>\log5>2T\), and the second from \(\log8>\log5>2T\). For the six signed shifts

\[
\mathcal S=\{a,b,c,-a,-b,-c\},
\]

define the signed-image pairing

\[
H_{ij}(\alpha,\beta)
=\int_{I_{\alpha,\beta}}\overline{P_i(x+\alpha)}P_j(x+\beta)\,dx,
\]
\[
I_{\alpha,\beta}
=[-1,1]\cap[-1-\alpha,1-\alpha]\cap[-1-\beta,1-\beta].
\]

The exact endpoints and length are

\[
L=-1-\min(0,\alpha,\beta),\quad
R=1-\max(0,\alpha,\beta),\quad
|I_{\alpha,\beta}|=\max\{0,2-[\max(0,\alpha,\beta)-\min(0,\alpha,\beta)]\}.
\]

Positive length requires the bracketed span to be strictly less than 2. Equality gives a singleton, which is set-theoretically nonempty but has zero integral. A span greater than 2 gives the empty set.

For two positive shifts \(s,t\), the domain is \([-1,1-\max(s,t)]\). For two negative shifts \(-s,-t\), it is \([-1+\max(s,t),1]\). Every such domain has positive length because \(c<2\). Opposite signs \(s,-t\) give \([t-1,1-s]\), with positive length exactly when \(s+t<2\). Only \(s=t=a\) meets this condition in the present window. Its central domain is

\[
I_{a,-a}=I_{-a,a}=[a-1,1-a],\qquad |I|=2-2a>0.
\]

The following table enumerates all ordered pairs. \(S_u^+=[-1,1-u]\), \(S_u^-=[u-1,1]\), \(C=[a-1,1-a]\), and \(\varnothing\) means an actually empty domain in this open window.

| First / second | a | b | c | -a | -b | -c |
|---|---|---|---|---|---|---|
| a | S_a^+ | S_b^+ | S_c^+ | C | ∅ | ∅ |
| b | S_b^+ | S_b^+ | S_c^+ | ∅ | ∅ | ∅ |
| c | S_c^+ | S_c^+ | S_c^+ | ∅ | ∅ | ∅ |
| -a | C | ∅ | ∅ | S_a^- | S_b^- | S_c^- |
| -b | ∅ | ∅ | ∅ | S_b^- | S_b^- | S_c^- |
| -c | ∅ | ∅ | ∅ | S_c^- | S_c^- | S_c^- |

There are 36 ordered pairs, not 16: 18 same-sign positive-length pairs, two central opposite-sign pairs, and 16 empty opposite-sign pairs. Both orientations of every mixed 2/3, 2/4 and 3/4 pairing are included. For each distinct prime-power pair there are eight signed ordered pairs; four survive and four are empty. For 2/2 all four survive; for 3/3 and 4/4 only the two same-sign image pairs survive.

Equivalently, the 20 surviving pairs consist of the eight same-sign pairs already present in the old two-prime geometry, ten new surviving pairs involving 4, and the two newly surviving opposite-sign 2/2 pairs.

There is an important indexing distinction. The displayed domain belongs to \(\langle U_\alpha P_i,U_\beta P_j\rangle\), hence to the operator product \(U_{-\alpha}U_\beta\), not literally \(U_\alpha U_\beta\). Literal composition has constraints

\[
x\in[-1,1],\quad x+\alpha\in[-1,1],\quad
x+\alpha+\beta\in[-1,1].
\]

Changing variable \(y=x+\alpha\) gives the image-pair domain \(I_{-\alpha,\beta}\). The full sum is unchanged by reindexing the six signs, but an individual label is not. In particular the newly surviving opposite-sign image pairs represent the new literal compositions \(U_a^2=U_c\) and \(U_{-a}^2=U_{-c}\). Conversely \(U_aU_{-a}\) is nonzero even in the old window; it is represented there by a same-sign image pair. This distinction prevents an incorrect compressed-shift product shortcut.

## What changes from the frozen two-prime audit

The frozen auditor independently sums four signed shifts and their 16 image pairs. At its old support both positive shifts exceed 1. Its explicit check that every opposite-sign intersection is empty is correct there. That check cannot be transplanted here.

Three changes are mandatory in a new arithmetic reconstruction:

1. Add both one-sided 4 contributions with coefficient \(-\log2/2\).
2. Add all 20 ordered signed image pairs involving 4. Ten have positive length and ten are empty. This includes the full 2/4 and 3/4 mixed squares and the 4/4 square.
3. Retain the two newly nonempty opposite-sign 2/2 image pairs on \(C\). The other old opposite-sign pairs remain empty.

The old positive- and negative-sign 2/3 pairings were already present. They were not missing from C-0096. The old empty-intersection branch would now reject on the 2/2 geometry; silently changing it to unconditional omission would instead produce the wrong square. Neither response qualifies a new window.

## Cells, mass, parity and source consistency

The eight ordered breakpoints throughout the open window are

\[
-1<1-c<1-b<a-1<1-a<b-1<c-1<1.
\]

The strict middle comparisons follow from \(a+b>2\). There are seven open cells, with no internal topology change anywhere in the window. The central cell and each outermost cell have width \(2-2a>0\). In their left-to-right order the active shifts are

\[
\{a,b,c\},\quad\{a,b\},\quad\{a\},\quad
\{a,-a\},\quad\{-a\},\quad\{-a,-b\},\quad\{-a,-b,-c\}.
\]

Endpoints do not affect integration. Each image on a cell is a polynomial, and the combined image is the sum of all active signed contributions before squaring. A basis of degrees 0 through \(N-1\) produces products of degree at most \(2N-2\). Exact Gauss-Legendre order \(N\), or a higher independently chosen order, therefore integrates the polynomial part exactly. This does not remove the need to enclose uncertain nodes, endpoints, logarithms, weights and coefficients.

The generic implementation builds these combined cell images without assuming every shift exceeds 1. Its topology routine requires strict certified ordering and common exact support metadata. Unresolved ordering raises `PiecewiseTopologyError`; midpoint sorting or midpoint activity decisions are not a substitute. At the excluded lower endpoint some breakpoints coincide. The present strict-cell proof is not an equality-case proof for that routine.

Let \(P_j\) denote ordinary Legendre polynomials, and write \(\mathsf P\) for their low quadratic-form matrix. Then

\[
D_{jj}=\int_{-1}^1P_j(x)^2dx=\frac2{2j+1},
\]
\[
\mathsf P_{ij}=\langle P_i,PP_j\rangle,
\qquad \mathsf S_{ij}=\langle PP_i,PP_j\rangle,
\qquad \mathsf G_P=\mathsf S-\mathsf P D^{-1}\mathsf P.
\]

Equivalently,

\[
\mathsf S_{ij}=\sum_{\alpha,\beta\in\mathcal S}
 d_{m(\alpha)}d_{m(\beta)}H_{ij}(\alpha,\beta).
\]

The minus signs in \(P\) cancel in the square. The matrix \(\mathsf S\) is the compression of the operator square, not the ordinary low matrix square. In particular

\[
P^2=P_2^2+P_3^2+P_4^2
 +P_2P_3+P_3P_2+P_2P_4+P_4P_2+P_3P_4+P_4P_3.
\]

There is no commutativity assumption, and summing three separately formed tail Grams drops mixed terms. Every pair uses the same source support, coefficients and ordinary mass as the low \(P\).

Reflection sends \(U_s\) to \(U_{-s}\), so it commutes with each full prime-power term, with \(P\), with \(P^2\), and with the Legendre projection. Therefore \(\mathsf P\), \(\mathsf S\) and \(\mathsf G_P\) have exact zero entries when \(i+j\) is odd. Individual signed-pair terms need not have parity zeros; one must justify parity from the full reflection-invariant sum rather than erase individual contributions.

The unitary scaling from physical time is \(g(x)=\sqrt T f(Tx)\). It gives the mass \(D\) above, without an extra factor of \(T\) in arithmetic entries. This agrees with the C-0096 normalization. The Fourier band and pole retain their own scaling factors from that source identity. A uniform operator error \(E I\) becomes the quadratic-form allowance \(E D\), not \(E\) times the coordinate identity. An entrywise form error may be bounded by \(E\sqrt{D_iD_j}\). Endpoint uncertainty is either integrated rigorously as interval uncertainty or paid by an explicit valid bound; it cannot be discarded as though it were a measure-zero exact endpoint.

## Threshold continuity and its limits

At \(T=\log2\), the essential 2-chain length is 2, not 3. Immediately above that threshold, three-point fibers occur on a positive, possibly very small, residue set. Their norm does not shrink with that set's measure, since a unit vector can concentrate there. Similarly the 4 operator is zero at activation but has a nonzero operator norm at every strictly larger support. Thus the single-shift and joint dyadic norm bounds can jump at this threshold.

For any fixed polynomial pair, the low entries remain continuous. Translated polynomials and coefficients vary continuously; the relevant interval integrals vary continuously with their endpoints. The new central interval and the newly activated 4-support intervals shrink to length zero at the lower threshold. The finite entries of \(P\), the operator-square compression and \(G_P\) therefore have continuous limits even though the uniform operator-norm bounds jump. Strong continuity of compressed translations is consistent with this behavior; it is weaker than operator-norm continuity.

No discontinuity of a Weil eigenvalue follows from the jump in a sufficient norm bound. No negative direction follows either. A failed scalar or finite sufficient lower rejects that lower bound, not the operator. A negative direction of a bounded Fourier minorant would reject that minorant, not automatically the original Weil form whose nonnegative exterior was dropped. These statements do not assert a complete unbounded Weil operator realization or spectral-continuity theorem.

## Exact countercontrols for later execution

These are executable mathematical specifications, not reports that controls were run. The rational toy shifts below are not a proposed arithmetic support and do not replace the logarithmic source constants.

### A three-point fiber and a mass trap

Take toy shift \(a=3/4\) and a nonzero indicator on \((-1/8,1/8)\). Translate it to centers \(-3/4,0,3/4\) and normalize the three disjoint functions to equal mass 1. Their span is invariant under the symmetric \(a\) and \(2a\) shifts. The matrices are exactly the three-point adjacency and its second-neighbor edge, with no fourth point in the interval. Apply the weights \(1/\sqrt2\) and \(1/2\) to recover \(B\) above. Scaling the middle basis function by \(\sqrt2\) gives the exact rational pair \((R,G)\).

Check the characteristic polynomial, \(GR=R^tG\), and the generalized norm calculation against the exact radical spectrum. Treating \(R\) as Euclidean self-adjoint, replacing \(U_aU_{-a}\) by \(I\), or counting a four-point chain must fail this control. Keeping \(U_a^2=U_{2a}\) must pass. This isolates the joint-norm argument without a numerical support choice.

### A seven-cell square that detects the missing central pair

Use toy shifts \(a=3/4\), \(b=7/5\), \(c=3/2=2a\), each signed one-sided coefficient equal to 1, and the constant polynomial \(f=1\). The exact breakpoints are

\[
-1,-1/2,-2/5,-1/4,1/4,2/5,1/2,1.
\]

The counts of active signed shifts on the seven cells are \(3,2,1,2,1,2,3\). Consequently the negative combined operator has

\[
\langle1,P1\rangle=-47/10,\qquad
\langle P1,P1\rangle=121/10.
\]

Enumerating all 36 pair domains must reproduce the same square. Omitting the two central opposite-sign \(a/a\) image pairs loses exactly 1 and gives the incorrect \(111/10\). Omitting every contribution involving \(c\) instead gives low entry \(-37/10\) and square \(71/10\). This checks both the new 4 contribution and the newly nonempty old-sign intersection.

For the one-dimensional low space spanned by 1, use \(D_0=2\). The correct tail Gram is

\[
121/10-(-47/10)^2/2=211/200>0.
\]

Using identity mass gives a negative result instead, so it detects the mass error. Halving every consumer coefficient gives exactly half the low entry, one quarter the square and one quarter the tail Gram. A source-consistency check must reject those altered quantities for the original operator.

### Ordered-product and parity controls

For the same toy geometry, compare direct action of \(U_a^2\) against \(U_c\) on the three-point fiber. Compare the corresponding Gram term \(H(a,-a)\) on the central interval. They agree after the sign reindexing and change of variable described above; matching literal composition labels directly to \(I_{a,a}\) is wrong.

Next use the degree-0 and degree-1 Legendre polynomials on all seven cells. Reflect cells and exchange both shift signs. This pairs each even/odd integral with its negative and proves that the complete off-parity entries vanish exactly. Dropping one orientation of a mixed pair or one reflected cell must break the full reconstruction or its parity identity. Check the complete sum before applying parity projection, so a forced zero cannot hide an omission.

### Equality and topology controls

For a single toy shift \(s=1\), almost every fiber has two points. The apparent three-point endpoint chain has measure zero and must not change \(\|J_s\|=1/2\). For \(s=2\), the operator is zero. For a toy opposite-sign pair \((s,-t)\) with \(s+t=2\), the intersection is a singleton and its polynomial integral is exactly zero. Perturb the sum symbolically below and above 2 to distinguish positive length from emptiness.

For a deliberately unresolved interval comparison at a breakpoint or activation threshold, require a fail-closed result. Do not accept a guessed topology. Independently check \(\Lambda(4)=\log2\), the absence of an extra half coefficient, common support metadata, and the distinction between an operator-square compression and a low matrix square. These are source-semantic controls, not merely agreement between two consumers of the same bad input.

## Qualified conclusion

The full signed arithmetic geometry is qualified throughout \(\log2<T<\tfrac12\log5\), including all 36 ordered image products and the newly nonempty central 2/2 pair. The preferred joint dyadic bound gives \(\|P\|<49/32\), \(M\succeq63I/32\), and a bare sufficient-reference Schur lower \(7/9\). The independent triangle fallback gives \(\|P\|<27/16\), \(M\succeq29I/16\), and \(7/29\).

These are analytical qualifications and exact countercontrol specifications. No finite positivity matrix, executed numerical acceptance, new support theorem, all-support claim, new certificate format or production admission follows from this document.
