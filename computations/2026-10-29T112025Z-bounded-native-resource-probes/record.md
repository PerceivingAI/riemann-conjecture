# Bounded native arithmetic, preparation and enclosure observations

- **Computation ID:** `X-20261029-003`
- **Created:** `2026-10-29T11:20:25Z`
- **Last updated:** `2026-10-29T11:38:49Z`
- **Status:** `COMPLETE`, scoped nonproof measurements

## Objective

Measure separately bounded exact arithmetic, polynomial preparation, selected high-mode enclosures, native interval products, transport and owned-process memory. Distinguish representations, preparation cost, native work and input-dependent conditioning. This computation does not execute the complete T=1 Weil source, admit a theorem or establish a complete execution path.

## Mathematical quantities and scope

The reference declaration is C-0126 at T=1,N=5564,M=11128,K=132 with active powers2/3/4/5/7. Its source/audit starting bits25600/34304 are unchanged. Exact bindings appear in [inputs-v1.json](inputs-v1.json).

- Synthetic full2782-square Vandermonde matrix modulo verified prime65521. The native complete determinant equals an independent product of all pair differences, residue49071. This is a one-sided exact nonsingularity check for that synthetic matrix, not a target witness.
- Synthetic16-by2782 and2782-by16 integer products use512/107-bit operands and all2782 inner coordinates. Mass-weighted products use the actual odd-parity masses2/(4i+3), with10743-bit LCM. Selected outputs match independent Python integer sums; removing a genuine final inner term differs.
- A reduced65-dimensional exactly known row-scaled rational factor exercises native1024-bit block Cholesky and complete forward/back solves. All4225 factor intervals and the exact rational solve agree. A missing-cross-update control rejects. This is not target conditioning qualification.
- Six complete2782-square float64 arrays and a complete eigenspectrum/vector calculation measure dense nonproof workspace. Three eigenpair residuals pass the stated numerical check. These are synthetic matrices, not proposed target coordinates.
- Exact polynomial recurrence streams through degree11127 without retaining all prior polynomials; the highest polynomial matches the unchanged Rodrigues helper. Separate native and integer-ratio constructors are compared against that helper at degrees0/1/2/132/5563/11127, checking every coefficient and exact ratio division.
- At actual source25600/audit34304 bits, selected Gauss nodes of orders5564/8346 and modes5557/5563/11127 exercise completed512-grid values. The final translation cell retains all five active signed images and their mixed square. Three nodes are a declared partial quadrature domain, not the complete rule. Six image, nine partial-Gram and one head-value enclosures pass separate evaluation checks. Prime7 omission rejects at all three selected nodes.
- Selected frequency anchors1/30/59 retain the full recurrence through M and highest same-parity head modes11125/11127. Downward Bessel seeds and separate sine/cosine upward recurrence agree by containment through512-grid checkpoint and256-grid prefix publication. This is one off-diagonal entry at three anchors, not the whole kernel, its diagonal/terminal mass or the full59-anchor sum.
- Synthetic completed interval operands32-by8346 and8346-by32 retain every inner coordinate at native34304 bits. Four corner outputs contain the independently summed exact minimum/maximum endpoint products; omission of the last inner contribution rejects. Native threads were detected as6, not fixed in the program.
- Synthetic65536-record hex/gzip transport checks exact endpoints and corrupt-CRC rejection. Two simultaneous native descendants each retain a256-square copied34304-bit scalar matrix under one owned job. Their true row value is checked; all descendants are reaped. This does not implement a production parallel scheduler or recovery protocol.

## Environment and containment

Actual runtime: Windows x64, Python3.14.0, python-flint0.9.0, FLINT3.6.0. [Measured summary](data/measured-summary-v1.json) and raw results record NumPy/BLAS environment, program/input fingerprints, current/lifetime process memory, stage profiles and owned-job receipts. Source checkpoint was `a7d43f501cd7cf6ea74360c4092ecaa11392dbef`; the new measurement programs were uncommitted, with their actual bytes SHA-bound. No clean proof provenance is claimed.

Every numerical stage ran under the retained READY/GO supervisor with an explicit2048MiB owned-job commitment cap and512MiB declared floor. CPU availability was detected. Eight stages used one native thread; the compact-panel stage used the detected six. The aggregate stage has one top-level worker and two one-thread descendants. No dimension/precision/cap fallback or sweep was performed. All nine cleanup receipts pass. Job peaks are not clamped and do not include the external command supervisor's own buffers.

## Observations

Whole owned-stage elapsed time includes worker startup/profile/cleanup and is not the pure kernel time. Peaks are OS owned-job committed memory, not just sampled working set.

| Observation | Owned-stage wall s | Peak job commitment MiB |
| --- | ---: | ---: |
| exact | 9.289 | 162.648 |
| proposal | 5.905 | 651.344 |
| prepare | 215.607 | 116.188 |
| images | 3.283 | 25.977 |
| frequency | 3.370 | 75.758 |
| transport | 2.133 | 123.996 |
| aggregate | 1.250 | 637.480 |
| coefficients | 37.709 | 142.645 |
| panels | 3.000 | 92.930 |

