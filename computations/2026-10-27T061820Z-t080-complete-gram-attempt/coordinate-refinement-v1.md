# Fresh low-matrix coordinate conditioning

- **Created:** 2026-10-27T06:45:55Z
- **Scope:** numerical witness proposals only; no change to target source or sufficient inequality

The first [proposal](data/whole-proposal-v1.json) and [exact assessment](data/whole-exact-sign-v1.json) remain unchanged. In padded old coordinates, double precision classified the even A-minus-model minimum near-6.89e-10 while classifying its more heavily subtracted S minimum near+7.98e-9. The odd relative Gram diagnostic was about0.50558 but its unwhitened S minimum appeared near-3.86e-10. These are warning signs of dynamic-range/eigensolver loss, not certified signs. The exact complete assessment is UNRESOLVED in both parities: no positive Gershgorin certificate and no strict negative directional upper. Both original physical numerical-width goals pass.

## Derived coordinate change

Let U0 be the exact old complete-coordinate transform padded by five identity modes per parity. It is coordinates only. Form F=U0^T(A_model-LambdaD)U0 using fresh target intervals, and compute F=LL^T entirely in1024-bit Arb, requiring each computed Cholesky pivot strictly positive. No abs, diagonal jitter or clipping replaces a failed pivot. Set H'=L^-1(U0^T Head U0/eta)L^-T and E' analogously. Only then convert these well-scaled matrices to double for NONPROOF theta/eigenvector proposals.

For a floating eigen-whitening proposal R, compose W=L^-T R in native interval arithmetic, with each floating R entry first interpreted as its exact binary rational. Round W midpoints directly to80-bit dyadic rationals; never convert the composed ill-scaled W through double. The existing exact consumer prepends U0, so the final transform is U=U0W. This is not an inherited target sign.

[Proposer v2](propose-whole-v2.py) retains the original source, mathematical controls, Young inequality, model error and both exteriors. The same [zero-float sign consumer](verify-whole-sign-v1.py) checks exact nonsingularity, complete transformed interval radii and all rows for its newly published proposal. Any positive proposal still needs that exact check, successful separate native analytic acceptance on the identical source bytes, and the later retained reproduction/adversarial gate.
