"""Exact profile binding, logical domains, and metadata-only inspection controls."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import hashlib
from itertools import islice
import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.whole_source.contract import (
    ArithmeticPolicy, ArtifactRef, ContractError, GateReceipt, ModeRange,
    PartitionSpec, QuantityKey, SELECTED_T1_METADATA_PROFILE, TaskKey, bind_problem,
    canonical_bytes, collection_id, expected_domain, inspection_plan, problem_id,
    validate_plan, validate_problem, validate_task,
)
from scripts import weil_whole_source_split as cli

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PARAMETERS = {
    "retained-t081": (Fraction(81, 100), 826, 1652, 86, 710, 1420,
                       Fraction(821, 512), 4608, 6144, "supported_form"),
    SELECTED_T1_METADATA_PROFILE: (Fraction(1), 5564, 11128, 132, 4060, 8120,
                                   Fraction(2981, 1024), 25600, 34304,
                                   "direct_whole_line_multiplier"),
}
FALSE_CLAIMS = (
    "native_verification_executed", "matrix_computed", "positivity_proved",
    "production_admission", "execution_authorized",
)


@pytest.fixture(scope="module", params=tuple(PROFILE_PARAMETERS))
def spec(request):
    return bind_problem(request.param)


def copy_evidence(spec, root):
    for ref in spec.evidence:
        target = root / ref.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / ref.path).read_bytes())
    return root


def manifest_for(spec):
    return spec.input_manifest.path


def task_for(spec, plan, name, parity):
    key = QuantityKey(name, parity)
    domain = expected_domain(spec, key)
    return TaskKey(problem_id(spec), collection_id(spec, plan), key,
                   domain.rows, domain.columns, role="producer")


def assert_metadata_only(document):
    assert document["scope"] == "PROFILE_METADATA_ONLY"
    for claim in FALSE_CLAIMS:
        assert document[claim] is False


def test_reviewed_profiles_have_exact_physical_and_arithmetic_parameters(spec):
    support, n, m, k, r, rc, beta, source_bits, audit_bits, kind = PROFILE_PARAMETERS[spec.profile]
    assert (spec.support, spec.N, spec.M, spec.K, spec.R, spec.Rc) == (support, n, m, k, r, rc)
    assert (spec.alpha, spec.beta, spec.m, spec.eta) == (
        Fraction(1, 4), beta, Fraction(1, 3), 1 - Fraction(1, 2**128))
    assert spec.reference_kind == kind
    assert (spec.arithmetic.source_bits, spec.arithmetic.audit_bits) == (source_bits, audit_bits)
    assert [(term.m, term.prime, term.exponent) for term in spec.active_terms] == (
        [(2, 2, 1), (3, 3, 1), (4, 2, 2), (5, 5, 1)]
        + ([(7, 7, 1)] if spec.profile != "retained-t081" else []))
    prime_four = spec.active_terms[2]
    assert 0 < prime_four.coefficient_lower <= prime_four.coefficient_upper
    assert len(spec.kernel_coefficients) == k + 1
    assert spec.kernel_coefficients[:3] == (
        7 * support / 4, support**2 / 48, 9 * support**3 / 32)
    assert spec.activation_lower < 2 * support < min(spec.next_activation_upper, spec.pi_lower)
    assert spec.numerical_goal == spec.model_accuracy / 4
    assert 0 < spec.model_error <= spec.model_accuracy
    assert spec.source_gauss_order == 3 * n // 2
    assert spec.audit_square_gauss_order == n
    assert spec.frequency_edges[:2] == (Fraction(0), Fraction(r))
    assert spec.frequency_edges[-1] == 32 * r
    assert all(b == a * Fraction(17, 16)
               for a, b in zip(spec.frequency_edges[1:-2], spec.frequency_edges[2:-1]))
    assert spec.frequency_edges[-2] * Fraction(17, 16) >= spec.frequency_edges[-1]
    assert len(spec.inverse_weights) == len(spec.frequency_edges)
    assert spec.inverse_weights[0] == 3
    assert all(a >= b > 0 for a, b in zip(spec.inverse_weights, spec.inverse_weights[1:]))
    if spec.profile != "retained-t081":
        assert spec.numerical_goal == Fraction(1, 2**80)
        assert spec.numerical_goal_origin == "explicit-inspection-policy-not-historical-field"
    else:
        assert spec.numerical_goal_origin == "original-reviewed-declaration"


def test_canonical_serialization_is_exact_detached_and_non_proving(spec):
    document = spec.to_dict()
    assert_metadata_only(document)
    parameters = document["parameters"]
    assert parameters["support"] == {
        "numerator": hex(spec.support.numerator), "denominator": hex(spec.support.denominator)}
    assert parameters["eta"] == {"numerator": hex(2**128 - 1), "denominator": hex(2**128)}
    assert "_snapshots" not in parameters
    assert document["basis"] == "ordinary-Legendre"
    assert document["physical_mass"] == "2/(2*n+1)"
    raw = canonical_bytes(document)
    assert raw.endswith(b"\n")
    assert json.loads(raw) == document
    assert raw == (json.dumps(document, sort_keys=True, separators=(",", ":"),
                              ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")
    parameters["kernel_coefficients"][0]["numerator"] = "0x0"
    assert spec.to_dict()["parameters"]["kernel_coefficients"][0]["numerator"] != "0x0"
    with pytest.raises(FrozenInstanceError):
        spec.N = 1
    with pytest.raises(FrozenInstanceError):
        spec.arithmetic.source_bits = 1
    with pytest.raises(FrozenInstanceError):
        spec.active_terms[2].prime = 4
    receipt = GateReceipt(problem_id(spec), collection_id(spec, inspection_plan(spec)))
    assert_metadata_only(receipt.to_dict())
    with pytest.raises(TypeError):
        replace(receipt, positivity_proved=True)


@pytest.mark.parametrize("field", [
    "active_terms", "kernel_coefficients", "frequency_edges", "inverse_weights", "evidence",
])
def test_mutable_sequences_cannot_enter_bound_problem(spec, field):
    changed = replace(spec, **{field: list(getattr(spec, field))})
    with pytest.raises(ContractError):
        validate_problem(changed)


def test_every_bound_scalar_and_derived_arithmetic_change_is_rejected(spec):
    mutations = {
        field: value + 1 if type(value) is int else value + Fraction(1, 2**160)
        for field in ("support", "N", "M", "K", "R", "Rc", "alpha", "beta", "m", "eta",
                      "delta", "b_K", "model_error", "model_accuracy", "numerical_goal", "kappa",
                      "pi_lower", "activation_lower", "next_activation_upper",
                      "source_gauss_order", "audit_square_gauss_order")
        for value in [getattr(spec, field)]
    }
    mutations.update(
        reference_kind="different-reference",
        numerical_goal_origin="historical-proof",
        arithmetic=replace(spec.arithmetic, source_bits=spec.arithmetic.source_bits + 1),
        kernel_coefficients=(spec.kernel_coefficients[0] + 1,) + spec.kernel_coefficients[1:],
        frequency_edges=spec.frequency_edges[:-1] + (spec.frequency_edges[-1] + 1,),
        inverse_weights=spec.inverse_weights[:-1] + (spec.inverse_weights[-1] / 2,),
    )
    for field, value in mutations.items():
        with pytest.raises(ContractError):
            validate_problem(replace(spec, **{field: value}))
    for field, value in (("prime", 4), ("exponent", 1), ("m", 8),
                         ("coefficient_lower", spec.active_terms[2].coefficient_lower / 2)):
        terms = list(spec.active_terms)
        terms[2] = replace(terms[2], **{field: value})
        with pytest.raises(ContractError):
            problem_id(replace(spec, active_terms=tuple(terms)))


def test_relocated_evidence_preserves_identity_and_explicit_manifest_binding(spec, tmp_path):
    root = copy_evidence(spec, tmp_path / "relocated")
    relative = Path(manifest_for(spec))
    relocated = bind_problem(spec.profile, relative, root=root)
    assert relocated.to_dict() == spec.to_dict()
    assert problem_id(relocated) == problem_id(spec)
    assert bind_problem(spec.profile, root / relative, root=root).evidence == spec.evidence
    with pytest.raises(ContractError):
        bind_problem(spec.profile, root / "manifest.json", root=root)


@pytest.mark.parametrize("target", ["manifest", "source", "audit", "code", "dependency"])
def test_changed_evidence_and_historical_code_are_rejected(spec, tmp_path, target):
    root = copy_evidence(spec, tmp_path / "evidence")
    manifest = manifest_for(spec)
    bundle = manifest.rsplit("/", 1)[0] + "/"
    if target == "manifest":
        relative = manifest
    elif target == "source":
        relative = spec.to_dict()["input_artifacts"]["source"]["path"]
    elif target == "audit":
        relative = spec.to_dict()["input_artifacts"]["audit"]["path"]
    elif target == "code":
        relative = next(ref.path for ref in spec.evidence
                        if ref.path.startswith(bundle) and ref.path.endswith(".py"))
    else:
        relative = next(ref.path for ref in spec.evidence if not ref.path.startswith(bundle))
    path = root / relative
    raw = path.read_bytes()
    path.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
    with pytest.raises(ContractError):
        bind_problem(spec.profile, root=root)


def test_false_historical_proof_metadata_cannot_be_rebound(spec, tmp_path):
    root = copy_evidence(spec, tmp_path / "evidence")
    audit = root / spec.to_dict()["input_artifacts"]["audit"]["path"]
    document = json.loads(audit.read_bytes())
    document["target_positivity_proved"] = True
    document["production_admission"] = True
    audit.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ContractError):
        bind_problem(spec.profile, root=root)


def test_supported_profiles_cannot_share_a_manifest_or_inspection_plan():
    retained = bind_problem("retained-t081")
    successor = bind_problem(SELECTED_T1_METADATA_PROFILE)
    assert problem_id(successor) != problem_id(retained)
    assert collection_id(successor, inspection_plan(successor)) != collection_id(retained, inspection_plan(retained))
    with pytest.raises(ContractError, match="wrong input manifest for profile"):
        bind_problem(successor.profile, retained.input_manifest.path)
    with pytest.raises(ContractError):
        collection_id(successor, inspection_plan(retained))


@pytest.mark.parametrize("role", ["cost_inputs", "cost_source", "cost_audit", "comparison_manifest", "qualification"])
def test_successor_binds_comparison_and_qualification_bytes(role, tmp_path):
    spec = bind_problem(SELECTED_T1_METADATA_PROFILE)
    root = copy_evidence(spec, tmp_path)
    path = spec.to_dict()["input_artifacts"][role]["path"]
    (root / path).write_bytes((root / path).read_bytes() + b"\n")
    with pytest.raises(ContractError, match="artifact fingerprint mismatch"):
        bind_problem(spec.profile, root=root)


def test_successor_capture_excludes_diagnostic_and_legacy_t1_files(tmp_path):
    spec = bind_problem(SELECTED_T1_METADATA_PROFILE)
    root = copy_evidence(spec, tmp_path)
    for ref in spec.evidence:
        assert not any(fragment in ref.path for fragment in (
            "/diagnostics/", "measured-summary", "t1-reference-cost-qualification", "t1-direct-reference/"))
    assert bind_problem(spec.profile, root=root).to_dict() == spec.to_dict()


def test_retained_t081_scientific_binding_does_not_read_observational_inventory(tmp_path):
    spec = bind_problem("retained-t081")
    root = copy_evidence(spec, tmp_path)
    bundle = (root / spec.input_manifest.path).parent
    for relative in ("manifest.json", "data/isolated-replay-v1.json", "data/reference-source-v1-receipt.json"):
        path = bundle / relative
        assert not path.exists()
        path.write_bytes(b'corrected observational report\n')
    assert problem_id(bind_problem(spec.profile, root=root)) == problem_id(spec)
    with pytest.raises(ContractError, match="wrong input manifest"):
        bind_problem(spec.profile, bundle / "manifest.json", root=root)


@pytest.mark.parametrize("parity", [0, 1])
def test_domains_separate_low_head_and_finite_cross_band(spec, parity):
    low = ModeRange(parity, spec.N)
    head = ModeRange(spec.N + parity, spec.M)
    for name in ("A_model", "weighted_head", "weighted_complete_tail", "F_L", "J_F"):
        domain = expected_domain(spec, QuantityKey(name, parity))
        assert (domain.rows, domain.columns) == (low, low)
        assert domain.symmetric_upper is True
        assert domain.head_inner_axes == {"weighted_head": 2, "weighted_complete_tail": 1}.get(name, 0)
        assert domain.entries == (spec.N // 2) * (spec.N // 2 + 1) // 2
        assert list(islice(domain.coordinates(), 3)) == [
            (parity, parity), (parity, parity + 2), (parity, parity + 4)]
    high = expected_domain(spec, QuantityKey("K_H", parity))
    assert (high.rows, high.columns, high.symmetric_upper) == (head, head, True)
    coupling = expected_domain(spec, QuantityKey("F_H", parity))
    assert (coupling.rows, coupling.columns, coupling.symmetric_upper) == (head, low, False)
    assert coupling.entries == (spec.N // 2)**2
    assert next(coupling.coordinates()) == (spec.N + parity, parity)
    band = expected_domain(spec, QuantityKey("R_H", parity))
    assert (band.rows, band.columns) == (
        ModeRange(spec.N + parity, spec.N + spec.K), ModeRange(spec.N - spec.K + parity, spec.N))
    coordinates = list(band.coordinates())
    assert len(coordinates) == band.entries == (spec.K // 2)**2
    assert coordinates[0] == (spec.N + parity, spec.N - spec.K + parity)
    assert coordinates[-1] == (spec.N + spec.K - 2 + parity, spec.N - 2 + parity)
    assert all(row >= spec.N > column and row % 2 == column % 2 == parity
               for row, column in coordinates)


def test_problem_and_collection_identities_have_distinct_context(spec):
    plan = inspection_plan(spec)
    pid = problem_id(spec)
    cid = collection_id(spec, plan)
    assert plan.problem_sha256 == pid
    assert plan.arithmetic == spec.arithmetic
    for field in ("row_block", "column_block", "inner_block"):
        partition = replace(plan.partition, **{field: getattr(plan.partition, field) - 1})
        alternative = inspection_plan(spec, partition)
        assert alternative.problem_sha256 == pid
        assert collection_id(spec, alternative) != cid
    invalid_plans = (
        replace(plan, problem_sha256="0" * 64),
        replace(plan, arithmetic=replace(plan.arithmetic, source_bits=plan.arithmetic.source_bits + 1)),
        replace(plan, partition=PartitionSpec(spec.M + 1, 1, 1)),
        replace(plan, implementation=list(plan.implementation)),
        replace(plan, implementation=(replace(plan.implementation[0], sha256="0" * 64),)
                + plan.implementation[1:]),
        replace(plan, scope="EXECUTION_AUTHORIZED"),
    )
    for invalid in invalid_plans:
        with pytest.raises(ContractError):
            validate_plan(spec, invalid)
    assert problem_id(spec) == pid


@pytest.mark.parametrize("parity", [0, 1])
def test_complete_and_ragged_output_tiles_obey_physical_parity_and_triangle(spec, parity):
    plan = inspection_plan(spec, PartitionSpec(7, 11, 13))
    for name in ("A_model", "weighted_head", "weighted_complete_tail", "F_L", "F_H", "J_F", "K_H", "R_H"):
        task = task_for(spec, plan, name, parity)
        assert validate_task(spec, plan, task) is None
        ragged = replace(task, rows=ModeRange(task.rows.stop - 2 + parity, task.rows.stop),
                         columns=ModeRange(task.columns.stop - 2 + parity, task.columns.stop))
        assert validate_task(spec, plan, ragged) is None
        invalid = (
            replace(task, problem_sha256="0" * 64),
            replace(task, collection_sha256="0" * 64),
            replace(task, rows=ModeRange(task.rows.start + 1, task.rows.stop)),
            replace(task, columns=ModeRange(task.columns.start, task.columns.stop + 2)),
            replace(task, rows=ModeRange(task.rows.start, task.rows.start + 3)),
        )
        for candidate in invalid:
            with pytest.raises(ContractError):
                validate_task(spec, plan, candidate)
    high = task_for(spec, plan, "F_H", parity)
    with pytest.raises(ContractError):
        validate_task(spec, plan, replace(high, rows=ModeRange(parity, spec.N)))
    symmetric = task_for(spec, plan, "A_model", parity)
    with pytest.raises(ContractError):
        validate_task(spec, plan, replace(symmetric,
            rows=ModeRange(spec.N - 2 + parity, spec.N), columns=ModeRange(parity, parity + 2)))


def test_task_roles_are_explicit_distinct_request_metadata(spec):
    plan = inspection_plan(spec)
    producer = task_for(spec, plan, "weighted_complete_tail", 0)
    requests = [replace(producer, role=role) for role in ("producer", "analytic", "exact")]
    assert len(set(requests)) == 3
    encoded = []
    for request in requests:
        assert validate_task(spec, plan, request) is None
        document = json.loads(canonical_bytes(request))
        assert document["role"] == request.role
        assert document["problem_sha256"] == producer.problem_sha256
        assert document["collection_sha256"] == producer.collection_sha256
        assert document["rows"] == {"start": 0, "stop": spec.N, "step": 2}
        encoded.append(canonical_bytes(request))
    assert len(set(encoded)) == 3
    for role in ("", "computed", "PRODUCER", True, False, None, 0):
        with pytest.raises(ContractError):
            validate_task(spec, plan, replace(producer, role=role))
    with pytest.raises(TypeError):
        TaskKey(producer.problem_sha256, producer.collection_sha256,
                producer.quantity, producer.rows, producer.columns)
    with pytest.raises(TypeError):
        TaskKey(producer.problem_sha256, producer.collection_sha256,
                producer.quantity, producer.rows, producer.columns, "producer")


@pytest.mark.parametrize("factory,args", [
    (ModeRange, (0, 0)), (ModeRange, (0, 8, 1)), (ModeRange, (True, 8)),
    (QuantityKey, ("computed_chunk", 0)), (QuantityKey, ("A_model", True)),
    (QuantityKey, ("A_model", 2)), (PartitionSpec, (0, 1, 1)),
    (ArithmeticPolicy, (2048, 1024)),
    (ArtifactRef, ("../outside", "0" * 64, 1)),
])
def test_invalid_contract_values_are_rejected(factory, args):
    with pytest.raises(ContractError):
        factory(*args)


def test_fresh_inspection_writes_bound_documents_and_non_proving_receipt(spec, tmp_path):
    output = tmp_path / "inspection"
    report = cli.inspect_profile(spec.profile, output)
    assert {path.name for path in output.iterdir()} == {
        "problem.json", "inspection-plan.json", "inspection.json"}
    assert json.loads((output / "inspection.json").read_bytes()) == report
    assert_metadata_only(report)
    assert (report["support"], report["N"], report["M"], report["K"]) == (
        str(spec.support), spec.N, spec.M, spec.K)
    assert report["problem_id"] == problem_id(spec)
    assert report["collection_id"] == collection_id(spec, inspection_plan(spec))
    assert report["evidence_files"] == len(spec.evidence)
    assert report["bound_bytes"] == sum(ref.size for ref in spec.evidence)
    for artifact in report["artifacts"]:
        raw = (output / artifact["path"]).read_bytes()
        assert len(raw) == artifact["size"]
        assert hashlib.sha256(raw).hexdigest() == artifact["sha256"]
    problem = json.loads((output / "problem.json").read_bytes())
    assert problem == dict(spec.to_dict(), problem_id=problem_id(spec))
    plan = json.loads((output / "inspection-plan.json").read_bytes())
    assert plan["execution_authorized"] is False
    assert len(plan["domains"]) == 12
    assert {domain["quantity"]["name"] for domain in plan["domains"]} == {
        "A_model", "weighted_head", "weighted_complete_tail", "F_H", "R_H", "K_H"}


def test_file_sync_failure_cannot_publish_success(spec, tmp_path, monkeypatch):
    output = tmp_path / "sync-failure"
    original = cli.os.fsync
    calls = 0

    def refuse_sync(handle):
        nonlocal calls
        calls += 1
        if calls == 3:
            raise OSError("owned sync refusal")
        return original(handle)

    monkeypatch.setattr(cli.os, "fsync", refuse_sync)
    with pytest.raises(OSError):
        cli.inspect_profile(spec.profile, output)
    assert not (output / "inspection.json").exists()
    failure = json.loads((output / "failure.json").read_bytes())
    assert failure["status"] == "PROFILE_BINDING_REJECTED"
    assert failure["execution_authorized"] is False


def test_bad_binding_retains_only_failure_and_existing_output_is_untouched(spec, tmp_path):
    output = tmp_path / "failure"
    with pytest.raises(ContractError):
        cli.inspect_profile(spec.profile, output, Path("wrong-manifest.json"))
    assert {path.name for path in output.iterdir()} == {"failure.json"}
    failure = json.loads((output / "failure.json").read_bytes())
    assert failure["status"] == "PROFILE_BINDING_REJECTED"
    assert failure["native_verification_executed"] is False
    assert failure["execution_authorized"] is False
    sentinel = output / "keep.bin"
    sentinel.write_bytes(b"untouched")
    before = {path.name: path.read_bytes() for path in output.iterdir()}
    with pytest.raises(FileExistsError):
        cli.inspect_profile(spec.profile, output)
    assert {path.name: path.read_bytes() for path in output.iterdir()} == before
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(FileExistsError):
        cli.inspect_profile(spec.profile, empty)
    assert list(empty.iterdir()) == []


def test_missing_profile_inventory_keeps_physical_root_out_of_failure(tmp_path):
    output = tmp_path / "inspection-failure"
    with pytest.raises(FileNotFoundError):
        cli.inspect_profile("retained-t081", output, root=tmp_path / "PRIVATE_PROFILE_INPUT_ROOT")
    raw = (output / "failure.json").read_bytes()
    error = json.loads(raw)["error"]
    assert error["type"] == "FileNotFoundError" and error["errno"] == 2
    assert b"PRIVATE_PROFILE_INPUT_ROOT" not in raw
    assert not (output / "inspection.json").exists()


def test_successful_inspection_cannot_be_resumed_or_overwritten(spec, tmp_path):
    output = tmp_path / "bound"
    cli.inspect_profile(spec.profile, output)
    before = {path.name: path.read_bytes() for path in output.iterdir()}
    with pytest.raises(FileExistsError):
        cli.inspect_profile(spec.profile, output)
    assert {path.name: path.read_bytes() for path in output.iterdir()} == before


@pytest.mark.parametrize("arguments", [[], ["compute"], ["run"], ["verify"],
    ["inspect", "--profile", "unknown", "--output-dir", "unused"]])
def test_cli_exposes_only_reviewed_profile_inspection(arguments, capsys):
    with pytest.raises(SystemExit) as caught:
        cli.main(arguments)
    assert caught.value.code == 2
    assert "error:" in capsys.readouterr().err


def test_cli_rejects_retired_profile_before_writing_output(tmp_path, capsys):
    output = tmp_path / "binding"
    with pytest.raises(SystemExit) as caught:
        cli.main(["inspect", "--profile", "selected-t1", "--output-dir", str(output)])
    assert caught.value.code == 2
    assert "invalid choice: 'selected-t1'" in capsys.readouterr().err
    assert not output.exists()


@pytest.mark.parametrize("profile", tuple(PROFILE_PARAMETERS))
def test_cli_inspection_runs_without_site_packages_or_numerical_imports(tmp_path, profile):
    output = tmp_path / "stdlib-only"
    program = """
