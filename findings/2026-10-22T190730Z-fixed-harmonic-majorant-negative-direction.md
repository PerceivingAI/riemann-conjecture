# A negative direction for the fixed finite harmonic-tail majorant

- **Finding ID:** `F-20261022-002`
- **Created:** `2026-10-22T19:07:30Z`
- **Last updated:** `2026-10-22T19:07:30Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`, exact rational consequence conditional on the documented analytical enclosures. Not a new admitted theorem or independently reconstructed full Weil-form sign.
- **Claim:** `C-0073`

## Statement

At `T=3/5,N=192,M=211,K=32`, with active prime powers `[2,3]`, use the exact odd ordinary-Legendre trial retained in SYS-6.4 and the selected conservative positive tail scalar `mu`. For the C-0072 finite harmonic-tail majorant `U_211`, the source-qualified upper on the fixed trial satisfies

\[
\langle u,(A-U_{211})u\rangle
\le u_{\rm exact}<-\frac65<0.
\]

The complete rational `u_exact` is retained in [X-20261022-002](../computations/2026-10-22T190532Z-directional-exact-screen/record.md), whose exact-result artifact SHA-256 is `c6ae1b0b5ab624df903c7c7a27179743d6f270cdb0a6b62c8ac644f48dc26b59`.

Thus this **finite sufficient matrix `A-U_211` is not positive** under the stated source assumptions. The statement does not concern the sign of the exact diagonal-inverse reference or Weil form.

## Derivation

C-0072 proves the whole-tail majorant identity with `w_k=(mu+H_k-H_192)^-1` and `G=B*B`:

\[
U_{211}=w_{211}G+\sum_{k=192}^{210}(w_k-w_{211})T_k^*T_k,
\qquad T_ku=\langle e_k,Bu\rangle.
\]

The `w_211 G` term retains all omitted infinite modes. Exact odd parity eliminates the even indices in the finite correction, leaving nine modes `193,195,...,209`. The accepted source packet encloses each full signed V/P2/P3/R moment in `I_k=[l_k-delta,h_k+delta]`. Its physical mass norm is independently checked below one, so the full residual enlargement is valid. Retained residual image degree is 223; its high pairings were not discarded.

Let `d_k=dist(0,I_k)`, and use the original one-sided full-source `a_up,g_low`. Then

\[
u_{\rm exact}=a_{\rm up}-w_{211}g_{\rm low}
-\sum_{k=193,195,\ldots,209}(w_k-w_{211})d_k^2
\]

is a valid upper for the displayed quadratic form. Its exact rational value was computed from immutable packets and independently reproduced by a separate direct-harmonic-sum/endpoint-square implementation. Both checked `<-6/5` by rational comparison. No float enters that sign decision.

## Dependencies and trust

- C-0072, with C-0058 and C-0063–C-0065 and their existing local Suzuki source premises.
- [SYS-6.4 original record](../computations/2026-10-18T090311Z-sys6-selective-support/record.md), original A/G directional enclosures and exact odd trial.
- [X-20261022-001](../computations/2026-10-22T185054Z-directional-source-validation/record.md), independent acceptance of all 45 new component/sum source intervals and scalar prerequisites.
- [X-20261022-002](../computations/2026-10-22T190532Z-directional-exact-screen/record.md), exact rational screen and separate exact replay.

The new moment reconstruction does not retroactively independently reconstruct the original A/G inputs. The conclusion inherits their generator-source-qualified analytical trust and the shared Suzuki/Arb premises. Neither exact arithmetic replay proves those transcendental source identities. This is not Lean-kernel checked or a production certificate admission.

## Verification and scope

Twelve focused behavioral tests passed, including interval sign/distance branches, equality versus strict negativity, the full omitted-tail charge, wrong metric, missing residual/mode/component acceptance and immutable input bytes. The actual screen and separate replay exited 0; source inputs were not regenerated and no retry was used. Exact artifacts, source/test snapshots and process observations are retained in the computation bundle.

C-0072 orders the matrices as

\[
A-U_{211}\preceq A-B^*C_0^{-1}B\preceq A-B^*C^{-1}B.
\]

Negativity of the first matrix does not imply negativity of either larger matrix. This result rejects only the fixed finite majorant and configuration, not the exact reference, true Schur complement, Weil form, another cutoff/dimension/support, or RH. No full low-space positivity check or global support-covering family was established. No further parameter or precision was tried. Admissions remain eight v1, zero v2 and one v3; RH unresolved.
