"""Exact whole-transform determinants, physical masses, and conditional outcomes."""
from copy import deepcopy
from fractions import Fraction
from itertools import permutations
from math import lcm
import builtins
import sys
from types import SimpleNamespace

import pytest

from scripts.whole_source import exact_global


class Tile:
    def __init__(self, data, i, j, rows, cols, entries):
        self.data = data
        self.i, self.j = i, j
        self.rows, self.cols = rows, cols
        self.entries = entries

    def nrows(self):
        return self.rows

    def ncols(self):
        return self.cols

    def __getitem__(self, key):
        r, c = key
        assert 0 <= r < self.rows and 0 <= c < self.cols
        self.entries.append((self.i + r, self.j + c))
        return self.data[self.i + r][self.j + c]


def reader(data, panel):
    calls, entries = [], []
    n = len(data)

    def read_tile(i, j):
        calls.append((i, j))
        return Tile(data, i, j, min(panel, n - i), min(panel, n - j), entries)

    return read_tile, calls, entries


def determinant(data):
    """Independent literal permutation expansion for small fixtures only."""
    total = 0
    for perm in permutations(range(len(data))):
        inversions = sum(perm[i] > perm[j] for i in range(len(data))
                         for j in range(i + 1, len(data)))
        term = (-1) ** inversions
        for i, j in enumerate(perm):
            term *= data[i][j]
        total += term
    return total


def modular(data, panel=2, workspace_bytes=1 << 20):
    pytest.importorskip("flint")
    read_tile, calls, entries = reader(data, panel)
    report = exact_global.full_modular_nonsingularity(
        len(data), panel, read_tile, workspace_bytes=workspace_bytes,
    )
    return report, calls, entries


def block(**changes):
    result = {
        "width": Fraction(1, 8), "goal": Fraction(1, 8),
        "modular_nonsingular": True, "margin": Fraction(3, 2),
        "tau": Fraction(2), "direction_upper": Fraction(1),
        "direction_mass": Fraction(1), "direction_index": 0,
    }
    result.update(changes)
    return result


def assessment(blocks, **changes):
    args = {"eta": Fraction(2), "m": Fraction(3),
            "b_K": Fraction(4), "delta": Fraction(1, 2)}
    args.update(changes)
    return exact_global.assess(blocks, **args)


def assert_no_admission(report):
    assert report["source_conditional"] is True
    assert report["analytical_source_acceptance"] is False
    assert report["production_admission"] is False


def test_full_matrix_singular_despite_invertible_diagonal_tiles():
    # Both diagonal tiles are I_2; the complete transform repeats its rows.
    data = [[1, 0, 1, 0], [0, 1, 0, 1],
            [1, 0, 1, 0], [0, 1, 0, 1]]
    report, calls, entries = modular(data)
    assert determinant([row[:2] for row in data[:2]]) == 1
    assert determinant([row[2:] for row in data[2:]]) == 1
    assert report["residue"] == 0
    assert report["nonsingular"] is False
    assert report["global_input_entries"] == 16
    assert calls == [(0, 0), (0, 2), (2, 0), (2, 2)]
    assert sorted(entries) == [(i, j) for i in range(4) for j in range(4)]


def test_zero_residue_is_unresolved_not_exact_singularity():
    data = [[65521, 0], [0, 1]]
    report, _, _ = modular(data, panel=1)
    assert determinant(data) == 65521
    assert report["prime"] == 65521
    assert report["residue"] == 0
    result = assessment([block(modular_nonsingular=report["nonsingular"]), block()])
    assert result["status"] == "UNRESOLVED_MODULAR_NONSINGULARITY"
    assert result["sigma"] is result["gamma"] is None
    assert_no_admission(result)


@pytest.mark.parametrize("panel", [1, 2, 3, 8])
def test_literal_complete_modulus_and_all_original_coordinates(panel):
    data = [[65522, -2, 3], [7, 2 * 65521 + 11, -13], [17, 19, 23]]
    report, calls, entries = modular(data, panel)
    assert report["residue"] == determinant(data) % 65521
    assert report["nonsingular"] is (determinant(data) % 65521 != 0)
    assert report["global_input_entries"] == 9
    assert report["word_payload_bytes"] == 72
    assert report["workspace_account_bytes"] >= 2 * 72
    assert calls == [(i, j) for i in range(0, 3, panel)
                     for j in range(0, 3, panel)]
    assert len(entries) == 9
    assert sorted(entries) == [(i, j) for i in range(3) for j in range(3)]
    assert all(type(value) in (int, bool) for value in report.values())


def test_modular_budget_rejected_before_import_allocation_or_tile_read(monkeypatch):
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        assert name != "flint", "FLINT import occurred before workspace admission"
        return original_import(name, *args, **kwargs)

    def forbidden_reader(i, j):
        pytest.fail("tile read occurred before workspace admission")

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    with pytest.raises(MemoryError, match="workspace"):
        exact_global.full_modular_nonsingularity(
            10**6, 16, forbidden_reader, workspace_bytes=1024,
        )


