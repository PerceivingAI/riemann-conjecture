# Exact residual cross band and complete model-error control

- **Created:** 2026-10-26T19:19:41Z
- **Last updated:** 2026-10-26T19:19:41Z
- **Scope:** Existing T3/4,N312. Whole-low residual representation and complete error budget, not a mixed-Gram sign or support extension.

## 1. Actual source, model and unchanged stopped completion

C-0063/C-0115 give B=Q(V+P+R)Pi in the unitary scaled space L²(-1,1), ordinary Legendre mass D_n=2/(2n+1). R includes the full signed polar rank2. C-0116 rejects treating the whole R cross as an independent isotropic error r. It does not reject a model retaining signed R action and its correlation with V/P.

Use the canonical local expansion, not a new residual identity:

    R_K(x,y)=sum_(d=0)^K c_d |x-y|^d,
    c_d=-T^(d+1) a_d,
    a_d=Taylor coefficient of r_even_second at positive0.

The unchanged scripts.cert.residual_kernel coefficients are exact rationals. Its complete positive-side remainder at2T gives

    ||R-R_K||<=delta_K=2T * tail_radius(2T,K).

The factor2T is kernel prefactor T times row/column interval length2. Require2T<pi; no global-support claim or changed canonical refusal behavior. All pole and regular-source tails are paid. Even polynomial terms may vanish from this cross but NOT from the actual low block.

## 2. Exact whole-map band, not sampled columns

For even K, put s=K, with2K<N. Every even d<=K has polynomial kernel(x-y)^d, hence range degree<=d<N and Q R_d Pi=0. For odd d, differentiating the kernel d+1 times yields2d! times the delta distribution. Thus for a Legendre input P_n,

    R_d P_n=2d! c_d I^(d+1)P_n + polynomial of degree<=d.

Boundary polynomials are not set to zero; Q_N kills them because d<N. A polynomial input of degree n has image degree at most n+d+1. Therefore the exact finite cross is

    Q_N R_K Pi_N
      = P_[N,N+K) R_K P_[N-K,N).

This acts on ALL312 low vectors. Every other low column and every output beyond N+K-1 is exactly zero for the MODEL, not for the full residual. The remainder delta_K pays the entire remaining infinite operator. Both parity sectors and every odd coefficient are retained.

For j>=1,

    I P_j=(P_(j+1)-P_(j-1))/(2j+1).

Since2K<N, all degrees in the needed walks are positive. This yields exact rational coefficient-map entries U_mn. Stored entries are EXPANSION coefficients, not inner products: <P_m,R_K P_n>=D_m U_mn. Output energy is sum D_m |sum U_mn x_n|². The physical mass must never be inserted twice or omitted. The independent consumer instead repeatedly integrates exact power polynomials and removes high Legendre terms, not the source's Legendre coefficient walk.

## 3. Known full-gap control without circularity

Only at this already accepted support, reuse C-0100's exact positive parity proof, g=min accepted finite mass gaps. C-0099 gives mu=63/32-4e-49 and the full bounded-source cross bound b0<=49/32+2e-24. C-0086's domain-safe square completion gives

    ell=min(g/[1+2(b0/mu)^2],mu/2)>1e-15.

The proof packet is SHA-bound. Its mass trace/transform and exact gap conversion are checked. Bounded H0>=ell I and the complete nonnegative Fourier exterior imply actual q_W>=ell I on its form domain. Adopt the conservative known control ell0=1e-15. This is not the gap of the NEW energy-reference Schur matrix or an assumption at an unproved support. It supplies a genuine whole-low error scale, unlike C-0116's Rayleigh UPPERS, which must never be used as gap lowers.

## 4. Complete residual-aware Schur-error interface

Let A_K retain the actual low harmonic,V,P and FULL low R_K, and let

    B_K=Q(V+P+R_K)Pi,
    G_K=integral (JB_K)^*(JB_K)/h.

R_K is part of the SIGNED combined source before forming this Gram. Its V/R_K and P/R_K mixed terms are not dropped or bounded separately as the stopped r²/m identity charge.

The same global remainder gives ||A-A_K||<=delta and ||B-B_K||<=delta with NO source-column factor. C-0085 and C-0097/C-0115 imply

    b_K=pi/2+49/32+1/300000+delta >=||B_K||.

For m1/3 and eta>=eta_low=1-9e-49, weighted Cauchy-Schwarz yields

    S_true >= A_K-eta_low^-1 G_K-Lambda I,
    Lambda=delta+eta_low^-1[2 b_K delta/m+delta²/m].

This is a full matrix-order criterion, including both low source and infinite coupling errors. G_K remains positive before scaling by eta_low. No finite inverse or old positive Gram is substituted. A complete implementation must still evaluate G_K and the actual A_K with all their errors.

Select the FIRST EVEN K>=2 whose published complete remainder upper satisfies delta<=ell0/1024. This is a derived enclosure order, not a search for a favorable Schur sign. Check2K<N and Lambda<=ell0/16. Then

    A_K-Lambda I >= (ell0-delta-Lambda)I >= (7ell0/8)I.

This whole-low NECESSARY BUDGET check passes independently of selected directions. It does NOT establish positivity after subtracting G_K/eta_low. It proves that this residual-model approximation does not impose the previous low-source identity-floor obstruction. An error budget at the known positive control gives no unknown-support parameter/gap law.

## 5. Executed qualification and limits

Construct and independently verify every entry of the exact band, all kernel coefficients, complete tail bounds/order policy, physical masses, inherited control-gap conversion and the global model-error inequality. Reconstruct the two retained C-0116 critical vectors, their exact model output, and the FULL residual image allowance including the remainder. These diagnostic directional estimates do not replace the global matrix-order proof.

A successful result qualifies this residual-aware representation, not full mixed-Schur usefulness. No support/projection enlargement, whole new low/Gram source, production admission, root library/CLI upgrade or a new uniform residual theorem is selected. The old stopped completion and every historical source/result remain unchanged. The missing weighted mixed V/P/R_K coupling and actual low-model sign remain explicit.
