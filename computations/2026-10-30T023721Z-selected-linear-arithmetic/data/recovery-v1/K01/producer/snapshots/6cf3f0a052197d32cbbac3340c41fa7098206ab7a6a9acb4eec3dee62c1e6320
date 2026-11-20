"""Bind reviewed scalar evidence without importing or executing numerical code.

A bound profile is metadata, not fresh analytical verification, a matrix result,
or permission to execute a calculation. Historical bytes are read unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from fractions import Fraction
import hashlib
import json
from math import factorial
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Iterator

ROOT = Path(__file__).resolve().parents[2]
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
MAX_FILES = 256
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_PROFILES = {
    "retained-t081": (
        "computations/2026-10-27T132236Z-t081-prime-five-qualification",
        "a1431dac564a4aafa0b2cba5f86ca28f95e12bb63f9b7aa331300a204f1d6da9",
        "data/target-declaration-source-v1.json",
        "data/target-declaration-audit-v1.json",
    ),
    "selected-t1": (
        "computations/2026-10-29T004611Z-t1-direct-reference",
        "a219367eb15c168b92aef9f32a5ecb43ea5e7e1539b9b847aa9bc5b6d3a5ebab",
        "data/source-v1.json", "data/audit-v1.json",
    ),
}
PROFILES = tuple(_PROFILES)
_QUANTITIES = ("A_model", "weighted_head", "weighted_complete_tail",
               "F_L", "F_H", "J_F", "K_H", "R_H")


class ContractError(ValueError):
    """The requested metadata does not match the closed research contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _integer(value: object, label: str, minimum: int = 0) -> int:
    _require(type(value) is int and minimum <= value <= 1_000_000,
             "invalid integer: " + label)
    return value


def _fraction(text: object) -> Fraction:
    _require(type(text) is str and 0 < len(text) <= 4096,
             "bounded canonical rational string required")
    try:
        value = Fraction(text)
    except (ValueError, ZeroDivisionError) as exc:
        raise ContractError("invalid exact rational") from exc
    _require(str(value) == text, "noncanonical exact rational")
    return value


def _reject_number(_: str) -> None:
    raise ContractError("nonexact JSON number")


def _unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        _require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def _load(raw: bytes) -> dict:
    try:
        result = json.loads(raw, object_pairs_hook=_unique,
                            parse_float=_reject_number, parse_constant=_reject_number)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ContractError("invalid exact JSON snapshot") from exc
    _require(type(result) is dict, "JSON object required")
    return result


def _relative(value: object) -> str:
    _require(type(value) is str and value and "\\" not in value and
             ":" not in value and "\0" not in value, "portable relative path required")
    path = PurePosixPath(value)
    _require(not path.is_absolute() and all(p not in ("", ".", "..")
             for p in value.split("/")), "unsafe relative path")
    return value


