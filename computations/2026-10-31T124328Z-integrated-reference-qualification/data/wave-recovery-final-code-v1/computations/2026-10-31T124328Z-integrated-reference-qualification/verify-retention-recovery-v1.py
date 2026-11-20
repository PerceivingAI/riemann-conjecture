"""Metadata-only inventory recovery and CLI boundary evidence, not scientific acceptance."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.whole_source import retention
from scripts.whole_source.contract import ROOT, canonical_bytes


def inventory(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    output = parser.parse_args().output_dir.resolve()
    output.relative_to(ROOT)
    output.mkdir(parents=True, exist_ok=False)
    run = output/'metadata-bundle'
    run.mkdir()
    (run/'member.bin').write_bytes(b'METADATA_ONLY_NO_SCIENTIFIC_ACCEPTANCE\n')
    original = retention._write

    def fail_final(path, raw):
        if Path(path) == run/'retained-manifest.json':
            raise OSError('controlled final manifest publication failure')
        return original(path, raw)

    with patch.object(retention, '_write', side_effect=fail_final):
        try:
            retention._seal(run)
        except OSError as exc:
            initial_error = str(exc)
        else:
            raise AssertionError('controlled failure did not occur')
    before = inventory(run)
    assert not (run/'retained-manifest.json').exists()
    command = [sys.executable, '-B', '-m', 'scripts.weil_whole_source_split',
               'finalize-retention', '--run-dir', str(run),
               '--assessment', str(output/'assessment.json')]
    missing = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=60)
    assert missing.returncode == 2, missing.stdout + missing.stderr
    assert not (run/'retained-manifest.json').exists()
    recovered = retention._seal(run)
    assert recovered['status'] == 'PASS_RETAINED_INVENTORY'
    after = inventory(run)
    assert all(after[name] == digest for name, digest in before.items())
    manifest = json.loads((run/'retained-manifest.json').read_bytes())
    assert manifest['format'] == 'whole-source-retained-inventory-v2'
    sealed = inventory(run)
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=60)
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == 'PASS_RETAINED_INVENTORY'
    assert inventory(run) == sealed
    result = {'status':'PASS_METADATA_RETENTION_RECOVERY',
        'scope':'Real publication/retry. Missing assessment rejects unsealed recovery; completed inventory CLI is verification-only. No mathematical execution or approval.',
        'initial_error':initial_error, 'preserved_files':before,
        'all_prior_bytes_preserved':True, 'recovered':recovered,
        'missing_assessment_cli':{'exit_code':missing.returncode, 'stderr':missing.stderr.strip()},
        'completed_inventory_cli':{'exit_code':completed.returncode, 'stdout':completed.stdout.strip()},
        'active_generation':manifest['generation']}
    (output/'verification.json').write_bytes(canonical_bytes(result))
    print(result['status'])
    print('Prior files preserved:',len(before))
    print('Unsealed recovery without assessment rejected:',missing.returncode)
    print('Completed inventory read-only verification:',completed.returncode)


if __name__ == '__main__':
    main()
