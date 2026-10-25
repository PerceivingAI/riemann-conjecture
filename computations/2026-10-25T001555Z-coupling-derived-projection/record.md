# Retained-mode diagnosis and coupling-derived projection

- **Computation ID:** `X-20261025-001`
- **Created:** `2026-10-25T00:15:55Z`
- **Last updated:** `2026-10-25T00:32:20Z`
- **Status:** `COMPLETE`, projection20 selected with exact certificates on the original P16 compression only
- **Finding:** [F-20261025-001](../../findings/2026-10-25T001555Z-coupling-derived-projection.md)
- **Claim:** C-0090

## Objective and scope

Identify which coupled modes caused the C-0089 N16 reference failures and derive a projection choice from those accepted data. Do not guess a larger source dimension from scalar positivity or infer full enlarged-space positivity from two trial directions.

The executed selector tests the entire known P16 subspace while changing its tail projection L and reference weights. Its first even projection with exact lower certificates for both8-dimensional old-subspace parity blocks is L20. New low directions16..19 and their combined couplings are not certified by this computation. No full P20 source assessment, new support or theorem admission is claimed.

## Commit and environment

Before this investigation, the completed C-0088/C-0089 public work was committed locally as `ed6946669b459c261f7670a849d4cb3240ecfc48`, main. All161 staged public blobs were checked byte-identical to working files; private documents were excluded. No push was performed. This new investigation's additive code and results were uncommitted during execution and are not a clean-production proof artifact.

`environment.json` records Python3.14, python-flint, NumPy, pytest, Windows platform and precision. The source consequence uses352-bit outward rational intervals; the independent evaluator uses the previously accepted narrower512-bit receipt intervals with Arb1536. Exact rational congruences establish the positive old-subspace lower. Floating linear algebra only proposes witnesses.

No fresh analytical matrix or head arrays were generated. Input integrity and the prior exact result are rechecked, then consequences are computed from retained source/receipt arrays. One owned command executes at a time on the local PC; no GPU, WSL, external compute or new dependency was used.

## Inputs and faithful versions

The four pinned inputs are from [X-20261024-006](../2026-10-24T231555Z-tail-complement-weighted-reference/record.md), all at T=1353/2048,K38,n0=16,m54:

- Source SHA256 `8c7626b05e5f686155eca520d05c9908f829f3c78fbfe3cea900cd22b63da8af`.
- Independent receipt SHA256 `563f7ad158e7362d5417166c01b9a63e4289378961cc70c85f885c7c0d477335`.
- Original result SHA256 `ce6f31d8393452ee5d55b1c8e12049d8090b60556d1ab4c689d788a4d9c521d9`.
- Pinned C-0088 scalar file SHA256 `65cc22df9e5edfbaebd9b183edbc29b179c7d3474731e24170cc9abc543a0b9a`.

The older C-0087 baseline selection is also copied because the immutable original reference loader uses it to bind the original scalar selection. All five exact input copies and their original repository-relative paths are bound in `inputs/manifest.json`. `source-v1/manifest.json` binds24 captured source/environment files. Historical source, tests, packets and their seals are not edited.

The new source and independent auditor are `scripts.weil_coupling_projection` and `scripts.verify_coupling_projection`. Their fingerprint maps bind the relevant prior scientific helpers as well. The provisional pre-evaluation derivation is preserved exactly in `derivation-v1.md`.

## Projection mathematics

The original complete Gram is G16=(Q16 W_K P16)*(Q16 W_K P16). For ordinary combined signed head rows t_k, physical inverse tail mass is1/d_k=(2k+1)/2. Promoting modes16..L-1 changes the Gram by

\[
G_L^{(16)}=G16-\sum_{16\le k<L}t_k^*t_k/d_k.
\]

The complete weighted majorant is

\[
U_{L,54}=w_{54,L}G16-w_{54,L}\sum_{16\le k<L}t_k^*t_k/d_k
+\sum_{L\le k<54}(w_{k,L}-w_{54,L})t_k^*t_k/d_k.
\]

Unknown k>=54 energy is still paid; deleting a head row without the negative Gram-prefix subtraction is wrong. The changed reference uses the certified C-0088 mu_L and w_(k,L)=1/(mu_L+H_k-H_L). Keeping H16 instead of H_L would also be wrong. The full b-based residual allowance is retained with the new mu, and ordinary low-space masses remain d_j=2/(2j+1), j<16.

The source computes signed integer-interval rank updates. The independent auditor instead subtracts the prefix from the narrower native Gram, then adds nonnegative weighted corrections with Arb1536. It checks every source U triangle by containment and verifies exact congruences on the source lower matrices. It independently reconstructs exact residual coefficients, scalar complements, signed modal amplitudes and all full-source directional errors.

## Mode attribution

Mode16 alone forces the original even reference failure; mode17 alone forces the odd failure. The full-source reverse-triangle error is paid in those prefix conclusions.

The even mode16 weighted energy is about3.071139864 against low-form upper1.950032883. Its V/P self charges are0.974675956/0.585502862 and constructive cross charge1.510861425. The odd mode17 weighted energy is1.832913796 against1.348318535, with self charges0.616891305/0.323082167 and constructive cross0.892875310. Values are displays of retained interval bounds, on the original nearly unit-mass rational trials, not new eigenvalues.

