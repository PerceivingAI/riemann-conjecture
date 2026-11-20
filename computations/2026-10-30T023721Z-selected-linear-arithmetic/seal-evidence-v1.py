"""Seal this completed selection's retained bytes without rewriting any member."""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE/'manifest.json')
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    tests = ET.parse(HERE/'development/final-suite-v6.xml').getroot()
    assert len(tests.findall('.//testcase')) == 190
    assert not any(tests.findall('.//'+kind) for kind in ('failure', 'error', 'skipped'))
    boundaries = json.loads((HERE/'data/boundaries-v3/qualification.json').read_bytes())
    assert boundaries['all_five_controls_passed']
    members = []
    excluded = {output, HERE/'retained-verification-v1.json'}
    for path in sorted(HERE.rglob('*')):
        if not path.is_file() or path in excluded:
            continue
        assert not path.is_symlink(), path
        digest = hashlib.sha256()
        size = 0
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024*1024), b''):
                size += len(block)
                digest.update(block)
        members.append({'path': path.relative_to(HERE).as_posix(), 'sha256': digest.hexdigest(), 'size': size})
        if len(members) % 10000 == 0:
            print(json.dumps({'event': 'retained_members_hashed', 'members': len(members)}), flush=True)
    result = {'format': 'selected-complete-arithmetic-evidence-v1', 'computation_id': 'X-20261030-001',
              'created_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
              'status': 'QUALIFIED_SELECTED_COMPLETE_ARITHMETIC', 'profile': 'retained-t081',
              'scope': 'SELECTED_COMPLETE_ARITHMETIC_ONLY', 'complete_entries': 6,
              'scientific_recovery_cuts': 13, 'affected_tests_passed': 190,
              'full_source': False, 'matrix_positivity': False, 'production_admission': False,
              'members': members}
    raw = (json.dumps(result, sort_keys=True, indent=2)+'\n').encode('utf-8')
    with output.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({'status': 'SEALED_RETAINED_MEMBERS', 'members': len(members),
                      'member_bytes': sum(row['size'] for row in members), 'manifest_bytes': len(raw)}, sort_keys=True))


if __name__ == '__main__':
    main()
