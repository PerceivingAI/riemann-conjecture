"""CONTROL_ONLY: independent residual equivalence, traversal and bounded residency."""
import argparse
import hashlib
import importlib.abc
import json
from pathlib import Path
import sys
from time import perf_counter_ns
from unittest.mock import patch


class NoProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'scripts.whole_source.producer':
            raise ImportError('producer import forbidden in analytical control')


def exercise(problem):
    from flint import arb, ctx
    from scripts.whole_source import analytic
    from scripts.whole_source.pipeline import math_problem
    assert 'scripts.whole_source.producer' not in sys.modules
    image_function = getattr(analytic, '_residual_image', None)
    if image_function is None:
        image_function = analytic._residual_tile_image
    image_symbol = '_residual_image' if hasattr(analytic, '_residual_image') else 'residual_bilinear'
    original = getattr(analytic, image_symbol)
    counts = {'reduced': 0, 'full': 0}
    phase = 'reduced'
    def counted(*args, **kwargs):
        counts[phase] += 1
        return original(*args, **kwargs)
    def digest(value):
        return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()
    def endpoints(values):
        return [[str(x.lower().fmpq()), str(x.upper().fmpq())] for x in values]
    model = math_problem(problem, True)
    reduced = []
    started = perf_counter_ns()
    with patch.object(analytic, image_symbol, counted):
        for n in range(model.N):
            full_f = analytic.operator_column(model, n)
            values = analytic.head_column(model, n, full_f)
            assert len(values) == (model.M-model.N)//2
            reduced.append(endpoints(values))
    reduced_ns = perf_counter_ns()-started
    # Full-size F is explicitly manufactured zero algebra, not evaluated source data.
    phase = 'full'
    full_heads = []
    started = perf_counter_ns()
    with patch.object(analytic, image_symbol, counted):
        for n in (824, 825):
            values = analytic.head_column(problem, n, [arb(0) for _ in range(problem.M//2)])
            assert len(values) == 413
            full_heads.append(endpoints(values))
    full_ns = perf_counter_ns()-started
    exact_rows = []
    extents = []
    for n in (0, 1, 86, 87, 738, 739, 740, 741, 824, 825):
        image = image_function(problem, n)
        sizes = {'input':n, 'image_coefficients':len(image), 'max_row_coefficients':0,
                 'max_product_coefficients':0, 'max_primitive_coefficients':0,
                 'max_live_exact_payload_bytes':0}
        for m in (n % 2, 86+n % 2, 826+n % 2, 910+n % 2, 912+n % 2, 1650+n % 2):
            row = analytic.rodrigues_ratio(m)
            product = row*image
            primitive = product.integral()
            value = primitive(1)-primitive(-1)
            assert value == analytic.residual_bilinear(problem, m, n)
            exact_rows.append([m, n, str(value)])
            sizes['max_row_coefficients'] = max(sizes['max_row_coefficients'], len(row))
            sizes['max_product_coefficients'] = max(sizes['max_product_coefficients'], len(product))
            sizes['max_primitive_coefficients'] = max(sizes['max_primitive_coefficients'], len(primitive))
            payload = sum((int(c.numerator).bit_length()+int(c.denominator).bit_length()+7)//8
                          for poly in (image, row, product, primitive) for c in poly)
            sizes['max_live_exact_payload_bytes'] = max(sizes['max_live_exact_payload_bytes'], payload)
        extents.append(sizes)
    assert 'scripts.whole_source.producer' not in sys.modules
    return {'status':'PASS_CONTROL_ONLY_RESIDUAL_REUSE', 'precision_bits':ctx.prec,
        'native_threads':ctx.threads, 'image_constructions':counts,
        'science':{'reduced_head_digest':digest(reduced), 'reduced_head_values':18,
                   'manufactured_full_head_digest':digest(full_heads),
                   'manufactured_full_head_values':826,
                   'exact_residual_digest':digest(exact_rows), 'exact_residual_pairs':len(exact_rows)},
        'polynomial_extents':extents,
        'observed_wall_ns':{'reduced':reduced_ns, 'manufactured_full':full_ns},
        'producer_import_blocked':True, 'full_F_operands':'MANUFACTURED_ZERO_ALGEBRA_ONLY',
        'full_source_evaluated':False, 'scientific_acceptance':False}


def evaluate(task, staging):
    from flint import ctx
    from scripts.whole_source.execution import _WORKER
    if (task.get('operation') != 'residual-reuse-control' or _WORKER is None or
            _WORKER[-1] is not staging or staging.spec.role != 'analytic' or
            ctx.prec != staging.spec.problem.arithmetic.audit_bits or
            ctx.prec != _WORKER[0].precision_bits or ctx.threads != staging.spec.native_threads):
        raise RuntimeError('bound owned analytical control required')
    staging._check()
    blocker = NoProducer()
    sys.meta_path.insert(0, blocker)
    try:
        result = exercise(staging.spec.problem)
        assert result['image_constructions'] == {'reduced':6, 'full':2}
        return result
    finally:
        sys.meta_path.remove(blocker)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--code-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.code_root.resolve()))
    sys.meta_path.insert(0, NoProducer())
    from flint import ctx
    from scripts.whole_source.contract import bind_problem
    ctx.prec, ctx.threads = 6144, 1
    result = exercise(bind_problem('retained-t081', root=args.code_root))
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
