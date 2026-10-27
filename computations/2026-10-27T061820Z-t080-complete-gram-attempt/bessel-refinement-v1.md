# Paid midpoint spherical-Bessel enclosure refinement

- **Created:** 2026-10-27T06:36:45Z
- **Status:** scalar qualification passed; complete source/sign result recorded separately

The executed first producer stopped with a relative-seed-accuracy exception, before generating a complete target packet. Its [source](build-whole-source-v1.py) and [actual receipt](data/native-source-v1.run.json) remain unchanged. The initial seed guard2048 is retained, not suppressed.

## Measured failure

The [scalar diagnosis](data/bessel-diagnosis-v1.json) evaluates exactly the two high spherical-Bessel seeds644/645 on all59 positive declared anchors. Direct native J_nu on nonexact Arb argument balls loses substantial input precision in intermediate regimes: at source3072 the minimum relative accuracy is1063 bits and9 anchors fail2048; at4096 the minimum is1446 bits and4 fail. Raising working precision once therefore does not settle this guard. These are valid but wide enclosures, not mathematical negativity.

The old control T3/4 has dyadic frequency arguments on its dyadic anchor partition. New T4/5 arguments carry an irreducible denominator5; their Arb arguments have nonzero radii. This exposes native input-ball propagation overestimation. The diagnosis makes no assertion that an inaccurate midpoint is the true result.

## Full uncertainty is paid analytically

The primary [DLMF10.54.2](https://dlmf.nist.gov/10.54.E2.tex) gives, after t=cos(theta),

`j_n(c)=(-i)^n/2 integral_[-1,1] exp(ict)P_n(t)dt`.

For real c, differentiate the finite integral. Cauchy-Schwarz and ordinary Legendre mass give

`|j_n'(c)| <= (1/2) sqrt[(integral t^2 dt)(integral P_n^2 dt)] = 1/sqrt[3(2n+1)] <= 1`.

Thus if the exact real argument lies in c0+[-r,r], then j_n(c) lies in the native enclosure for j_n(c0) enlarged in radius by r. V2 takes the EXACT dyadic Arb midpoint c0, evaluates sqrt(pi/(2c0))J_(n+1/2)(c0) with full native rounding, then adds the entire original c.rad() to its output radius. No input radius or multiplier uncertainty is discarded. All declared arguments are strictly positive. The subsequent downward recurrence and band formulas retain interval arithmetic on the original argument ball.

The [bounded qualification](data/midpoint-seeds-v1.json) exercises all118 seeds at3072 bits: minimum relative accuracy2249, original2048 guard passed. Separately computed4096-bit midpoint-plus-paid-radius enclosures are contained in every source seed enclosure. This scalar check is not independent whole-matrix acceptance; the full consumer instead reconstructs elementary sine/cosine seeds and upward recurrence.

## Version and scope

New [producer v2](build-whole-source-v2.py) changes only this evaluator and its separate output directory. New [consumer v2](verify-whole-source-v2.py) changes only its adjacent producer byte identity; its independent mathematics is unchanged. Original v1 consumer remains available but was not executed on a complete target packet. Controls T4/5,N322,K76,M644, source3072/consumer4096 and publication256 are unchanged. The frozen declaration/seal and first-attempt input bytes are unchanged. No stronger reference, new projection, residual refinement, support grid or theorem admission is introduced.
