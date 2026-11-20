# T=1 dense-layout constraint and bounded contraction assessment

- **Computation ID:** `X-20261029-002`
- **Created:** `2026-10-29T01:39:29Z`
- **Last updated:** `2026-10-29T02:01:19Z`
- **Status:** `COMPLETE` scoped execution assessment; full target `NOT_ADMITTED`
- **Evidence:** Static allocation/lifetime inspection, actual full-length moment vectors/native copies, restricted target-precision contractions and preserved bounded native failures. No new mathematical claim ID or theorem admission.

## Objective and fixed quantity

Determine whether the accepted C-0126 T=1,N5564,K132,M11128 declaration encounters an implementation layout constraint, a measured machine-capacity constraint for that layout, or an unresolved execution cost. Hold the mathematical controls and source25600/audit34304/publication256-bit policies fixed. Do not infer target positivity from a smaller matrix or turn a cap refusal into a mathematical negative.

The [allocation and algebra contract](allocation-contract-v1.md) traces the existing fixed-.81 producer/auditor, exact matrix shapes, live Python locals, structured identities and required verification boundaries. No historical source, input, result, execution guard or contract is modified. The frozen .81 producer/auditor are not relabelled as generic T=1 operations.

## Results

### 1. An identified dense allocation cannot fit this host configuration

The independent audit's arithmetic_blocks constructs `tail_moments[k,j]=moments[2k+parity+j]` as an N-by-N native Arb matrix. We reconstructed all16691 required moments at the actual T=1 windows for every active prime power2,3,4,5,7, at both starting precisions. Reflected windows and both parity multiplicities were checked explicitly. There are30958096 independently copied matrix entries, although only16691 distinct scalar moments are required.

Native opaque scalar/vector accounting verifies fresh copies, including a48-byte Arb body, rather than using Python __sizeof__ or extrapolating the old7.6GiB peak. Every one of ten4096-entry native vectors matches the independently summed scalar account exactly.

| Specified power-moment representation | Explicit midpoint payload,bytes | Dense native-copy account,bytes | Account,GiB |
| --- | ---: | ---: | ---: |
| 25600-bit comparison | 99,065,907,200 | 100,551,895,808 | 93.6463 |
| Declared34304-bit audit | 132,748,315,648 | 134,234,304,256 | 125.0154 |

The25600-bit row is the SAME POWER TABLE at that precision, not a measured source logarithmic-table requirement. Source logarithmic moments, complete output matrices and all other live allocations remain separate.

This account excludes allocator overhead, row pointers, Python lists, coefficients, other live matrices and temporary products. It is NOT an allocated target matrix or an observed full-process peak. Even its audit midpoint payload alone exceeds the observed host's total commit50,345,074,688 bytes and physical RAM33,702,076,416 bytes. Thus this specified uncompressed dense layout is incompatible with the observed host configuration before other work. More CPU threads do not remove that allocation.

This does not prove the mathematical operation requires125GiB under another representation, that a different implementation cannot run here, or that buying larger hardware is necessary. Availability/commit snapshots and hidden-ancestor visibility limits are retained; they are not reservations.

### 2. Blocking removes a demonstrated allocation without changing the selected quantity

The restricted comparison uses T=1,m2,parity1,34304-bit arithmetic, full5564 inner powers, four actual high Legendre modes5557/5559/5561/5563 and twelve selected power rows including5563. It is not the complete matrix or all arithmetic terms. Both routes independently validate all48 selected outputs by polynomial composition and endpoint antiderivatives, and reject omission of a genuine nonzero highest-power contribution. All four successful executions publish the same48 dyadic endpoint pairs.

| Selected contraction | Largest live Hankel entries | Native component account,bytes | Observed process commit while Hankel live,bytes | Contraction wall,s |
| --- | ---: | ---: | ---: | ---: |
| Dense12-row observed v2 | 66,768 | 289,506,048 | 567,123,968 | 1.7708 |
| Blocked2-row observed v2 | 11,128 | 48,251,008 | at most305,504,256 | 2.2289 |

