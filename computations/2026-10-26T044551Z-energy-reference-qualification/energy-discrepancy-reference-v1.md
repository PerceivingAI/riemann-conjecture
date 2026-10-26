# Exact pole cancellation and a logarithmic energy reference

- **Created:** `2026-10-26T04:45:51Z`
- **Last updated:** `2026-10-26T05:00:39Z`
- **Scope:** exact operator/form identities, a conditional outside estimate and qualification of a proposed bound; no new finite positivity sign

## 1. Complete source and a different reference requirement

Fix T>0 on H_T=L²(-T,T), with zero extension and Fourier measure dt/(2pi). Include every prime power with log(m)<2T and d_m=Lambda(m)/sqrt(m). Write P=-sum d_m(U_log(m)+U_-log(m)). The signed pole has kernel

    K_pole(u,v)=2cosh((u-v)/2)
              =exp(|u-v|/2)+exp(-|u-v|/2).

Equivalently K_pole=2 h_c h_c* -2 h_s h_s*, h_c=cosh(u/2), h_s=sinh(u/2). The negative odd term remains essential. On the original smooth tests the qualified source identity is

    Q_W[f]=q_A[f]+<f,(P+K_pole)f>,
    q_A[f]=integral A(t)|hat f(t)|² dt/(2pi),
    A(t)=Re psi(1/4+it/2)-log pi.

These are the existing Suzuki/source conventions, not a new operator-domain identification. The archimedean form is unbounded; P and the pole are bounded at every fixed finite T.

## 2. Exact cancellation against the prime continuum

Let psi(x)=sum_(m<=x) Lambda(m) and

    E(l)=psi(exp(l))-exp(l)+1, l>=0.

In particular E(0)=0. Define the bounded signed discrepancy operator through the finite signed measure

    D_E=integral_(0,2T) exp(-l/2)(U_l+U_-l) dE(l).

At an arithmetic endpoint l=2T the compressed shift vanishes on L²; including its zero atom or using the strict upper limit is equivalent. No prime power is removed by endpoint convention. The continuous part has density -exp(l)dl.

Let L_T be the integral operator with kernel exp(-|u-v|/2). Integrating the continuous shift density gives exactly

    P+K_pole=L_T-D_E.

Indeed the continuous term with density exp(l/2) is the kernel exp(|u-v|/2), which cancels that part of the signed pole kernel. Both signs are included before taking a bound. L_T is positive, since the Fourier transform of exp(-|u|/2) is1/(t²+1/4), obtained by integrating the two elementary exponential half-lines. It is compact on H_T because its continuous kernel is square integrable on the finite time square. K_pole is rank two. Consequently

    D_E=-P+(L_T-K_pole)

is a compact correction of -P, not a compact operator in general. The exact continuum cancellation does not make the discrete translation part disappear in operator norm.

