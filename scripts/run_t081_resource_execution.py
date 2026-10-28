"""Run the versioned, resource-budgeted complete T81/100 research operation."""
from pathlib import Path
import runpy
import sys


BUNDLE = Path(__file__).resolve().parents[1] / (
    "computations/2026-10-28T034134Z-t081-resource-execution"
)


def main() -> None:
    # Keep the measured numerical and orchestration programs byte-unchanged.
    sys.path.insert(0, str(BUNDLE))
    runpy.run_path(str(BUNDLE / "run-execution-v1.py"), run_name="__main__")


if __name__ == "__main__":
    main()
