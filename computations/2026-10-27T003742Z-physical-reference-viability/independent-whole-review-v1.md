## Independent review of the proposed complete Gram upper

**Approved as a mathematical enclosure operation**, subject to the physical-mass and outward-enclosure requirements below. I found no defect in the proposed Bessel formulas, frequency-step indexing, leakage bound, or decomposition of the omitted physical tail. This approval does not assert a favorable finite sign.

### 1. Whole-line step majorant

Let
\[
k(t)=h(t)^{-1}.
\]
The established evenness and monotonicity of \(A_F\) imply that \(k\) is even and nonincreasing on \(t\ge0\). Suppose
\[
0=\Omega_0<\Omega_1<\cdots<\Omega_L,\qquad
b_0\ge b_1\ge\cdots\ge b_L>0,\qquad
b_j\ge k(\Omega_j).
\]
Then
\[
k(t)\le b_L+\sum_{j=0}^{L-1}(b_j-b_{j+1})
                  {\bf1}_{|t|\le\Omega_{j+1}}.
\]
On \(\Omega_j<|t|\le\Omega_{j+1}\), the right side is \(b_j\), which bounds \(k(t)\). Beyond \(\Omega_L\), it is \(b_L\), which also bounds \(k(t)\).

Thus, in the ordinary Legendre basis,
\[
\boxed{
K_M\preceq b_LD_M+
\sum_{j=0}^{L-1}(b_j-b_{j+1})F_{\Omega_{j+1}}.
}
\]
Here \(D_M=\operatorname{diag}(2/(2n+1))\) is required because \(J\) is isometric, but the ordinary Legendre basis is not orthonormal.

The first anchor \(256\), geometric ratio \(17/16\), and terminal anchor \(8192\) are computational choices for a majorant. They do not change \(h\), \(g\), \(N\), or the support. The \(b_LD_M\) term pays the entire frequency exterior.

When constructing the anchor list, retain only geometric anchors strictly below \(8192\), then append \(8192\). Appending it after an overshooting anchor would violate the required ordering.

### 2. Band-concentration formulas and normalization

For the unitary transport of \(P_n\) from the scaled interval,
\[
\widehat{U_T^{-1}P_n}(t)=2\sqrt T\,(-i)^n j_n(Tt).
\]
Consequently, with \(c=T\Omega\),
\[
(F_\Omega)_{nm}
=\frac4\pi(-1)^{(m-n)/2}\int_0^c j_n(z)j_m(z)\,dz
\]
for equal parity, and it is zero for opposite parity.

For \(n\ne m\), the spherical-Bessel equations give
\[
\frac{d}{dc}
 \left[c^2(j_n'j_m-j_m'j_n)\right]
=[n(n+1)-m(m+1)]j_nj_m.
\]
The boundary contribution at zero vanishes. Therefore the proposed formula is correct:
\[
\boxed{
(F_\Omega)_{nm}
=\frac4\pi(-1)^{(m-n)/2}
\frac{c^2(j_n'j_m-j_m'j_n)}
     {n(n+1)-m(m+1)}.
}
\]

For the diagonal, define
\[
D_n(c)=(2n+1)\int_0^c j_n(z)^2\,dz.
\]
Then
\[
D_0(c)=\operatorname{Si}(2c)+\frac{\cos(2c)-1}{2c},
\]
and
\[
D_n(c)=D_{n-1}(c)-c(j_{n-1}(c)^2+j_n(c)^2).
\]
To verify the recurrence, differentiation using the adjacent-order Bessel identities yields
\[
\frac d{dc}\left[c(j_{n-1}^2+j_n^2)\right]
=(2n-1)j_{n-1}^2-(2n+1)j_n^2.
\]
All terms vanish appropriately at zero. Hence
\[
\boxed{(F_\Omega)_{nn}=\frac4{\pi(2n+1)}D_n(c).}
\]
Use the removable value \(D_0(0)=0\), rather than division by an interval containing zero.

These formulas include both frequency halves and the \(dt/(2\pi)\) measure. No additional \(T\) or physical-mass factor belongs in them.

### 3. Inverse-weight bound on \(Q_M\)