P is the combined arithmetic source, so these data do not isolate one prime. Later mixed charges have both signs: mode18 has V/P cross about-0.125112217; mode19 about-0.052678053. All76 mode rows include ordinary V/P/RK amplitudes, three self terms, all signed doubled cross terms, physical unweighted energy and original inverse-weighted energy. The full R_T-R_K remainder is retained in every sign conclusion.

The five largest original weighted charges are at even modes16,26,18,34,24 and odd modes17,19,21,27,23. Ranking is deterministic by certified lower endpoint then mode index; it is not a proposal for a noncontiguous basis. The selected projection is an ordinary contiguous Legendre projection.

## Projection result

The source evaluates consecutive even projections16,18,20 and stops at the first complete known-subspace certificate.

- L16: both retained trials have genuine negative reference uppers, reproducing C-0089's obstruction.
- L18: the two recorded trials now have strictly positive full-reference lowers, displaying1.431789118 even and1.009342963 odd. The whole P16 lower remains uncertified. This is not proof that L18 is impossible.
- L20: both8-dimensional known-subspace lower blocks have exact positive congruence witnesses. Conservative mass-normalized lower displays are1.2043113561921998e-9 even and5.752414055738578e-8 odd. These are not full spectral minima.

The selected projection is therefore20 under this declared certificate rule. It promotes16,17,18,19 and resolves the entire original low-space obstruction with the available data, not merely the two stored trials. It does not prove all P20 reference directions positive.

The exact reference lower displays are mu16=0.25554921158237676, mu18=0.36997194134349726 and mu20=0.4726350157991974. The corresponding H_L subtraction is always applied. Since lambda_(k,L)=H_k-cT_upper-p_upper-rho_L_upper, the H_L increase does not produce an artificial uniform increase in all surviving denominators.

## Reproduction and outputs

Run from repository root with locked dependencies and fresh output names in an existing directory:

```text
uv run --locked python -m scripts.weil_coupling_projection analyze --output computations/<fresh-bundle>/data/projection.json
uv run --locked python -m scripts.verify_coupling_projection computations/<fresh-bundle>/data/projection.json --output computations/<fresh-bundle>/data/audit.json
uv run --locked python -m scripts.weil_coupling_projection replay --result computations/<fresh-bundle>/data/projection.json --output computations/<fresh-bundle>/data/replay.json
uv run --locked --extra test python -m pytest -n 0 -q tests/test_coupling_projection.py
```

Actual mathematical CLI launches used the locked environment's Python executable. Exact invocations, times, stdout/stderr and exit codes are in `data/*.run.json` and matching logs.

- `data/projection-v1.json`, SHA256 `74f8cc2e4e62af60392a1a15b02902c8ab461620f778bbd3aa657e4c78357587`.
- `data/projection-audit-v1.json`, SHA256 `7010026f00aa906a02cf3dddf6b69c34fe266865b1178bf10ee0f032eaf87d4c`.
- `data/projection-replay-v1.json`, SHA256 `193c715b38b49fe53c3d97004b1e87055ffe2d17ffb87e31391b7141448dc217`.
- `data/result-summary.json` retains selected mode details, all candidate classifications, original-trial brackets and exact gap values.

For isolated historical replay:

```text
uv run --locked python computations/2026-10-25T001555Z-coupling-derived-projection/replay-archived-v1.py --output-dir computations/<fresh-replay-directory>
```

The launcher verifies and restores24 source/environment files and5 inputs into an isolated tree, checks loaded project scripts originate there, recomputes the exact consequence using stored witnesses and independently audits the original report. The exact replay receipt is byte-identical; every independent receipt field matches except elapsed time. It uses installed locked dependencies, not a new environment provisioner.

## Executed verification

All source, independent audit, exact replay and isolated replay commands exit0. The independent evaluator checks76 mode rows and408 U entries across three projections, plus scalar identities, complements, complete-tail/directional bounds, both witnesses and first-certified selection. It consumes the retained native512 inputs rather than rerunning analytical source generation.

Both permanent finite-operator controls pass in0.44 seconds. They distinguish correct physical masses and H_L rebasing, promoted-prefix subtraction, signed off-diagonal coupling and complete unknown-tail payment. Their expected energies come from explicit finite operators, not copies of the implementation's formula.

Five actual altered-report controls exit2 without success outputs: dropped constructive cross, unpaid infinite tail, altered positive margin, uncertified projection18 selection and falsely expanded known dimension20. Their bytes and launch receipts are preserved; outcomes are in `data/rejection-summary.json`.

Observed outer-process times are source0.659580 s, independent audit0.570280 s, exact replay0.490968 s and isolated replay1.899643 s. These are retained-data consequence costs, not fresh full-source or whole-P20 proof times. No broad Python suite, Rust or Lean check was run or claimed.

A separate agent qualified the projection algebra and implemented the independently organized auditor. It did not run numerical jobs, builds or tests. Its final response is captured in `independent-review.json`; source and mathematical derivation make the scope independently readable.

## Interpretation and preservation

The selected N20 is coupling-informed: the first omitted modes and their constructive signed correlations explain the recorded failures, the two trials are cured at18, and whole-known-space lower witnesses first appear at20 under this fixed-data rule. The unresolved new low block is stated explicitly. No full P20 positivity, optimal dimension, new support, method-wide success/failure, production admission, literature priority or RH claim follows.

All original research code, tests and bundles remain byte-identical; current public maintained records add factual results without rewriting older entries. The bundle seal binds exact inputs, source, initial derivation, outputs, failed controls and executable reproduction. Admissions remain8v1/0v2/1v3. RH remains unresolved. No push was performed.
