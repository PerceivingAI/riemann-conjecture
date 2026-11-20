"""Live-allocation instrumentation of the unchanged successful v1 contraction.

The v1 result remains its own artifact. This wrapper retains a separate live
allocation observation so pre-existing setup high-waters cannot be mistaken for
contraction peaks. Only the matrix constructor is observed; values/operators,
precision, inner powers, independent checks and negative control are unchanged.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / 'computations/2026-10-28T034134Z-t081-resource-execution'
sys.path.insert(0, str(BASE))


def main():
    arguments = sys.argv[1:]
    input_path = Path(arguments[arguments.index('--inputs') + 1])
    output_path = Path(arguments[arguments.index('--output') + 1])
    config = json.loads(input_path.read_bytes())['product']
    observation_path = output_path.parent / 'live-allocations-v2.json'
    if observation_path.exists():
        raise FileExistsError(observation_path)
    spec = importlib.util.spec_from_file_location('unchanged_product_probe_v1', HERE / 'probe-product-v1.py')
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    from resource_limits_v1 import windows_resource_snapshot
    constructor = probe.arb_mat
    observations = []
    expected_rows = len(config['power_rows']) if config['algorithm'] == 'dense' else config['block_rows']
    def observed_matrix(*args, **kwargs):
        is_hankel = (len(args) == 1 and isinstance(args[0], list) and
                     len(args[0]) == expected_rows and
                     all(isinstance(row, list) and len(row) == config['N'] for row in args[0]))
        before = windows_resource_snapshot()['process'] if is_hankel else None
        wall = time.monotonic()
        result = constructor(*args, **kwargs)
        if is_hankel:
            after = windows_resource_snapshot()['process']
            observations.append({'rows':len(args[0]),'columns':config['N'],
                'before_native_matrix':before,'native_matrix_live':after,
                'committed_delta_bytes':after['committed_bytes'] - before['committed_bytes'],
                'working_set_delta_bytes':after['working_set_bytes'] - before['working_set_bytes'],
                'construction_wall_seconds':time.monotonic() - wall})
        return result
    probe.arb_mat = observed_matrix
    code = probe.main()
    assert len(observations) == (len(config['power_rows']) + expected_rows - 1) // expected_rows
    payload = {'format':'t1-live-hankel-allocations-v2',
        'status':'PASS_OBSERVED_UNCHANGED_CONTRACTION',
        'algorithm':config['algorithm'],'support':'1','N':config['N'],
        'precision':config['precision'],'full_inner_powers':config['N'],
        'program_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'arithmetic_program_sha256':hashlib.sha256((HERE/'probe-product-v1.py').read_bytes()).hexdigest(),
        'arithmetic_result_sha256':hashlib.sha256(output_path.read_bytes()).hexdigest(),
        'observations':observations,'target_positivity_proved':False,'production_admission':False}
    with observation_path.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
