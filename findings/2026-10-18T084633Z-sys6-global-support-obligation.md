# SYS-6.3 — Exact all-support Weil requirement and limits of combined-Schur continuation

- **Finding ID:** F-20261018-005
- **Created:** 2026-10-18T08:46:33Z
- **Last updated:** 2026-10-18T08:51:38Z
- **Type:** MATHEMATICAL LOGICAL-QUANTIFIER AUDIT / SOURCE-CHECKED GLOBAL OBLIGATION / CONDITIONAL METHOD ASSESSMENT
- **Status:** **COMPLETE for SYS-6.3 obligation identification**, NOT a global positivity theorem or proof of RH.
- **Dependencies:** C-0063–C-0065 (local conditional combined-Schur statements), C-0067 (one admitted strict fixed-support result), C-0068 (source-dependent nonquantitative right neighborhood), F-20261018-003/004, R-0028 / EXT-0002.
- **External sources checked:** Masatoshi Suzuki, *Weil's quadratic form via the screw function*, arXiv [2606.09096v3](https://arxiv.org/html/2606.09096v3), September 23, 2026, §1.1 (Weil criterion), Theorem 1.1, Corollary 1.2, Theorem 1.3 and the accompanying nondegeneracy discussion, eqs. (1.7), (2.2), (4.5). These are *attributed external mathematical results*, not independently kernel-reproved in this study. Prior primary published source: Masatoshi Suzuki, [*Aspects of the screw function corresponding to the Riemann zeta-function*](https://doi.org/10.1112/jlms.12785), 2023, §3.2.

## 1. The actual unrestricted mathematical goal

Fix the **single unscaled**, globally defined Weil quadratic form
\[
Q_W(f)=W(f*\widetilde f), \qquad f\in C_c^\infty(\mathbb R).
\]
By the externally established Weil positivity criterion (Suzuki v3 §1.1),
\[
\boxed{\mathrm{RH}\ \Longleftrightarrow\
      \forall f\in C_c^\infty(\mathbb R),\ Q_W(f)\ge0 .}
\tag{1}
\]
The **nonnegative**, not support-uniformly coercive, form inequality in (1) is the actual goal. Defining
\[
\mathcal D_T=C_c^\infty(-T,T),\qquad
\lambda(T)=\inf_{0\ne f\in\mathcal D_T}{Q_W(f)\over\|f\|_2^2},
\]
Suzuki v3 Corollary 1.2 identifies this smooth-core Rayleigh infimum with the canonical localized form's lowest eigenvalue, and Theorem 1.3 shows \(\lambda\) is continuous. These are **external source statements**, and no new independently checked full-domain operator equality is asserted here.

The following are **elementary logical equivalences conditional only on the global Weil criterion, not numerical experiments**:
\[
\begin{aligned}
\mathrm{RH}
&\Longleftrightarrow \forall T>0,\ \forall f\in\mathcal D_T,\ Q_W(f)\ge0\\
&\Longleftrightarrow \forall n\in\mathbb N_{\ge1},\
  \forall f\in\mathcal D_n,\ Q_W(f)\ge0\\
&\Longleftrightarrow \exists(T_j)_{j\ge1}\text{ with }\sup_j T_j=\infty,\
  \forall j,\ \forall f\in\mathcal D_{T_j},\ Q_W(f)\ge0.
\end{aligned}
\tag{2}
\]
**Proof:** Every compact support lies inside \((-T,T)\) for some T, inside some \((-n,n)\), and inside an unbounded sequence member; conversely each \(\mathcal D_T\subset C_c^\infty(\mathbb R)\). These are universal implications about *the same* form, not about different normalized numerical matrices.

Test-space inclusion also proves \(\lambda(T_2)\le\lambda(T_1)\) whenever \(0<T_1<T_2\). This does **not** imply any positive lower bound for larger T. Under Suzuki v3's **additional external nondegeneracy equivalence** explained after Theorem 1.3, the stronger per-support condition \(\lambda(T)>0\) for every finite T also characterizes RH; this latter equivalence uses the cited external spectral/nondegeneracy facts and is **not required** to derive (1)–(2). The proof obligation here is conservatively recorded as \(\lambda(T)\ge0\) for every finite T.

**Crucial distinction:** \(\forall T\exists\varepsilon_T>0\) and one positive \(\varepsilon>0\) for **all** T are different statements. Neither a common global \(\varepsilon\) nor a bound on \(\inf_{T>0}\lambda(T)\) is required by (1). Coercivity at finitely many supports with a finite maximum reaches only the corresponding bounded test-support space, *not* RH.

## 2. A fully quantified conditional combined-Schur route

