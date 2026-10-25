"""Replay the captured source and independent audit without importing the live tree."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

BUNDLE = Path(__file__).resolve().parent
BASELINE = "computations/2026-10-24T191616Z-weighted-support-extension/data/selection-v1.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((BUNDLE/"source-v1/manifest.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="rh-residual-tail-v1-") as temporary:
        isolated = Path(temporary)
        for relative, expected in manifest.items():
            source = BUNDLE/"source-v1"/relative
            raw = source.read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError(f"captured source changed: {relative}")
            destination = isolated/relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
        baseline = isolated/BASELINE
        baseline.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(BUNDLE/"data/baseline-selection-v1.json", baseline)
        launch = (
            "import pathlib,runpy,sys; "
            "root=pathlib.Path(sys.argv[1]).resolve(); module=sys.argv[2]; "
            "sys.path.insert(0,str(root)); sys.argv=[module]+sys.argv[3:]; "
            "runpy.run_module(module,run_name='__main__'); "
            "loaded=[pathlib.Path(m.__file__).resolve() for name,m in sys.modules.items() "
            "if name.startswith('scripts.') and getattr(m,'__file__',None)]; "
            "assert loaded and all(p.is_relative_to(root) for p in loaded), loaded"
        )
        for label, module, arguments in (
            ("source", "scripts.weil_residual_tail_bound", ["--output", str(output/"scalars-v1.json")]),
            ("audit", "scripts.verify_residual_tail_bound", [str(output/"scalars-v1.json"), "--output", str(output/"audit-v1.json")]),
        ):
            result = subprocess.run([sys.executable, "-I", "-c", launch, str(isolated), module, *arguments],
                                    cwd=isolated, capture_output=True, check=False)
            (output/f"{label}.stdout.txt").write_bytes(result.stdout)
            (output/f"{label}.stderr.txt").write_bytes(result.stderr)
            if result.returncode:
                raise RuntimeError(f"isolated {label} failed: exit {result.returncode}")
        compared = {}
        for name in ("scalars-v1.json", "audit-v1.json"):
            raw = (output/name).read_bytes()
            if raw != (BUNDLE/"data"/name).read_bytes():
                raise ValueError(f"isolated replay differs: {name}")
            compared[name] = hashlib.sha256(raw).hexdigest()
        receipt = {"status": "PASS", "captured_files": len(manifest),
                   "live_script_imports": False, "byte_identical": compared}
        (output/"receipt.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8", newline="\n")
        print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
