# Qualification outer-path capture correction

- **Created:** 2026-10-27T09:10:13Z
- **Scope:** capture installation only, no mathematical source or criterion change

The first retained replay stops before any mathematical subprocess can run its qualification. Its actual receipt is data/native-isolated-replay-v1.run.json. The outer qualification entrypoint reads qualification-inputs-v1.json in its bundle before invoking the nested immutable31-file replay. V1 had captured those bytes inside the nested captured-inputs-v1 layout but did not install an alias at the outer bundle path. This is the observed FileNotFoundError, not numerical failure or a negative mathematical result.

The first replay code, manifest and every captured byte remain unchanged. New replay-acceptance-v2.py creates captured-source-inputs-v2.json as an extension of the first manifest, recording its SHA256 and five required outer aliases. Those aliases reuse already captured bytes for the three input declarations and two contracts. No old source, input, helper, model parameter, precision, witness or result is refreshed. Expected target source/matrix/sign outputs remain outside the scientific execution tree.

The complete v2 run is required to execute the original scalar/reference qualification, fresh target source, separate native all-entry audit and zero-float sign, not merely pass an installation check. Its own temporary tree must be removed. The actual result is recorded separately; this correction note alone claims no successful replay or accepted theorem.
