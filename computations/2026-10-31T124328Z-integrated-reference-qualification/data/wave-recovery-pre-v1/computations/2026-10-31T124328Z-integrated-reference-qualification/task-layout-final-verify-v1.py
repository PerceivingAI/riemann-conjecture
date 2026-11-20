"""Bind completed task-layout evidence and raw inventories without rerunning science."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    data, output = args.data_dir.resolve(), args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    from scripts.whole_source.contract import canonical_bytes
    from scripts.whole_source.retention import _hash_file
    def load(name):
        return json.loads((data/name).read_bytes())
    baseline = load('task-layout-baseline-closeout-v1.json')
    parallel = load('task-layout-owned-parallel-v1/verification.json')
    serial = load('task-layout-owned-serial-v1/verification.json')
    for key in ('proposal_science','exact_science','assessment'):
        assert baseline[key] == parallel[key] == serial[key], key
    assert all(row['workers'] == row['task_workers'] == row['threads'] == 1 for row in serial['stages'])
    assert all(any(row['function'] == function and row['task_workers'] == 2 for row in parallel['stages'])
               for function in ('evaluate_proposal','evaluate_exact'))
    source = load('task-layout-source-v1/verification.json')
    assert source['entries_checked'] == 36
    boundaries = load('task-layout-boundaries-v1/verification.json')
    inputs = load('task-layout-input-boundaries-v3.json')
    assert len(boundaries['cases']) == 3 and len(inputs['cases']) == 2
    assert all(row['no_final_report'] and row['cleanup_verified'] for row in boundaries['cases']+inputs['cases'])
    tests = []
    successful = set()
    for name in ('task-layout-group-tests-v1.xml','task-layout-math-tests-v1.xml',
                 'task-layout-math-tests-v2.xml','task-layout-math-tests-v3.xml'):
        suite = ET.parse(data/name)
        for case in suite.findall('.//testcase'):
            if not any(item.tag in ('failure','error','skipped') for item in case):
                successful.add((case.attrib['classname'],case.attrib['name']))
        tests.append({'path':name,**_hash_file(data/name)})
    assert len(successful) == 269
    runs = []
    for name in ('task-layout-owned-baseline-v1','task-layout-owned-parallel-v1','task-layout-owned-serial-v1',
                 'task-layout-source-v1','task-layout-boundaries-v1','task-layout-input-boundaries-v1'):
        root = data/name
        inventory = output/(name+'-inventory.jsonl')
        count, size = 0, 0
        with inventory.open('xb') as stream:
            for path in sorted(root.rglob('*')):
                if not path.is_file():
                    continue
                assert not path.is_symlink()
                row = {'path':path.relative_to(root).as_posix(),**_hash_file(path)}
                stream.write(canonical_bytes(row))
                count += 1
                size += row['size']
        runs.append({'run':name,'files':count,'logical_bytes':size,
                     'inventory':{'path':inventory.name,**_hash_file(inventory)}})
    bound = []
    for path in sorted(data.glob('task-layout-*.json')):
        bound.append({'path':path.relative_to(data).as_posix(),**_hash_file(path)})
    for name in ('task-layout-owned-parallel-v1','task-layout-owned-serial-v1','task-layout-source-v1',
                 'task-layout-boundaries-v1'):
        path=data/name/'verification.json'
        bound.append({'path':path.relative_to(data).as_posix(),**_hash_file(path)})
    for name in ('task-layout-pre-v1','task-layout-integrated-v1','task-layout-final-v1','task-layout-final-v2'):
        for leaf in ('capture-manifest.json','preservation-manifest.json','preservation-environment.json'):
            path=data/name/leaf
            bound.append({'path':path.relative_to(data).as_posix(),**_hash_file(path)})
    for path in sorted(data.parent.glob('task-layout-*-v*.py')):
        bound.append({'path':path.relative_to(ROOT).as_posix(),**_hash_file(path)})
    for path in (data.parent/'record.md',ROOT/'scripts/README.md'):
        bound.append({'path':path.relative_to(ROOT).as_posix(),**_hash_file(path)})
    report = {'status':'PASS_CONTROL_ONLY_TASK_LAYOUT_FINAL_BINDING','unique_passing_cases':len(successful),
              'baseline_parallel_serial_mathematics_equal':True,'two_worker_roles':['proposal','exact'],
              'reduced_source_entries':36,'failure_cases':5,'runs':runs,'tests':tests,'bindings':bound,
              'numerical_work_rerun':False,'full_qualification':False,'production_admission':False}
    with (output/'verification.json').open('xb') as stream:
        stream.write(canonical_bytes(report))
    print(json.dumps({'status':report['status'],'unique_passing_cases':len(successful),
                      'inventoried_files':sum(row['files'] for row in runs)}))


if __name__ == '__main__':
    main()
