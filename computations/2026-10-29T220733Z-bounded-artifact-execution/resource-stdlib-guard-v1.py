"""Execute resource inspection with site packages absent and numerical imports denied."""
import builtins
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
allowed = {"scripts", "scripts.whole_source", "scripts.whole_source.contract",
           "scripts.whole_source.execution", "scripts.run_observability",
           "scripts.weil_whole_source_split"}
original = builtins.__import__

def guarded(name, globals=None, locals=None, fromlist=(), level=0):
    if not level and name.split(".")[0] not in sys.stdlib_module_names and name not in allowed:
        raise ImportError("nonstdlib import denied during resource inspection: " + name)
    return original(name, globals, locals, fromlist, level)

builtins.__import__ = guarded
from scripts.weil_whole_source_split import main
code = main(sys.argv[1:])
if code == 0:
    assert not any(name in sys.modules for name in ("flint", "numpy", "scipy"))
    print("STDLIB_ONLY_RESOURCES_CONFIRMED")
raise SystemExit(code)
