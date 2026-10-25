"""Small independent-auditor regressions, without source generation."""
from fractions import Fraction as Q
import hashlib
from pathlib import Path

from flint import arb, ctx, fmpq_mat
import pytest

from scripts import verify_m4_fourier_matrix as audit


def test_exact_json_and_fixed_identity_types():
    with pytest.raises(ValueError, match="duplicate JSON key"):
        audit.decode(b'{"a":1,"a":2}')
    with pytest.raises(ValueError, match="nonexact JSON"):
        audit.decode(b'{"a":1.5}')
    with pytest.raises(ValueError, match="not canonical"):
        audit.exact_q("2/4")
    assert not audit.same_exact([True, 4], [1, 4])
    assert not audit.same_exact(512.0, 512)


def test_all_ordered_domains_and_opposite_sign_22():
    with ctx.workprec(256):
        shifts = {m: arb(m).log() / audit.qarb(Q(3, 4)) for m in (2, 3, 4)}
        signed = [(m, sign) for m in (2, 3, 4) for sign in (-1, 1)]
        nonempty = opposite_22 = 0
        for m, sign in signed:
            for other, other_sign in signed:
                domain = audit.image_intersection(
                    sign * shifts[m], other_sign * shifts[other],
                    (m, sign) == (other, other_sign))
                expected = sign == other_sign or m == other == 2
                assert (domain is not None) == expected
                if domain is not None:
                    nonempty += 1
                    assert domain[1] > domain[0]
                    opposite_22 += int(m == other == 2 and sign != other_sign)
        assert nonempty == 20
        assert opposite_22 == 2
        with pytest.raises(ValueError, match="uncertified signed shift"):
            audit.image_intersection(arb(1, 1), arb(1, 1), False)


def test_fourth_coefficient_and_combined_gp(monkeypatch):
    monkeypatch.setattr(audit, "DIMENSION", 4)
    monkeypatch.setattr(audit, "ARITHMETIC_ORDER", 4)
    with ctx.workprec(256):
        p, square, gp = audit.arithmetic_matrices()
        t = audit.qarb(Q(3, 4))
        logs = {m: arb(m).log() for m in (2, 3, 4)}
        shifts = {m: logs[m] / t for m in logs}
        coefficients = {2: -logs[2] / arb(2).sqrt(),
                        3: -logs[3] / arb(3).sqrt(), 4: -logs[2] / 2}
        expected_p = 2 * sum((coefficients[m] * (2 - shifts[m])
                              for m in logs), arb(0))
        expected_square = 2 * sum((coefficients[m] * coefficients[n]
                                   * (2 - shifts[max(m, n)])
                                   for m in logs for n in logs), arb(0))
        expected_square += 2 * coefficients[2]**2 * (2 - 2 * shifts[2])
        assert p[0, 0].overlaps(expected_p)
        assert square[0, 0].overlaps(expected_square)
        expected_gp = square[0, 0] - sum((p[0, j] * p[j, 0]
                                          * audit.qarb(Q(2 * j + 1, 2))
                                          for j in range(4)), arb(0))
        assert gp[0, 0].overlaps(expected_gp)
        for matrix in (p, square, gp):
            assert matrix[0, 1] == 0