import importlib.abc
import sys
sys.path.insert(0, sys.argv[1])
class StdlibOnly(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        allowed = {'scripts', 'scripts.whole_source', 'scripts.whole_source.contract',
                   'scripts.whole_source.admission', 'scripts.weil_whole_source_split'}
        if fullname not in allowed and fullname.split('.')[0] not in sys.stdlib_module_names:
            raise AssertionError('Non-stdlib import: ' + fullname)
sys.meta_path.insert(0, StdlibOnly())
from pathlib import Path
from scripts.weil_whole_source_split import inspect_profile
print(inspect_profile(sys.argv[3], Path(sys.argv[2]))['problem_id'])
"""
    result = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", program,
                             str(ROOT), str(output), profile], cwd=tmp_path,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    report = json.loads((output / "inspection.json").read_bytes())
    assert_metadata_only(report)
    assert report["profile"] == profile
    assert report["problem_id"] in result.stdout


def test_actual_implementation_bytes_change_collection_not_problem_identity(spec, tmp_path):
    plan = inspection_plan(spec)
    relocated = tmp_path / "implementation"
    for ref in plan.implementation:
        target = relocated / ref.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / ref.path).read_bytes())
    altered = relocated / "scripts/weil_whole_source_split.py"
    altered.write_bytes(altered.read_bytes() + b"\n")
    program = """
import json
import sys
sys.path.insert(0, sys.argv[1])
from scripts.whole_source.contract import bind_problem, inspection_plan, problem_id, collection_id
from pathlib import Path
spec = bind_problem(sys.argv[3], root=Path(sys.argv[2]))
print(json.dumps([problem_id(spec), collection_id(spec, inspection_plan(spec))]))
"""
    result = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", program,
                             str(relocated), str(ROOT), spec.profile], cwd=tmp_path,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    relocated_problem, relocated_collection = json.loads(result.stdout)
    assert relocated_problem == problem_id(spec)
    assert relocated_collection != collection_id(spec, plan)
