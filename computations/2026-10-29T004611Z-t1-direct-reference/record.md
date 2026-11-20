# Direct signed T=1 reference improvement

- **Computation ID:** X-20261029-001
- **Created:** 2026-10-29T00:46:11Z
- **Last updated:** 2026-10-29T01:05:01Z
- **Status:** COMPLETE
- **Claim:** C-0126, source-conditional reference/error qualification only
- **Code baseline:** local commit a6ed03d plus new separately retained, uncommitted operation bytes

## Objective

At unchanged T=1, test whether direct signed discrepancy evaluation improves C-0125's inherited supported bound. Hold alpha1/4, floor1/3, eta1-2^-128, ordinary mapped Legendre projection family, accuracy2^-78 and parameter-selection policies fixed. Change the mathematical reference estimate rather than support, test class, implementation or error meaning.

## Mathematical quantity tested

The [complete proof contract](reference-contract-v1.md) establishes the WHOLE-LINE inequality

`rho_1(t)<=w(t)/4+2981/1024`,

where rho retains the complete signed2/3/4/5/7 arithmetic and continuum quotient. It replaces separate norm charges with direct finite-frequency cancellation, plus a rigorous analytic infinity cap. Restriction gives a stronger supported-form estimate than C-0125's beta3359/1024.

No actual T=1 low or coupled matrix, coupled sign, high-mode numerical width, smooth-test positivity or full-target execution cost is computed. C-0124 at T81/100 remains the retained positivity frontier. Production8v1/0v2/1v3 and RH unresolved remain unchanged.

## Controlled result

Both columns use the same mathematical controls. The old row is retained evidence, not a rerun of full matrices.

| Quantity | Inherited supported policy, C-0125 | Direct whole-line policy, C-0126 |
| --- | ---: | ---: |
| beta | 3359/1024 | 2981/1024 |
| First integer reference anchor R | 6641 | 4060 |
| First even sufficient-policy N | 9072 | 5564 |
| Residual order K | 132 | 132 |
| Physical extent M | 18144 | 11128 |
| Dimension per parity | 4536 | 2782 |
| Six triangular analytical entries | 61739496 | 23226918 |
| Source starting bits | 40960 | 25600 |
| Independent starting bits | 55296 | 34304 |
| Translation cells | 11 | 11 |

The policy dimension falls about38.67 percent, and the declared entry count about62.38 percent. This is demonstrated mathematical overestimation in the inherited reference, not a measured implementation speedup or a hardware finding. The new N remains a minimum only for the fixed sufficient scalar policy, not true positivity or every reference choice.

K132 and all133 exact coefficients retain the complete canonical model allowance below2.353e-24 against accuracy2^-78. Every preceding even order is checked. M11128,Rc8120, the complete physical inverse and all60 frequency weights including terminal infinity are freshly reconstructed. Old target gaps, matrices and positive coordinates are not reused.

## Frequency proof and independent verification

The producer begins with boundary256 and extends through512,1024 and2048. Its final9916 dyadic leaves cover[0,2048] without gaps. The analytic tail covers all higher frequencies; evenness covers negative frequencies. Boundary2048 is a proof partition endpoint, not a frequency truncation.

The independent consumer uses a real trigonometric continuum quotient rather than the producer's complex quotient, and128 positive digamma-prefix terms with a64-order uniform Binet remainder rather than producer digamma evaluation. At768 bits it performs19832 native cell-upper checks, six infinity checks and a lower-witness check. It checks both the source coarse derivative bound and a sharper independently derived derivative allowance.

Separate512/1024-bit reconstruction checks296 scalar interval containments and252 rational upper bounds, all133 formal residual coefficients,66 even residual orders, direct-factorial leakage at N,N-2,M, complete physical/frequency exteriors and the precision/shape policies. It reexecutes the accepted C-0125 native scalar proof and requires byte-identical prior audit results before comparison.

The certified finite witness at575295/2048 and complete proof give a supremum enclosure approximately[2.9068744511179827,2.9107624817156696], with exact rational width<=1/256. Consequently beta<=29/10 is impossible for this POINTWISE alpha1/4 envelope. Exact rational comparison gives a necessary1/1024-grid beta floor2977/1024, only four grid steps below the published2981/1024. This limits further refinement of this pointwise bound, not every support-aware form estimate or representation.

## Actual execution and controls

Actual source wall is4.693s; independent audit is13.755s. These scalar elapsed times are execution receipts, not full-target benchmarks.

All10 [substantive controls](data/negative-controls-v1.json) reject at the intended checks, with no PASS artifact: omitted prime7 coefficient, false finite-cell upper, missing frequency leaf, unpaid analytic infinity, false witness lower, missing canonical polar coefficient, unpaid terminal inverse weight, unpaid model discrepancy, floating mathematical input and falsely claimed achieved high-mode width. The control run takes52.775s. Every altered packet and native rejection receipt remains separate from the accepted source.

The [27-destination capture](captured-source-inputs-v1.json) contains860767 source/input bytes, including accepted comparison inputs but excluding expected NEW scientific outputs. An [isolated replay](data/isolated-replay-v1.json) reruns source and independent audit in18.488s. Both new scientific outputs reproduce BYTE-IDENTICALLY without field exclusions, and the owned tree is removed. The installed Python/FLINT environment is shared; this is source/input isolation, not an OS sandbox or an independent arithmetic library.

## Environment and provenance

The recorded environment is Python3.14.0, python-flint0.9.0, FLINT3.6.0 and Windows x64. Scalar jobs use one native thread. Source arithmetic is512 bits with192-bit scalar publication; direct-proof audit is768 bits, with512/1024-bit declaration checks. The25600/34304 full-target bit policies are starting declarations, not arithmetic performed on target matrices.

Actual argv, stdout/stderr, exits and elapsed times are retained in data/*-receipt.json and matching stream files. Existing C-0125 programs, packets, manifest, rejected first consumer, and earlier records remain untouched.

## Reproduction

Use fresh outputs from the repository root:

```text
uv run --locked python -B computations/2026-10-29T004611Z-t1-direct-reference/qualify-direct-v1.py --inputs computations/2026-10-29T004611Z-t1-direct-reference/inputs-v1.json --output <fresh-source.json>
uv run --locked python -B computations/2026-10-29T004611Z-t1-direct-reference/verify-direct-v1.py --inputs computations/2026-10-29T004611Z-t1-direct-reference/inputs-v1.json --source <fresh-source.json> --output <fresh-audit.json>
uv run --locked python -B computations/2026-10-29T004611Z-t1-direct-reference/exercise-direct-v1.py --mode replay --capture computations/2026-10-29T004611Z-t1-direct-reference/captured-source-inputs-v1.json --output <fresh-replay.json>
uv run --locked python -B computations/2026-10-29T004611Z-t1-direct-reference/exercise-direct-v1.py --mode controls --output <fresh-controls.json>
```

The finite-cover source packet and altered mathematical proof packets are retained proof/verifier inputs, not disposable raw samples. Preserve their bytes even where they exceed the general small-summary threshold.

## Interpretation and limits

The inherited reference was materially conservative at this same support. Direct signed cancellation reduces its sufficient dimension and precision requirements under unchanged controls. This neither measures practical RAM/time nor qualifies the full fixed-target execution pipeline at the new dimensions. No allocation/kernel optimization or full-target resource experiment is performed. The scalar improvement does not establish a complete positive Schur matrix, true Weil negativity, an optimal supported reference, external-proof agreement, literature priority, all-support viability, production admission or RH.
