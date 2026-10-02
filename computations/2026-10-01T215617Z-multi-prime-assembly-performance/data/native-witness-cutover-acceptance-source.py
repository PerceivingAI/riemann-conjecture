"""Run the full Python regression gate once after the native witness cutover."""
from pathlib import Path
import datetime
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

if __name__ == "__main__":
    destination = OUT / "native-witness-cutover-acceptance.json"
    if destination.exists():
        raise FileExistsError(destination)
    argv = ["uv", "run", "--locked", "--extra", "test", "python", "-m", "pytest", "-q"]
    begin = time.perf_counter()
    process = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True)
    report = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
              "role": "post-cutover full Python regression, not performance measurement",
              "argv": argv, "exit_code": process.returncode, "wall_seconds": time.perf_counter() - begin,
              "stdout": process.stdout, "stderr": process.stderr}
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(process.stdout, end="")
    print(process.stderr, end="")
    raise SystemExit(process.returncode)