@pytest.mark.parametrize("argument", [Q(1, 1024), Q(191)])
def test_entire_transform_low_modes(monkeypatch, argument):
    monkeypatch.setattr(audit, "DIMENSION", 6)
    with ctx.workprec(768):
        w = audit.qarb(argument)
        values = audit.transform_vector(w)
        spherical = [w.sin() / w, (w.sin() / w - w.cos()) / w]
        for n in range(1, 5):
            spherical.append((2 * n + 1) * spherical[-1] / w - spherical[-2])
        for n, value in enumerate(spherical):
            assert values[n].overlaps(2 * (-1 if (n // 2) % 2 else 1) * value)
        with pytest.raises(ValueError, match="strict anchor range"):
            audit.transform_vector(arb(192))


def test_negative_odd_pole_and_physical_mass(monkeypatch):
    monkeypatch.setattr(audit, "DIMENSION", 4)
    with ctx.workprec(256):
        pole = audit.pole_matrix()
        t = audit.qarb(Q(3, 4))
        s = t / 2
        constant = 2 * s.sinh() / s
        linear = 2 * (s * s.cosh() - s.sinh()) / s**2
        assert pole[0, 0] > 0 and pole[1, 1] < 0
        assert pole[0, 0].overlaps(2 * t * constant**2)
        assert pole[1, 1].overlaps(-2 * t * linear**2)
        assert pole[0, 1] == 0


def test_exact_analytic_radius_and_stripped_order_width(monkeypatch):
    monkeypatch.setattr(audit, "DIMENSION", 2)
    error = Q(3, 2 * audit.GRID)
    assert audit.analytic_grid_radius(error, 0, 0) == 3
    assert audit.analytic_grid_radius(error, 1, 1) == 1
    error = Q(1, audit.GRID)
    # Raw diagonal widths are 4 and 8. Published widths add twice R.
    triangle = [[[-4, 4], [0, 0]], [[-5, 5]]]
    expected = Q(12, audit.GRID) + Q(97188, audit.GRID)
    assert audit.numerical_order_loss(triangle, error) == expected
    assert audit.numerical_order_loss([[[-2, 2], [0, 0]], [[-4, 4]]]) == Q(12, audit.GRID)
    with pytest.raises(ValueError, match="exceeds published interval"):
        audit.numerical_order_loss([[[0, 0], [0, 0]], [[0, 0]]], error)


def test_reports_are_measured_not_trusted(monkeypatch):
    monkeypatch.setattr(audit, "DIMENSION", 2)
    plain = [[[-1, 1], [0, 0]], [[-1, 1]]]
    inflated = [[[-3, 3], [0, 0]], [[-2, 2]]]
    matrices = {name: inflated if name in {"A", "band"} else plain
                for name in audit.MATRIX_NAMES}
    error = Q(1, audit.GRID)
    reports = {name: str(Q(97191 if name in {"A", "band"} else 3, audit.GRID))
               for name in matrices}
    source = {"quadrature_operator_error_upper": str(error),
              "numerical_order_loss_bounds": reports}
    assert audit.validate_numerical_bounds(source, matrices) == reports
    reports["A"] = "0"
    with pytest.raises(ValueError, match="dishonest numerical"):
        audit.validate_numerical_bounds(source, matrices)


def test_full_containment_and_exact_congruence(monkeypatch):
    monkeypatch.setattr(audit, "DIMENSION", 2)
    from flint import arb_mat
    triangle = [[[audit.GRID, audit.GRID], [0, 0]], [[audit.GRID, audit.GRID]]]
    assert audit.contain_triangle(triangle, arb_mat([[1, 0], [0, 1]]), "toy") == 3
    with pytest.raises(ValueError, match="not contained"):
        audit.contain_triangle(triangle, arb_mat([[2, 0], [0, 1]]), "toy")
    proof = {"transform": [["1"]], "claimed_margin": "3",
             "mass_normalized_gap_exact": "9/2"}
    assert audit.verify_block(fmpq_mat([[3]]), proof, 1)["exact_margin"] == "3"
    proof["claimed_margin"] = "4"
    with pytest.raises(ValueError, match="dishonest exact congruence"):
        audit.verify_block(fmpq_mat([[3]]), proof, 1)


def test_source_identity_and_source_byte_binding(monkeypatch, tmp_path):
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    monkeypatch.setattr(audit, "validate_complement", lambda _: None)
    producer = tmp_path / "scripts" / "weil_m4_fourier_matrix.py"
    producer.parent.mkdir()
    producer.write_bytes(b"fixed producer bytes")
    source = dict(audit.FIXED,
                  quadrature_operator_error_upper="1", matrices={name: [] for name in audit.MATRIX_NAMES},
                  complement={}, source_sha256=hashlib.sha256(producer.read_bytes()).hexdigest(),
                  scope=audit.SOURCE_SCOPE, numerical_order_loss_bounds={})
    raw = b"original source packet bytes"
    proof = dict(source, blocks={}, source_packet_sha256=hashlib.sha256(raw).hexdigest(),
                 status="COMPLETE_POSITIVE_SUFFICIENT_LOWER")
    audit.validate_identity(proof, raw, source)
    audit.validate_identity(source, raw, source, source_only=True)
    with pytest.raises(ValueError, match="byte binding"):
        audit.validate_identity(proof, raw + b" ", source)
    changed = dict(source, source_precision=True)
    with pytest.raises(ValueError, match="fixed full-matrix source"):
        audit.validate_identity(changed, raw, changed, source_only=True)
    producer.write_bytes(b"changed producer bytes")
    with pytest.raises(ValueError, match="producer identity"):
        audit.validate_identity(proof, raw, source)


def test_source_only_is_never_exact_only():
    with pytest.raises(ValueError, match="cannot be exact-only"):
        audit.audit(Path("absent"), Path("absent"), exact_only=True, source_only=True)
    with pytest.raises(ValueError, match="same file"):
        audit.audit(Path("one"), Path("two"), source_only=True)


def test_pinned_data_rejects_changed_bytes(monkeypatch, tmp_path):
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    (tmp_path / "pinned.json").write_bytes(b"{}\n")
    with pytest.raises(ValueError, match="source bytes changed"):
        audit.pinned_data("pinned.json", hashlib.sha256(b"{}").hexdigest())
