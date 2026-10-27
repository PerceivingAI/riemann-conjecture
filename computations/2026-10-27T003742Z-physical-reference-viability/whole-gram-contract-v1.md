# Complete signed supported-Gram enclosure — 2026-10-27

This is a new assessment following the preserved nonrejecting physical-direction
checks. It changes neither the mathematical reference nor `(T,N)=(3/4,312)`.
The finite residual model remains `R56`, with its complete canonical discrepancy
paid by the previously accepted exact C117 allowance `Lambda`.

## Full physical output, not a finite-tail theorem

Write `B_model = C + E`, with physical degrees `312..623` in `C` and
`E=Q624(V+P)Pi312`. The exact residual band proves `Q624 R56 Pi312=0`.
`C` retains the signed sum `V+P+R56`; `E` retains the signed combined operator
`V+P`, with all active arithmetic powers `{2,3,4}` and all their square terms.
Neither the infinite output nor either mixed sign is dropped.

In the ordinary Legendre basis let `d_n=2/(2n+1)`. The stored cross matrices
are inner products; the expansion matrix is `C=D_tail^-1(V_tail+P_tail+R_tail)`.
For the complete omitted-output Gram:

- `GV = V2 - V_low^T D_low^-1 V_low - V_tail^T D_tail^-1 V_tail`;
- `GP = GP_Q312 - P_tail^T D_tail^-1 P_tail`;
- `GVP = VP_full - V_low^T D_low^-1 P_low - V_tail^T D_tail^-1 P_tail`;
- `E*E = GV + GP + GVP + GVP^T`.

Here `V2` and `VP_full` are complete integrals on `[-1,1]`, not sampled or
truncated infinite expansions. The accepted combined `P,GP_Q312` intervals are
reused with their original raw-byte source pin. The old reference proxy matrix
`A` is NOT reused: actual `A_model=D(H-cT)+V+P+R56` is freshly reconstructed.
Even kernel terms, finite head boundary polynomials, and signed polar terms are
retained. The Gauss468 arithmetic rule is exact for the polynomial integrands of
maximum degree `623+311=934`; its nodes and weights are outward Arb enclosures.
The independent consumer uses a different exact-polynomial moment contraction.

## Entire frequency line

Let `h=max(1/3,g)` be the already fixed reference, and `k=1/h`.
Its inverse is even and nonincreasing in absolute frequency. For increasing
anchors `Omega[0]=0`, `Omega[1]=256`, successive ratios `17/16` strictly below
`8192`, then final anchor exactly `8192`, choose exact nonincreasing rational
`b_j >= k(Omega_j)`, with `b_0=3`. Pointwise on the WHOLE frequency line:

`k <= b_L + sum_j (b_j-b_(j+1)) 1_[abs(t)<=Omega_(j+1)]`.

Therefore `K_upper=b_L D_tail+sum_j(b_j-b_(j+1))F_(Omega_(j+1))`.
The base `b_L D_tail` pays every frequency beyond the final anchor by Parseval.
These computational anchors do not change the reference, support, or projection.

For equal parity and `c=T*Omega`, the exact band matrix is

`F_nm=(4/pi)(-1)^((m-n)/2)c^2(j_n' j_m-j_m' j_n)/[n(n+1)-m(m+1)]` for `n!=m`.

Its diagonal is `4 D_n(c)/(pi(2n+1))`, where
`D_0=Si(2c)+(cos(2c)-1)/(2c)` and
`D_n=D_(n-1)-c(j_(n-1)^2+j_n^2)`.
These follow by the spherical-Bessel differential equation and adjacent-order
recurrences; the zero endpoints vanish. Both frequency halves and `dt/(2pi)`
are included. Opposite parity entries vanish. The independent review confirmed
these factors and indices. The source uses entire-function/downward Bessel
values; the consumer uses sine/cosine upward recurrence at higher precision.

## Complete inverse-weight bound on the omitted physical output

For `M=624`, `Rc=512`, `c=T Rc=384`, the elementary complete leakage majorant is

`lambda <= (2c/pi)(2M+1)c^(2M)/((2M+1)!!)^2 / [1-c^2/((2M+1)(2M+3))]`.

The ratio is strictly below one (`384^2 < 1249*1251`). Choose rational
`0<=lambda_up<=1`, and `1/g(Rc)<=a_up<=3`. Then, directly from a pointwise
inverse-multiplier bound and the `Q624` leakage estimate,

`G_h(E) <= kappa E*E`, `kappa=a_up+(3-a_up)lambda_up`.

This is NOT an inverse-of-compressed-form substitution. Increasing either
scalar upper is conservative on the stated ranges. No residual model term is
hidden in this estimate: the full canonical remainder is separately in Lambda.

## Whole-matrix sign, not entrywise matrix ordering

For any exact positive `theta`, weighted Young gives

`G_model <= (1+theta) C^T K_upper C + (1+1/theta) kappa E*E`.

The complete sufficient sign is

`S = A_model - eta_lower^-1[(1+theta)H_head+(1+1/theta)H_tail] - Lambda D_low > 0`.

`eta_lower=1-9/10^49` and Lambda are retained accepted inputs. Proposal generation
may optimize theta and the congruence numerically. Proof must use their exact
serialized rational values and ALL interval uncertainty. The published matrices
contain the true Hermitian matrices entrywise; no entrywise upper endpoint is
called a Loewner upper. Exact rational interval congruence followed by complete
Gershgorin row-radius subtraction certifies the sign, or fails to close it.
A failed lower certificate is not a negative direction or a rejection of the
actual criterion. A positive certificate applies to the whole selected criterion
at this one unchanged control, not to a support-covering family or RH, and does
not alter any production theorem admission.