def _wire(value: object) -> object:
    if type(value) is Fraction:
        return {"numerator": hex(value.numerator), "denominator": hex(value.denominator)}
    if is_dataclass(value):
        return {f.name: _wire(getattr(value, f.name)) for f in fields(value)
                if not f.name.startswith("_")}
    if type(value) in (tuple, list):
        return [_wire(item) for item in value]
    if type(value) is dict:
        return {key: _wire(item) for key, item in value.items()}
    _require(value is None or type(value) in (str, int, bool), "unsupported contract value")
    return value


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(_wire(value), sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    path: str
    sha256: str
    size: int

    def __post_init__(self) -> None:
        _relative(self.path)
        _require(type(self.sha256) is str and _SHA.fullmatch(self.sha256), "invalid SHA256")
        _require(type(self.size) is int and 0 <= self.size <= MAX_FILE_BYTES,
                 "artifact exceeds byte cap")


@dataclass(frozen=True, slots=True)
class _Snapshot:
    role: str
    artifact: ArtifactRef
    raw: bytes = field(repr=False)


@dataclass(frozen=True, slots=True)
class ArithmeticTerm:
    m: int
    prime: int
    exponent: int
    coefficient_lower: Fraction
    coefficient_upper: Fraction


@dataclass(frozen=True, slots=True)
class ArithmeticPolicy:
    source_bits: int
    audit_bits: int
    publication_bits: int = 256
    checkpoint_bits: int = 512
    reduction_order: str = "canonical-domain-order-v1"

    def __post_init__(self) -> None:
        for name in ("source_bits", "audit_bits", "publication_bits", "checkpoint_bits"):
            _integer(getattr(self, name), name, 1)
        _require(self.audit_bits >= self.source_bits >= self.checkpoint_bits >
                 self.publication_bits, "invalid arithmetic precision ordering")
        _require(self.reduction_order == "canonical-domain-order-v1", "unsupported reduction order")


@dataclass(frozen=True, slots=True)
class ProblemSpec:
    profile: str
    support: Fraction
    N: int
    M: int
    K: int
    R: int
    Rc: int
    alpha: Fraction
    beta: Fraction
    m: Fraction
    eta: Fraction
    reference_kind: str
    active_terms: tuple[ArithmeticTerm, ...]
    kernel_coefficients: tuple[Fraction, ...]
    delta: Fraction
    b_K: Fraction
    model_error: Fraction
    model_accuracy: Fraction
    numerical_goal: Fraction
    numerical_goal_origin: str
    kappa: Fraction
    frequency_edges: tuple[Fraction, ...]
    inverse_weights: tuple[Fraction, ...]
    pi_lower: Fraction
    activation_lower: Fraction
    next_activation_upper: Fraction
    source_gauss_order: int
    audit_square_gauss_order: int
    arithmetic: ArithmeticPolicy
    evidence: tuple[ArtifactRef, ...]
    _snapshots: tuple[_Snapshot, ...] = field(repr=False)
    _validated_identity: str | None = field(default=None, init=False, repr=False, compare=False)

    def to_dict(self) -> dict:
        validate_problem(self)
        return _problem_document(self)

    @property
    def input_manifest(self) -> ArtifactRef:
        return next(snapshot.artifact for snapshot in self._snapshots if snapshot.role == "manifest")


def _problem_document(spec: ProblemSpec) -> dict:
    return {"format": "whole-source-split-problem-v1", "parameters": _wire(spec),
            "input_artifacts": _wire({s.role: s.artifact for s in spec._snapshots}),
            "basis": "ordinary-Legendre", "physical_mass": "2/(2*n+1)",
            "physical_scaling": "f(t)=T^(-1/2)*u(t/T)",
            "trust": "original reviewed scalar audits; shared source/form and FLINT/Arb/Gauss premises",
            "scope": "PROFILE_METADATA_ONLY", "native_verification_executed": False,
            "matrix_computed": False, "positivity_proved": False,
            "production_admission": False, "execution_authorized": False}


class _Reader:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.raw: dict[str, bytes] = {}
        self.refs: dict[str, ArtifactRef] = {}
        self.total = 0

    def read(self, ref: ArtifactRef) -> bytes:
        if ref.path in self.refs:
            _require(self.refs[ref.path] == ref, "conflicting artifact binding")
            return self.raw[ref.path]
        _require(len(self.refs) < MAX_FILES and self.total + ref.size <= MAX_TOTAL_BYTES,
                 "metadata closure exceeds aggregate cap")
        path = self.root
        for part in ref.path.split("/"):
            path = path / part
            info = path.lstat()
            _require(not path.is_symlink() and not getattr(info, "st_file_attributes", 0) & 0x400,
                     "reparse/symlink metadata path")
        _require(path.resolve().is_relative_to(self.root) and stat.S_ISREG(path.stat().st_mode),
                 "metadata path outside root or not a regular file")
        with path.open("rb") as handle:
            raw = handle.read(ref.size + 1)
        _require(len(raw) == ref.size and hashlib.sha256(raw).hexdigest() == ref.sha256,
                 "artifact fingerprint mismatch: " + ref.path)
        self.refs[ref.path] = ref
        self.raw[ref.path] = raw
        self.total += len(raw)
        return raw


def _member(path: str, row: dict) -> ArtifactRef:
    _require(type(row) is dict and type(row.get("sha256")) is str, "invalid artifact record")
    size = row.get("size", row.get("bytes"))
    _require(type(size) is int and 0 <= size <= MAX_FILE_BYTES, "invalid artifact byte count")
    return ArtifactRef(_relative(path), row["sha256"], size)


def _manifest_members(bundle: str, manifest: dict) -> dict[str, ArtifactRef]:
    _require(type(manifest.get("members")) is list and len(manifest["members"]) <= 256,
             "invalid manifest member inventory")
    result = {}
    for row in manifest["members"]:
        path = bundle + "/" + _relative(row.get("path"))
        _require(path not in result, "duplicate manifest member")
        result[path] = _member(path, row)
    return result


def _snapshot_names(profile: str) -> dict[str, str]:
    _, _, source, audit = _PROFILES[profile]
    names = {"source": source, "audit": audit, "capture": "captured-source-inputs-v1.json"}
    if profile == "retained-t081":
        names.update(reference="data/supported-reference-source-v1.json",
                     reference_audit="data/supported-reference-audit-v1.json",
                     pi="data/supported-reference-source-v1.json")
    else:
        names["pi"] = "captured-inputs-v1/computations/2026-10-27T050743Z-t080-target-qualification/data/reference-v1.json"
    return names


def _closure(profile: str, snapshots: tuple[_Snapshot, ...]) -> tuple[ArtifactRef, ...]:
    bundle, manifest_sha, source_name, audit_name = _PROFILES[profile]
    by_role = {s.role: s for s in snapshots}
    _require(len(by_role) == len(snapshots), "duplicate snapshot role")
    names = {"manifest": "manifest.json", **_snapshot_names(profile)}
    _require(set(by_role) == set(names) and all(
        by_role[role].artifact.path == bundle + "/" + name for role, name in names.items()),
        "incorrect scalar snapshot roles")
    manifest_snapshot = by_role["manifest"]
    _require(manifest_snapshot.artifact.path == bundle + "/manifest.json" and
             hashlib.sha256(manifest_snapshot.raw).hexdigest() == manifest_sha,
             "unreviewed profile manifest")
    members = _manifest_members(bundle, _load(manifest_snapshot.raw))
    refs = {manifest_snapshot.artifact.path: manifest_snapshot.artifact}
    for snap in snapshots:
        _require(type(snap.raw) is bytes and len(snap.raw) == snap.artifact.size and
                 hashlib.sha256(snap.raw).hexdigest() == snap.artifact.sha256,
                 "snapshot byte identity mismatch")
        if snap.role != "manifest":
            _require(members.get(snap.artifact.path) == snap.artifact,
                     "snapshot is not bound by reviewed manifest")
        refs[snap.artifact.path] = snap.artifact
    _require(by_role["source"].artifact.path == bundle + "/" + source_name and
             by_role["audit"].artifact.path == bundle + "/" + audit_name,
             "wrong declaration/audit role")
    capture = _load(by_role["capture"].raw)
    rows = capture["members"] if profile == "retained-t081" else capture["destinations"]
    _require(type(rows) is list and 0 < len(rows) <= 128, "invalid captured input inventory")
    for row in rows:
        project = _relative(row["project_path"] if profile == "retained-t081" else row["destination"])
        stored = bundle + "/" + _relative(row["captured_path"])
        for path in (project, stored):
            ref = _member(path, row)
            _require(path not in refs or refs[path] == ref, "conflicting captured dependency")
            if path == stored:
                _require(members.get(path) == ref, "capture not bound by reviewed manifest")
            refs[path] = ref
    for path, ref in members.items():
        if path.endswith(".py"):
            _require(path not in refs or refs[path] == ref, "conflicting code binding")
            refs[path] = ref
    return tuple(refs[path] for path in sorted(refs))


def _bounds(row: dict) -> tuple[Fraction, Fraction]:
    _require(type(row) is dict and set(row) == {"lower", "upper"}, "invalid scalar enclosure")
    lo, hi = _fraction(row["lower"]), _fraction(row["upper"])
    _require(lo <= hi, "reversed scalar enclosure")
    return lo, hi


def _fixed(row: dict, expected: dict) -> None:
    for name, value in expected.items():
        _require(type(row.get(name)) is type(value) and row[name] == value,
                 "incorrect retained field: " + name)


def _kernel(support: Fraction, order: int) -> tuple[Fraction, ...]:
    denominator = [Fraction(0)] + [Fraction((-1)**(j+1)*2**j, factorial(j))
                                    for j in range(1, order+3)]
    regular, result = [], []
    for n in range(order+1):
        rhs = Fraction(-1, 2)**(n+1)/factorial(n+1)-denominator[n+2]/2
        rhs -= sum((denominator[j]*regular[n+1-j] for j in range(2, n+2)), Fraction(0))
        quotient = rhs/denominator[1]
        regular.append(quotient)
        polar = Fraction(2, 2**n*factorial(n)) if n % 2 == 0 else Fraction(0)
        result.append(-support**(n+1)*(quotient-polar))
    return tuple(result)


def _normalize(profile: str, snapshots: tuple[_Snapshot, ...], evidence: tuple[ArtifactRef, ...]) -> ProblemSpec:
    docs = {s.role: _load(s.raw) for s in snapshots}
    source, audit = docs["source"], docs["audit"]
    bundle = _PROFILES[profile][0]
    _fixed(audit, {"status": "PASS", "production_admission": False,
                   "target_positivity_proved": False})
    _require(audit["source_sha256"] == next(s.artifact.sha256 for s in snapshots if s.role == "source"),
             "stale scalar audit source binding")
    producer_key = "consumer_sha256" if profile == "retained-t081" else "audit_code_sha256"
    verifier_name = "verify-target-declaration-v1.py" if profile == "retained-t081" else "verify-direct-v1.py"
    refs = {r.path: r.sha256 for r in evidence}
    _require(audit[producer_key] == refs[bundle + "/" + verifier_name], "stale scalar audit code binding")
    for doc in docs.values():
        modules = doc.get("imported_project_module_sha256", {})
        _require(type(modules) is dict, "invalid imported code inventory")
        for path, digest in modules.items():
            _require(refs.get(path) == digest, "missing/changed imported code: " + path)
    if profile == "retained-t081":
        reference = docs["reference"]
        _fixed(source, {"format": "t081-qualified-target-declaration-v1", "support": "81/100",
                       "status": "QUALIFIED_TARGET_PARAMETERS_NOT_POSITIVITY", "N": 826, "M": 1652,
                       "K": 86, "R": 710, "Rc": 1420, "production_admission": False,
                       "target_low_coupling_matrix_computed": False, "target_positivity_proved": False})
        _fixed(docs["reference_audit"], {"status": "PASS"})
        reference_sha = next(s.artifact.sha256 for s in snapshots if s.role == "reference")
        audit_sha = next(s.artifact.sha256 for s in snapshots if s.role == "reference_audit")
        _require(source["bindings"]["reference_source_sha256"] == reference_sha and
                 source["bindings"]["reference_audit_sha256"] == audit_sha and
                 docs["reference_audit"]["source_sha256"] == reference_sha,
                 "stale supported reference binding")
        _require(source["bindings"]["producer_sha256"] == refs[bundle + "/declare-target-v1.py"] and
                 source["bindings"]["inputs_sha256"] == refs[bundle + "/parameter-inputs-v1.json"],
                 "stale declaration code/input binding")
        terms = reference["active_terms"]
        kind = "supported_form"
        coefficients = source["kernel_coefficients"]
        delta, cross, model = (source[k] for k in ("complete_remainder_upper",
            "combined_model_cross_norm_upper", "complete_model_error_upper"))
        accuracy, goal = source["model_error_accuracy_goal"], source["precision"]["numerical_error_physical_norm_goal"]
        origin = "original-reviewed-declaration"
        kappa = source["weighted_physical_tail_inverse_upper"]
        edges, weights = source["frequency_edges"], source["inverse_weight_step_uppers"]
        bits = source["precision"]
        arithmetic = ArithmeticPolicy(bits["source_bits"], bits["independent_bits"])
        q_source = source["first_attempt"]["source_arithmetic_Gauss_order"]
        q_square = source["first_attempt"]["independent_combined_square_Gauss_order"]
        last_log = _bounds(reference["support_thresholds"]["log5"])[1]
        next_log = _bounds(reference["support_thresholds"]["log7"])[0]
        _fixed(source["finite_model_cross_band"], {"dimension": 86, "input_start": 740,
            "input_end": 825, "output_start": 826, "output_end": 911,
            "all_other_model_cross_entries_zero": True, "low_even_and_polar_terms_required": True})
        _fixed(audit, {"N": 826, "verifiedK": 86,
            "frequency_exterior_paid_by_terminal_Parseval_weight": True,
            "full_remainder_and_coefficient_checks": True})
        _require(audit["required_numerical_physical_width_goal"] == goal, "changed numerical goal")
    else:
        _fixed(source, {"format": "t1-direct-reference-source-v1", "support": "1",
            "status": "DIRECT_REFERENCE_AND_ERROR_QUALIFIED_NOT_POSITIVITY", "N": 5564,
            "M": 11128, "K": 132, "R": 4060, "Rc": 8120, "production_admission": False,
            "target_matrix_computed": False, "target_positivity_proved": False,
            "reference_kind": "direct_whole_line_multiplier"})
        _fixed(audit, {"N": 5564, "M": 11128, "K": 132, "R": 4060, "Rc": 8120,
            "complete_inverse_qualified": True, "terminal_infinity_step_checked": True,
            "high_mode_widths_achieved": False, "gauss_accuracy_achieved": False})
        _require(source["producer_sha256"] == refs[bundle + "/qualify-direct-v1.py"] and
                 source["inputs_sha256"] == refs[bundle + "/inputs-v1.json"] and
                 audit["inputs_sha256"] == source["inputs_sha256"], "stale direct code/input binding")
        terms, kind = source["active_terms"], source["reference_kind"]
        coefficients = source["residual"]["coefficients"]
        selected = [r for r in source["residual"]["ladder"] if type(r.get("K")) is int and r["K"] == source["K"]]
        _require(len(selected) == 1 and selected[0].get("passes") is True, "nonunique/unqualified residual order")
        row = selected[0]
        delta, cross, model = row["delta"]["upper"], row["cross"]["upper"], row["Lambda_upper"]
        accuracy, goal = source["residual"]["accuracy_goal"], str(Fraction(1, 1 << 80))
        origin = "explicit-inspection-policy-not-historical-field"
        kappa = source["reference"]["inverse"]["kappa_upper"]
        edges, weights = source["frequency"]["edges"], source["frequency"]["inverse_weight_step_uppers"]
        bits = source["precision"]
        arithmetic = ArithmeticPolicy(bits["source_bits"], bits["audit_bits"])
        q_source, q_square = bits["source_gauss_order"], bits["audit_square_gauss_order"]
        _require(audit["precision"] == bits, "inconsistent retained precision policies")
        c2 = _bounds(terms[0]["coefficient"]); c7 = _bounds(terms[-1]["coefficient"])
        # Exact consequences of retained c_p=log(p)/sqrt(p) enclosures.
        # sqrt(7)<8/3 and sqrt(2)>7/5; no new transcendental evaluation.
        last_log, next_log = c7[1]*Fraction(8, 3), 3*c2[0]*Fraction(7, 5)
    active = []
    expected_powers = ((2, 2, 1), (3, 3, 1), (4, 2, 2), (5, 5, 1))
    if profile == "selected-t1":
        expected_powers += ((7, 7, 1),)
    _require(type(terms) is list and len(terms) == len(expected_powers), "incomplete active powers")
    for term, (power, prime, exponent) in zip(terms, expected_powers, strict=True):
        _fixed(term, {"m": power, "prime": prime, "exponent": exponent})
        lo, hi = _bounds(term["coefficient"])
        _require(0 < lo <= hi, "nonpositive arithmetic coefficient")
        active.append(ArithmeticTerm(power, prime, exponent, lo, hi))
    support = _fraction(source["support"])
    pi_lower = _bounds(docs["pi"]["support_thresholds"]["pi"])[0]
    _require(last_log < 2*support < next_log and 2*support < pi_lower,
             "strict active-set/local-series premise failed")
    for key in ("N", "M", "K", "R", "Rc"):
        _integer(source[key], key, 1)
    _integer(q_source, "source Gauss order", 1); _integer(q_square, "audit square Gauss order", 1)
    _require(type(bits["matrix_publication_bits"]) is int and bits["matrix_publication_bits"] == 256,
             "changed publication precision")
    _fixed(source, {"alpha": "1/4", "m": "1/3", "eta": str(1-Fraction(1, 1 << 128)),
                   "beta": "821/512" if profile == "retained-t081" else "2981/1024"})
    parsed_coefficients = tuple(_fraction(x) for x in coefficients)
    _require(parsed_coefficients == _kernel(support, source["K"]), "incorrect complete residual coefficients")
    parsed_edges = tuple(_fraction(x) for x in edges)
    expected_edges = [Fraction(0), Fraction(source["R"])]
    while expected_edges[-1]*Fraction(17, 16) < 32*source["R"]:
        expected_edges.append(expected_edges[-1]*Fraction(17, 16))
    expected_edges.append(Fraction(32*source["R"]))
    _require(parsed_edges == tuple(expected_edges), "incomplete frequency partition")
    parsed_weights = tuple(_fraction(x) for x in weights)
    _require(len(parsed_weights) == len(parsed_edges) and parsed_weights[0] == 3 and
             all(a >= b > 0 for a, b in zip(parsed_weights, parsed_weights[1:])),
             "invalid inverse weights or unpaid terminal mass")
    result = ProblemSpec(profile, support, source["N"], source["M"], source["K"], source["R"], source["Rc"],
        _fraction(source["alpha"]), _fraction(source["beta"]), _fraction(source["m"]), _fraction(source["eta"]),
        kind, tuple(active), parsed_coefficients, _fraction(delta), _fraction(cross), _fraction(model),
        _fraction(accuracy), _fraction(goal), origin, _fraction(kappa), parsed_edges, parsed_weights,
        pi_lower, last_log, next_log, q_source, q_square, arithmetic, evidence, snapshots)
    _require(2*result.K < result.N and result.M >= result.N+result.K and result.M == 2*result.N,
             "invalid physical residual domains")
    _require(result.delta > 0 and result.b_K > 0 and 0 < result.model_error <= result.model_accuracy and
             result.numerical_goal == result.model_accuracy/4 and 0 < result.kappa <= 1/result.m,
             "invalid model/error/reference allowances")
    _require(2*q_source-1 >= result.M+result.N-2 and q_square == result.N,
             "insufficient declared polynomial Gauss order")
    return result


def bind_problem(profile: str, input_manifest: Path | None = None, *, root: Path = ROOT) -> ProblemSpec:
    """Read exact bounded snapshots of one reviewed scalar/code closure.

    The optional manifest must be the selected profile's canonical file beneath
    root, with the original reviewed bytes. root may be a relocated input tree.
    No numerical module, scalar verifier or subprocess is imported/executed.
    """
    _require(type(profile) is str and profile in _PROFILES, "unsupported research profile")
    root = Path(root).resolve()
    bundle, digest, source_name, audit_name = _PROFILES[profile]
    manifest_path = bundle + "/manifest.json"
    if input_manifest is not None:
        supplied = Path(input_manifest)
        supplied = supplied if supplied.is_absolute() else root / supplied
        _require(supplied == root / manifest_path, "wrong input manifest for profile")
    path = root / manifest_path
    size = path.stat().st_size
    _require(size <= MAX_FILE_BYTES, "manifest exceeds metadata cap")
    reader = _Reader(root)
    manifest_ref = ArtifactRef(manifest_path, digest, size)
    manifest_raw = reader.read(manifest_ref)
    members = _manifest_members(bundle, _load(manifest_raw))
    names = _snapshot_names(profile)
    snapshots = [_Snapshot("manifest", manifest_ref, manifest_raw)]
    for role, name in names.items():
        ref = members[bundle + "/" + name]
        snapshots.append(_Snapshot(role, ref, reader.read(ref)))
    frozen = tuple(snapshots)
    evidence = _closure(profile, frozen)
    for ref in evidence:
        reader.read(ref)
    spec = _normalize(profile, frozen, evidence)
    validate_problem(spec)
    return spec


def validate_problem(spec: ProblemSpec) -> None:
    _require(type(spec) is ProblemSpec and type(spec.profile) is str and spec.profile in _PROFILES,
             "invalid problem profile")
    # Every reachable mathematical/input field is frozen. dataclasses.replace
    # constructs a new instance with this non-init witness unset.
    if spec._validated_identity is not None:
        return
    _require(type(spec._snapshots) is tuple and all(type(s) is _Snapshot for s in spec._snapshots),
             "bound immutable input snapshots required")
    for name in ("active_terms", "kernel_coefficients", "frequency_edges", "inverse_weights"):
        _require(type(getattr(spec, name)) is tuple, "immutable tuple required: " + name)
    _require(all(type(term) is ArithmeticTerm for term in spec.active_terms) and
             type(spec.arithmetic) is ArithmeticPolicy, "invalid immutable arithmetic values")
    expected_evidence = _closure(spec.profile, spec._snapshots)
    _require(type(spec.evidence) is tuple and spec.evidence == expected_evidence, "changed evidence closure")
    expected = _normalize(spec.profile, spec._snapshots, expected_evidence)
    _require(canonical_bytes(_problem_document(spec)) == canonical_bytes(_problem_document(expected)),
             "problem differs from reviewed exact profile")
    object.__setattr__(spec, "_validated_identity", _digest(_problem_document(spec)))


def problem_id(spec: ProblemSpec) -> str:
    validate_problem(spec)
    return spec._validated_identity


@dataclass(frozen=True, slots=True)
class ModeRange:
    start: int
    stop: int
    step: int = 2

    def __post_init__(self) -> None:
        _integer(self.start, "range start"); _integer(self.stop, "range stop", 1)
        _require(type(self.step) is int and self.step == 2 and self.start < self.stop,
                 "invalid physical mode range")

    def __iter__(self) -> Iterator[int]:
        return iter(range(self.start, self.stop, self.step))

    def __len__(self) -> int:
        return len(range(self.start, self.stop, self.step))


@dataclass(frozen=True, slots=True)
class QuantityKey:
    name: str
    parity: int
    entry: tuple[int, int] | None = field(default=None, kw_only=True)


    def __post_init__(self) -> None:
        _require(type(self.name) is str and self.name in _QUANTITIES + ("P_L", "P_H"), "unsupported quantity")
        _require(type(self.parity) is int and self.parity in (0, 1), "invalid parity")
        _require(self.entry is None or
                 self.name in ("P_L", "P_H") and type(self.entry) is tuple and len(self.entry) == 2 and
                 all(type(mode) is int and mode >= 0 and mode % 2 == self.parity for mode in self.entry),
                 "invalid selected physical entry")

    @classmethod
    def from_dict(cls, value: dict) -> QuantityKey:
        _require(type(value) is dict and set(value) in
                 ({"name", "parity"}, {"name", "parity", "entry"}), "invalid quantity key")
        if "entry" not in value:
            return cls(**value)
        _require(type(value["entry"]) is list and len(value["entry"]) == 2, "invalid entry coordinates")
        return cls(value["name"], value["parity"], entry=tuple(value["entry"]))


def quantity_document(key: QuantityKey) -> dict:
    value = {"name": key.name, "parity": key.parity}
    if key.entry is not None:
        value["entry"] = list(key.entry)
    return value


@dataclass(frozen=True, slots=True)
class DomainSpec:
    quantity: QuantityKey
    rows: ModeRange
    columns: ModeRange
    symmetric_upper: bool
    head_inner_axes: int

    def __post_init__(self) -> None:
        _require(type(self.quantity) is QuantityKey and type(self.rows) is ModeRange and
                 type(self.columns) is ModeRange, "invalid domain values")
        _require(type(self.symmetric_upper) is bool and
                 (not self.symmetric_upper or self.rows == self.columns),
                 "invalid symmetric output domain")
        _require(type(self.head_inner_axes) is int and self.head_inner_axes in (0, 1, 2),
                 "invalid coupled-head axes")

    @property
    def entries(self) -> int:
        n, m = len(self.rows), len(self.columns)
        return n*(n+1)//2 if self.symmetric_upper else n*m

    def coordinates(self) -> Iterator[tuple[int, int]]:
        for row in self.rows:
            for column in self.columns:
                if not self.symmetric_upper or row <= column:
                    yield row, column


def expected_domain(spec: ProblemSpec, key: QuantityKey) -> DomainSpec:
    validate_problem(spec)
    _require(type(key) is QuantityKey, "quantity key required")
    p = key.parity
    low, head = ModeRange(p, spec.N), ModeRange(spec.N+p, spec.M)
    if key.name in ("P_L", "P_H"):
        rows = head if key.name == "P_H" else low
        columns = low
        if key.entry is not None:
            m, n = key.entry
            _require(m in rows and n in columns and (key.name == "P_H" or m <= n),
                     "selected arithmetic entry outside physical domain")
            rows = ModeRange(m, min(rows.stop, m+2))
            columns = ModeRange(n, min(columns.stop, n+2))
        return DomainSpec(key, rows, columns, key.name == "P_L" and rows == columns, 0)
    if key.name == "F_H":
        return DomainSpec(key, head, low, False, 0)
    if key.name == "R_H":
        return DomainSpec(key, ModeRange(spec.N+p, spec.N+spec.K),
                          ModeRange(spec.N-spec.K+p, spec.N), False, 0)
    if key.name == "K_H":
        return DomainSpec(key, head, head, True, 0)
    axes = {"weighted_head": 2, "weighted_complete_tail": 1}.get(key.name, 0)
    return DomainSpec(key, low, low, True, axes)


@dataclass(frozen=True, slots=True)
class PartitionSpec:
    """Descriptive output ranges, not a native allocation/admission policy."""
    row_block: int
    column_block: int
    inner_block: int

    def __post_init__(self) -> None:
        for name in ("row_block", "column_block", "inner_block"):
            _integer(getattr(self, name), name, 1)


@dataclass(frozen=True, slots=True)
class PlanSpec:
    problem_sha256: str
    arithmetic: ArithmeticPolicy
    partition: PartitionSpec
    implementation: tuple[ArtifactRef, ...]
    scope: str = "METADATA_DESCRIPTION_ONLY"


def _implementation_refs() -> tuple[ArtifactRef, ...]:
    result = []
    for path in ("scripts/whole_source/__init__.py", "scripts/whole_source/contract.py",
                 "scripts/weil_whole_source_split.py"):
        with (ROOT/path).open("rb") as stream:
            raw = stream.read(MAX_FILE_BYTES+1)
        result.append(ArtifactRef(path, hashlib.sha256(raw).hexdigest(), len(raw)))
    return tuple(result)


def inspection_plan(spec: ProblemSpec, partition: PartitionSpec | None = None) -> PlanSpec:
    """Describe a complete logical partition. This never admits native work."""
    validate_problem(spec)
    if partition is None:
        partition = PartitionSpec(spec.N//2, spec.N//2, spec.N//2)
    plan = PlanSpec(problem_id(spec), spec.arithmetic, partition, _implementation_refs())
    validate_plan(spec, plan)
    return plan


def validate_plan(spec: ProblemSpec, plan: PlanSpec) -> None:
    validate_problem(spec)
    _require(type(plan) is PlanSpec and plan.scope == "METADATA_DESCRIPTION_ONLY" and
             plan.problem_sha256 == problem_id(spec), "incompatible inspection plan")
    _require(type(plan.arithmetic) is ArithmeticPolicy and plan.arithmetic == spec.arithmetic,
             "unsupported arithmetic policy")
    _require(type(plan.partition) is PartitionSpec and
             max(plan.partition.row_block, plan.partition.column_block, plan.partition.inner_block) <= spec.M,
             "invalid descriptive partition")
    _require(type(plan.implementation) is tuple and plan.implementation == _implementation_refs(),
             "invalid implementation binding")


def collection_id(spec: ProblemSpec, plan: PlanSpec) -> str:
    validate_plan(spec, plan)
    return _digest({"format": "whole-source-split-inspection-plan-v1", "plan": plan})


@dataclass(frozen=True, slots=True)
class TaskKey:
    """Output-tile metadata only, never a partial sum or computation receipt."""
    problem_sha256: str
    collection_sha256: str
    quantity: QuantityKey
    rows: ModeRange
    columns: ModeRange
    role: str = field(kw_only=True)


def validate_task(spec: ProblemSpec, plan: PlanSpec, task: TaskKey) -> None:
    _require(type(task) is TaskKey and task.problem_sha256 == problem_id(spec) and
             task.collection_sha256 == collection_id(spec, plan), "incompatible task identity")
    _require(type(task.role) is str and task.role in ("producer", "analytic", "exact"),
             "invalid task role")
    domain = expected_domain(spec, task.quantity)
    for requested, full in ((task.rows, domain.rows), (task.columns, domain.columns)):
        _require(type(requested) is ModeRange and requested.start >= full.start and
                 requested.stop <= full.stop and (requested.start-full.start) % 2 == 0 and
                 (requested.stop == full.stop or (requested.stop-full.start) % 2 == 0),
                 "task outside physical/parity domain")
    if domain.symmetric_upper:
        last_column = task.columns.start + task.columns.step * (len(task.columns)-1)
        _require(task.rows.start <= last_column, "empty canonical upper output tile")


@dataclass(frozen=True, slots=True)
class GateReceipt:
    problem_sha256: str
    collection_sha256: str

    def to_dict(self) -> dict:
        _require(_SHA.fullmatch(self.problem_sha256) and _SHA.fullmatch(self.collection_sha256),
                 "invalid inspection receipt identity")
        return {"format": "whole-source-split-inspection-v1", "status": "BOUND_RETAINED_PROFILE_METADATA",
                "scope": "PROFILE_METADATA_ONLY", "problem_id": self.problem_sha256,
                "collection_id": self.collection_sha256, "native_verification_executed": False,
                "matrix_computed": False, "positivity_proved": False,
                "production_admission": False, "execution_authorized": False}
