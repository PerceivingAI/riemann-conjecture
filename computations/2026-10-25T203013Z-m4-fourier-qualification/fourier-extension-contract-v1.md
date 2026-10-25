# Full Fourier-reference contract on the first post-m4 window

- **Created:** `2026-10-25T20:30:13Z`
- **Scope:** mathematical qualification on log2<T<log5/2, not a selected support or a low-matrix sign
- **Evidence:** [independent arithmetic qualification](independent-arithmetic-qualification.md), [executed controls](data/qualification-controls-v1.json)

## 1. Source, Hilbert space and reference

The C-0094 smooth-test identity from Suzuki arXiv2606.09096v3 applies with the complete active arithmetic set. On H_T=L²(-T,T), using zero extension, hat f(t)=int f(u)exp(-itu)du and Fourier measure dt/(2pi),

Q_W[f]=<f,H0 f>+int_(abs(t)>Omega)(A(t)-a)|hat f(t)|²dt/(2pi),

where A(t)=Re psi(1/4+it/2)-log pi and H0=M+K, M=aI+P. K is the signed rank-two pole plus the finite-band term F_Omega*(A-a)F_Omega. H0 is bounded on all H_T. The original exterior/form uses the logarithmic Fourier domain and is not a bounded form on all H_T.

All active terms are exactly2,3,4 in the open interval. The signed operator is P=-sum d_m(U_tau_m+U_-tau_m), d_m=Lambda(m)/sqrt(m). In particular d4=log2/2. The ordinary scaled Legendre basis has physical mass D_j=2/(2j+1), under f(u)=T^-1/2 p(u/T). No extra1/2 belongs on the API's one-sided coefficient.

The independent arithmetic argument proves

p_*=(log2)(1+sqrt17)/4+log3/sqrt3 < p0=49/32.

The joint2/4 norm uses U_tau2²=U_tau4 and the exact three-point fiber eigenvalues; it does not assume those shifts are independent or that their spectrum is symmetric. With a=7/2,

M >= m0 I, m0=63/32.

The weaker individual-term triangle bound remains valid but is not the preferred allowance. The bare M-only scalar-reference Schur bound7/9 is not a positivity result for M+K.

## 2. Exterior and form-domain obligations

A is even, and DLMF5.7.6 gives

A'(t)=(t/2)sum_(k>=0)(k+1/4)/[(k+1/4)²+t²/4]² >0 for t>0.

The existing independently qualified scalar record proves A(256)-7/2>1/5. This statement is independent of support T. Thus the same a=7/2,Omega256 gives a nonnegative complete exterior throughout this window; no new cutoff is forced by the activation of4 alone.

The natural log-weighted Fourier form domain and the smooth-core approximation argument are unchanged for each fixed finite T. The bounded arithmetic/pole/band sum preserves lower semiboundedness of the closed exterior form. This is not a new identification of all closed operator domains with Suzuki's canonical realization. The relevant smooth-test source identity remains an external premise, and no RH assertion is assumed.

## 3. Complete compact complement and mixed Gram

For a Legendre projection retaining degrees0,...,N-1, set c=T Omega and

E_N(z)=(2N+1)z^(2N)/((2N+1)!!)^2/[1-z²/((2N+1)(2N+3))].

Require the displayed geometric ratio below1. The unchanged scalar band weight satisfies W=max(abs(A(0)-a),abs(A(Omega)-a))<9. Put beta=2T Omega/pi and

kappa(T,N)=9 beta E_N(T Omega)+4T exp(T)E_N(T/2),

eta(T,N)=9 sqrt(beta E_N(T Omega))+4T exp(T)sqrt(E_N(T/2)).

The plane-wave/Rodrigues and exact signed-pole arguments of C-0094 prove the FULL bounds

||Q_N K Q_N||<=kappa, ||Q_N K||<=eta.

The second is one-sided, not an unjustified reuse of a double compression. No finite columns stand in for the complement. Let d=m0-kappa>0 and epsilon=2p0 eta+eta². Then

Q_N H0 Q_N>=dI,

G_total=Pi(P+K)Q(P+K)Pi <= GP+epsilon I,

where GP=Pi P Q P Pi contains the full2/3/4 combined square, including every mixed product. In ordinary Legendre form coordinates the allowance is epsilon D, not epsilon times the coordinate identity.

Consequently, for complete Loewner enclosures of the actual low matrices,

A_- - [(GP)_+ + epsilon D]/d >0 in both complete parity blocks

implies H0>0 on all H_T and hence smooth-test Weil positivity. A negative sufficient lower does not prove H0 negative. The finite sign is uncomputed here.

## 4. Uniform analytic comparison at the existing projection

This paragraph uses a rational majorant, not a support probe. Positive finite exponential sums prove log5/2<13/16. Thus T Omega<208 and T/2<13/32 on the entire window. Both E_N and all displayed prefactors are increasing in their positive arguments. At the already existing comparison order N312, executed512-bit scalar controls therefore give

