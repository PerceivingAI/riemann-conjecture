from __future__ import annotations

import builtins
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

import pytest
from flint import arb, ctx

from scripts import weil_multi_prime_schur_scout as scout_module
from scripts import weil_multi_prime_support_candidate_check as candidate_module
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.multi_prime_legendre_schur import assemble_multi_prime_schur


def test_multi_prime_scout_is_floating_and_reports_combined_prime_data() -> None:
    result = scout_module.scout(
        max_mode=24,
        quadrature_order=96,
        shift_order=64,
        n_values=[8, 12],
        support=Fraction(3, 5),
    )
    assert result["role"] == "floating_reconnaissance_only"
    assert [term["m"] for term in result["active_terms"]] == [2, 3]
    assert result["arithmetic_complement_loss_scout"] > 0
    rows = result["schur_rows"]
    assert len(rows) == 2
    assert set(rows[0]["component_tail_gram_operator_norms"]) == {"GV", "GP", "GR"}
    conditioning = rows[0]["combined_prime_conditioning"]
    assert conditioning["low_block_operator_norm"] > 0
    assert set(conditioning["per_term_tail_operator_norms"]) == {"2", "3"}


@pytest.fixture(autouse=True)
def forbid_test_only_acceptance_inputs(monkeypatch):
    forbidden = {"certificate-v2-cross-layer-v1.json", "multi-prime-admission-v2.json"}
    path_open, builtin_open = Path.open, builtins.open

    def guarded_path_open(path, *args, **kwargs):
        assert path.name not in forbidden, f"production read of test corpus: {path}"
        return path_open(path, *args, **kwargs)

    def guarded_builtin_open(path, *args, **kwargs):
        if isinstance(path, (str, Path)):
            assert Path(path).name not in forbidden, f"production read of test corpus: {path}"
        return builtin_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded_path_open)
    monkeypatch.setattr(builtins, "open", guarded_builtin_open)


@pytest.mark.parametrize("support", [Fraction(1, 4), Fraction(11, 20), Fraction(3, 5), Fraction(7, 10)])
def test_real_arithmetic_complement_diagnostics_enclose_each_term(support):
    with ctx.workprec(192):
        assembled = assemble_multi_prime_schur(
            n=8, prec=192, residual_order=16, support_num=support.numerator,
            support_den=support.denominator, require_positive_mu=False,
        )
        rows, contributions = candidate_module._active_term_diagnostics(assembled, 64)
    assert [row["m"] for row in rows] == [term.m for term in assembled["active_terms"]]
    for term, row, interval in zip(assembled["active_terms"], rows, contributions, strict=True):
        coefficient = arb_to_rational_enclosure(term.coefficient)
        bound = arb_to_rational_enclosure(assembled["arithmetic_norm_bounds"][term.m])
        products = [c * b for c in coefficient for b in bound]
        assert interval.lo <= min(products) <= max(products) <= interval.hi
        raw = row["complement_contribution"]
        assert interval.lo <= Fraction(raw["lower"]) <= Fraction(raw["upper"]) <= interval.hi
        assert Fraction(row["rounded_complement_contribution"]["lower"]) == interval.lo
        assert Fraction(row["rounded_complement_contribution"]["upper"]) == interval.hi
        assert interval.hi - interval.lo <= Fraction(raw["width"]) + Fraction(2, 1 << 64)


