# Quantitative bounded-reference closure and global real-residual bounds

- **Finding ID:** `F-20261025-005`
- **Created:** `2026-10-25T14:24:24Z`
- **Last updated:** `2026-10-25T15:04:56Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED` analytical bounds and source-conditional scalar consequences; no new positivity theorem or admission

## Statement

Two explicit estimates are qualified. They are different mathematical contributions, not evidence that either establishes all-support positivity.

### C-0094: a complete bounded-minorant sufficient criterion

On H_T=L²(-T,T), with zero extension and Fourier measure dt/(2pi), Suzuki's smooth-test form splits as

\[
Q_W[f]=\langle f,H_0f\rangle+
\int_{|t|>\Omega}(A(t)-a)|\widehat f(t)|^2\frac{dt}{2\pi},
\]

where A(t)=Re psi(1/4+it/2)-log pi, H0=aI+P+K, P is the complete signed compressed prime-power sum, and K is the finite-band Archimedean term plus the signed rank-two pole. In particular the odd pole is negative. H0 is bounded and K compact; the original form still has its logarithmic Fourier domain.

At each T in {3/5,1353/2048}, with a=7/2, Omega256 and the scaled Legendre projection Pi retaining degrees0,...,311, rigorous scalar bounds give

\[
A(t)-a>1/5\ (|t|\ge256),\quad\|P\|<9/8,
\]
\[
\|QKQ\|<10^{-82},\qquad\|QK\|<10^{-40},\qquad Q=I-\Pi.
\]

Let A312=Pi H0 Pi and GP=Pi P Q P Pi, using the combined arithmetic square including2/3 mixed products. Then

\[
\boxed{A312-\frac{GP+3\cdot10^{-40}I}{19/8-10^{-82}}\succ0
\ \Longrightarrow\ H_0\succ0\ \Longrightarrow\ Q_W>0
\text{ on nonzero admissible smooth tests}.}
\]

This pays the entire outside block and all arithmetic/compact cross terms. The finite low-matrix sign has **not** been evaluated. Neither a positive M=aI+P alone nor the small compact tail proves H0 positive.

### C-0095: complete real residual, without the local Taylor cutoff

For every finite T>0, write the exact scaled residual kernel as

\[
R_T(x,y)=2T\cosh(T(x-y)/2)-Tg(T|x-y|),
\]
\[
g(t)=\frac{e^{-t/2}}{1-e^{-2t}}-\frac1{2t}
=\frac1{4\cosh(t/2)}+t\sum_{n\ge1}\frac{(-1)^n}{t^2+4\pi^2n^2}.
\]

Its removable endpoint has g(0)=1/4 and g'(0+)=-1/48. Uniform real bounds |g'|<=5/48 and |g''|<23/288 imply

\[
C(T)=11T^2/24+23T^3/144,
\]
\[
\boxed{\|Q_NR_TQ_N\|\le\frac{C(T)}{N(N+1)}+4Te^T E_N(T/2),}
\]
\[
\boxed{\|Q_NR_T\|\le\frac{C(T)}{N(N+1)}+
4\sqrt{Te^T\sinh(T)E_N(T/2)}.}
\]

Here N>=1 retains degrees0,...,N-1 and

\[
E_N(z)=\frac{(2N+1)z^{2N}}{((2N+1)!!)^2}
\left(1-\frac{z^2}{(2N+1)(2N+3)}\right)^{-1}
\]

requires its displayed ratio below1. This can be satisfied at every finite support. The estimate has no2T<pi condition or fixed Taylor-error floor. The one-sided estimate controls low-to-tail maps too; C-0088's polynomial-removal double-tail estimate cannot simply be reused for that purpose.

## Evidence / derivation

Full derivations and independent written qualifications are retained in [X-20261025-005](../computations/2026-10-25T142424Z-reference-route-selection/record.md):

- [Bounded-minorant closure](../computations/2026-10-25T142424Z-reference-route-selection/bounded-minorant-closure-v1.md) and [independent Fourier qualification](../computations/2026-10-25T142424Z-reference-route-selection/fourier-qualification.md).
- [Real-kernel derivation](../computations/2026-10-25T142424Z-reference-route-selection/physical-tail-derivation-v1.md) and [independent real-kernel qualification](../computations/2026-10-25T142424Z-reference-route-selection/physical-tail-qualification.md).
- [Actual scalar output](../computations/2026-10-25T142424Z-reference-route-selection/data/scalar-controls-v1.json) and [rational threshold checks](../computations/2026-10-25T142424Z-reference-route-selection/data/rational-decision-checks-v1.json).

