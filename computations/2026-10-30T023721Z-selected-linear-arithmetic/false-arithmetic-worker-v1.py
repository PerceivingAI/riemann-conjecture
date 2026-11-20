"""Deliberately false complete arithmetic candidates for independent rejection."""
from fractions import Fraction
from flint import arb, arb_poly, ctx, fmpq
from scripts.whole_source.analytic import rodrigues_ratio, binomial_shift, power_window_moments, integrate_window
from scripts.whole_source.artifacts import encode_rational


def endpoint(value):
    q = value.fmpq()
    return Fraction(int(q.numerator), int(q.denominator))


def evaluate(task, staging):
    problem = staging.spec.problem
    kind = task['fault']
    m, n = (1, 1) if kind == 'reverse-shift' else (problem.M-1, problem.N-1)
    row, column = rodrigues_ratio(m), rodrigues_ratio(n)
    if kind == 'omit-power':
        column[n] = 0
    bits = 512 if kind == 'premature-arithmetic-grid' else problem.arithmetic.audit_bits
    with ctx.workprec(bits):
        factorials = [1]
        for k in range(1, problem.N):
            factorials.append(factorials[-1]*k)
        total = arb(0)
        for term in problem.active_terms:
            tau = arb(term.m).log()/arb(fmpq(problem.support.numerator, problem.support.denominator))
            coefficient = -arb(term.prime).log()/arb(term.m).sqrt()
            for window in range(2):
                left, right, shift = ((arb(-1), 1-tau, tau) if window == 0 else
                                       (-1+tau, arb(1), -tau))
                if kind == 'reverse-shift' and window == 0:
                    shift = -shift
                shifted = binomial_shift(column, shift, factorials, problem.N)
                moments = power_window_moments(left, right, problem.M+problem.N-2)
                total += coefficient*integrate_window(row, shifted, moments)
        if not total.is_finite():
            raise ArithmeticError('nonfinite deliberately false native candidate')
        lower, upper = endpoint(total.lower()), endpoint(total.upper())
    return {'fault': kind, 'entry': [m, n], 'lower': encode_rational(lower, 8192),
            'upper': encode_rational(upper, 8192), 'evaluated_bits': bits,
            'complete_active_terms': len(problem.active_terms), 'signed_windows': 8,
            'full_low_power_positions': problem.N, 'full_moment_positions': problem.M+problem.N-1,
            'scope': 'DELIBERATELY_FALSE_MATH_CONTROL'}
