from __future__ import annotations

from fractions import Fraction
from types import SimpleNamespace

from flint import arb

from scripts import weil_multi_prime_schur_scout as scout_module
from scripts import weil_multi_prime_support_candidate_check as candidate_module


def _zero_matrix(n: int) -> list[list[arb]]:
    return [[arb(0) for _ in range(n)] for _ in range(n)]


def _fake_assembled(n: int) -> dict[str, object]:
    zero = _zero_matrix(n)
    a = _zero_matrix(n)
    for i in range(n):
        a[i][i] = arb(5)
    terms = (
        SimpleNamespace(
            m=2,
            prime=2,
            exponent=1,
            tau=arb("1.1"),
            coefficient=arb("0.01"),
        ),
        SimpleNamespace(
            m=3,
            prime=3,
            exponent=1,
            tau=arb("1.8"),
            coefficient=arb("0.01"),
        ),
    )
    return {
        "active_terms": terms,
        "arithmetic_norm_bounds": {2: arb(1), 3: arb(1)},
        "A": a,
        "GV": zero,
        "GP": zero,
        "GR": zero,
        "P": zero,
        "P_squared": zero,
        "mu": arb("0.5"),
        "rho_R": arb(0),
        "delta_R": arb(0),
    }


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


def test_multi_prime_candidate_reports_requested_diagnostics(monkeypatch) -> None:
    monkeypatch.setattr(
        candidate_module,
        "assemble_multi_prime_schur",
        lambda **kwargs: _fake_assembled(int(kwargs["n"])),
    )
    result = candidate_module.run_candidate(
        Fraction(3, 5),
        dimension=8,
        prec=128,
        comparison_prec=96,
        residual_order=16,
        matrix_bits=48,
        witness_bits=24,
    )
    assert result["role"] == "generator_side_exact_multi_prime_candidate_only"
    assert result["precision_bits"] == 128
    assert result["matrix_bits"] == 48
    assert result["witness_bits"] == 24
    assert [term["m"] for term in result["active_terms"]] == [2, 3]
    assert all("complement_contribution" in term for term in result["active_terms"])
    working = result["working_precision_diagnostics"]
    assert "GP" in working["matrix_widths"]
    conditioning = working["combined_prime_conditioning"]
    assert conditioning["active_term_count"] == 2
    assert "GP_max_width" in conditioning
    contraction = result["precision_contraction"]
    assert contraction["status"] == "compared"
    assert contraction["from_precision_bits"] == 96
    assert contraction["to_precision_bits"] == 128
    assert Fraction(result["mu_lower"]) > 0
    assert Fraction(result["even_gershgorin_margin"]) > 0
    assert Fraction(result["odd_gershgorin_margin"]) > 0
    assert result["all_margins_positive"] is True


def test_precision_comparison_is_optional_and_independent(monkeypatch) -> None:
    monkeypatch.setattr(
        candidate_module,
        "assemble_multi_prime_schur",
        lambda **kwargs: _fake_assembled(int(kwargs["n"])),
    )
    result = candidate_module.run_candidate(
        Fraction(3, 5),
        dimension=8,
        prec=160,
        residual_order=16,
        matrix_bits=64,
        witness_bits=32,
    )
    assert result["precision_bits"] == 160
    assert result["matrix_bits"] == 64
    assert result["witness_bits"] == 32
    assert result["comparison_precision_bits"] is None
    assert result["precision_contraction"]["status"] == "not_requested"


def test_new_stages_do_not_reuse_frozen_one_prime_stage_implementations() -> None:
    assert "require_one_prime_support" not in scout_module.__dict__
    assert "assemble_exact_prime_schur" not in candidate_module.__dict__
