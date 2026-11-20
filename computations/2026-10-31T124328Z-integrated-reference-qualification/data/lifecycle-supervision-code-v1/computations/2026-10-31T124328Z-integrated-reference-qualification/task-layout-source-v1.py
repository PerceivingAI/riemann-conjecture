"""Check complete reduced source/audit compatibility with the new runtime closure."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--origin-commit', required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    from scripts.whole_source import pipeline, resources
    from scripts.whole_source.contract import bind_problem, canonical_bytes
    from scripts.whole_source.execution import _write
    from scripts.whole_source.receipts import discover_receipts, verify_stage
    allocate = resources.auto_plan
    def bounded(template, *, parallel, memory_mib=None, helper_root=ROOT):
        return allocate(template, parallel=parallel, cpus=2, memory_mib=2048, helper_root=helper_root)
    with patch.object(resources, 'auto_plan', bounded):
        inputs = pipeline.prepare_source_inputs(bind_problem('retained-t081'), output/'inputs', control=True,
            tile_modes=2, origin_git_commit=args.origin_commit, origin_git_dirty=True)
    for operation in ('source', 'audit'):
        command = [sys.executable, '-B', '-m', 'scripts.weil_whole_source_split', operation,
                   '--problem', str(inputs['problem']), '--execution', str(inputs['execution']),
                   '--output-dir', str(output/operation)]
        if operation == 'audit':
            command += ['--source', str(output/'source/producer/source-manifest.json')]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        (output/(operation+'-stdout.txt')).write_text(result.stdout, encoding='utf-8')
        (output/(operation+'-stderr.txt')).write_text(result.stderr, encoding='utf-8')
        assert result.returncode == 0, result.stderr
    audit = json.loads((output/'audit/analytical-receipt.json').read_bytes())
    assert audit['entries_checked'] == 36 and audit['full_mathematical_source'] is False
    stages = [verify_stage(path)['record'] for path in discover_receipts(output)]
    report = {'status': 'PASS_CONTROL_ONLY_SOURCE_COMPATIBILITY', 'entries_checked': 36,
              'stages': stages, 'full_qualification': False, 'production_admission': False}
    _write(output/'verification.json', canonical_bytes(report))
    print(json.dumps({'status': report['status'], 'stages': len(stages), 'entries_checked': 36}))


if __name__ == '__main__':
    main()
