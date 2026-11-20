# Exact whole-source scalar profile binding and metadata inspection

- **Computation ID:** `X-20261029-004`
- **Created:** `2026-10-29T17:55:45Z`
- **Last updated:** `2026-10-29T18:16:02Z`
- **Status:** `COMPLETE`, metadata binding and behavioral validation only

## Objective

Implement and exercise exact immutable bindings for two already reviewed scalar research profiles. Distinguish the mathematical/profile description, descriptive collection identity and this inspection operation from native analytical verification, computed matrices, resource admission, positivity and production theorem acceptance.

The delivered command is `scripts.weil_whole_source_split inspect`. Its only subcommand is inspect. `scripts/whole_source/contract.py` implements the exact metadata, provenance, physical-domain and descriptive identity checks. The package initializer has no numerical imports. The command neither imports nor executes the archived mathematical programs whose bytes it fingerprints.

## Mathematical quantity and scope

| Profile | Support | N | M | K | Reference meaning | Declared source/audit bits | Bound evidence files |
| --- | --- | --- | --- | --- | --- | --- | --- |
| retained-t081 | 81/100 | 826 | 1652 | 86 | Supported-form bound | 4608/6144 | 78 |
| selected-t1 | 1 | 5564 | 11128 | 132 | Direct whole-frequency-line multiplier bound | 25600/34304 | 58 |

Original inputs are the Q/C-0122 declaration/audit at `computations/2026-10-27T132236Z-t081-prime-five-qualification` and D/C-0126 at `computations/2026-10-29T004611Z-t1-direct-reference`. Their reviewed original manifest hashes are fixed independently in the binder. A manifest validates the selected scalar snapshots, code members and captured-input/original-destination closure; this is not a new audit of every member in every historical bundle. Their raw hashes, sizes and semantic roles are in each problem artifact.

Exact checks preserve active powers2/3/4/5 and2/3/4/5/7, including von Mangoldt base2 for m4; N/M/K/R/Rc, reference/eta/model scalars; complete formal residual coefficients; exact frequency partition, nonincreasing positive inverse weights and terminal mass; ordinary Legendre mass2/(2n+1), physical low/head/band geometry and prescribed polynomial Gauss degree policies. The strict local-series predicate uses the original retained pi enclosure. The T1 activation check uses exact rational consequences of retained c7/c2 enclosures and sqrt7<8/3, sqrt2>7/5; it does not freshly evaluate a transcendental function.

The .81 numerical goal is the original exact rational. T1's2^-80 goal is explicitly new inspection-contract policy, equal to one quarter of its2^-78 accuracy choice. It is not added to D, not an achieved matrix width and not a presumed target gap. Checkpoint512/final256 metadata does not establish acceptable numerical error in a calculation.

Full logical partitions and bounded output-tile descriptors are descriptions only. Requests distinguish producer/analytic/exact roles; no partial arithmetic contribution or computed chunk is accepted. Coupled head metadata retains two contracted head axes; the complete exterior projection retains one. The mathematical/profile ID binds the complete normalized reviewed description and its inputs; the descriptive collection ID additionally binds declared arithmetic, partition and current implementation bytes. Neither grants execution permission.

## Environment and inputs

Executed on Windows x64 with:

- Python 3.14.0 (tags/v3.14.0:ebf955d, Oct  7 2025, 10:15:03) [MSC v.1944 64 bit (AMD64)]
- Python 3.12.13 (main, Jul 18 2026, 17:08:38) [MSC v.1944 64 bit (AMD64)]
- pytest9.1.1, hypothesis6.165.10 and xdist3.8.0 for the focused suite, run sequentially.

[Execution summary](data/execution-summary-v1.json) binds actual source/test snapshots and interpreter observations. [Invocations](data/invocations-v1.json) records argv, actual exits and streams. The code was uncommitted; no clean provenance is claimed. No environment, numerical dependency, VM, container or cloud resource was provisioned.

Every retained input is read under an8MiB per-file,64MiB aggregate and256-file bound with duplicate-key/nonexact-number/canonical-rational/path/reparse checks. Scalar JSON is parsed, original code is only fingerprinted, and no matrix or polynomial-basis array is allocated. These are metadata input caps, not measured process peaks or mathematical execution limits. Final profiles bind5848007/3915431 bytes respectively. No native workspace, end-to-end performance or target-fit inference is made.

## Reproduction procedure

From the repository root, with fresh nonexistent output directories:

```text
uv run --locked python -B -m scripts.weil_whole_source_split inspect --profile retained-t081 --output-dir <fresh-reference-directory>
uv run --locked python -B -m scripts.weil_whole_source_split inspect --profile selected-t1 --output-dir <fresh-target-directory>
uv run --locked --extra test python -m pytest -n 0 -q tests/test_whole_source_contract.py
```

