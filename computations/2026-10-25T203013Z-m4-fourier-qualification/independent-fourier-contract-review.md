# Independent review of the full Fourier extension contract

- Date: 2026-10-25
- Reviewed object: fourier-extension-contract-v1.md, sections 1 through 7.
- Verdict: qualified mathematical contract, conditional on its stated source and historical scalar-enclosure premises. No mathematical error requiring a repair was found. New low finite positivity remains uncomputed.
- Method: symbolic review and inspection of retained documents and source only. No numerical job, matrix job, test, build, lint or formatter was run for this review.

## Evidence and scope

I read the complete extension contract, independent-arithmetic-qualification.md, C94's bounded-minorant-closure-v1.md, and C96's matrix-enclosure-derivation-v1.md. I inspected qualification-controls-v1.json and the frozen C96 auditor's finite hypergeometric sum, transform recurrence, band assembly and signed pole assembly.

The controls are retained evidence, not runs performed by this reviewer. I did not regenerate their arithmetic or independently certify their hashes or provenance. Suzuki's smooth-test identity and the historical scalar exterior enclosure remain explicit premises. This review does not reproduce Suzuki's paper or identify its canonical closed operator domain.

## 1. Arithmetic normalization and geometry

Contract sections 1 and 5 are consistent with the independent arithmetic derivation. Under g(x)=sqrt(T)f(Tx), ordinary Legendre mass is D_j=2/(2j+1). The coefficient of each one-sided shift is d_m=Lambda(m)/sqrt(m), so d4=log(2)/2. There is no additional factor one half or physical factor T in these shift coefficients.

The active set is exactly 2,3,4 because 4<exp(2T)<5. Put s=log(2)/T. Then 2/3<s<1 and tau4=2s. On three-point dyadic fibers, the joint 2/4 adjacency matrix divided by log(2) has nearest-neighbor entries 1/sqrt(2) and outer edge 1/2. Its characteristic factors are

(lambda+1/2)(lambda^2-lambda/2-1).

Its largest absolute eigenvalue is (1+sqrt(17))/4; shorter fibers have smaller norm. Adding the 3 contribution in norm yields the stated p_star, without commutativity or spectral symmetry assumptions. The independent elementary rational envelope proves p_star<49/32 and M>=63I/32.

The seven-cell ordering is correct. For signed shifts alpha,beta, the image-pair intersection has length

max(0,2-[max(0,alpha,beta)-min(0,alpha,beta)]).

All 18 same-sign ordered pairs survive. Among opposite signs only the two ordered 2/2 pairs survive, giving 20 positive-length pairs and 16 empty pairs. Of the 20 pairs involving 4, ten survive and ten are empty. The image-pair product is U_-alpha U_beta. The newly surviving opposite-sign image pairs therefore represent literal same-sign shift squares, not opposite-sign compositions. The contract states this distinction correctly.

Products on each cell have degree at most 2N-2, within Gauss order N exactness through degree 2N-1. This does not remove the obligation to enclose uncertain geometry, coefficients, nodes and weights. Parity follows from the complete reflection-invariant signed sum.

The bare arithmetic comparison is also correct:

m0-p0^2/m0=(63^2-49^2)/(32*63)=7/9.

It establishes no sign for M+K.

## 2. Exterior and domain statement

The derivative in section 2 has the correct factor:

A'(t)=(t/2) sum_(k>=0) (k+1/4)/[(k+1/4)^2+t^2/4]^2>0.

The derivative series converges locally uniformly. Evenness and the historical A(256)-7/2>1/5 enclosure control the entire exterior. Neither statement depends on T. Activating the arithmetic term 4 does not alter A or require a new cutoff by itself.

The contract correctly separates bounded H0 on all H_T from the unbounded logarithmic Fourier form. The nonnegative exterior is a closed weighted Fourier form. Restricting it to zero-extended functions with fixed compact support remains closed in the form norm, and bounded arithmetic, pole and band perturbations preserve closedness and lower semiboundedness. Smooth tests belong to the domain. The inherited fixed-T core statement is not a claim to identify Suzuki's complete canonical operator domain. The positivity implication needed here already holds directly on smooth tests, without that stronger identification.

## 3. Full compact complement and mixed Gram

Section 3 distinguishes the one-sided and double-compression estimates correctly. Rodrigues' formula bounds the real plane-wave Legendre tail squared by 2T E_N(T|t|). The ratio of consecutive nonnegative majorant terms is

z^2/[(2n+1)(2n+3)],

which decreases in n. This gives E_N when its first ratio is below one. Integrating over both halves of the frequency band with measure dt/(2pi) yields beta E_N, beta=2T Omega/pi.

Writing the band operator as F*BF, with ||B||<=9 and ||F||<=1, gives

||Q K_band Q||<=9 beta E_N,

||Q K_band||<=9 sqrt(beta E_N).

The second estimate is on the whole right-hand Hilbert space. A double compression alone would not justify it.

For the signed pole, let v_plus/minus(u)=exp(plus/minus u/2). Its operator is

K_pole=|v_plus><v_minus|+|v_minus><v_plus|,

which equals 2|cosh><cosh|-2|sinh><sinh|. Bounds ||v_plus/minus||^2<=2T exp(T) and ||Q v_plus/minus||^2<=2T exp(T)E_N(T/2) give exactly the factors 4T exp(T) in kappa and eta. The negative odd pole is retained. There is no missing factor two.