For f in H_T, write phi_f(l)=<f,(U_l+U_-l)f>. The identity above holds as a bounded-form identity. For smooth compactly supported f, phi_f is differentiable, phi_f(0)=2||f||² and phi_f(2T)=0. Stieltjes integration by parts gives

    d_E[f]=<f,D_E f>
          =-integral_0^(2T) E(l)exp(-l/2)[phi_f'(l)-phi_f(l)/2]dl.

There is no extra origin term because E(0)=0. This is an exact signed identity, not a bound on prime error inferred from sampled values.

## 3. Explicit scalar discrepancy bound and its actual strength

Put

    B(T)=integral_0^(2T) exp(-l/2)|E(l)|dl.

Every finite T gives a finite B. It can be evaluated from all active prime-power intervals: on each interval E(l)=s-exp(l) with s=1+the cumulative von Mangoldt sum; its only possible zero is l=log(s). The primitive of exp(-l/2)E(l) is -2s exp(-l/2)-2exp(l/2). Certified interval splitting at that zero evaluates the absolute integral without a numerical sampling assumption.

Cauchy gives |phi_f|<=2||f||² and |phi_f'|<=2||f|| ||f'||. Thus

    |d_E[f]| <= B(T)[2||f|| ||f'||+||f||²].

This is a valid H¹ bound, not yet a bound in logarithmic archimedean energy. No zero-free theorem, RH estimate or asymptotic prime-error constant is assumed.

For the already accepted T3/4 only, exact rigorous scalar checks certify E(l)<=0 throughout0<=l<=3/2: between consecutive arithmetic jumps it decreases, and its post-jump values at2,3,4 are strictly negative. Therefore the same B can independently be computed by

    B(T)=2(exp(T)+exp(-T)-2)
         -2 sum_active Lambda(m)[m^(-1/2)-exp(-T)].

This scalar formula is qualified only after that sign check. It is not asserted at other supports, where E may change sign.

## 4. A positive logarithmic reference and an explicit tail bound

Let A0=A(0) and use the positive form

    d_A[f]=q_A[f]+(1-A0)||f||²
          =integral [A(t)-A0+1]|hat f(t)|² dt/(2pi).

Since A is even and increasing for t>0, d_A>=||f||². Its domain is the logarithmically weighted Fourier form domain. This does not require globally positive aI+P or a frequency cutoff exp(a).

For the Legendre tail Q_N, the full Fourier/HS bound from C-0104 gives, for R>0 and a valid geometric E_N(TR),

    integral_(|t|<=R)|hat f(t)|²dt/(2pi)
      <= min(1,lambda_N(R))||f||²,
    lambda_N(R)=(2TR/pi)E_N(TR), f in Q_N H_T.

Writing d_R=A(R)-A0+1>=1 yields the genuine tail form bound

    d_A[f]>=mu_N(R)||f||²,
    mu_N(R)=1+(d_R-1)max(0,1-lambda_N(R)).

This uses the entire band leakage, not retained columns. An explicit choice R=N/(3T) has N>=3TR, so C-0104 gives lambda_N(R)<=(2N/pi)2^(-N). Thus the reference's own tail coercivity grows logarithmically with N at each fixed T. It does not itself certify the complete Weil tail.

One precise sufficient interface would be a proved one-sided discrepancy estimate

    d_E[f] <= alpha(T) d_A[f]+b(T)||f||²,
    0<=alpha(T)<1, b(T)>=0.

If it holds on the form domain, positivity of L_T and the exact identity give the outside lower

    Q_W[f] >= [(1-alpha)mu_N(R)+A0-1-b]||f||²,
    f in Q_N intersect the form domain.

Only when this scalar lower is positive is that outside reference qualified. The complete finite low/cross and Schur positivity obligations remain independent; no earlier positive matrix can be inherited merely because the support is the same. This changes the outside energy estimate rather than the order of a finite Schur elimination. It establishes no strict improvement over another same-source criterion.

The interface alone is not RH in disguise: a trivial bound with alpha0 and b>=||D_E|| always exists for any bounded D_E, without any sign assertion for Q_W. Useful quantitative alpha,b and the independent low sign are the missing information. Claiming all-support Weil positivity instead of proving those estimates would be circular.

## 5. The proposed H¹ closure cannot supply that interface

Fix any real unit g in C_c^infinity(-T,T), put c_g=||g'||, and f_n(u)=exp(inu)g(u). Then

    ||f_n'||²=n²+c_g².

Using C-0103 for |t|>=1, monotonicity for smaller t and a loose constant gives A(t)<=2+(1/2)log(1+t²) for every real t. For the unit Fourier probability measure, the tangent-line bound for concave log gives

    d_A[f_n] <=3-A0+(1/2)log(1+n²+c_g²).

Consequently ||f_n|| ||f_n'|| grows linearly while d_A[f_n] grows at most logarithmically. No finite constants c1,c2 depending only on this fixed support can satisfy

    ||f|| ||f'|| <=c1 d_A[f]+c2||f||²

on all smooth test functions. Hence, whenever B(T)>0, the derivative majorant in section3 cannot be absorbed into logarithmic energy by such a bound. This rejects the proposed absolute-value/integration-by-parts closure, not the actual discrepancy form: D_E itself is bounded on L² and always has a scalar norm bound. Confusing the coarse H¹ majorant with D_E would falsely claim that the true form is not relatively bounded.

The fixed T3/4 scalar check proves B>0. A normalized cosine on[-T,T], zero extended, supplies an H¹_0 numerical illustration with c_g=pi/(2T); it is not claimed to be a smooth Weil test or a positivity computation. The mathematical obstruction above uses genuinely smooth g and is not inferred from finite modulation samples.

## 6. What compact corrections can and cannot repair

The separately proved [compact-correction lemma](compact-correction-obstruction-v1.md) shows that, for T>=7/2, nonnegativity of bI+P+C for any compact self-adjoint C still requires b>(3/20)exp(T); coercivity reserve adds m. It uses finite-phase recurrence and weakly null modulations, not any conjecture on prime distribution. Thus moving the pole or other compact pieces into a bounded scalar reference, or taking only a scalar norm after the exact continuum cancellation, cannot remove that necessary rate.

Since D_E=-P plus a compact correction, an energy-independent one-sided bound d_E[f]<=b||f||² also forces b>=a_*(T): apply the lemma to bI-D_E. This excludes replacing the full norm by a cheaper scalar one-sided discrepancy bound as an escape from the same rate. A useful improvement must genuinely exploit the retained unbounded energy, not only the algebraic continuum cancellation.

In particular the existing bounded Fourier minorant H0=aI+P+K_pole+K_band has only compact corrections at every fixed finite cutoff. Therefore H0>=0 itself requires a>=a_*(T), even if one drops the separate sufficient premise aI+P>=0. When a<a_*(T), the lemma supplies negative directions for that bounded H0. This is a new extension of the earlier scalar-reference obstruction, not a retroactive change to the earlier records. It does not imply Weil negativity: the discarded unbounded exterior can repair the bounded minorant.

The same necessary floor persists after removing any finite-dimensional low space. Thus moving finitely many modes into a different Schur block, adding the signed pole to the reference, or retaining another finite frequency band cannot by itself remove this bounded-reference obstruction. The conclusion does not extend to an unbounded logarithmic outside form.

This does not apply to the unbounded logarithmic reference d_A. At the resonant high modulations used in the compact lemma, archimedean energy need not stay bounded. There is therefore no new Weil negative direction or contradiction with RH.

## 7. Qualification outcome

The exact signed decomposition and the positive logarithmic reference/tail estimate are qualified mathematical identities and bounds. The attempted derivative-based discrepancy closure is rejected as a route to the required logarithmic form estimate. Compact-correction scalar-floor variants are also ruled out as an escape from the already identified necessary reference rate.

No useful alpha,b satisfying the needed outside inequality, new complete low/cross source, positive finite sign, support extension, all-support family or practical cost advantage has been established. This is a completed qualification with explicit unsuccessful bounds and a precise remaining estimate, not an implemented alternative proof system. No generic tooling upgrade, old-source rewrite, production admission, literature-originality claim or assumed uniform coercivity is introduced.
