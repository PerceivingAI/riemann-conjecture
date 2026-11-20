"""Exercise the real inspection CLI with site packages unavailable."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


class StdlibOnly:
    def find_spec(self, fullname, path=None, target=None):
        delivered = {"scripts", "scripts.whole_source", "scripts.whole_source.contract",
                     "scripts.weil_whole_source_split"}
        if fullname not in delivered and fullname.split(".")[0] not in sys.stdlib_module_names:
            raise ImportError("Non-stdlib inspection dependency: " + fullname)
        return None


sys.meta_path.insert(0, StdlibOnly())
from scripts.weil_whole_source_split import main

code = main(sys.argv[1:])
if code == 0:
    print("STDLIB_ONLY_INSPECTION_CONFIRMED")
raise SystemExit(code)