def _independent_dyadic_bounds(value, bits):
    lo, hi = arb_to_rational_enclosure(value)
    scale = 1 << bits
    return Fraction(lo.numerator * scale // lo.denominator, scale), \
        Fraction(-((-hi.numerator * scale) // hi.denominator), scale)


def _linear_bounds(coefficients, intervals):
    lower, upper = Fraction(0), Fraction(0)
    for coefficient, (lo, hi) in zip(coefficients, intervals, strict=True):
        products = (coefficient * lo, coefficient * hi)
        lower += min(products)
        upper += max(products)
    return lower, upper


def _independent_witness_margin(block, witness):
    # Signed exact interval linear combinations, without production congruence.
    n = len(block)
    left = [
        [_linear_bounds(row, [(block[k][j].lo, block[k][j].hi) for k in range(n)])
         for j in range(n)] for row in witness
    ]
    congruence = [[_linear_bounds(row, left[i]) for row in witness] for i in range(n)]
    return min(row[i][0] - sum(
        (max(abs(lo), abs(hi)) for j, (lo, hi) in enumerate(row) if j != i), Fraction(0),
    ) for i, row in enumerate(congruence))


@pytest.mark.parametrize(("prec", "matrix_bits", "witness_bits"), [
    (256, 64, 32), (256, 72, 40), (384, 64, 32),
])
def test_real_candidate_rounding_and_exact_witnesses_survive_independent_controls(
    prec, matrix_bits, witness_bits,
):
    witnesses = []
    make_witness = candidate_module.make_witness

    def observe(block, bits):
        witness, margin = make_witness(block, bits)
        witnesses.append((block, witness, margin))
        return witness, margin

    with patch.object(candidate_module, "make_witness", observe):
        result = candidate_module.run_candidate(
            Fraction(2, 5), dimension=40, prec=prec, comparison_prec=128,
            residual_order=32, matrix_bits=matrix_bits, witness_bits=witness_bits,
        )
    for (block, witness, margin), name in zip(
        witnesses, ("even_gershgorin_margin", "odd_gershgorin_margin"), strict=True,
    ):
        assert _independent_witness_margin(block, witness) == Fraction(result[name]) == margin
        assert margin > 0
        assert all(value.denominator <= 1 << witness_bits for row in witness for value in row)
    term = result["active_terms"][0]
    contribution = term["rounded_complement_contribution"]
    with ctx.workprec(prec):
        c_t = _independent_dyadic_bounds(candidate_module.c_T_enclosure(prec, 2, 5), matrix_bits)
        assembled = assemble_multi_prime_schur(n=40, prec=prec, residual_order=32, support_num=2, support_den=5)
        rho = _independent_dyadic_bounds(assembled["rho_R"], matrix_bits)
    expected_mu = candidate_module.harmonic(40) - c_t[1] - Fraction(contribution["upper"]) - rho[1]
    assert Fraction(result["mu_lower"]) == expected_mu > 0
    assert result["precision_contraction"]["all_reported_widths_nonincreasing"]
    rounded = {}
    for name in ("A", "GV", "GP", "GR"):
        rounded[name] = [[_independent_dyadic_bounds(value, matrix_bits) for value in row]
                         for row in assembled[name]]
        rounded_width = max(hi - lo for row in rounded[name] for lo, hi in row)
        assert rounded_width == Fraction(
            result["exact_rounding_diagnostics"]["matrix_widths"][name]["max_width"],
        )
        arb_width = max(hi - lo for row in assembled[name]
                        for lo, hi in (arb_to_rational_enclosure(value) for value in row))
        assert arb_width <= rounded_width <= arb_width + Fraction(2, 1 << matrix_bits)
    factor = Fraction(3) / expected_mu
    for parity, (block, _, _) in enumerate(witnesses):
        for i, original_i in enumerate(range(parity, 40, 2)):
            for j, original_j in enumerate(range(parity, 40, 2)):
                a_lo, a_hi = rounded["A"][original_i][original_j]
                gram_lo = sum((rounded[name][original_i][original_j][0]
                               for name in ("GV", "GP", "GR")), Fraction(0))
                gram_hi = sum((rounded[name][original_i][original_j][1]
                               for name in ("GV", "GP", "GR")), Fraction(0))
                assert (block[i][j].lo, block[i][j].hi) == (
                    a_lo - factor * gram_hi, a_hi - factor * gram_lo,
                )
    assert not result["theorem_status"]
    assert not result["independently_verified"]
    assert not result["automatic_promotion"]


def test_real_nonpositive_candidate_fails_at_exact_witness_gate():
    with pytest.raises(candidate_module.CandidateStageError) as error:
        candidate_module.run_candidate(
            Fraction(2, 5), dimension=24, prec=256, residual_order=32,
            matrix_bits=64, witness_bits=32,
        )
    assert error.value.stage == "witness"


def test_candidate_with_width_outside_binary64_reaches_exact_witness_gate(monkeypatch):
    def assemble_with_unresolved_gram(**kwargs):
        assembled = assemble_multi_prime_schur(**kwargs)
        assembled["GP"][0][0] += arb(0, arb("1e400"))
        return assembled

    monkeypatch.setattr(candidate_module, "assemble_multi_prime_schur", assemble_with_unresolved_gram)
    with pytest.raises(candidate_module.CandidateStageError) as error:
        candidate_module.run_candidate(
            Fraction(2, 5), dimension=24, prec=256, residual_order=32,
            matrix_bits=64, witness_bits=32,
        )
    assert error.value.stage == "witness"
