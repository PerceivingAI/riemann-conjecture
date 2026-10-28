# Test-count interpretation correction

- **Computation:** X-20261028-002
- **Created:** 2026-10-28T18:09:07Z
- **Status:** COMPLETE, metadata-only correction

The final pytest command printed93 passed and one skipped from94 collected tests. The retained [raw JUnit](data/execution-tests-v3.xml) contains94 unique testcase elements, one skipped, no errors and no failures. Its aggregate tests attribute says96. That aggregate does not match its own testcase elements.

The first [measurement summary](data/measured-summary-v1.json) incorrectly trusted the aggregate, deriving95 passed. The cause is the postprocessor's unchecked assumption that the aggregate equals the number of cases. The origin of pytest's inconsistent aggregate is not established and no pytest implementation change is claimed.

[Measurement summary v2](data/measured-summary-v2.json) counts the actual unique cases and preserves the aggregate attributes separately. The authoritative result is **93 passed, one skipped**. The computation record and maintained prose already state this observed result correctly. All timing/CPU/memory rows are unchanged.

The original summary, raw XML, [record](record.md), [manifest v1](manifest.json), code, mathematical source, complete analytical/exact results and nine controls remain byte-unchanged. [Manifest v2](manifest-v2.json) adds this correction and the new summary, retains the original manifest as a member, and selects v2 as the active measurement index. This is not another test run or a mathematical correction.
