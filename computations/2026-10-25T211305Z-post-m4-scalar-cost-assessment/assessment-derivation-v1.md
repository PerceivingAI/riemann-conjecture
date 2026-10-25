# Pointwise Fourier allowances and explicit enclosure accounting

- **Created:** `2026-10-25T21:13:05Z`
- **Scope:** executed scalar/error and contraction-volume assessment at T=3/4,N312,a7/2,Omega256
- **No low-matrix sign is evaluated.**

## Geometry and pointwise complement

C-0097/C-0098 qualify the full open window log2<T<log5/2. At T=3/4, both threshold distances exceed1/20. The overlap of one signed4 translation, divided by the full interval length, is1-log2/T and lies strictly between3/40 and19/250. Its display is0.0758037592534. The central2/2 image intersection has the same scaled length as either4 image interval. This is a positive-measure geometry change, not an equality or infinitesimal activation.

The exact one-sided coefficient at4 is log2/2. The dyadic joint norm and the3 norm give p0=49/32, m0=63/32. With the C-0098 pointwise formulas at c=T Omega=192, executed512-bit controls prove

kappa<k0=4e-49,

eta<1.9e-24,

2p0 eta+eta²<epsilon0=6e-24.

Hence d0=m0-k0>0, and a valid complete finite sufficient lower is

S_-=A_- - [(GP)_+ +epsilon0 D]/d0.

The actual kappa display is3.73314664893e-49 and eta display1.83298444730e-24. The mixed allowance is substantially sharper here than the whole-window5e-13 envelope. No condition on the unknown low positive gap was used to derive it. Ordinary Legendre mass is D_j=2/(2j+1).

## Frequency accuracy compared on the same mathematical error

The exact68 panels,4096 complex digamma envelope and Cauchy operator remainder are unchanged. The complete scalar quadrature errors evaluated at T=3/4 are about1.00426310714e-20 at q48,2.51065776786e-21 at q49 and2.33823225634e-30 at q64.

The SHA-pinned corrected C-0096 source records a complete q48 operator error about4.32907935139e-21. Thus q48 at the larger support is worse than that baseline, whereas q49 is better. Since this analytic bound decreases by exactly4 for each increment of q,49 is the least integer order meeting that specific comparison. This is not an optimality assertion for actual Gaussian errors or a necessary positivity requirement.

## Operator error is not the interval-box order loss

The current source method represents the complete band quadrature error by symmetric entry radii

r_ij=E sqrt(D_i D_j)

within each parity block. The midpoint-minus-radius-row-sum lower is valid, but its possible loss is larger than E D. Let p=N/2=156 and let C be the midpoint. For every symmetric B in that interval box,

||D^-1/2(B-C)D^-1/2||<=pE,

||D^-1/2 diag(sum_j r_ij)D^-1/2||

<= E max_i sum_j sqrt(D_j/D_i).

Therefore B minus the resulting lower is bounded above by F E D, with

F=p+max_i sum_j sqrt(D_j/D_i).

The maximum occurs at the largest degree in its parity. Executed ball sums give F_even about469.989661725 and F_odd about454.328916047, both strictly below470. A complete input/error account must pay this conversion. Treating E as the final scalar lower loss would be wrong. This does not invalidate the historical interval proofs, which use their actual exact row sums.

A separate exact two-dimensional control uses mass diag(1,4), a centered interval box with radii [[1,2],[2,4]], and true matrix vv^t for v=(1,2). The existing order helper produces lower diag(-3,-6). On trial(1,0), the true-to-lower mass-normalized loss is4 even though the nominal operator radius parameter is1. The control executes the existing order helper; it does not merely assert a formula.

## Conditional complete resolution

Define the ideal finite scalar-reference comparison S_star=A-GP/m0. This ideal is a diagnostic mathematical object, not the full inverse Schur and not an assertion of positivity. Since0<=GP<=p0² D, the compact-tail payment contributes at most

epsilon0/d0+p0²*k0/(d0*m0)

to S_star-S_- in mass units, before finite source uncertainty. If all numerical/root/rounding low-A order losses excluding the analytically paid band radius are at most1e-27, and the GP order losses at most1e-28, then

0<=S_star-S_-

<= [470*(3e-21)+1e-27+(1e-28)/d0

    +epsilon0/d0+p0²*k0/(d0*m0)] D

<1.5e-18 D.

The premise uses one-sided true-to-ordered-bound losses, not midpoint radius alone. Numerical band/root uncertainty is included in the low-A numerical budget. Independent audit quadrature and all audit interval uncertainties must still be paid in their own analytical source reconstruction.

For an otherwise exact entry rounded outward on the128-bit fractional grid, the endpoint radius is at most2^-128. The true-to-ordered-bound mass loss is at most2p/d_min times this radius, namely97188*2^-128, about2.856e-34. Thus that publication grid is not itself an obstacle to the stated numerical budgets. This proves no bound on the unexecuted working-precision/root/anchor widths; actual propagated intervals must satisfy those budgets. The384-order Fourier and128-order pole tail contracts of C-0098 remain sufficient at w<192, but every prefactor and recurrence error must be propagated.

The1.5e-18 ceiling is an explicit conditional resolution, not a predicted positive gap. The historical same-N positive gap need not survive at this larger support. A finite sufficient lower may fail even with exact source inputs.

## Work accounting, not a runtime forecast

Six serialized complete matrix triangles still have292968 slots, including structural parity zeros. Each actual finite parity proof block is156 by156. New geometry changes the arithmetic work, not that output dimension.

The producer integrates combined signed images over7 nonempty cells instead of4. It forms P and P² in both parity blocks, giving4 contractions per cell. The independent direct-intersection organization has6 low-shift domains plus20 square domains, instead of4 plus8. These26 domains are sequential contractions, not26 simultaneously retained source matrices.

For ordinary dense classical contraction-volume accounting with qA=N for the producer and qA=N+1 for the independent reconstruction, define

V_source=4*cells*p²*N+2*p²*(68*q_frequency)+2*p³,

V_audit=(low_domains+square_domains)*N²*(N+1)+N²*(68*64)+N³.

The first terms count arithmetic contraction dimensions, second terms the finite band and third terms GP contraction. The ratios are1964/1479, about1.328, for source and6401/4210, about1.520, for audit. Source frequency evaluations change from3264 at q48 to3332 at q49; audit q64 remains4352. The same measured baseline precisions512/768 are the comparison inputs, not a proof those precisions resolve new enclosures.

These are exact shape/accounting identities. They are NOT FLOP counts, FLINT algorithm counts, peak-memory measurements or execution-time bounds. They exclude polynomial/vector/special-function setup, interval-width effects, serialization, parsing and exact witness costs. Native multiplication need not follow the classical model. C-0096's25.12-second source and73.30-second audit receipts are context, not measurements of this case. No speedup or demonstrated scaling law is inferred.

## Circularity and limitations

No RH-equivalent positivity is assumed. The sufficient finite sign remains open. No low matrix, candidate eigenvalue, witness, source/audit implementation for this support, new theorem or production admission is generated by this assessment. The existing fixed generator and checker retain their original closed scope. Shared Suzuki/Arb premises and the inherited exterior proof remain explicit.