Blocking reduces this component sixfold and the observed current process commitment at those construction boundaries. It does NOT establish a speedup: the selected blocked contraction was slower. Whole-process peaks stay near917MB because coefficient setup had already established a higher high-water. Original v1 runs remain separate: dense1.7545s and blocked2.5801s contractions; v2 adds live-allocation observation without changing the successful arithmetic. No old timing or artifact is overwritten.

The v2 measurements distinguish current commitment/working set from lifetime peaks. Native component account, sampled current commitment and raw OS job high-water are different metrics and are retained separately.

### 3. The structured convolution attempt remains unqualified under its selected cap

The Hankel coefficient identity in the contract avoids materializing H algebraically. The actual native polynomial-convolution implementation aborted with `GNU MP: Cannot reallocate memory`, exit3221226505, under the1536MiB owned-job cap. Repeating the same arithmetic with ONLY native threads changed6 to1 also aborted under that cap. No result.json or successful worker profile exists for either failed run; the independent selected-output checks were not reached.

Both failed receipts, logs, resource snapshots and raw OS counters are preserved. Owned cleanup succeeds in both cases. Raw high-water counters slightly exceed the configured cap, consistent with Windows' previously documented counting of denied allocation demand; they are not clamped or asserted to be retained memory. These runs identify failed configurations, not a host-wide capacity limit, a mathematical rejection, a required workspace minimum, or a reason to abandon the identity. Changing thread count alone did not remedy the observed refusal. No higher-cap run or convolution speedup is claimed.

## Existing cost/lifetime evidence

At the OLD fixed .81 workload, the retained independent audit profile reports arithmetic_blocks5735.21875 CPU seconds/1578.00183 wall seconds and combined square1660.625 CPU/607.87119 wall seconds. These identify relevant kernels, not a T=1 timing forecast. [Prior profile](../2026-10-28T034134Z-t081-resource-execution/data/run-v1/independent-audit/profile.json).

Other explicit risks include both parity frequency kernels retained together; previous-parity returned dictionaries remaining live during the next reconstruction; dense coefficient, Gram, mass and output matrices; all rational polynomial storage; source list/JSON/gzip materialization; and fixed32MiB consumer payload guards. Blocking one moment product does not qualify these other stages, all transformed widths, or the complete exact witness path.

## Environment and resource controls

Windows10.0.26300 x64, Python3.14.0, python-flint0.9.0, FLINT3.6.0. The [environment observation](data/environment-v1.json), actual per-run budgets, program/config fingerprints and stage receipts retain the software and machine evidence. Git base is local `a6ed03d`, dirty research worktree; no clean-source proof provenance is claimed. The native DLL is SHA-bound, not vendored.

Each probe ran sequentially in a separate owned job with1536MiB committed-memory cap, READY/GO attachment before numerical work, one worker and detected six-CPU allowance. Native threads were six except the expressly selected one-thread comparison. The shared neutral containment, policy and worker are unchanged; only the measurement run identity is specialized to support1/dimension5564. Reused T081 protocol/profile names denote infrastructure formats, not a claim that the fixed .81 mathematical runner accepted T=1. All seven numerical jobs finish with zero owned active processes, including native aborts.

The full-length storage census took42.6874s inside main,40.59375 process CPU seconds, with owned-job peak281,899,008 bytes. Successful selected contraction executions take about53-56s including coefficient setup and independent checks, not just the1.8-2.6s contraction. Raw receipts contain startup/cleanup totals and distinguish those scopes.

## Reproduction commands

From the repository root, use fresh output directories. The native library binding selects the measured Windows environment; other binaries/platforms require separately versioned measurements, not relabelled hashes.

