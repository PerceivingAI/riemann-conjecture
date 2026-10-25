# Independent review of the scalar/error and contraction-volume assessment

## Verdict and scope

**Overall correctness: correct. Confidence: 0.97.**

No mathematical defect requiring repair was found in `assessment-derivation-v1.md`, `assessment-v1.py`, or `data/assessment-v1.json`. The factor below 470, conditional resolution below \(1.5\times10^{-18}\), physical-mass and rounding factors, q49 comparison, and contraction-volume ratios are consistent with the qualified C-0098 contract and the retained corrected C-0096 producer/auditor.

This review used mathematical reasoning and read-only inspection. I did not execute the assessment, independently reproduce its scalar arithmetic, authenticate its hashes, or run tests, builds, formatters, matrix computations, or positivity checks. The recorded successful scalar execution is retained evidence, not a run performed by this reviewer.

The complete review text is returned here because the available tools do not provide an authorized repository-file write under the read-only review restrictions.

## 1. Pointwise complement and physical normalization

The assessment substitutes \(T=3/4\), \(N=312\), and \(\Omega=256\) into C-0098's complete formulas:
\[
\begin{aligned}
\kappa&=9\beta E_N(T\Omega)+4Te^T E_N(T/2),\\
\eta&=9\sqrt{\beta E_N(T\Omega)}
       +4Te^T\sqrt{E_N(T/2)},\\
\beta&=\frac{2T\Omega}{\pi}.
\end{aligned}
\]
The source helper computes the stated rational Legendre-tail majorant, including its geometric denominator.

The retained scalar intervals support the stated bounds
\[
\kappa<4\times10^{-49},\qquad
\eta<1.9\times10^{-24}.
\]
With \(p_0=49/32\),
\[
2p_0(1.9\times10^{-24})+(1.9\times10^{-24})^2
<6\times10^{-24}.
\]
Thus \(k_0=4\times10^{-49}\), \(\epsilon_0=6\times10^{-24}\), and \(d_0=63/32-k_0>0\) are consistent conservative allowances.

The ordinary Legendre mass is
\[
D_j=\frac{2}{2j+1}.
\]
Consequently, Hilbert-space scalar allowances become multiples of \(D\), not the coordinate identity. The assessment uses that convention consistently.

The arithmetic normalization also agrees with C-0097/C-0098. The coefficient of each one-sided shift at 4 is \(\log(2)/2\), without another factor of one half. The stated positive-measure overlap and central opposite-sign 2/2 image intersection agree with the qualified seven-cell geometry.

## 2. Interval-box conversion and the factor below 470

Let \(C\) be a symmetric midpoint matrix in one parity block, let
\[
r_{ij}=E\sqrt{D_iD_j},
\qquad
R=\operatorname{diag}\left(\sum_jr_{ij}\right),
\]
and let \(L=C-R\) be the row-radius lower bound.

For every symmetric \(B\) in the box, \(B-L\succeq0\). Each entry of
\[
D^{-1/2}(B-C)D^{-1/2}
\]
has absolute value at most \(E\). A block has \(p=156\) rows, so its operator norm is at most \(pE\). Also,
\[
\left\|D^{-1/2}RD^{-1/2}\right\|
=E\max_i\sum_j\sqrt{\frac{D_j}{D_i}}.
\]
It follows that
\[
0\preceq B-L
\preceq
\left(p+\max_i\sum_j\sqrt{\frac{D_j}{D_i}}\right)ED.
\]

For ordinary Legendre mass, the sum is
\[
\sqrt{2i+1}\sum_{j\text{ in block}}\frac1{\sqrt{2j+1}},
\]
so its maximum occurs at the largest degree in that parity block. The source evaluates precisely this expression. The retained intervals give approximately
\[
F_{\rm even}=469.9896617245776,\qquad
F_{\rm odd}=454.3289160470118,
\]
with both upper endpoints below 470.

The factor 470 is therefore valid for the specified symmetric entry-box conversion. It is conservative, not an assertion that the actual operator quadrature error is amplified by that amount before conversion.

The two-dimensional control is consistent with the existing exact order helper. It produces \(\operatorname{diag}(-3,-6)\); the true matrix minus this lower has trial loss 4 on \((1,0)\), whose mass is 1. This correctly refutes treating the nominal operator-radius parameter as the complete true-to-ordered-bound loss.

## 3. Conditional \(S_\star\)-to-\(S_-\) loss

Write \(G=GP\), and define the actual one-sided enclosure losses by
\[
\Delta_A=A-A_-\succeq0,\qquad
\Delta_G=G_+-G\succeq0.
\]
Then the exact identity is
\[
S_\star-S_-=
\Delta_A+\frac{\Delta_G}{d_0}
+\frac{\epsilon_0}{d_0}D
+\frac{k_0}{d_0m_0}G,
\qquad
S_\star=A-\frac{G}{m_0}.
\]
Since \(0\preceq G\preceq p_0^2D\), this proves both nonnegativity and the stated upper estimate.