From C-0063–C-0065, **inside the locally established \(0<T<\pi/2\) range**, the scaled form \(\mathfrak l_T\) decomposes (on its stated form domain) into a positive harmonic-number Legendre jump part \(J\), nonnegative logarithmic potential V, the **full signed combined** prime-power compressed translations \(P_T\), a full Suzuki residual \(R_T\), and the scalar \(-c_T I\). Let \(\Pi_N\) be the \(N\)-mode orthogonal Legendre projection, \(Q_N=I-\Pi_N\),
\[
\begin{split}
A_{T,N}&=\Pi_N\mathfrak l_T\Pi_N\quad\text{(low *form* matrix)},\\
B_{T,N}&=Q_N(V+P_T+R_T)\Pi_N,\\
\mathfrak c_{T,N}[q]&=\mathfrak l_T[q]\quad(q\in Q_N\mathcal F_T).
\end{split}
\tag{3}
\]
The established conditional **full-form** sufficient criterion is
\[
\begin{cases}
\mathfrak c_{T,N}[q]\ge\mu_{T,N}\|q\|_2^2
\quad\forall q\in Q_N\mathcal F_T,\quad \mu_{T,N}>0,\\
A_{T,N}-\mu_{T,N}^{-1}B_{T,N}^{*}B_{T,N}\succ0.
\end{cases}
\tag{4}
\]
A proof of (4) at any T in the valid domain, with the **complete residual** and source normalization, implies strict test-class form positivity there. In implementation one checks a mathematically justified
\[
\underline A_{T,N}-
\underline\mu_{T,N}^{-1}\overline G_{T,N}\succ0
\quad
(\underline A\preceq A,\ B^*B\preceq\overline G,\
0<\underline\mu\le\mu).
\tag{5}
\]
Every inequality here must be **Loewner/matrix order**, not entrywise positivity or a positive empirical eigenvalue. In unnormalized Legendre coordinates, residual identity majorants include \(D_N=\operatorname{diag}(2/(2i+1))\), not a naked identity matrix; all \(V,P_T,R_T\) mixed terms and mixed prime-power contributions are required.

A **hypothetical** proof of the following global quantified family would imply RH:
\[
\forall n\in\mathbb N_{\ge1},\
\exists N_n,K_n,\eta_n,\underline\mu_n>0,\
\underline A_n,\overline G_n:
\begin{cases}
\text{global source/form identity and every residual/cross bound valid at }T=n,\\
\mathfrak c_{n,N_n}\ge\underline\mu_n I,\\
\underline A_n-\underline\mu_n^{-1}\overline G_n\succ0.
\end{cases}
\tag{6}
\]
This demands a **proof of the universal quantifier**, perhaps via a common inequality or a proved total certificate-producing method; merely specifying how an algorithm *would* generate a certificate for a given input is not a proof that it succeeds for all inputs. The proof obligations in (6) may vary with n. No fixed N, K, precision, positive margin, positive global constant, or uniform verification cost is logically required for (6), only a single valid general mathematical proof that each n is covered.

**Only sufficient, not an established equivalent reformulation of RH:** (6) is stronger than the needed nonnegativity (2) and depends on conservative sufficient inequalities. Neither Suzuki's theorem nor the local code proves that RH would imply the existence of such Schur witnesses at all supports. Accordingly, saying that (6) 'is equivalent to RH' without its reverse implication would be unjustified. Proving (6) nevertheless **would solve RH**, and so its unrestricted mathematical burden cannot be declared solved or strictly easier by finitely many computations.

## 3. Exact source/analytic break at unrestricted support

The **source Weil form itself** is globally defined: Suzuki v3 §1.1 and scaled expression (4.5) treat arbitrary \(a>0\), with a finite prime-power sum up to \(\exp(2a)\) and the full residual \(r''(a(x-y))\). There is **no source-imposed T<π/2 condition on the global Weil criterion**.

