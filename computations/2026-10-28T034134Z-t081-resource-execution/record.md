# Complete T81/100 resource-budgeted source and independent audit

- **Computation ID:** `X-20261028-002`
- **Created:** `2026-10-28T03:41:34Z`
- **Last updated:** `2026-10-28T17:41:03Z`
- **Status:** `COMPLETE`
- **Disposition:** Qualified fixed-workload execution improvement. No new mathematical claim or theorem admission.

## Objective

Reduce complete source and independent analytical-audit wall time without changing the mathematical target, precision, signed operators, publication or acceptance criteria. Apply one detected CPU/memory budget, retain live progress and exact execution evidence, and clean up only owned processes.

## Mathematical quantity tested

The unchanged T81/100,N826,K86,M1652 candidate has three triangular matrix families per parity and413 modes per full block. The source retains all active prime powers2/3/4/5, their combined square including mixed products, both VP orientations, physical Legendre masses, the full residual allowance and both infinite exteriors. The independent consumer reconstructs all512946 published analytical entries at6144 bits. The unchanged exact checker verifies both complete413-dimensional paid signs, transformed radii, numerical-width goals and nonsingularity.

This computation changes execution, not the sufficient positivity criterion. It does not execute a retained smooth-test admission or release a new full source-norm consequence. Production inventories remain8v1/0v2/1v3. RH is unresolved.

## Environment

The run started2026-10-28T12:36:13Z at Git46aa7c6e3dddb31b2963a1790d01d79a7daacf97 with `git_dirty=true`. The new uncommitted program bytes are retained and SHA-bound rather than described as clean-source proof provenance.

Windows10.0.26300,x64,32GB-class physical RAM and six logical CPUs were available. The locked interpreter is Python3.14.0 with python-flint0.9.0. The explicit post-run [environment observation](data/environment-observation-v1.json) reports FLINT3.6.0; it is not a before-run binary fingerprint. The actual [run identity](data/run-v1/.live/run.json), [budget](data/run-v1/execution-budget.json), worker profiles and logs are retained.

## Inputs and parameters

- Exact support81/100; N826, residual order86 and physical extent1652. Both low blocks have413 modes.
- Source4608 bits, publication256 bits, independent reconstruction6144 bits. No precision or dimension reduction in the full run.
- [Original capture](../2026-10-27T182100Z-t081-retained-acceptance/captured-source-inputs-v1.json) supplies55 declared destinations. Nine expected full-target outputs are withheld from the numerical child tree. The remaining captured inputs and every new arithmetic/execution program are copied into a fresh isolated tree.
- [Captured execution](data/run-v1/captured-execution-v1.json) binds all copied bytes. [Captured code](data/run-v1/captured-code-v1/) preserves the exact programs actually used.
- The old exact witness is only a proposed full transform. Its source binding is updated to the fresh source; the full exact determinant/sign/radius checks execute again.
- New source SHA-256 is `2375a873d638af115312ffb8aaf416a067ccfa9170a96a320254eb121b9d125f`. All six compressed matrix packets are byte-identical to the independently audited original. Complete type-sensitive source metadata comparison permits only the producer-SHA change.

## Selected execution and resource controls

The measured6144-bit,N256 arithmetic probe is explicitly NONPROOF. One native thread took219.505s and six took78.226s. It identifies a native kernel that scales; it does not establish the full-target result or justify reducing N. The selected full operation uses one numerical worker per sequential stage and native threads within that worker, not one full reconstruction per core.

`execution_resources_v2.py` resolves visible affinity/quota/job CPU limits and host/process/job memory availability, with explicit CLI/environment precedence. Requested worker counts above one are rejected for this implementation. Workers times native threads never exceeds the selected CPU budget. The actual run selected C6,W1,T6, a12.373GiB owned-job memory allowance and1.375GiB reserve. A9GiB planning requirement derives from the measured probe plus quadratic size scaling and headroom; it is not a mathematical bound or memory reservation.

Windows job objects impose process/aggregate committed-memory limits, CPU rate and kill-on-close ownership. A READY/GO barrier explicitly attaches both a venv launcher and the actual interpreter PID before mathematical imports. This avoids the observed redirector race. Neutral orchestration is shared; producer mathematics is not imported by the independent consumer.

The supervisor reuses `scripts/run_observability.py` atomic status, events and output locking. Separate stdout/stderr, coarse phase/work units, elapsed CPU/wall, job memory and native settings remain observable while a native call holds the numerical process's GIL. ETA uses only observed comparable unit costs and remains unavailable inside an opaque operation. Success, failure and cancellation reap the owned job tree; unrelated processes are not terminated. Cleanup also handles a worker exiting while an owned descendant retains output pipes.

## Reproduction procedure

From the repository root, use a fresh output directory:

```text
uv run --locked python -m scripts.run_t081_resource_execution --output-dir <fresh-directory>
uv run --locked python -B computations/2026-10-28T034134Z-t081-resource-execution/qualify-execution-v1.py --run-dir <fresh-directory> --output <fresh-qualification.json>
```

The canonical module dispatches to the byte-retained runner. Its actual help and low-memory rejection were exercised in [the module smoke](data/canonical-module-smoke-v1.json). The measured full run invoked that same runner directly with `--output-dir computations/2026-10-28T034134Z-t081-resource-execution/data/run-v1`. Full final qualification requires the second command, not only an intermediate source PASS.

Controls are `--cpus`, `--workers`, `--threads`, `--memory-mib` and `--reserve-mib`, with matching `T081_CPUS`, `T081_WORKERS`, `T081_THREADS`, `T081_MEMORY_MIB` and `T081_RESERVE_MIB`. CLI takes precedence. `--cpus 1 --workers 1 --threads 1` selects bounded single-worker reproduction. Excessive/inconsistent limits and an insufficient fixed-target memory allowance reject before arithmetic. No fallback reduces N/K/precision or converts resource failure into mathematical negativity.