Under the assessment's explicit hypotheses,
\[
\Delta_A\preceq
\left(470\cdot3\times10^{-21}+10^{-27}\right)D,
\qquad
\Delta_G\preceq10^{-28}D,
\]
one obtains
\[
S_\star-S_-\preceq
\left[
470\cdot3\times10^{-21}
+10^{-27}
+\frac{10^{-28}}{d_0}
+\frac{\epsilon_0}{d_0}
+\frac{p_0^2k_0}{d_0m_0}
\right]D
<1.5\times10^{-18}D.
\]

There is no missing denominator factor or mixed compact payment in this comparison.

The distinction between hypotheses and executed bounds is essential and is correctly stated:

- The scalar complement and analytic quadrature bounds have retained execution evidence.
- The \(10^{-27}\) low-\(A\) and \(10^{-28}\) \(GP\) numerical budgets are hypotheses, not measured enclosure widths.
- Anchor tails alone do not establish those budgets. Prefactors, both anchor balls, recurrence propagation, roots, weights, and arithmetic assembly remain part of the numerical enclosure.
- \(S_\star\) is a diagnostic scalar-reference comparison, not the exact inverse Schur complement and not a known positive matrix.

Independent audit reconstruction has its own quadrature and numerical enclosure obligations. Its q64 scalar bound does not establish containment of uncomputed reconstructed entries in uncomputed published intervals.

## 4. Outward-grid rounding

Let \(\delta=2^{-128}\). If entry radii are bounded by \(\delta\), the midpoint error and radius-row correction each have mass-normalized operator norm at most \(p\delta/d_{\min}\). Thus
\[
\text{true-to-ordered-bound loss}
\le\frac{2p}{d_{\min}}\delta.
\]
Here
\[
d_{\min}=\frac2{623},
\qquad
\frac{2p}{d_{\min}}=97188.
\]
Therefore
\[
97188\,2^{-128}\approx2.856\times10^{-34}
\]
is a valid conservative bound.

For an otherwise exact entry, ordinary floor/ceiling publication actually gives midpoint radius at most \(\delta/2\). The assessment's use of \(\delta\) is conservative and does not require repair. It establishes that the publication grid alone is sufficiently fine, not that propagated working intervals satisfy the numerical budgets.

## 5. Meaning of the q49 comparison

The assessment uses the complete C-0098 quadrature formula, including all 68 panels, the 4096 analytic envelope, and the correct support-dependent prefactor and exponential. Its formula agrees with the historical producer's operator-error formula after replacing the support.

For fixed support and panels,
\[
E_{\rm quad}(T,q+1)=\frac14E_{\rm quad}(T,q).
\]
The retained data place the historical corrected q48 upper between the new q48 and q49 bounds:
\[
2.51065776786\times10^{-21}
<
4.32907935139\times10^{-21}
<
1.00426310714\times10^{-20}.
\]
Hence 49 is the least integer order meeting this particular analytic-bound comparison.

This does not compare actual quadrature errors, complete matrix-order losses, or positive margins. The historical comparison value is an outward-rounded analytic upper, which is exactly the quantity identified by the assessment. No positivity conclusion follows from beating it.

## 6. Contraction-volume accounting

I inspected the retained corrected C-0096 producer and auditor, including their consuming matrix multiplications.

For the producer, each nonempty cell contributes two contractions per parity block, one for \(P\) and one for \(P^2\). Each has volume \(p^2N\). The band contributes two parity contractions per panel, and \(GP\) assembly contributes two \(p^3\) contractions. Thus
\[
V_{\rm source}
=4\,\text{cells}\,p^2N
+2p^2(68q)
+2p^3.
\]

For the auditor, each direct arithmetic domain uses a full \(N\times(N+1)\) by \((N+1)\times N\) contraction. Its band contractions are full-dimensional before parity projection, as is its \(GP\) contraction. Thus
\[
V_{\rm audit}
=(\text{low domains}+\text{square domains})N^2(N+1)
+N^2(68\cdot64)+N^3.
\]

The qualified geometry supplies seven producer cells, six low-shift domains, and twenty square domains. The historical counts are four, four, and eight. These yield the stated exact totals and ratios:
\[
\frac{382367232}{287943552}=\frac{1964}{1479},
\qquad
\frac{1246197888}{819636480}=\frac{6401}{4210}.
\]

The six serialized triangles contain
\[
6\frac{312\cdot313}{2}=292968
\]
slots, including structural parity zeros. Each actual parity proof block remains \(156\times156\).

These are contraction-shape identities under the declared classical model. They establish no runtime ratio, peak-memory requirement, native multiplication complexity, or scaling law. Twenty-six sequential arithmetic domains do not imply twenty-six simultaneously retained matrices. The historical timing receipts and precisions remain comparison context only.

## Findings and limitations

No blocking finding or mathematical repair is required.

The assessment establishes pointwise scalar complement allowances, complete analytic quadrature bounds, a valid interval-order conversion factor, a conditional finite-resolution estimate, and exact contraction-volume accounting. It does not establish the assumed numerical enclosure budgets or positivity of any new low matrix.

No new support positivity, runtime guarantee, memory guarantee, production admission, or RH conclusion follows. Historical records, source, tests, certificates, and admissions remain unchanged.