kappa <3e-27,

eta <7/(5*10^13)=1.4e-13,

epsilon <1/(2*10^12)=5e-13.

The direct majorant displays are kappa about2.02438068913e-27 and eta about1.34979354726e-13. Hence d>63/32-3e-27>0 uniformly. A valid whole-window sufficient predicate at this projection is

A_- - [(GP)_+ + 5e-13 D]/[63/32-3e-27] >0.

This proves a complete outside allowance and conditional finite criterion, NOT positivity of the uncomputed family. The pointwise kappa(T,N),eta(T,N) formulas should be used when useful; a future fixed case need not pay this worst-window mixed allowance. The old3e-40 allowance is not transferable unchanged. For N>=312 the geometric majorant decreases with N at c<=208, but no new test dimension is selected by this observation.

## 5. Correct arithmetic reconstruction

The seven strict global cells are bounded by

-1,1-tau4,1-tau3,tau2-1,1-tau2,tau3-1,tau4-1,1.

Their ordering follows from log6>2T. The active images from left to right are {+2,+3,+4},{+2,+3},{+2},{+2,-2},{-2},{-2,-3},{-2,-3,-4}. Every cell has positive length in the open window.

For image-pair Gram entries, integrate over

I_(alpha,beta)=[-1,1] intersect[-1-alpha,1-alpha] intersect[-1-beta,1-beta].

Of36 ordered signed-image pairs,18 same-sign and2 opposite-sign2/2 pairs have positive length. Sixteen are empty. Ten of the nonempty pairs involve4; ten additional pairs involving4 are empty. Literal composition U_alpha U_beta has different intermediate-point indexing; the Gram domains represent U_-alpha U_beta. The newly nonzero literal squares U_+-tau2² correspond to opposite-sign image pairs. These distinctions prevent the old skip-all-opposite-sign shortcut from losing the central2/2 terms.

On each cell the combined images are polynomials of degree at mostN-1, so Gauss order at leastN integrates all products exactly. A separate checker may use a different higher order and direct pair intersections. Every log, coefficient, threshold, cell order, node and weight uncertainty must remain enclosed. Reflection still preserves parity. The existing generic P2 core already defines these cases; it is not modified or reinterpreted here.

## 6. Frequency quadrature and expanded anchor range

The analytic operator has kernel (T/pi)[A_complex(z)-a]cos(Tz(x-y)), where

A_complex(z)=[psi(1/4+iz/2)+psi(1/4-iz/2)]/2-log pi.

The existing exact panels, radii rho=2h and uniform4096 bound for abs(A_complex-a) depend only on a and Omega, not on T. Their pole-exclusion and DLMF signed-tail proof therefore remain valid. The complete operator quadrature error is

E_quad(T,q)=sum_panels 8h(2T/pi)exp(2T rho)4096*2^(-2q).

At the support majorant13/16, controls give E_quad(T,48)<2e-20 and E_quad(T,64)<5e-30. These are bounds, not promises that either order suffices for an unknown low positive margin. In ordinary Legendre coordinates pay E_quad D, or valid entrywise radii E_quad sqrt(D_i D_j), together with all node/weight and rational rounding errors.

The actual positive frequency nodes now obey w=Tt<208. The frozen w<170 guard is therefore not a valid extension contract. For anchors n>=312 and K384, u=w²/4<=10816 and b=n+3/2>=313.5. The absolute first omitted0F1 term is at most35^385/385!, strictly below(3/11)^385 using e<3. Its following ratio is at most10816/[386*(1397/2)]<1/16. Thus the whole hypergeometric tail is bounded by

(16/15)(3/11)^385 <2^-720.

This is an absolute0F1 tail, not a per-mode error that survives downward recurrence unchanged. Multiply by w^n/(2n+1)!! and propagate both anchor balls through every exact recurrence. Strict positive node enclosures avoid the removable-zero division; otherwise an entire limit formula is required. No fixed precision is guaranteed to succeed solely by citing this tail.

For the pole, alpha=T/2<13/32 and its positive0F1 argument satisfies u=alpha²/4<169/4096. The same geometric first-omitted-term formula with128 terms and b>=3/2 provides a complete finite tail. Both pole signs and its exact rank remain unchanged.

## 7. What is qualified and what remains missing

The arithmetic, domains, exterior, complete compact complement and analytic source-enclosure method are qualified on the whole bounded window. The same a and Omega are admissible, and the existing projection provides an explicit uniform complement comparison. This removes no finite positivity obligation and proves no unbounded family.

No rational support has been selected and no new low matrix, witness or support theorem has been generated. A concrete case still needs justified parameters/accuracy, correctly versioned source/checker implementation and complete independent acceptance of its new entries. The frozen C-0096 program and certificate remain unchanged. No production format, whitelist, Rust/Lean contract or theorem admission is broadened.