def test_budget_boundary_and_single_direct_modular_allocation(monkeypatch):
    flint = pytest.importorskip("flint")
    native_nmod_mat = flint.nmod_mat
    allocations = []

    def allocate(*args):
        allocations.append(args)
        return native_nmod_mat(*args)

    monkeypatch.setitem(sys.modules, "flint", SimpleNamespace(nmod_mat=allocate))
    data = [[1, 0], [0, 1]]
    read_tile, _, _ = reader(data, 1)
    account = 4 * (8 * 2 * 2) + 256 * 2 + 16384
    with pytest.raises(MemoryError):
        exact_global.full_modular_nonsingularity(2, 1, read_tile, workspace_bytes=account - 1)
    assert allocations == []
    report = exact_global.full_modular_nonsingularity(2, 1, read_tile, workspace_bytes=account)
    assert allocations == [(2, 2, 65521)]
    assert report["workspace_account_bytes"] == account
    assert report["residue"] == 1


@pytest.mark.parametrize("parity", [0, 1])
@pytest.mark.parametrize("panel", [1, 2, 3, 9])
@pytest.mark.parametrize("bits", [0, 3])
def test_mass_trace_matches_literal_physical_norms(parity, panel, bits):
    data = [[1, -2, 0, 3, 1], [0, 2, 1, 0, -3], [3, 0, -1, 4, 0],
            [-2, 5, 0, 1, 2], [19, -23, 29, -31, 37]]
    read_tile, calls, entries = reader(data, panel)
    report = exact_global.mass_trace(5, parity, bits, panel, read_tile)
    masses = [Fraction(2, 2 * (2 * i + parity) + 1) for i in range(5)]
    literal = [sum((masses[i] * Fraction(data[i][j], 1 << bits) ** 2
                    for i in range(5)), Fraction(0)) for j in range(5)]
    expected_lcm = lcm(*(mass.denominator for mass in masses))
    assert report == {
        "mass_lcm": expected_lcm,
        "mass_weights": [int(expected_lcm * mass) for mass in masses],
        "minimum_mass": masses[-1],
        "tau": sum(literal, Fraction(0)),
        "direction_masses": literal,
    }
    assert report["direction_masses"][-1] >= masses[-1] * Fraction(37, 1 << bits) ** 2
    assert calls == [(i, j) for i in range(0, 5, panel) for j in range(0, 5, panel)]
    assert len(entries) == 25
    assert sorted(entries) == [(i, j) for i in range(5) for j in range(5)]
    assert type(report["mass_lcm"]) is int
    assert all(type(value) is int for value in report["mass_weights"])
    assert all(type(value) is Fraction for value in report["direction_masses"])


@pytest.mark.parametrize("parity,expected", [(0, Fraction(2)), (1, Fraction(2, 3))])
def test_one_dimensional_mass_and_zero_transform(parity, expected):
    read_tile, _, _ = reader([[1]], 4)
    report = exact_global.mass_trace(1, parity, 0, 4, read_tile)
    assert report["minimum_mass"] == report["tau"] == expected
    read_zero, _, _ = reader([[0]], 4)
    zero = exact_global.mass_trace(1, parity, 0, 4, read_zero)
    assert zero["tau"] == 0
    assert type(zero["tau"]) is Fraction
    assert zero["direction_masses"] == [Fraction(0)]


def test_mass_trace_has_no_numerical_import(monkeypatch):
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        assert name not in {"flint", "numpy", "scipy", "math"}
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    read_tile, _, _ = reader([[3]], 1)
    assert exact_global.mass_trace(1, 1, 2, 1, read_tile)["tau"] == Fraction(3, 8)
    assert assessment([block(), block()])["positive_paid_lower"] is True


def test_positive_width_equality_and_full_gamma_formula():
    blocks = [block(), block(margin=Fraction(5), tau=Fraction(4))]
    before = deepcopy(blocks)
    report = assessment(blocks, control=True)
    assert blocks == before
    assert report == {
        "status": "PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL",
        "sigma": Fraction(3, 4), "gamma": Fraction(6, 17),
        "width_passed": True, "global_nonsingularity": True,
        "positive_paid_lower": True, "source_conditional": True,
        "control": True, "analytical_source_acceptance": False,
        "production_admission": False,
    }


def test_gamma_uses_eta_m_cap():
    report = assessment([block(margin=Fraction(100)), block(margin=Fraction(100))],
                        eta=Fraction(1), m=Fraction(1), b_K=Fraction(0), delta=Fraction(0))
    assert report["sigma"] == 50
    assert report["gamma"] == Fraction(1, 2)
    assert_no_admission(report)


