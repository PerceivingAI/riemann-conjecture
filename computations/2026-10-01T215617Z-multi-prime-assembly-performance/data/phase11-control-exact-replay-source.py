"""Independent fresh-process positive-control audits; not frozen-target qualification."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def main():
    results = []
    for precision in (512, 640):
        for kind in ("base", "confirmation"):
            filename = f"phase11-control-base{precision}-{kind}-attempt1-audit-inputs.json"
            source = OUT / filename
            destination = OUT / filename.replace("-audit-inputs.json", "-exact-audit.json")
            if destination.exists():
                raise FileExistsError(destination)
            inputs = json.loads(source.read_text(encoding="utf-8"))
            assert inputs["support"] == "2/5" and inputs["dimension"] == 40
            assert inputs["matrix_bits"] == 64 and inputs["witness_bits"] == 32
            assert inputs["precision_bits"] == precision + (128 if kind == "confirmation" else 0)
            assert inputs["theorem_status"] is False
            argv = ["uv", "run", "--locked", "python", "-m", "scripts.audit_multi_prime_candidate", "--input", str(source.relative_to(ROOT)), "--output-json", str(destination.relative_to(ROOT))]
            begin = time.perf_counter()
            process = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True)
            row = {"argv": argv, "exit_code": process.returncode, "wall_seconds": time.perf_counter() - begin,
                   "stdout": process.stdout, "stderr": process.stderr,
                   "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
            results.append(row)
            if process.returncode:
                raise RuntimeError(row)
            row["audit"] = json.loads(destination.read_text(encoding="utf-8"))
            print(f"Independent positive-control audit: {filename} PASS", flush=True)
    higher640 = json.loads((OUT / "phase11-control-base512-confirmation-attempt1-audit-inputs.json").read_text(encoding="utf-8"))
    fresh640 = json.loads((OUT / "phase11-control-base640-base-attempt1-audit-inputs.json").read_text(encoding="utf-8"))
    assert higher640 == fresh640
    report = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
              "role": "fresh-process rational positive-control replay, not successful frozen targets",
              "status": "PASS", "results": results, "independent_fresh_640_exact_inputs_identical": True,
              "qualification_run": False, "theorem_admission": False}
    (OUT / "phase11-control-exact-replay.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
