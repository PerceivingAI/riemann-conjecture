# Complete joint-source tail on the preserved odd trial

- **Finding ID:** `F-20261023-005`
- **Created:** `2026-10-23T18:52:53Z`
- **Last updated:** `2026-10-23T19:02:50Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`, scoped to the reviewed source formulas, separately organized Arb reconstruction and exact rational consequences. Not an admitted theorem or Lean proof.
- **Claim:** C-0079.
- **Evidence:** [X-20261023-003](../computations/2026-10-23T185253Z-joint-source-tail/record.md).

## Statement and fixed question

C-0077's full correlated tail is evaluated here on the unchanged T=3/5,N=192,K=32 exact odd trial, active arithmetic terms [2,3], at the natural residual-degree boundary L=224. The original source, trial and nine-mode accepted prefix ending before 211 are unchanged. This calculation supplies the original-trial G_L,C_L and regular-tail inputs that the earlier [jump-model comparison](2026-10-23T174341Z-jump-resolved-tail-correlation.md) did not evaluate.

The complete source-tail upper improves the earlier separate norm control and yields a strictly positive concentration correction. The resulting directional upper remains positive and inconclusive. An exact lower-tail consequence proves that numerical refinement of this same L=224 concentration formula cannot make its reported upper negative. This does not reject the source, the broader method, other indices or stronger weight-sensitive inequalities.

## 1. Whole source images minus finite heads

Use the normalization and signed decomposition of C-0077:

\[
u=\sum_{j=0}^{191}z_jP_j,\quad e_k=\sqrt{(2k+1)/2}\,P_k,
\quad q=\mathcal P_Tu=s+r,\quad g=Vu+s.
\]

The complete scalar tails are

\[
G=\|g\|^2-\sum_{k<224}|g_k|^2,\qquad
C=\langle g,r\rangle-\sum_{k<224}g_kr_k,\qquad
\mathcal R=\|r\|^2-\sum_{k<224}|r_k|^2.
\]

All functions are real and odd. Only the 112 odd head indices 1,3,...,223 contribute. Independently form

\[
M=\|Vu+q\|^2-\sum_{k<224}|(Vu+q)_k|^2
 =G+2C+\mathcal R.
\]

These are complete infinite tails, not finite sums over high modes. No new source prefix is substituted into the retained C-0074 predicate. No derivative bound is needed because the regular tail itself is enclosed by its whole norm minus head.

For x>0, put a_m=tau_m-1, tau_m=log(m)/T and c_m=log(m)/sqrt(m). On (a_2,a_3) and (a_3,1),

\[
q(x)=-\sum_{a_m<x}c_m u(x-\tau_m),\qquad
s(x)=u(1)\sum_{a_m<x}c_m.
\]

Both vanish on (0,a_2). The signed combined q is formed before squaring, retaining the prime-2/prime-3 cross term. Squared and mixed products are even, so doubling the positive-cell integrals is valid. Potential-only whole norms and heads use global moments and therefore retain the central-cell contribution.

## 2. Independent organization and interval acceptance

The new fixed consumer `scripts.weil_joint_source_tail` uses existing mathematical primitives. Its generator uses exact ordinary-Legendre coefficients, Horner translations, two doubled positive cells, grouped rational harmonic contractions for the potential square and potential heads, and existing logarithmic cell moments at 1536 bits.

The reconstruction uses a separately coded exact Legendre recurrence, binomial/Taylor translations, four signed cells without doubling, independently coded logarithmic cell moments, and per-monomial global potential moments at 3072 bits. Both use Arb, the same source identities and projection algebra. This is independent implementation organization, not independent foundational arithmetic or a new proof of Suzuki's source identity.

Outward publication uses the fixed 352-bit dyadic grid. The entire reference interval, not just its midpoint or an overlap, must lie in the published generator interval. All 15 scalar and 336 head containments passed. Eighteen V/combined-q compatibility checks against the previously accepted nine-mode source packet passed, as did full containment in the earlier complete step-model tail. Exact physical norm and trial polynomial identities agree between the two constructions.

The direct and correlated whole-minus-head forms agree within their rigorous intervals. The upper cap is the minimum of their valid upper endpoints. Negative computed uppers on nonnegative masses are rejected, not clipped.

## 3. Evaluated original-trial quantities

The following are decimal displays only. Exact published endpoints and raw reconstruction endpoints are retained in [the result packet](../computations/2026-10-23T185253Z-joint-source-tail/data/result.json).

