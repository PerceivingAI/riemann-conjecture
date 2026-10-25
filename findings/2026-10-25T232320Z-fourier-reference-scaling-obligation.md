# Fixed positive arithmetic references cannot cover unbounded supports

- **Finding ID:** `F-20261025-010`
- **Created:** `2026-10-25T23:23:20Z`
- **Last updated:** `2026-10-25T23:33:31Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED` independently reviewed necessary-growth argument and executed retained/scalar controls, not a global positivity theorem

## Statement

Let P_T be the complete signed prime-power translation operator on L²(-T,T), with one-sided coefficient d_m=Lambda(m)/sqrt(m). For the normalized constant vector u_T,

r(T)=-<u_T,P_T u_T>=sum_(log(m)<2T) d_m(2-log(m)/T).

Then r(T)->infinity as T->infinity. Therefore any globally nonnegative arithmetic reference M_T=a(T)I+P_T on supports T_j->infinity requires a(T_j)->infinity. This does not assume a common positive coercivity constant; even M_T>=0 suffices.

For the present nonnegative complete Fourier exterior A(t)-a(T), continuity at the cutoff requires a(T)<=A(Omega(T)), where A(t)=Re psi(1/4+it/2)-log pi. Since A is finite on compact real intervals, Omega(T_j)->infinity too. Thus fixed a and Omega cannot cover unbounded supports through this particular globally positive-M construction.

If the existing geometric Legendre-tail majorant continues to be used, it additionally requires

(T Omega)^2<(2N+1)(2N+3),

or N>sqrt((T Omega)^2+1)/2-1. Its dimension must consequently grow along that family. This is only an enclosure prerequisite, not a minimum positivity dimension or a sufficient error/low-sign condition.

## Evidence / derivation

The [complete argument](../computations/2026-10-25T232320Z-fourier-structural-assessment/reference-scaling-obligation-v1.md) evaluates the bounded arithmetic reference on the constant L² vector. No claim that the constant belongs to the smooth Weil source domain is used.

Primes p<=exp(T) contribute at least log(p)/sqrt(p). Elementary finite Euler products dominate harmonic partial sums, proving divergence of sum_p1/p; comparison then proves divergence of the weighted prime sum. No prime number theorem, RH, quantitative prime estimate or cancellation premise is needed. No growth rate is obtained.

[X-20261025-010](../computations/2026-10-25T232320Z-fourier-structural-assessment/record.md) also assesses the completed C-0096/C-0100 structural crossing. Held finite dimension, working precisions and full slot counts are distinguished from changed arithmetic, reference denominators, frequency order and uncertainty bookkeeping. Observed operation times and exact shape ratios are not converted into a scaling or speedup claim.

## Verification

Independent mathematical review accepts the normalization, divergence, exterior inequality, quantifiers and dimension condition without performing numerical runs. Its stage-specific evidence limitation is preserved. Subsequent canonical and isolated captured-code comparison calculations exit0 with byte-identical reports, using12 SHA-pinned original source/proof/audit/receipt inputs and their original seals.

Fresh512-bit scalar r(T) evaluations at BOTH already accepted supports are contained in the original constant-coordinate source intervals with physical mass2. Exact finite Euler-product and strict geometric-boundary controls pass. These finite checks corroborate the formulas; the unbounded conclusion follows from the written argument, not from sampling. No new support matrix or finite sign is computed.

## Dependencies

The complete arithmetic convention of C-0039/C-0058 and the maintained prime-power contract; C-0094/C-0098 exterior multiplier and Legendre-tail estimate; C-0096/C-0100 retained finite-case evidence. The new necessary-growth proof uses unique factorization, elementary geometric products and harmonic divergence. It introduces no external theorem or new numerical backend.

## Significance and limits

The successful4 transition establishes a real fixed-case capability. It does not establish a fixed-parameter all-support mechanism. The actual construction would need changing reference/cutoff parameters and, when using this tail bound, growing dimension. The present full-triangle packet has3N(N+1) slots; that identity is not a lower bound on all alternative representations or algorithms.

Failure of globally positive M is not H0 negativity, Weil negativity or a no-go for a different outside reference, decomposition or Fourier method. No quantitative optimal growth rate, practical global cost, low positive-gap law, efficient positive family, literature originality or RH conclusion follows. The two existing finite positives and all production admissions remain unchanged.

## Timestamped addenda / corrections

None. Earlier records, source, tests and proof artifacts are preserved unchanged.