```text
uv run --locked python -B computations/2026-10-29T013929Z-t1-execution-allocation/run-probes-v1.py --probe storage --inputs computations/2026-10-29T013929Z-t1-execution-allocation/probe-inputs-v1.json --output-dir <fresh-storage-directory> --memory-mib 1536
uv run --locked python -B computations/2026-10-29T013929Z-t1-execution-allocation/run-probes-v1.py --probe product --inputs computations/2026-10-29T013929Z-t1-execution-allocation/product-dense-inputs-v1.json --output-dir <fresh-dense-v1-directory> --memory-mib 1536
uv run --locked python -B computations/2026-10-29T013929Z-t1-execution-allocation/run-probes-v1.py --probe product --inputs computations/2026-10-29T013929Z-t1-execution-allocation/product-blocked-inputs-v1.json --output-dir <fresh-blocked-v1-directory> --memory-mib 1536
uv run --locked python -B computations/2026-10-29T013929Z-t1-execution-allocation/run-product-v2.py --inputs computations/2026-10-29T013929Z-t1-execution-allocation/product-dense-inputs-v1.json --output-dir <fresh-dense-v2-directory> --memory-mib 1536
uv run --locked python -B computations/2026-10-29T013929Z-t1-execution-allocation/run-product-v2.py --inputs computations/2026-10-29T013929Z-t1-execution-allocation/product-blocked-inputs-v1.json --output-dir <fresh-blocked-v2-directory> --memory-mib 1536
```

The two following retained configurations FAILED and are not required to manufacture another failure before reading the evidence:

```text
uv run --locked python -B computations/2026-10-29T013929Z-t1-execution-allocation/run-convolution-v1.py --inputs computations/2026-10-29T013929Z-t1-execution-allocation/product-convolution-inputs-v1.json --output-dir <fresh-six-thread-attempt> --memory-mib 1536
uv run --locked python -B computations/2026-10-29T013929Z-t1-execution-allocation/run-convolution-v2.py --inputs computations/2026-10-29T013929Z-t1-execution-allocation/product-convolution-inputs-v1.json --output-dir <fresh-one-thread-attempt> --memory-mib 1536 --threads 1
```

Check the retained evidence without rerunning arithmetic:

```text
uv run --locked python -B computations/2026-10-29T013929Z-t1-execution-allocation/qualify-measurements-v2.py --output <fresh-qualification.json>
```

The [v2 qualifier](data/qualification-v2.json) passes: ten storage cases,40960 native-vector copy checks,192 independent selected-output containments across four completed product runs, four genuine omitted-term rejections, matching selected dyadic pairs, two preserved native failures and seven successful owned cleanups. Version1 qualified locally; separately retained version2 resolves program filenames relative to this bundle rather than trusting original machine-specific receipt paths. No isolated arithmetic replay is claimed. [Capture index](captured-source-inputs-v1.json) binds11 dependencies/2,331,312 bytes; scripts, exact inputs, outputs and logs are retained in this bundle. Large captured declaration bytes are existing required proof inputs, not a new raw benchmark dataset.

The additional [relocated evidence replay](data/relocated-qualification-v1.json) copies111 files into a fresh owned tree, withholds both expected qualification reports and reproduces qualification v2 byte-identically using its local retained code/inputs/receipts. The tree is removed. This exercises path neutrality of the EVIDENCE qualifier, not independent reconstruction or another native arithmetic run:

```text
uv run --locked python -B computations/2026-10-29T013929Z-t1-execution-allocation/replay-qualification-v1.py --output <fresh-relocated-qualification.json>
```

## Joint execution decision and limits

**Full T=1 execution: NOT_ADMITTED.** The mathematical declaration is independently qualified, but the complete target implementation/verification path does not exist, and a literal extension of its dense audit layout exceeds the observed host capacity. A selected blocked product is feasible; a complete bounded-memory source/audit/exact pipeline has not been established. No full-target wall/CPU requirement, total peak, all-entry width, sufficient-matrix sign or positivity is measured.

This is a demonstrated implementation-layout obstacle interacting with a specified host configuration, not evidence against the mathematical criterion or a universal hardware no-go. The new information is that some storage is avoidable while other whole-pipeline costs remain unresolved; simply increasing CPU utilization does not close that gap.

Retained smooth-test positivity remains C-0124 at T81/100. C-0126 remains scalar-only. Production inventories8v1/0v2/1v3 and RH unresolved are unchanged. No Rust/Lean theorem replay, new production tool/dependency, cloud/VM setup, external mathematical literature search or full support challenge occurs. FLINT allocation API documentation is cited for the software accounting premise.
