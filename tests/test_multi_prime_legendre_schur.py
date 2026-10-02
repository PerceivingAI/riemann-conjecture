from __future__ import annotations

import pytest
from flint import arb, ctx

from scripts.cert.legendre_schur import (
    assemble_exact_prime_schur,
    first_prime_matrices,
    legendre_polynomials,
)
from scripts.cert.multi_prime_legendre_schur import assemble_multi_prime_schur
from scripts.cert.prime_power_terms import assemble_combined_prime_power_operator


def _assert_ball_overlap(left: arb, right: arb, *, label: str) -> None:
    assert left.overlaps(right), f"nonoverlapping Arb enclosures for {label}: {left} vs {right}"


def _assert_matrix_overlap(left: list[list[arb]], right: list[list[arb]], *, label: str) -> None:
    assert len(left) == len(right)
    for i in range(len(left)):
        assert len(left[i]) == len(right[i])
        for j in range(len(left[i])):
            _assert_ball_overlap(left[i][j], right[i][j], label=f"{label}[{i},{j}]")


@pytest.mark.parametrize(
    ("support_num", "support_den", "dimension", "prec"),
    [
        (7, 20, 16, 128),
        (2, 5, 24, 160),
        (17, 40, 28, 160),
        (9, 20, 32, 192),
    ],
)
def test_generic_assembler_matches_frozen_one_prime_path(
    support_num: int,
    support_den: int,
    dimension: int,
    prec: int,
) -> None:
    new = assemble_multi_prime_schur(
        n=dimension,
        prec=prec,
        residual_order=32,
        support_num=support_num,
        support_den=support_den,
    )
    old = assemble_exact_prime_schur(
        n=dimension,
        prec=prec,
        residual_order=32,
        support_num=support_num,
        support_den=support_den,
    )
    polys = legendre_polynomials(dimension - 1)
    old_p, old_p_squared = first_prime_matrices(
        polys,
        prec,
        support_num,
        support_den,
    )

    assert [term.m for term in new["active_terms"]] == [2]
    _assert_matrix_overlap(new["P"], old_p, label="P")
    _assert_matrix_overlap(new["P_squared"], old_p_squared, label="P_squared")
    _assert_matrix_overlap(new["GP"], old["G2"], label="GP/G2")
    _assert_matrix_overlap(new["GV"], old["GV"], label="GV")
    _assert_matrix_overlap(new["GR"], old["GR"], label="GR")
    _assert_matrix_overlap(new["A"], old["A"], label="A")
    _assert_ball_overlap(new["rho_R"], old["rho_R"], label="rho_R")
    _assert_ball_overlap(new["mu"], old["mu"], label="mu")
    assert new["schur"] is not None
    assert old["schur"] is not None
    _assert_matrix_overlap(new["schur"], old["schur"], label="schur")


def test_two_prime_operator_square_contains_cross_terms() -> None:
    dimension = 4
    prec = 192
    result = assemble_multi_prime_schur(
        n=dimension,
        prec=prec,
        residual_order=32,
        require_positive_mu=False,
        support_num=3,
        support_den=5,
    )
    terms = result["active_terms"]
    assert [term.m for term in terms] == [2, 3]

    polys = legendre_polynomials(dimension - 1)
    only_two = assemble_combined_prime_power_operator(polys, [terms[0]], prec=prec)
    only_three = assemble_combined_prime_power_operator(polys, [terms[1]], prec=prec)

    combined_square = result["P_squared"]
    cross = [
        [
            combined_square[i][j]
            - only_two.p_squared_matrix[i][j]
            - only_three.p_squared_matrix[i][j]
            for j in range(dimension)
        ]
        for i in range(dimension)
    ]

    # The constant mode already gives a rigorous nonzero mixed contribution.
    assert cross[0][0].lower() > 0
    assert not combined_square[0][0].overlaps(
        only_two.p_squared_matrix[0][0] + only_three.p_squared_matrix[0][0]
    )

    # This is an assembler-level assertion, not merely a low-level operator
    # test: GP must be derived from the same combined square.
    for i in range(dimension):
        for j in range(dimension):
            assert result["GP"][i][j].overlaps(result["GP"][j][i])


def test_multi_prime_norm_bound_generalizes_beyond_tau_two_above_one() -> None:
    with ctx.workprec(160):
        result = assemble_multi_prime_schur(
            n=4,
            prec=160,
            support_num=7,
            support_den=10,
            require_positive_mu=False,
        )
        assert [term.m for term in result["active_terms"]] == [2, 3, 4]
        bounds = result["arithmetic_norm_bounds"]
        assert bounds[2].overlaps(arb(2).sqrt())
        assert bounds[3] == 1
        assert bounds[4] == 1


@pytest.mark.parametrize("tau", ["1", "1 +/- 0.01"])
def test_norm_bound_fails_closed_at_unresolved_chain_length(tau) -> None:
    from dataclasses import replace

    from scripts.cert.multi_prime_legendre_schur import compressed_shift_norm_bound
    from scripts.cert.prime_power_terms import prime_power_term

    term = replace(prime_power_term(2, 7, 10, prec=128), tau=arb(tau))
    with pytest.raises(ValueError, match="chain length"):
        compressed_shift_norm_bound(term, 128)