The final focused suite was:

```text
uv run --locked --extra test python -m pytest -n 0 -q tests/test_t081_resources_v2.py tests/test_t081_execution_supervisor.py tests/test_t081_comparer_v3.py tests/test_t081_execution_corrections.py tests/test_t081_profile_v2.py --junitxml=computations/2026-10-28T034134Z-t081-resource-execution/data/execution-tests-v3.xml
```

## Output

The [full captured execution](data/run-v1/qualification.json) reports `PASS_CAPTURED_SOURCE_ANALYTICAL_EXACT_AND_NINE_CONTROLS`. The separate [final qualifier](data/final-qualification-v1.json) reports `PASS_COMPLETE_LOCAL_EXECUTION_QUALIFICATION`, verifies code/log/budget/source bindings and complete exact block equality, and confirms temporary-tree removal and all owned workers reaped. Finalizer code is separately SHA-bound post-processing added after the arithmetic capture.

All512946 independently reconstructed analytical entries and both complete exact signs/nonsingularity/width goals pass. All nine controls pass:

- Six false-source cases test the low constant, weighted head payment, complete physical exterior, terminal inverse weight, prime5 low term and prime5 mixed square. They reuse the fresh even reconstruction already positively checked in the full audit. These are native subset rejection probes, not six additional full reconstructions.
- The singular full transform rejects with exit1 and the expected determinant error. A synthetic selected-negative matrix reports selected sufficient-matrix negativity, not Weil negativity. A widened numerical packet reports numerical-width failure, not a false positive.

The [derived even-control summary](data/run-v1/native-controls/native-even-control.json) binds the full audit and its256473-entry positive even result. It fills the subset receipts' shared-control reference without rewriting those receipts or claiming another reconstruction.

The focused suite collected94 tests:93 passed and one OS-specific allocation test skipped. Actual Windows cases cover allocation denial, aggregate child limits, attachment failure before arithmetic, unrelated-process safety, progress, cancellation, inherited output pipes and native-thread initialization after legacy imports. Installed Python3.12 also passes actual one-CPU Windows affinity detection and insufficient-memory CLI preflight; no Python3.12 FLINT arithmetic is claimed.

### Measured complete-target phases

Baseline walls are the retained one-thread replay in [X-20261027-007](../2026-10-27T182100Z-t081-retained-acceptance/record.md). New stage walls include worker startup and cleanup. CPU and peak resident measurements are for the numerical process. Exact arithmetic is unchanged; its faster observation is not a separate algorithmic optimization claim.

| Phase | Baseline wall,s | New wall,s | Observed ratio | New CPU,s | Peak working set,GiB |
| --- | ---: | ---: | ---: | ---: | ---: |
| source | 4591.961 | 1767.866 | 2.60x | 4191.703 | 6.272 |
| independent-audit | 9213.553 | 2845.007 | 3.24x | 8798.297 | 7.606 |
| exact-sign | 33.565 | 27.855 | 1.21x | 32.281 | 0.984 |

The new audit additionally executes the six false-source subset probes, so its ratio is not an identical-operation kernel benchmark. One run per implementation does not establish a scaling curve or statistical speedup guarantee. [Measured summary](data/measured-summary-v1.json) retains exact counters, main-versus-stage overhead and comparison limits. Source and audit average2.37 and3.09 CPU equivalents during main respectively; some phases remain serial or do not scale to all six CPUs.

The largest observed raw owned-job committed-memory high-water is7.862GiB, below the12.373GiB configured ceiling. The audit process's resident high-water is7.606GiB. Memory is bounded and measured; absence of a memory regression against the unmeasured old audit is not claimed.

## Interpretation

The complete source and independent analytical consumer now both use measured native parallelism under one CPU/memory policy. Correctness is established for this fixed execution through a fresh independent reconstruction, complete exact checks, substantive false-source/control rejection and six-packet identity. Historical source/profile/candidate/replay programs and outputs remain unchanged. The earlier251-file preservation check passed without differences.

## Limitations

Qualification is on this Windows host. Visible Linux hierarchy fixtures run in the policy suite; no live non-Windows or larger-core-host scaling result is claimed. Windows ancestor jobs are not enumerable here, and hidden cgroup ancestors are not visible. Detection reports those limits. Availability is a snapshot, not a reservation against other applications. The kernel job limit covers the owned numerical tree; parent/system headroom is separate.

The forced-memory probe in [Windows accounting](data/windows-job-accounting-v1.json) observed a denied allocation and current commit below its limit while raw OS high-water counters exceeded it. Those counters are retained verbatim, not clamped or used as a retained-allocation ceiling assertion. Allocation denial and current accounting establish the exercised enforcement behavior.

These are Python/Arb source and exact-rational research checks, not a new production Rust/Lean theorem, a general continuation engine, a proof of all-support positivity or RH. The retained smooth-test admission is not executed or substituted by this compute qualification.

## Related claims, attempts and findings

- Existing fixed-target C-0122 and provisional C-0123 are unchanged; no new claim ID is created.
- [Original complete source](../2026-10-27T140745Z-t081-complete-gram-attempt/record.md), [retained replay](../2026-10-27T182100Z-t081-retained-acceptance/record.md) and [earlier source-only correction](../2026-10-28T024305Z-t081-execution-corrections/record.md) remain preserved.
- [Manifest](manifest.json) binds this record, versioned programs, exact retained outputs, numerical/control packets, logs, profiles and execution evidence. Large packets are proof/control evidence with deterministic regeneration above, not an external dataset.
