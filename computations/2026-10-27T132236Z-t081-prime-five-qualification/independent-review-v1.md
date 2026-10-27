# Independent T81/100 qualification review

- **Created:** `2026-10-27T13:49:47Z`
- **Last updated:** `2026-10-27T13:49:47Z`
- **Method:** separate read-only reviewer; no calculations or tests executed by reviewer

## Verdict: scope-approved

**No concrete defect found in the reviewed supported-reference, parameter/error qualification, or four-mode diagnostic.** This approval applies only to the executed scalar/error qualification at \(T=81/100\), not to full target matrices or positivity.

**Overall correctness:** correct within the assigned scope.  
**Confidence:** 0.92.

All file references below are relative to `computations/2026-10-27T132236Z-t081-prime-five-qualification/`, unless otherwise indicated.

### 1. Supported-reference transfer is mathematically sound

The transfer uses the old **whole-frequency multiplier inequality**, not old positivity, dimension, or spectral-gap information. A global multiplier inequality can be integrated against the Fourier density of a new-support input in the logarithmic form domain.

The new compressed discrepancy increment is
\[
c_5S_{\log5}-\int_{8/5}^{81/50}e^{l/2}S_l\,dl.
\]
For \(T<l<2T\), the two shift edges are disjoint: \(U_l^2=0\), and \(S_l^2\) is their support projection. Thus \(\|S_l\|=1\). Both the new prime shift and the added continuum strip satisfy this geometry. The resulting upper charge is correctly
\[
c_5+2(e^{81/100}-e^{4/5}),
\]
without an extra factor of two and without incorrectly treating small overlap measure as a small operator norm.

Evidence: `reference-and-error-contract-v1.md`, §3; `qualify-reference-v2.py:149–175`; `verify-reference-v2.py:218–285`. The consumer pins the old inputs/source/audit, invokes the old standalone checker, and requires its reconstructed audit to equal the retained audit before accepting the transfer.

The supported publication \(\beta=821/512\) is correctly distinguished from the fresh global pointwise comparison \(\beta_{\mathrm{global}}=1933/1024\). The code checks the global finite cover and analytic infinity separately; it does not assert the smaller supported constant pointwise (`verify-reference-v2.py:279–346`).

### 2. Source, domain, and physical mass agree

The source identity retains the signed continuum and pole contributions:
\[
\mathfrak l_T=q_{A_F}+\langle f,L_Tf\rangle-d_{E,T}.
\]
The positive \(L_T\) term does not replace or reverse the original pole. Under the declared unitary scaling, ordinary Legendre mass remains \(D_n=2/(2n+1)\); support factors belong in the mapped operators.

This agrees with the baseline `reference-contract-v1.md`, §§1 and 4, and the C-0063 source/domain convention. The new contract does not claim equality of entire operator domains. The arithmetic activation checks reconstruct exactly \(2,3,4,5\), including \(\Lambda(4)=\log2\), independently on the consumer side (`verify-reference-v2.py:145–174`).

**Premise boundary:** the Suzuki/source identification and existing analytic source theorems remain shared mathematical premises. Consumer independence here concerns reconstruction and acceptance—not a new proof of those source premises or independent arithmetic.

### 3. Outside, leakage, eta, and inverse bounds are complete

The consumer independently reconstructs the factorial expression for complete Legendre leakage, checks every preceding even cutoff, and verifies both
\[
g(R)-(g(R)-g(0))\lambda_N(R)\ge m,
\qquad
(m-g(0))\lambda_N(R)/m\le2^{-128}.
\]
It also verifies the first integer anchor by its predecessor and monotonicity. These establish the stated sufficient-policy minimum \(R=710,N=826\), rather than a minimum true positivity dimension.

At \(M=1652,R_c=1420\), the consumer checks complete leakage, \(0<a<1/m\), and
\[
\kappa=a+(1/m-a)\lambda_M(R_c)<1/m.
\]
The declaration’s use of published upper endpoints is conservative because this expression is increasing in both arguments on the checked ranges.

Evidence: `verify-reference-v2.py:348–414`; `verify-target-declaration-v1.py:248–260`. The 60 inverse-frequency anchors retain a strictly positive terminal Parseval weight, so frequencies above \(32R\) are paid, not discarded (`verify-target-declaration-v1.py:359–380`).

### 4. Canonical error and precision qualification are properly separated

The declaration consumer reconstructs the complete canonical coefficient list by exact formal division, checks \(c_1=T^2/48\), and independently evaluates the analytic remainder and cross majorant. It checks
\[
\Lambda_K=\delta_K+\frac{2B_K\delta_K+\delta_K^2}{m\eta}
\]
for the selected order and every preceding even order. The finite-band conditions \(2K<N\) and \(M\ge N+K\) are explicit; zero polynomial-model output beyond \(M\) does not erase the true residual discrepancy.

Evidence: `verify-target-declaration-v1.py:168–197, 328–358, 381–404`. The retained audit reports \(K=86\), with all 42 preceding even orders checked.

The old selected-Schur scalar supplies an **accuracy choice only**. Source4608, independent6144, and publication256 are independently reconstructed **starting precision policies**, not achieved target enclosure widths. Actual full target matrices must still satisfy the complete physical numerical-radius goal, accuracy/4. The consumer and contract explicitly preserve that distinction.

### 5. Four-mode diagnostics check the intended structural hazards

The producer forms the complete signed arithmetic image before squaring. Its generic assembly consumes every active term, so prime 5 reaches the combined square and projected Gram rather than being silently dropped.

The independent consumer reconstructs all five \(4\times4\) families—\(P,P^2,G_P,VP,PV\)—using Rodrigues polynomials, binomial shifts, and ordinary/logarithmic moments. It checks native containment for all 80 entries across the complete translation partition. It reconstructs VP and PV separately and requires a same-parity VP asymmetry, which would reject premature symmetrization. All three mixed prime-5 constant-mode contributions are also checked.

Evidence: `qualify-prime-five-topology-v1.py:54–76`; `verify-prime-five-topology-v1.py:178–242`; generic dispatch in `scripts/cert/prime_power_terms.py:426–449, 551–591`.

This is appropriate representative structural coverage: both parities, off-diagonal ordered products, all activated shifts, and every new mixed pair. It is **not** numerical qualification of high modes or the full target computation.

### Evidence and limits

The retained supported-reference, declaration, and topology audits record PASS, respectively including 1563 scalar intervals, 42 rejected preceding residual orders, and 80 checked diagnostic entries. I inspected those records and the accepting code; **I did not rerun them**, edit files, or execute matrices, tests, builds, or benchmarks.

The independent consumers do not import producer mathematics. They do share FLINT/Arb arithmetic and transcendental enclosures; the scalar consumer additionally shares FLINT’s exact Bernoulli values. Native enclosure containment—not rounded-report overlap—is enforced, including through the declaration consumer’s replay of reference acceptance.

The false matrix/sign/admission flags and qualification-only statuses match the reviewed computations. **No \(T=0.81\) positivity proof, full target low/coupling sign, or production admission follows from this bundle.** The legacy fixed-\((2,3,4)\) full-target generator/consumer paths are outside this executed qualification and are not approved here for a prime-5 target run.