| Quantity | Display |
| --- | ---: |
| G_224 | 5.298159039690437 |
| Signed C_224 | -5.035764911900693 |
| Regular tail | 5.478412757711674 |
| Complete truncated joint tail M_224 | 0.7050419736007247 |
| Full-source tail upper after collective residual | 0.7050419736007582 |
| Earlier separate full-source control upper | 6.664365418102699 |
| Retained omitted-mass lower R_minus | 0.7987791726070741 |
| Concentration lower on J | 0.2804530089619544 |
| Resulting directional upper on s0 | 1.3818804654839518 |
| Tail cap required for this negative-upper test | 0.24316921753565277 |

This evaluates the full mixed term C, unlike the earlier arithmetic-only C_sr. The cancellation between G,2C and the regular tail is retained in the reported bound. The new upper is strictly smaller than the previous separate control; this improvement now comes from actual joint source evaluation. It is not a positivity or negativity certificate for the reference.

The full residual is restored collectively. With accepted delta and n=||u||^2,

\[
\|Q_{224}f\|^2\le E_+
 =\operatorname{upper}\bigl(\sqrt{M_+}+\delta\sqrt n\bigr)^2,
\qquad f=(V+\mathcal P_T+R_T)u.
\]

Q_224 R_32 u=0 follows from the accepted degree 223; the omitted residual is not discarded. The retained exact mu defines the unchanged weight w_223. With h=a_up-P_lower,

\[
J\ge w_{223}\max(0,R_{\rm minus}-E_+),\qquad
s_0\le h-w_{223}\max(0,R_{\rm minus}-E_+).
\]

The correction is nonzero, but this upper remains positive. It does not show that s0 is positive.

## 4. Remaining loss at this fixed comparison index

Let m be the published lower endpoint of M and d the accepted delta. The exact consequence replay verifies

\[
0<m<1,\quad 0<n<1,\quad d\ge0,\quad m>d^2n.
\]

Reverse triangle and the last strict inequality give

\[
\|Q_{224}f\|^2\ge(\sqrt m-d\sqrt n)^2
 =m-2d\sqrt{mn}+d^2n\ge m-2d=:E_-.
\]

The exact replay establishes E_->7/10, with display 0.7050419736006850. Thus the observed tail is not an artifact of a loose numerical upper or forgotten cancellation. In particular E_- exceeds the required cap R_minus-h/w_223.

The function Phi(E)=h-w_223 max(0,R_minus-E) is nondecreasing. Every valid full-tail upper E satisfies E>=E_-, so

\[
\Phi(E)\ge\Phi(E_-)>69/50>0.
\]

The replayed display of Phi(E_-) is 1.3818804654837327. **This bounds the formula's reported upper from below, not the actual reference value.** It excludes negative certification by this fixed L=224 formula with retained h,R_minus,w_223 even if its tail input were exact. It says nothing about other proof indices or a more informative inverse-weighted source estimate. The distribution of omitted mass under the varying harmonic inverse weights remains uncomputed.

## Verification and reproduction

The canonical module execution returned 0 and `INCONCLUSIVE`. A separate retained standard-library rational procedure replayed all 351 interval containments, the collective-residual upper, exact harmonic weight, concentration result and lower-tail comparison. A changed-first-input smoke returned 2 with empty result stdout before either numerical construction. Its disposable directory was removed; original inputs were untouched.

Independent read-only mathematical review accepted the scalar identities, positive-cell reduction, normalized heads, signed terms, outward directions, residual and concentration formulas. It inspected the implementation and compatibility additions and separately checked the lower-tail argument. The reviewer did not execute or independently rerun the numerical results.

Three owned direct children exited without timeout or retry. New charged execution was 12.480469300062396 seconds; cumulative analytical-cycle charge is 17.100813700119033/180 seconds, with a 60-second cap per child. No test suite, full matrix/inverse, Rust verifier, retained-theorem replay or Lean build was run. The earlier source modules, model consumer and research records remain unchanged. [The new bundle](../computations/2026-10-23T185253Z-joint-source-tail/record.md) retains the predeclared contract, exact executed sources, outputs, endpoint receipts and execution metadata separately.

## Dependencies, circularity and limits

Dependencies are C-0063 through C-0065 for the local source/form/metric, C-0072/C-0074 for reference weights and retained one-sided inputs, and C-0077/C-0078 for the refinement and previous control. The accepted source identities and Arb remain trusted. Original A/G is still generator-source-qualified, not independently reconstructed here. The local residual restriction 2T<pi remains in force. No unknown positivity, uniform cancellation or RH-equivalent estimate is assumed.

No actual diagonal-reference, true Schur or Weil sign is determined. No support theorem, global covering family, certificate profile or admission changes. RH remains unresolved; admissions remain eight frozen v1, zero v2 and one v3 C-0067.