@pytest.mark.parametrize("modular_ok", [False, True])
def test_width_failure_precedes_positive_negative_and_modular_outcomes(modular_ok):
    report = assessment([block(width=Fraction(1, 8) + Fraction(1, 10**30),
                               modular_nonsingular=modular_ok,
                               direction_upper=Fraction(-1)), block()])
    assert report["status"] == "WIDTH_GOAL_FAILED"
    assert report["width_passed"] is False
    assert report["positive_paid_lower"] is False
    assert report["sigma"] is report["gamma"] is None
    assert_no_admission(report)


def test_negative_direction_needs_nonzero_mass_not_global_nonsingularity():
    report = assessment([block(modular_nonsingular=False, direction_upper=Fraction(-1)), block()])
    assert report["status"] == "SELECTED_PAID_LOWER_NEGATIVE_NOT_WEIL_NEGATIVITY"
    assert report["global_nonsingularity"] is False
    assert report["positive_paid_lower"] is False
    assert report["sigma"] is report["gamma"] is None
    assert_no_admission(report)


@pytest.mark.parametrize("margin,tau", [(Fraction(0), Fraction(1)),
                                        (Fraction(-1), Fraction(1)),
                                        (Fraction(1), Fraction(0)),
                                        (Fraction(1), Fraction(-1))])
def test_nonpositive_margin_or_trace_never_passes(margin, tau):
    report = assessment([block(margin=margin, tau=tau), block()])
    assert report["status"] == "UNRESOLVED_PAID_LOWER"
    assert report["positive_paid_lower"] is False
    assert report["sigma"] is report["gamma"] is None
    assert_no_admission(report)


@pytest.mark.parametrize("modular_ok,expected", [
    (False, "UNRESOLVED_MODULAR_NONSINGULARITY"),
    (True, "UNRESOLVED_PAID_LOWER"),
])
def test_zero_transform_cannot_supply_a_negative_direction(modular_ok, expected):
    report = assessment([block(modular_nonsingular=modular_ok, margin=Fraction(0),
                               tau=Fraction(0), direction_upper=Fraction(-1),
                               direction_mass=Fraction(0)), block()])
    assert report["status"] == expected
    assert report["sigma"] is report["gamma"] is None
    assert_no_admission(report)


@pytest.mark.parametrize("field,value", [("width", 0.125), ("goal", True),
                                         ("tau", "2"), ("modular_nonsingular", 1),
                                         ("direction_index", True), ("direction_index", -1)])
def test_assess_rejects_inexact_or_wrong_scalar_types(field, value):
    with pytest.raises((TypeError, ValueError)):
        assessment([block(**{field: value}), block()])


@pytest.mark.parametrize("argument,value", [("eta", 0.5), ("m", True),
                                           ("b_K", "4"), ("delta", 0.0),
                                           ("control", 1)])
def test_assess_rejects_inexact_global_scalars(argument, value):
    with pytest.raises(TypeError):
        assessment([block(), block()], **{argument: value})


@pytest.mark.parametrize("argument,value", [("eta", 0), ("m", -1),
                                           ("b_K", -1), ("delta", -1)])
def test_assess_rejects_invalid_bound_signs(argument, value):
    with pytest.raises(ValueError):
        assessment([block(), block()], **{argument: value})


def test_assess_requires_both_parities_and_exact_fields():
    for blocks in ([], [block()], [block(), block(), block()],
                   [block(extra=Fraction(1)), block()]):
        with pytest.raises(ValueError):
            assessment(blocks)


@pytest.mark.parametrize("dimension,parity,bits,panel", [
    (0, 0, 0, 1), (2, 2, 0, 1), (2, 0, -1, 1), (2, 0, 0, 0),
    (True, 0, 0, 1), (2, True, 0, 1), (2, 0, 0.0, 1),
])
def test_mass_rejects_invalid_dimensions_and_exponents_before_read(dimension, parity, bits, panel):
    def forbidden_reader(i, j):
        pytest.fail("invalid input must not read a tile")

    with pytest.raises((TypeError, ValueError)):
        exact_global.mass_trace(dimension, parity, bits, panel, forbidden_reader)


def test_wrong_tile_shape_and_noninteger_entries_rejected():
    bad_shape, _, _ = reader([[1]], 1)
    with pytest.raises(ValueError, match="shape"):
        exact_global.mass_trace(2, 0, 0, 2, bad_shape)
    for value in (Fraction(1, 2), 1.0, True):
        read_tile, _, _ = reader([[value]], 1)
        with pytest.raises(TypeError):
            exact_global.mass_trace(1, 0, 0, 1, read_tile)


def test_native_integer_tile_support():
    flint = pytest.importorskip("flint")
    source = flint.fmpz_mat([[3, -5], [7, 11]])
    read_tile = lambda i, j: source
    mass = exact_global.mass_trace(2, 1, 1, 2, read_tile)
    assert mass["tau"] == Fraction(2, 3) * Fraction(34, 4) + Fraction(2, 7) * Fraction(170, 4)
    mod = exact_global.full_modular_nonsingularity(2, 2, read_tile, workspace_bytes=1 << 20)
    assert mod["residue"] == 68
