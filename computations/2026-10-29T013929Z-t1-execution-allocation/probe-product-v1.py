"""Restricted-row/column target-precision contraction, not a full target proof.

All 5564 inner powers are retained. Selected high input modes use full exact
Rodrigues polynomials; selected tail-power rows include the highest target row.
Dense and blocked executions run in separate owned processes. An independent
polynomial antiderivative checks EVERY selected output and an omitted leading
term must fail. No changed math policy or high-mode truncation is permitted.
"""
from __future__ import annotations
import argparse
import gc
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
from flint import arb, arb_mat, arb_poly, ctx, fmpq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / 'computations/2026-10-28T034134Z-t081-resource-execution'


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publish(value, bits=256):
    scale = 1 << bits
    return [int((value.lower().fmpq() * scale).floor()) - 1,
            int((value.upper().fmpq() * scale).ceil()) + 1]


def contained(value, pair):
    scale = 1 << 256
    return fmpq(pair[0], scale) <= value.lower().fmpq() <= value.upper().fmpq() <= fmpq(pair[1], scale)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    inputs = json.loads(args.inputs.read_bytes())
    for binding in inputs['bindings'].values():
        assert sha(ROOT / binding['path']) == binding['sha256'], binding['path']
    config = inputs['product']
    assert config['N'] == 5564 and config['precision'] == 34304
    assert config['support'] == '1' and config['prime_power'] == 2
    assert config['algorithm'] in ('dense', 'blocked')
    ctx.prec = config['precision']
    sys.path.insert(0, str(BASE))
    helper = module(BASE / 'verify-whole-source-v2.py', 'target_contraction_scalar_helper')
    from resource_limits_v1 import windows_resource_snapshot
    n, parity = config['N'], config['parity']
    rows, modes = config['power_rows'], config['input_modes']
    assert len(set(rows)) == len(rows) and all(0 <= row < n for row in rows)
    assert len(set(modes)) == len(modes) and all(0 <= mode < n and mode % 2 == parity for mode in modes)
    assert max(rows) == n - 1 and max(modes) == n - 1
    start_wall, start_cpu = time.monotonic(), time.process_time()
    tau = arb(config['prime_power']).log()
    left, right = arb(-1), 1 - tau
    factorials = [math.factorial(k) for k in range(n)]
    coefficients = []
    exact_polynomials = []
    for mode in modes:
        polynomial = helper.rodrigues(mode)
        exact_polynomials.append(polynomial)
        coefficients.append(helper.binomial_shift(polynomial, tau, factorials) + [arb(0)] * (n - mode - 1))
    shifted = arb_mat(coefficients).transpose()
    del coefficients, factorials
    moments = helper.power_window_moments(left, right, 3 * n - 2)
    setup = {'wall_seconds':time.monotonic() - start_wall,
             'cpu_seconds':time.process_time() - start_cpu,
             'process':windows_resource_snapshot()['process']}
    print('PRODUCT_SETUP ' + json.dumps({'algorithm':config['algorithm'],'wall_seconds':setup['wall_seconds']}), flush=True)
    before = windows_resource_snapshot()['process']
    wall, cpu = time.monotonic(), time.process_time()
    output = arb_mat(len(rows), len(modes))
    block_rows = len(rows) if config['algorithm'] == 'dense' else config['block_rows']
    assert 0 < block_rows <= len(rows)
    max_live_rows = 0
    for start in range(0, len(rows), block_rows):
        selected = rows[start:start + block_rows]
        hankel = arb_mat([[moments[2 * row + parity + j] for j in range(n)] for row in selected])
        product = hankel * shifted
        for i in range(len(selected)):
            for j in range(len(modes)):
                output[start + i, j] = product[i, j]
        max_live_rows = max(max_live_rows, len(selected))
        del hankel, product
    contraction_wall, contraction_cpu = time.monotonic() - wall, time.process_time() - cpu
    after = windows_resource_snapshot()['process']
    del moments, shifted
    gc.collect()
    # Independent shifted polynomial via native composition, not the helper's
    # factorial convolution. Antiderivatives do not use a Hankel moment table.
    independent_wall = time.monotonic()
    published, checks = [], 0
    shift = arb_poly([tau, arb(1)])
    composed = [arb_poly([arb(x) for x in p.coeffs()])(shift) for p in exact_polynomials]
    for i, row in enumerate(rows):
        degree = 2 * row + parity
        row_pairs = []
        for j, polynomial in enumerate(composed):
            primitive = arb_poly([arb(0)] * degree + polynomial.coeffs()).integral()
            independent = primitive(right) - primitive(left)
            pair = publish(output[i, j])
            assert contained(independent, pair), ('antiderivative containment', row, modes[j])
            assert pair[1] - pair[0] <= 4, ('selected probe precision unresolved', row, modes[j])
            row_pairs.append(pair)
            checks += 1
        published.append(row_pairs)
    # This removes an actual nonzero high-mode contribution, not a metadata flag.
    leading = composed[-1][n - 1]
    row = rows[-1]
    exponent = 2 * row + parity + n - 1
    missing = leading * (right ** (exponent + 1) - left ** (exponent + 1)) / (exponent + 1)
    assert not contained(output[len(rows)-1, len(modes)-1] - missing, published[-1][-1]), 'omitted leading-power control did not reject'
    result = {'format':'t1-restricted-target-contraction-probe-v1',
        'status':'PASS_SELECTED_FULL_INNER_RANGE_CONTRACTION_ONLY',
        'inputs_sha256':sha(args.inputs),'program_sha256':sha(Path(__file__)),
        'consumer_helper_sha256':sha(BASE / 'verify-whole-source-v2.py'),
        'algorithm':config['algorithm'],'support':'1','prime_power':2,
        'N':n,'precision':ctx.prec,'native_threads':ctx.threads,'parity':parity,
        'selected_power_rows':rows,'selected_input_modes':modes,'inner_powers':n,
        'max_live_hankel_rows':max_live_rows,
        'live_hankel_entries':max_live_rows * n,
        'setup':setup,'contraction_wall_seconds':contraction_wall,
        'contraction_cpu_seconds':contraction_cpu,'process_before_contraction':before,
        'process_after_contraction':after,'independent_checked_entries':checks,
        'independent_seconds':time.monotonic() - independent_wall,
        'omitted_nonzero_leading_power_rejected':True,
        'publication_bits':256,'selected_output_pairs':published,
        'wall_seconds':time.monotonic() - start_wall,'cpu_seconds':time.process_time() - start_cpu,
        'full_target_matrices_computed':False,'target_numerical_goals_checked':False,
        'target_positivity_proved':False,'production_admission':False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PRODUCT_COMPLETE ' + json.dumps({'algorithm':config['algorithm'],'checked_entries':checks,'wall_seconds':result['wall_seconds']}), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
