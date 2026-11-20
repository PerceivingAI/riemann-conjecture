"""Compare a rigorous general LU candidate without changing production arithmetic."""
from fractions import Fraction
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    from flint import arb, arb_mat, ctx, fmpq, fmpq_mat
    from scripts.whole_source.proposal import _dense_solve
    ctx.prec, ctx.threads = 1024, 1
    rows = []
    for n in (3, 8, 16, 32):
        lower = fmpq_mat([[fmpq(i+2) if i == j else fmpq((i+j)%5-2, 7) if i > j else fmpq(0)
                          for j in range(n)] for i in range(n)])
        right = fmpq_mat([[fmpq((i*3+j)%7-3, 11) for j in range(3)] for i in range(n)])
        for transpose in (False, True):
            a = arb_mat(lower)
            actual = a.transpose() if transpose else a
            b = arb_mat(right)
            reference = (lower.transpose() if transpose else lower).solve(right)
            observed = []
            for method in ('scalar', 'native-lu'):
                start = time.perf_counter_ns()
                for _ in range(4):
                    value = _dense_solve(a, b, transpose=transpose) if method == 'scalar' else actual.solve(b, algorithm='lu')
                elapsed = time.perf_counter_ns()-start
                assert value.contains(reference)
                encoding = '\n'.join(str(value[i,j].mid().fmpq())+':'+str(value[i,j].rad().fmpq())
                                      for i in range(n) for j in range(3)).encode()
                observed.append({'method': method, 'four_calls_ns': elapsed,
                                 'digest': hashlib.sha256(encoding).hexdigest(), 'contains_exact_reference': True})
            rows.append({'dimension': n, 'transpose': transpose, 'methods': observed,
                         'identical_enclosures': observed[0]['digest'] == observed[1]['digest']})
    # Existing strict-positive pivot semantics differ from a general LU solver.
    uncertain = arb_mat([[arb(0,1), 0], [1, 2]])
    try:
        _dense_solve(uncertain, arb_mat([[1],[1]]))
    except Exception as error:
        pivot_refusal = type(error).__name__+': '+str(error)
    else:
        raise AssertionError('uncertain pivot was accepted')
    report = {'status': 'PASS_CONTROL_ONLY_NATIVE_CANDIDATE_COMPARISON', 'rows': rows,
              'installed_solve_interfaces': [name for name in dir(arb_mat) if any(
                  part in name.lower() for part in ('solve','chol','triang','ldl'))],
              'source_documentation': 'https://python-flint.readthedocs.io/en/latest/arb_mat.html',
              'candidate': 'rigorous general solve algorithm=lu, never approx',
              'uncertain_pivot_refusal': pivot_refusal, 'production_arithmetic_changed': False,
              'full_qualification': False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'status': report['status'], 'identical': [row['identical_enclosures'] for row in rows],
                      'production_arithmetic_changed': False}))


if __name__ == '__main__':
    main()
