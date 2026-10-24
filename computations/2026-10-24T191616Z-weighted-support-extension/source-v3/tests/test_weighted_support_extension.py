"""Independent source checks across support/order and a full residual control."""
from fractions import Fraction as Q

from flint import fmpq, fmpq_mat
import pytest

from scripts import verify_weighted_low_space_inputs as validation
from scripts import verify_weighted_support_extension_inputs as audit
from scripts import weil_weighted_support_extension as source
from scripts.weil_weighted_extension_diagnostics import uniform_residual


@pytest.mark.parametrize('support,order', [(Q(3, 5), 8), (Q(1353, 2048), 38)])
def test_fresh_source_matches_independent_reconstruction_across_support_and_order(support, order):
    n, boundary = 4, 4+order+4
    generated = source.generate_low(support, n, order, 1024)
    reference = audit.reconstruct_low(support, n, order, 2048)
    for name in ('A_K', 'G_K'):
        for i in range(n):
            for j in range(i, n):
                validation.reference_pair(reference[name][i, j],
                    generated['matrices'][name][i][j-i], 352, name,
                    parity_zero=bool((i-j) % 2))
    for name in ('delta', 'complement'):
        validation.reference_pair(reference[name], generated[name], 352, name)
    heads, signature = source.generate_heads(support, n, order, boundary, 1024)
    independent = audit.reconstruct_heads(support, n, order, boundary, 2048, reference['residual'])
    assert signature == reference['residual_signature']
    for name in ('V', 'P', 'RK'):
        for k in range(n, boundary):
            for j in range(n):
                validation.reference_pair(independent[name][k-n, j], heads[name][k-n][j],
                                          352, name, parity_zero=bool((k-j) % 2))
    # Equal parity and still inside the largest residual degree. Only the
    # column-specific degree may justify this zero; column2 remains nonzero.
    assert heads['RK'][order+2-n][0] == [0, 0]
    lo, hi = heads['RK'][order+2-n][2]
    assert lo > 0 or hi < 0


def test_uniform_residual_pays_signed_cross_energy_in_physical_mass():
    delta, mu = Q(1, 100), Q(3, 5)
    mass = fmpq_mat([[2, 0], [0, fmpq(2, 3)]])
    B = fmpq_mat([[fmpq(6, 5), fmpq(1, 4)], [-fmpq(1, 3), fmpq(1, 5)]])
    # The squared mass-normalized Frobenius norm is below1, hence ||B||<=1.
    frobenius = sum((Q(str(B[i, j]))**2/Q(str(mass[j, j]))
                     for i in range(2) for j in range(2)), Q())
    assert frobenius < 1
    inverse = fmpq_mat([[fmpq(5, 3), 0], [0, fmpq(20, 17)]])
    energy = B.transpose()*inverse*B
    # E=delta*B has norm <=delta and retains the signed off-diagonal coupling.
    added = energy*fmpq((2*delta+delta**2).numerator, (2*delta+delta**2).denominator)
    r = uniform_residual(delta, Q(1), mu)
    remainder = mass*fmpq((r-delta).numerator, (r-delta).denominator)-added
    assert remainder[0, 0] >= 0 and remainder[1, 1] >= 0 and remainder.det() >= 0
    missing_cross = mass*fmpq((delta**2/mu).numerator, (delta**2/mu).denominator)-added
    assert missing_cross[0, 0] < 0


def test_altered_selection_cannot_relax_the_residual_budget():
    from scripts.weil_weighted_extension_diagnostics import select_parameters

    selected = select_parameters()
    selected['residual_allowance_limit'] = str(2*Q(selected['residual_allowance_limit']))
    with pytest.raises(validation.InputRejected):
        source.validate_selection(selected)