Set X=Q P Pi and Y=Q K Pi. Then ||X||<=p0, ||Y||<=eta and

(X+Y)*(X+Y)<=X*X+(2p0 eta+eta^2)I.

This pays both signed mixed terms and the compact square without assuming the mixed terms positive. Also Q H0 Q>=m0-kappa=d>0. These are the needed Schur hypotheses.

In ordinary quadratic-form coordinates, GP=S-P_low D^-1 P_low. Hilbert-space scalar allowances become epsilon D, not epsilon times the coordinate identity. Complete low Loewner enclosures and two strictly positive parity blocks therefore imply strictly positive H0 by bounded-operator square completion. A negative sufficient lower does not prove H0 negative.

## 4. Uniform comparison is not support selection

Section 4 uses 13/16 only as an upper bound on log(5)/2, certified by a positive finite exponential sum at exponent 13/8. It does not choose T=13/16 as a support or assert that its active arithmetic set is 2,3,4.

At N=312 and c<=208, the geometric ratio is below one because 208^2<625*627. E_N, beta and the pole prefactor increase in the relevant positive arguments. Substitution of the rational upper bound for T is valid for these error estimates. Increasing N decreases E_N in this range by the successive-term ratio and the improved geometric denominator. This selects no new case.

The retained outward endpoints support kappa<3e-27 and eta<1.4e-13. Even their rounded upper bounds imply

2*(49/32)*(1.4e-13)+(1.4e-13)^2<5e-13.

Thus d>63/32-3e-27>0. The displayed uniform finite predicate uses a conservative upper numerator and lower positive denominator. The historical 3e-40 allowance cannot replace this whole-window mixed allowance. None of these bounds supplies a finite matrix sign.

## 5. Complete frequency quadrature

The complex kernel scaling in section 6 agrees with C96. Even-frequency reduction gives T/pi, and Schur's kernel estimate on an interval of length two gives

M=(2T/pi)exp(2T rho)*4096.

The digamma poles are z=plus/minus i(2n+1/2). The first two panel disks have imaginary extent at most 1/4; every later disk lies strictly in the right half-plane. The historical pole exclusion and uniform 4096 envelope survive. Their proof depends on the panels, a and Omega, not T.

With rho=2h, the Cauchy Taylor remainder after degree 2q-1 is at most 2M*2^(-2q). The integral and positive Gaussian rule each have total weight 2h. Their combined panel error is therefore 8hM*2^(-2q), exactly the contract's factor. Summing all panels bounds the complete band rather than a frequency sample.

The retained q48 and q64 displays lie below 2e-20 and 5e-30. These are historical scalar enclosures, not newly executed results and not a promise to resolve an unknown low margin. E_quad D is the operator-form allowance. The alternative entrywise radii E_quad sqrt(D_i D_j) are valid but still need a valid matrix-enclosure conversion; entrywise intervals alone are not Loewner bounds.

## 6. Expanded anchors and pole truncation

The frozen auditor's transform_vector rejects w>=170, whereas the new analytic envelope gives only w<208. The contract explicitly does not accept that frozen implementation for the expanded envelope. I inspected the consuming downward recurrence and band assembly as well as the anchor producer.

The summation convention includes indices k=0 through k=384, so the first omitted index is 385. This agrees with the frozen finite_hypergeometric loop. With b=n+3/2>=313.5 and u<=10816,

u^385/[385! (b)_385]<=35^385/385!,

because u/b<35. The factorial bound 385!>=(385/e)^385 and e<3 give the strict upper bound (3/11)^385. Every following ratio is at most

10816/[386*(1397/2)]<1/16.

The whole absolute 0F1 tail is therefore at most (16/15)*(3/11)^385. Its stated binary threshold is the finite exact integer comparison

16*3^385*2^720<15*11^385.

This is not a floating special-function assumption. The tail must be multiplied by w^n/(2n+1)!! separately for both anchors. The exact recurrence

j_(n-1)=((2n+1)/w)j_n-j_(n+1)

must then propagate both anchor balls. Its divisions can amplify radii. The contract correctly guarantees no fixed precision success and requires strictly positive node enclosures or an entire limit treatment at zero.

The pole proof can be made explicit without any numerical run. With alpha=T/2, u<169/4096 and b>=3/2, summing k=0 through 128 leaves

R_pole <= [(169/4096)^129/(129! (3/2)_129)]

          /[1-(169/4096)/(130*(261/2))].

The denominator is positive and all subsequent ratios decrease. This expands the contract's geometric-tail instruction into a uniform formula; it is not a correction. Multiplying by 2 alpha^n/(2n+1)!! encloses the entire pole vector coefficient. The pole form remains 2T times the even outer product minus the odd outer product, retaining both signs and rank at most two.

## Findings and limitations

No blocking mathematical defect was found. No source or proof repair is proposed. The explicit pole remainder and inclusive anchor-index explanation above are derivation details, not findings against the contract.

Qualified conclusions are the whole-window enclosure method, nonnegative complete exterior, strictly positive complement denominator, and conditional complete finite criterion, subject to the stated historical source and scalar premises.

Uncomputed obligations are positivity of any new low matrix, positivity of the family over the interval, and positivity at any newly selected support. A concrete case still needs complete arithmetic and compact low matrices at its exact support, all source and quadrature errors, valid Loewner enclosures, and strict positivity of both complete parity blocks. The frozen C96 source, fixed support, certificate and admissions remain unchanged. No numerical jobs or tests were performed for this review.