DLMF's digamma series proves A'(t)>0 for t>0. A4096-term signed-tail enclosure and direct512-bit Arb digamma corroborate the exterior lower. Rodrigues bounds on real and imaginary plane waves control the full compact complement. The total Gram is bounded by GP+(2||P|| eta+eta²)I, eta=||QK||, not by omitting mixed terms.

For C-0095, the csch partial-fraction identity gives global derivative estimates. Differentiating the absolute-value kernel contributes the essential multiplier -T²(1-x²)/24. Its remaining kernel has a Schur bound C(T). H² range, vanishing Legendre endpoint flux and Parseval justify the spectral inverse1/[N(N+1)]. The pole is retained at exact rank two with norm2T+2sinh(T).

## Executed scalar comparison

| Quantity | Support | Order | Upper-bound display |
| --- | --- | --- | --- |
| Fourier compact double tail | 3/5 | 312 | 9.57560433089e-110 |
| Fourier compact double tail | 1353/2048 | 312 | 1.32582535176e-83 |
| Global real-residual double tail | 1353/2048 | 312 | 2.52001201167e-6 |
| Retained local C-0088 double tail | 1353/2048 | 312 | 5.93923468717e-7 |
| Global real-residual double tail | 2 | 312 | 3.18578593339e-5 |

The two rows for the physical residual at the current support bound the same residual double compression. Their ratio is about4.243, so the new global estimate is **coarser locally**, not an improvement in that allowance. Fourier rows bound a different compact operator and must not be compared to physical residual norms as a cross-method speed or positivity advantage.

The time-band gap has qualitative positivity, but exact bump trials give upper bounds displaying8.624e-66 and1.633e-72. Those are not lower certificates. C-0094 drops the nonnegative exterior and does not require that gap as a quantitative reserve.

## Dependencies

- `R-0028`: Suzuki [arXiv2606.09096v3](https://arxiv.org/html/2606.09096v3), especially §§1.1,2.4,4.2.
- `R-0030`: [DLMF5.7.6](https://dlmf.nist.gov/5.7.E6), digamma series and the locally uniform derivative argument.
- `R-0036`: [DLMF4.36.5](https://dlmf.nist.gov/4.36.E5), the hyperbolic partial fraction.
- C-0088 for the existing spectral-domain argument and the distinct retained local comparison. Its Taylor remainder is not a premise of C-0095.
- C-0063/C-0072/C-0093 for the existing trust distinctions and the matched-reference comparison, not as substitutes for a new H0 sign.

## Significance for RH research

C-0094 supplies explicit full-complement control for a genuinely different bounded reference, rather than relabeling the same dense elimination. C-0095 removes one source-enclosure radius restriction analytically and controls one-sided residual maps. Both are intermediate mathematical capabilities.

Neither is a new support-positivity result. Larger support changes the entire arithmetic reference and can force larger a and Omega. A proved unbounded support-covering positive family is still missing. These standard-source derivations and their explicit local application are not accompanied by a literature originality or priority claim.

## Limits

No finite H0 positivity matrix, negative H0 trial, matrix source generator, production certificate, Rust admission or Lean proof was produced. The existing local kernels and their refusal behavior remain unchanged. The global residual's boundedness does not identify every closed operator domain with Suzuki's canonical realization. Smooth-core agreement and complete operator-domain equality remain distinct statements. Admission inventory stays8v1/0v2/1v3; RH remains unresolved.

## Verification

Independent written reviews qualify both source/sign/domain arguments and derivative constants. The actual research CLI exits0; the captured-source execution under isolated Python also exits0 and reproduces the full scalar report byte-for-byte. Direct digamma versus signed finite series and direct kernel derivatives versus partial fractions are separate formulas within the same Arb trust premise, not independent libraries. No permanent tests, full suite, Rust or Lean checks were run for this analytical investigation. Initial type-conversion failure and line-ending-only source-identity mismatch are preserved with their exact procedures and records.

## Timestamped addenda / corrections

None. The independent Fourier qualification notes a scaling typo in one Suzuki display; the source's later Rayleigh formula and the unitary scaling used here are consistent. This is not a retrospective change to earlier repository evidence.