Put
\[
a=\frac1{g(R_c)},\qquad g(R_c)>\frac13.
\]
Since \(h\ge1/3\) everywhere and \(h=g\ge g(R_c)\) outside the band,
\[
h^{-1}(t)\le a+(3-a){\bf1}_{|t|\le R_c}.
\]
For \(y\in Q_MH\), this gives
\[
\int h^{-1}|Jy|^2
\le\left[a+(3-a)\lambda_M(R_c)\right]\|y\|^2.
\]
Thus the proposed \(\kappa_M\) is correct.

The displayed leakage bound agrees with the existing elementary Legendre majorant:
\[
\lambda_M(R_c)\le
\min\left(
1,\frac{2c}{\pi}
\frac{(2M+1)c^{2M}}{((2M+1)!!)^2}
\frac1{1-c^2/[(2M+1)(2M+3)]}
\right),
\quad c=TR_c.
\]
The geometric-ratio condition must be proved. At the stated indices it is the explicit rational comparison
\[
384^2<1249\cdot1251.
\]

This is a bound on the compressed **inverse-weight multiplier form**, derived pointwise and then restricted. It makes no substitution involving an inverse of a compressed unbounded form.

For rational serialization, take \(a_{\rm up}\ge1/g(R_c)\) with \(a_{\rm up}\le3\), and a leakage upper \(\lambda_{\rm up}\in[0,1]\). The expression
\[
a_{\rm up}+(3-a_{\rm up})\lambda_{\rm up}
\]
is conservative because it is increasing in both variables on those ranges.

### 4. Physical split and complete Gram upper

Let \(C\) denote the finite physical output in degrees \(312,\ldots,623\), and
\[
E=Q_{624}(V+P)\Pi_{312}.
\]
C117's exact band proves
\[
Q_{624}R_{56}\Pi_{312}=0,
\]
so \(B_{\rm model}=C+E\) is exact for the model.

Weighted Young's inequality gives, for every exact \(\theta>0\),
\[
G_{\rm model}
\preceq(1+\theta)C^*K_MC
 +(1+\theta^{-1})\kappa_M E^*E.
\]
Also,
\[
E^*E
\preceq2\left(G_{V,Q_M}+G_{P,Q_M}\right).
\]
Therefore the proposed upper
\[
\boxed{
G_{\rm upper}=
(1+\theta)C^*K_{\rm upper}C+
2(1+\theta^{-1})\kappa_M
       (G_{V,Q_M}+G_{P,Q_M})
}
\]
is valid.

The finite \(C\) retains every signed \(V/P/R_{56}\) mixed contribution. Applying the factor two only to the omitted \(Q_M(V+P)\) output is conservative and does not silently drop those mixed contributions.

For \(X=V,P\), the exact omitted-output Gram is
\[
(G_{X,Q_M})_{ij}
=\langle XP_i,XP_j\rangle
-\sum_{m=0}^{M-1}
 \frac{\overline{\langle P_m,XP_i\rangle}
             \langle P_m,XP_j\rangle}{d_m}.
\]
For \(V\), the first term is the complete \(V^2\) moment source. For \(P\), it is the square of the complete combined signed arithmetic operator, including all active \(2/3/4\) terms.

### 5. Requirements for a certified positive result

The proposed final condition is sound:
\[
\boxed{
A_{\rm model}
-\eta_{\rm low}^{-1}G_{\rm upper}
-\Lambda D_N\succ0.
}
\]
Here \(A_{\rm model}\) must be a rigorous lower enclosure, and all other displayed sources must have the enclosure direction required by the expression.

Three implementation requirements are essential:

- If \(C\) stores **expansion coefficients**, use \(C^*K_{\rm upper}C\) directly. If it stores inner products with output Legendre polynomials, convert by the output \(D_M^{-1}\) first.
- An entrywise upper matrix is not automatically a Loewner upper. Errors in \(F_\Omega\), \(C\), and the omitted-output Grams must enter a valid matrix-order enclosure, for example through a Hermitian row-sum error allowance. In particular, do not subtract an uncertain nominal projection Gram as though it were an exact lower.
- Choose and serialize an exact positive \(\theta\), then certify the resulting matrix. Numerical optimization of \(\theta\) is proposal generation, not evidence of positivity.

C117's \(\Lambda D_N\) then pays the complete canonical residual discrepancy, including the infinite physical remainder. No additional residual tail is missing from \(E\).

A verified positive sign would certify the entire selected supported-Gram sufficient criterion at the unchanged \(T,N\). Neither the reported nonrejecting physical witness test nor the mathematical validity of this enclosure establishes that sign.
