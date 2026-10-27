# Complete T4/5 source and sign attempt

- **Created:** 2026-10-27T06:18:20Z
- **Scope:** research candidate source/sign; no production admission or independently accepted positivity.

The frozen [declaration](../2026-10-27T050743Z-t080-target-qualification/data/target-declaration-v1.json) and [source/error contract](../2026-10-27T050743Z-t080-target-qualification/target-source-error-contract-v1.md) apply unchanged: T4/5,N322,K76,M644, source3072, consumer4096, publication256. Whole ordinary-Legendre physical mass is d_n=2/(2n+1).

For each161-dimensional parity, publish six total core symmetric matrices: actual A_model, weighted_head, weighted_complete_tail. P is freshly combined over2/3/4, with c4=log2/2. P_squared is the integral of the complete signed piecewise translation sum squared, including all mixed products. GP=P_squared-P D^-1 P. No earlier arithmetic matrix or positivity sign is inherited. VP is the full low-space integral V(x)P_n(x)P_j(x+tau) with both translation windows paid.

Let VT,PT,RT denote low-to-outputN..M-1 matrices in ordinary physical inner products, and let VV be the complete V-square low Gram. Then the complete outside Gram is E=VV-V D^-1 V-VT^T Dt^-1 VT+GP-PT^T Dt^-1 PT+[VP-V D^-1 P-VT^T Dt^-1 PT]+transpose(last). This is the full signed Q_M(V+P) square, never a sum of separate arithmetic squares or an omitted VP. R_K has no output at M or above, by the exact finite degree/band theorem. Its low even/polar and primitive boundary terms remain in A_model.

C=Dt^-1(VT+PT+RT). K_h is the complete inverse-frequency step bound, including terminal positive Parseval mass. Head=C^T K_h C, Tail=kappa E. Use DECLARED exact frequency anchors/weights, eta, kappa and complete canonical Lambda. Source matrices are intervals, not entrywise Loewner upper matrices.

For exact positive parity-specific theta, S_theta=A_model-[(1+theta)Head+(1+1/theta)Tail]/eta-Lambda D. The physical numerical-radius goal in the declaration must be checked after theta selection. Full exact nonsingular congruence/Gershgorin with transformed interval radii can establish both finite sufficient matrices positive. A negative directional UPPER rejects only this selected conservative S_theta, not the actual criterion, Weil positivity or RH. A failed lower or floating negative is unresolved.

## Packet interface

Producer and consumer are separate scripts in this bundle. Both take --inputs whole-inputs-v1.json and --output FRESH.json; consumer additionally takes --source PACKET.json. Source format t080-complete-signed-weighted-Gram-source-v1 carries support,N,order,physical_extent,bits,precision,inputs_sha256,producer_sha256,eta_lower,model_error_upper,frequency_edges,inverse_weight_uppers,weighted_tail_norm_upper and matrices. Six descriptors use keys A_model-0/1,weighted_head-0/1,weighted_complete_tail-0/1. Each confined path is relative to the SOURCE JSON PARENT (data), and binds sha256,size. Gzip payload has kind,parity,dimension161,bits256 and upper_triangle as lexicographic row-major inclusive pairs of integer DYADIC numerators. Native independent enclosures must be contained, not merely overlap.

The consumer imports no producer or project mathematical implementation. It independently reconstructs coefficients, residual primitives, translation windows/full combined square, complete mixed infinity, both frequency halves and physical masses. Shared python-flint/Arb and original analytical source identities remain premises. A separate exact sign check imports no floating library and does not pretend that sign acceptance validates analytic source truth. Source/sign research assessment here is distinct from independent accepted new-support positivity.
