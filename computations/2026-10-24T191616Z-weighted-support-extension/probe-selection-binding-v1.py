"""Actual validation regression: only the embedded residual budget is changed."""
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts import weil_weighted_support_extension as experiment

BUNDLE = Path(__file__).resolve().parent
raw = (BUNDLE/'data/extension-source-v1.json.gz').read_bytes()
packet = json.loads(gzip.decompress(raw))
packet['selection'] = dict(packet['selection'])
original = packet['selection']['residual_allowance_limit']
packet['selection']['residual_allowance_limit'] = str(2*Fraction(original))
rejected, reason = False, None
try:
    experiment.validate_packet(packet)
except ValueError as exc:
    rejected, reason = True, str(exc)
print(json.dumps({'status': 'REGRESSION_PASS' if rejected else 'REGRESSION_FAIL',
                  'altered_budget_rejected': rejected, 'reason': reason,
                  'source_packet_sha256': hashlib.sha256(raw).hexdigest(),
                  'original_budget': original,
                  'altered_budget': packet['selection']['residual_allowance_limit'],
                  'validator_sha256': hashlib.sha256(Path(experiment.__file__).read_bytes()).hexdigest(),
                  'scope': 'Metadata validation only; no analytical reconstruction or matrix sign evaluated'}))
raise SystemExit(0 if rejected else 1)