The full synthetic modular determinant itself took3.222927s. The full synthetic float eigensolver took4.544417s. These observations do not establish data-independent upper bounds or a complete target runtime.

The streamed exact recurrence took184.799256s. The following independently timed constructors produce the SAME complete selected polynomial; every coefficient was checked outside the individual construction timers:

| Degree | Unchanged Rodrigues helper s | Integer-ratio construction s | Native exact construction s |
| --- | ---: | ---: | ---: |
| 5563 | 5.557539 | 0.033570 | 0.002949 |
| 11127 | 30.882430 | 0.150542 | 0.015774 |

The ratio derives directly from `A_k=(-1)^k*binom(n,k)*binom(2n-2k,n)`:

`A_(k+1)=-A_k*(n-2k)*(n-2k-1)/(2*(k+1)*(2n-2k-1))`, with exact integer division and common denominator2^n. The original helper and earlier records are unchanged. These are constructor observations, not a whole-source speedup.

The compact native product took0.381637s of wall and1.562500s of process CPU. Construction took1.640295s separately. The four checked output midpoint mantissas had541 bits despite34304-bit context. This shows why a context-only limb account is not a measured allocation for completed low-width operands. It does not apply to cancellation-sensitive coefficients, roots or every native workspace.

The transport sample was17,620,194 raw bytes and5,623,497 compressed bytes. Encode/compress/fsync took0.704349s; first uncontrolled-cache read/hash/decode/parse0.301033s and repeated warm processing0.295026s. Cache was not flushed; this is not cold-disk bandwidth, target compression or large-dataset throughput qualification.

The image probe also records a conditional checkpoint-rounding-only full P-square physical bound about5.405e-146, using the complete signed coefficient bound, |P_n|<=1, exact quadrature mass and ordinary Legendre masses. This is below the explicit2^-80 comparison threshold but excludes native input uncertainty, other families, publication and transformed proof effects. It is NOT complete target numerical-width acceptance.

## Reproduction procedure

Programs are separate versioned research entry points. Existing frozen source/audit/proof programs are not patched. Run from repository root using the recorded environment. The actual numerical invocations used `.venv/Scripts/python.exe -B` in place of `uv run --locked python -B` below; exact argv/environment are retained in each receipt.

```text
uv run --locked python -B scripts/run_bounded_resource_probes_v1.py --mode exact --inputs computations/2026-10-29T112025Z-bounded-native-resource-probes/inputs-v1.json --output-dir <fresh-exact-dir> --memory-mib 2048 --threads 1
```

The same entry point was exercised separately with `--mode proposal`, `prepare`, `images`, `frequency`, `transport` and `aggregate`, each in a fresh directory with the same cap/thread setting. Those modes are independent observations, not a chained positivity workflow.

```text
uv run --locked python -B scripts/probe_coefficient_reuse_v1.py --inputs computations/2026-10-29T112025Z-bounded-native-resource-probes/inputs-v1.json --output-dir <fresh-coefficient-dir> --memory-mib 2048
uv run --locked python -B scripts/probe_compact_native_panels_v1.py --inputs computations/2026-10-29T112025Z-bounded-native-resource-probes/inputs-v1.json --output-dir <fresh-panel-dir> --memory-mib 2048
uv run --locked python -B scripts/verify_bounded_resource_observations_v1.py --bundle computations/2026-10-29T112025Z-bounded-native-resource-probes --output <fresh-qualification.json>
```

The last command reads retained results and checks their bindings/semantic controls/cleanup. It does not repeat numerical measurements. Large scratch arrays/chunks are generated in owned temporary directories and removed; small summaries and raw streams/profiles/receipts remain. [Manifest](manifest.json) binds this bundle, six new entry points and retained dependency fingerprints. Shared installed runtime/native library premises remain explicit rather than pretending to capture an independent OS image.

## Interpretation and limitations

The tested bounded representations, selected enclosures and exact mechanisms are supported by the recorded evidence. The data expose substantial avoidable polynomial setup work and distinguish completed compact operands from full-working-precision tables. No existing production implementation has been replaced.

No full low/head/exterior family, complete analytical source, actual target proposal/conditioning, complete exact sign, new retained smooth-test consequence or end-to-end target runtime/peak is established. Selected outer/node/anchor slices do not stand for missing domains. All native products, parses, controls, source-error payments and complete reproduction remain necessary for any later mathematical result. No universal speedup, host maximum, live-Linux/larger-core qualification, GPU conclusion or hardware purchase follows.

C-0124 at T81/100 remains the source-conditional retained research positivity frontier. C-0126 remains scalar-only at T1. Production8v1/0v2/1v3 and RH unresolved are unchanged. No theorem or priority claim is created.
