"""Full frozen-contract check for this versioned research execution."""
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts import weil_weighted_extension_diagnostics as diagnostics
from scripts import weil_weighted_support_extension as source

BUNDLE = Path(__file__).resolve().parent
DATA = BUNDLE/'data'
raw_selection = (DATA/'selection-v1.json').read_bytes()
selection = json.loads(raw_selection)
selector = BUNDLE/'source-v1/scripts/weil_weighted_extension_diagnostics.py'
selector_sha = hashlib.sha256(selector.read_bytes()).hexdigest()
expected = diagnostics.select_parameters()
expected['selection_source_sha256'] = selector_sha
if selection != expected:
    raise SystemExit('frozen selection differs from complete recomputed contract')
packet_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA/'extension-source-v1.json.gz'
raw_packet = packet_path.read_bytes()
packet = json.loads(gzip.decompress(raw_packet))
if packet['selection'] != selection:
    raise SystemExit('packet changes the frozen complete selection')
if packet['selection_sha256'] != hashlib.sha256(raw_selection).hexdigest():
    raise SystemExit('packet changes the original selection-byte binding')
source.validate_packet(packet)
if Fraction(packet['cross_norm_upper']) != Fraction(selection['cross_norm_upper']):
    raise SystemExit('packet changes the frozen cross-norm bound')
print(json.dumps({'status': 'FULL_FROZEN_CONTRACT_PASS',
                  'packet_sha256': hashlib.sha256(raw_packet).hexdigest(),
                  'selection_sha256': hashlib.sha256(raw_selection).hexdigest(),
                  'selector_sha256': selector_sha,
                  'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}))
