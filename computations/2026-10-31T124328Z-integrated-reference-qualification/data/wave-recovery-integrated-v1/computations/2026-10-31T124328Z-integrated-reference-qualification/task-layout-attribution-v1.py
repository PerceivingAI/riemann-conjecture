"""Attribute real persisted finite-control costs without claiming pipeline speedup."""
from pathlib import Path
import argparse
import importlib
import json
import runpy
import sys
import time
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--code-root', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    root = args.code_root.resolve()
    output = args.output_dir.resolve()
    assert not output.exists()
    sys.path.insert(0, str(root))
    timings, stack, patches = {}, [], []
    targets = {'proposal': ('_raw', '_json', '_dense_solve', 'blocked_cholesky', 'triangular_solve'),
               'exact': ('_raw', '_json', 'paid_integer_tiles', 'integer_congruence'),
               'exact_global': ('mass_trace', 'full_modular_nonsingularity')}
    def wrap(label, function):
        def measured(*values, **kwargs):
            frame = [time.perf_counter_ns(), 0]
            stack.append(frame)
            try:
                return function(*values, **kwargs)
            finally:
                elapsed = time.perf_counter_ns()-frame[0]
                stack.pop()
                if stack:
                    stack[-1][1] += elapsed
                row = timings.setdefault(label, {'calls': 0, 'exclusive_ns': 0, 'inclusive_ns': 0})
                row['calls'] += 1
                row['exclusive_ns'] += elapsed-frame[1]
                row['inclusive_ns'] += elapsed
        return measured
    for module, names in targets.items():
        obj = importlib.import_module('scripts.whole_source.'+module)
        for name in names:
            if hasattr(obj, name):
                patches.append(patch.object(obj, name, wrap(module+'.'+name, getattr(obj, name))))
    for item in patches:
        item.start()
    start, cpu = time.perf_counter_ns(), time.process_time_ns()
    try:
        sys.argv = ['operand-reuse-control-v1.py', '--code-root', str(root), '--output-dir', str(output)]
        runpy.run_path(str(root/'computations/2026-10-31T124328Z-integrated-reference-qualification/operand-reuse-control-v1.py'), run_name='__main__')
    finally:
        for item in reversed(patches):
            item.stop()
    elapsed, cpu = time.perf_counter_ns()-start, time.process_time_ns()-cpu
    # Geometry-derived candidate groups. No timing claim about worker startup.
    blocks = 4
    candidates = {'factor_diagonal_tasks': blocks, 'factor_offdiagonal_tasks': blocks*(blocks-1)//2,
                  'solve_column_tasks_per_pass': blocks, 'first_contraction_row_tasks': blocks,
                  'upper_output_tasks': blocks*(blocks+1)//2,
                  'upper_adjacent_pair_batches': sum((blocks-i+1)//2 for i in range(blocks))}
    report = {'status': 'PASS_FINITE_CONTROL_ATTRIBUTION', 'exclusive_timings': timings,
              'wall_ns': elapsed, 'process_cpu_ns': cpu, 'candidate_geometry_per_parity': candidates,
              'dimension': 7, 'panel_size': 2, 'parities': [0, 1],
              'worker_startup_measured': False, 'physical_io_measured': False,
              'source': 'MANUFACTURED_FINITE_CONTROL', 'full_qualification': False}
    with (output/'attribution.json').open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'status': report['status'], 'wall_ns': elapsed, 'timings': timings}))


if __name__ == '__main__':
    main()