The exact canonical profile manifest may be supplied with --input-manifest; another profile's manifest is rejected even if it is itself reviewed. A library caller may bind an identically laid-out relocated evidence root, with every original identity still checked.

The isolated commands actually exercised both profiles under Python3.14 and3.12:

```text
python -I -S -B computations/2026-10-29T175545Z-whole-source-profile-binding/inspect-stdlib-v1.py inspect --profile retained-t081 --output-dir <fresh-isolated-reference>
python -I -S -B computations/2026-10-29T175545Z-whole-source-profile-binding/inspect-stdlib-v1.py inspect --profile selected-t1 --output-dir <fresh-isolated-target>
```

Use each recorded interpreter to reproduce its corresponding runtime. Site packages are disabled and an import hook rejects everything except the four delivered modules and Python's standard library. Both profiles print STDLIB_ONLY_INSPECTION_CONFIRMED. Problem/collection IDs agree exactly between the two interpreters. This does not qualify any FLINT arithmetic on Python3.12 or any other operating system.

Outputs are problem.json, inspection-plan.json and inspection.json published last from exclusive, flushed temporary files. Exact rational values use canonical signed-hex numerator/positive-denominator records. A binding failure retains failure.json when writable and returns exit2; an existing output directory, including an empty one, is refused without changes. Metadata publication is not a scientific checkpoint/resume protocol or a power-loss durability claim.

## Actual output and controls

- Both final real profiles pass inspection with explicit metadata-only scope and all native-verification/matrix/positivity/production/execution-authorization flags false. Outputs are under [final reference](data/final-retained-t081/inspection.json) and [final target](data/final-selected-t1/inspection.json).
- The focused final suite passes67/67, no errors/skips, in93.33s on the recorded run. [Raw JUnit](data/contract-tests-v2.xml) and [parsed result](data/test-summary-v1.json) are retained. These are behavioral regressions, not67 independent mathematical proofs.
- Controls cover altered exact scalars, prime bases, coefficients, series/activation bounds, goals/precision/weights; stale code/audit/input bytes and false historical proof metadata; immutable values; relocated input trees; head/low/parity/triangle/ragged requests; explicit roles; partition/code identity; no-site-packages execution; file-sync failure without a final success receipt; failure retention and no-overwrite behavior.
- A real CLI request using the wrong reviewed manifest returns2 and retains [failure.json](data/rejected-manifest/failure.json), without inspection.json. A real attempted overwrite returns2 and every previously successful output byte remains unchanged. Actual argv/stderr are retained.
- A separate read-only source review reports no actionable findings within the metadata scope. It did not run mathematical code and is not analytical acceptance.

## Preserved development versions

The initial normal locked inspections under data/retained-t081 and data/selected-t1 exited0; their exact runtime source is preserved under captured-code-v1. Those initial metadata descriptions are SUPERSEDED, not qualification authorities: exterior head-axis metadata was corrected from0 to1, task role became explicit, input-role provenance became visible, and metadata writes were made completion-safe against sync failures. No mathematical result or original source artifact changed.

The first integrated suite is preserved as [contract-tests-v1.xml](data/contract-tests-v1.xml), its stdout and captured-code-v2. It has67 passes/one failure. That failure was an incorrect standalone-test assumption that equal source/audit precision512 must itself be invalid. The generic policy permits ordered equal precisions; applying a different arithmetic policy to either closed profile remains rejected. The incorrect case was deleted, not replaced with a new arbitrary precision default and not used to tighten production behavior. Final source and corrected test bytes are retained under captured-code-v3. All earlier outputs/code/tests remain verbatim.

To reproduce an archived version, use an owned source-tree copy, install its captured files at their recorded relative paths, retain the bound original evidence files and execute the recorded argv with fresh outputs. Never install old source over the working tree or substitute a current passing run for the preserved version.

## Interpretation and limitations

This delivers a working exact metadata inspection interface and observable fail-closed behavior. It does not reconstruct analytical source entries, compute a witness/sign/coercivity bound, measure native resources or demonstrate complete target practicality. It does not implement scientific chunk publication, recovery, a numerical scheduler or arbitrary-support calculation. No such operation is exposed as a command.

C-0124 remains the retained source-conditional positivity result at T81/100 under its original premises. C-0126 remains scalar-only at T1. Production inventory8v1/0v2/1v3 and RH unresolved remain unchanged. Original records/programs/inputs/outputs are preserved. No commit or push is part of this computation.
