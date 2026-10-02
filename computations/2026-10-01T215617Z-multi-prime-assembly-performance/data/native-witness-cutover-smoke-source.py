"""One real candidate and retained positive kernel replay, not a benchmark sweep."""
from pathlib import Path
from fractions import Fraction
import datetime
import hashlib
import json
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts import weil_multi_prime_continuation_driver
from scripts.weil_multi_prime_support_candidate_check import CandidateStageError, run_candidate
from scripts.cert.multi_prime_exact_witness import make_witness
from scripts.cert.matrices import RationalInterval
from scripts.audit_multi_prime_candidate import _margin

OUT = Path(__file__).resolve().parent


def main():
    destination = OUT / "native-witness-cutover-smoke.json"
    if destination.exists():
        raise FileExistsError(destination)
    source = OUT / "phase11-candidate-inputs-N196-p512-m104-w56.zip"
    with zipfile.ZipFile(source) as archive:
        expected = json.loads(archive.read("candidate-inputs.json"))
    begin = time.perf_counter()
    try:
        run_candidate(Fraction(11, 20), dimension=196, prec=512,
                      residual_order=32, matrix_bits=104, witness_bits=56)
    except CandidateStageError as error:
        assert error.stage == "witness"
        assert error.audit_inputs == expected
        failure = str(error)
    else:
        raise AssertionError("Frozen rejected target was incorrectly accepted")
    candidate_seconds = time.perf_counter() - begin
    original_failure = json.loads((OUT / "phase11-candidates-512-104-56.json").read_text())["samples"][1]
    assert failure == original_failure["error"]["message"]

    kernel_source = OUT / "phase11-witness-kernel-N196-prefix97.zip"
    with zipfile.ZipFile(kernel_source) as archive:
        proof = json.loads(archive.read("kernel-inputs-and-witness.json"))
    block = [[RationalInterval(Fraction(lo), Fraction(hi)) for lo, hi in row] for row in proof["block"]]
    expected_witness = [[Fraction(value) for value in row] for row in proof["witness"]]
    begin = time.perf_counter()
    witness, margin = make_witness(block, 56)
    witness_seconds = time.perf_counter() - begin
    assert witness == expected_witness and margin == Fraction(proof["reported_margin"]) > 0
    assert _margin([[(entry.lo, entry.hi) for entry in row] for row in block], witness) == margin

    previous = json.loads((OUT / "phase9-final-integrity-checks.json").read_text())["final_source_test_sha256"]
    controls = json.loads((OUT / "phase9-source-provenance.json").read_text())["frozen_shared_controls_unchanged"]
    frozen = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == previous[path] for path in controls}
    assert all(frozen.values())
    dependencies = (*weil_multi_prime_continuation_driver.CACHE_SOURCE_PATHS, "tests/test_multi_prime_exact_witness.py")
    report = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
              "role": "one real candidate and retained positive kernel smoke, not qualification",
              "status": "PASS", "candidate": {"dimension": 196, "precision_bits": 512, "matrix_bits": 104,
                  "witness_bits": 56, "outcome": "WITNESS_FAILED", "reason": failure,
                  "complete_rounded_inputs_identical": True, "wall_seconds": candidate_seconds,
                  "previous_same_input_wall_seconds": original_failure["wall_seconds"]},
              "positive_kernel": {"dimension": 97, "proper_principal_block_only": True,
                  "exact_witness_and_margin_identical": True, "independent_exact_margin_replay": "PASS",
                  "wall_seconds": witness_seconds, "exact_margin": str(margin)},
              "frozen_shared_byte_checks": frozen,
              "source_sha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in dependencies},
              "input_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (source, kernel_source)},
              "theorem_admission": False, "qualification_run": False}
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Real N196 candidate: identical witness rejection and all rounded inputs, {candidate_seconds:.3f}s")
    print(f"Complete 97-mode witness: identical dyadic witness/margin, independent exact PASS, {witness_seconds:.3f}s")
    print(f"Frozen shared/v1 source bytes: {len(frozen)}/{len(frozen)} unchanged")


if __name__ == "__main__":
    main()