By contrast, current local C-0063 expressly works only for \(0<T<\pi/2\). The existing exact residual component uses a Bernoulli/Taylor series and geometric remainder bound derived for \(|u|<\pi\), where \(u=T(x-y)\) and \(|x-y|\le2\); therefore its uniform enclosure is justified only for \(2T<\pi\). The exact current source \`scripts/cert/residual_kernel.py::_suzuki_residual_tail_radius\` raises \`ValueError\` when the magnitude is not rigorously below \(\pi\); \`scripts/cert/multi_prime_legendre_schur.py::_residual_rho\` inherits this guard.

**Executed negative capability control, 2026-10-18:** under \`uv run --locked python\`, \`_residual_rho(arb(1)/2,32)\` returned a finite enclosure, while \`_residual_rho(arb(2),32)\` raised \`ValueError: Suzuki residual series requires |T(x-y)| < pi\`; expected refusal, **exit 0 for the enclosing test command**. This demonstrates an **actual local proof-tool applicability boundary**, not the impossibility of global residual analysis, not a contradiction in Suzuki, and not a failure of RH.

Any all-support use of the combined Schur route would thus require a **globally valid residual treatment or equivalent independent analytic decomposition**, including a rigorous full-source connection and bounds at every support. The existing one-support Arb-1024/2048 enclosures, \(K=32\) remainder, and v3 SHA-pinned positive matrix cannot be reinterpreted as valid across the \(\pi/2\) boundary.

## 4. Quantities that a general form inequality must control

| Mathematical obligation | What the current project has | Missing global inference |
| --- | --- | --- |
| **Global source-domain/test-function identification** | Suzuki's **external** global form/Weil criterion; local audited scaled identity C-0063 for \(T<\pi/2\) and C-0067 at \(11/20\) | An all-T valid, justified form reduction; no unproved full canonical-domain equality or silent analytic continuation |
| **Active prime-power arithmetic** | Rigorous exact enumeration of \(\log m<2T\), signed \(\Lambda(m)/\sqrt m\), merged \(P_T\) including mixed arithmetic images | A proof controlling the growing sums and mixed terms through every \(m=p^k\) transition, not a fixed two-prime calculation |
| **High-mode complement** | C-0058 lower bound \(H_N-c_T-\sum c_m b_m-\rho_R(T)\), with \(\mu_N>0\) as a gate; SYS-6.2 cutoffs 109,160,238,331,624 for five supports | Parameter-dependent coercivity at all supports and control of conservative losses (not necessarily a single global \(\mu>0\)) |
| **Full combined cross coupling** | Exact identity \(B^*B\) including all ordered \(V,P,R\) products, Loewner enclosure, one positive \(192\times192\) example | Strict positive *lower Schur* bound at arbitrarily large supports, including any \(N(T)\) and threshold behavior |
| **Complete Suzuki residual** | Rigorous K=32 Taylor truncation plus norm allowance inside \(2T<\pi\), growing \(\rho_R,\delta_K\) on sampled supports | Source-valid nonlocal kernel and rigorous remainder/Loewner control beyond the local Taylor convergence domain |
| **Low cutoff and spectral gap** | \(J e_k=H_k e_k\), \(H_N\sim\log N+\gamma\); selected \(\mu_N\)-only cutoffs | Prove that **both** tail and low Schur inequalities succeed at all supports, not merely that \(\mu_N>0\) can be forced by increasing \(N\) |
| **Mixed cancellation** | One full combined Gram retained and signed mixed trace diagnostics | Parameter-wide matrix-order/spectral control in the potentially small negative direction; aggregate trace signs cannot substitute |
| **Numerics/certificates** | One source-verified finite \(T,N\) and exact-rational v3 theorem; research width/precision profiles | A **symbolic general inequality** or a proved total quantified certificate construction; finite interval runs and SHA checks alone do not discharge \(\forall T\) |

**Existing external quasi-RH prime-distribution results:** C-0061/0062 (under EXT-0001) provide asymptotic weighted prime estimates but **do not** automatically yield positive operator-order bounds or control all support-dependent Legendre modes. These are background partial bounds, not a replacement for (4)–(6); no unproved transfer of their error terms into Schur positivity is made.

A positive \(\mu_N\) is *not* positivity of the Schur matrix. At larger T, even making \(N\) immense to overwhelm the **crude scalar** costs does not establish the low mixed-Gram sign. The actual lowest localized eigenvalue is continuous by Suzuki v3 Theorem 1.3 despite potentially discontinuous conservative shift-norm estimates at arithmetic thresholds. The distinction between the **true form** and **lossy sufficient bounds** is essential.

### Tail-complement existence is not a mathematical obstruction inside the current local range

There is an elementary **new logical consequence** of the established complement formula, independently of the SYS-6.2 sample table:

\[
\boxed{\forall T\in(0,\pi/2)\quad \exists N=N(T)\in\mathbb N:
\quad \mu_N(T)>0.}
\tag{7}
\]

**Proof (within the paper-level C-0058/C-0063 trust base).** Fix any \(0<T<\pi/2\). The active prime-power set \(\{\log m<2T\}\) is finite. Each compressed shift is bounded (\(\|S_{\log m/T}\|\le2\)), and each coefficient \(\Lambda(m)/\sqrt m\) is finite. Both \(c_T=\log(2\pi T)+\gamma\) and the C-0058 Suzuki residual majorant \(\rho_R(T)\) are finite, because its geometric Taylor-tail ratio satisfies \(2T/\pi<1\). Hence the combined scalar cost
\[
C(T):=c_T+
\sum_{\log m<2T}(\Lambda(m)/\sqrt m)\,b_m(T)+\rho_R(T)
\]
is finite and **independent of N**. Since \(H_N=\sum_{j=1}^N j^{-1}\to+\infty\), eventually \(H_N>C(T)\), proving (7). This proof is pointwise in T; \(N(T)\) need not have a manageable bound or grow continuously at prime-power thresholds, and \(N(T)\) may blow up as \(T\to\pi/2-\).

**Meaning:** the high-mode **complement gate alone** is always mathematically satisfiable at each fixed support within the presently justified local domain. It is not an intrinsic impossibility barrier there. However the **other** condition, positivity of the full mixed-Gram low Schur matrix \(A_{T,N}-\mu_N^{-1}B_{T,N}^*B_{T,N}\), has not been proved to hold for any such larger T merely by increasing N. This deduction does not apply to \(T\ge\pi/2\) because the current \(\rho_R\) enclosure is not justified there. Registered separately as **C-0071**; no further theorem certificate is admitted.

## 5. Why finite certificates and continuity do not close the global question

1. **Finite maximum:** Positive certificates at finitely many supports imply form positivity only through the largest (by nesting) and any justified existential local neighborhood. They do not reach arbitrary supports.
2. **Continuity is local:** \(\lambda(T_0)>0\) and Suzuki's continuity produce some positive interval near \(T_0\), but without a quantitative modulus and independent positive lower estimates they do not prevent a later zero crossing. Monotonicity gives no positive *upward* inheritance.
3. **Arbitrarily many observed finite tests:** Even a long list, a fast verifier or a source-unchecked extrapolation is still not a proof of \(\forall n\).
4. **A truly proved unbounded family would be enough:** If for every integer n one could mathematically prove positivity on \((-n,n)\), **the quantified proof** and compact support would immediately imply RH by (2). The fact that the family is countable is not an obstacle; failure to prove its universal validity is.
5. **Strict versus nonstrict:** The Weil criterion demands \(\ge0\). A Schur method proving \(>0\) for all T would be sufficient but is not necessary as the initial formulation. Under the separately attributed Suzuki spectral/nondegeneracy result, strict positive bottom eigenvalue at each finite T is also characterized by RH; this **uses additional published-source results**, not an implication established by the finite certificate.

Thus establishing global \(\mu_N(T)\) estimates without global positivity of the combined Schur is not enough. Conversely, failure of a **particular** conservative Schur upper bound is not a negative Weil vector, no-go theorem, or RH counterexample.

## 6. Research classification and mathematical circularity audit

- **PROVED in this record (elementary logic, conditional on the externally cited Weil criterion):** quantifier reductions (1)–(2), test-space nesting and monotonicity; a rigorously proved unbounded cover would suffice; finite maximal support does not suffice.
- **EXTERNALLY SOURCED, NOT KERNEL-REPROVED:** Suzuki v3 global Weil equivalence, canonical smooth-core eigenvalue equality, continuity/nondegeneracy discussion, global scaled quadratic form; distinct from local v3's own source trust model.
- **VERIFIED CURRENT SOURCE BEHAVIOR:** local Taylor/Bernoulli enclosure explicitly enforces \(2T<\pi\); executed negative control confirms refusal at T=2.
- **CONDITIONAL SUFFICIENT HILBERT-SPACE SCHEME:** (4)–(6) if independent source identity, domain, complete-tail and full-Loewner bounds hold for every quantified support. This is **not proved as a universal theorem**, not known to follow from RH, and not a shortcut already justified by local data.
- **NOT ESTABLISHED:** all-support test-class positivity/nonnegativity; a universal \(N(T),K(T),\mu(T)\) and positive Schur lower bound; a valid global residual verification method; no-go theorem for all Schur decompositions; RH.
- **No circularity falsely discharged:** None of the requirements was declared proved by restating 'the Weil form is positive' or by requiring the unproved sign of a matrix at every T. The proposed universally quantified sufficient condition *would itself imply RH*; claiming it solved without a genuinely independent all-T estimate would simply rename the open problem.

**SYS-6.3 completion classification: OBLIGATIONS FULLY CHARACTERIZED; GLOBAL ARGUMENT OPEN.** This is a mathematical accounting conclusion, not a new finite-support theorem, research road map, algorithmic totality theorem or RH proof. Frozen v1/v2/v3 proof-bearing code, exact admissions and their fingerprints remain unchanged.
