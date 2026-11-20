"""Consumer-visible arithmetic, containment, normalization and recovery boundaries."""
from copy import deepcopy
from fractions import Fraction

from flint import arb, ctx, fmpq
import pytest

from scripts.whole_source import producer
from scripts.whole_source.artifacts import decode_rational, encode_rational
from scripts.whole_source.contract import ContractError, QuantityKey, bind_problem, quantity_document
from scripts.whole_source.slice import check_entries, selected_pairs


@pytest.fixture(scope="module")
def problem():
    return bind_problem("retained-t081")


@pytest.mark.parametrize("point", [fmpq(-1), fmpq(-3, 7), fmpq(0), fmpq(2, 5), fmpq(1)])
def test_streamed_recurrence_encloses_exact_requested_polynomials(point):
    with ctx.workprec(256):
        values = producer.legendre_values(arb(point), 19)
        for n, value in enumerate(values):
            assert value.contains(producer.basis(n)(point))
            assert value.rad() < arb(2)**-200


def candidates(problem):
    source, consumer = [], []
    # These exercise the exact gate, not a claim to compute the Weil entries.
    for m, n in selected_pairs(problem):
        key = QuantityKey("P_L" if m < problem.N else "P_H", m % 2, entry=(m, n))
        exact = Fraction(m+1, n+2)
        row = {"quantity": quantity_document(key), "covered": 8*problem.source_gauss_order,
               "lower": encode_rational(exact-Fraction(1, 1<<510), 8192),
               "upper": encode_rational(exact+Fraction(1, 1<<510), 8192)}
        # Gate inputs are dyadic, as are real published checkpoints.
        scale = 1<<512
        center = Fraction((exact*scale).__floor__(), scale)
        row["lower"] = encode_rational(center-Fraction(4, scale), 8192)
        row["upper"] = encode_rational(center+Fraction(4, scale), 8192)
        source.append(row)
        consumer.append({**row, "covered": 8, "lower": encode_rational(center-Fraction(1, scale), 8192),
                         "upper": encode_rational(center+Fraction(1, scale), 8192)})
    return source, consumer


def test_exact_mass_normalization_and_paid_publication_enclose(problem):
    source, independent = candidates(problem)
    report = check_entries(problem, source, independent)
    for (m, n), raw, checked in zip(selected_pairs(problem), source, report):
        lo, hi = (decode_rational(raw[k], 8192) for k in ("lower", "upper"))
        expansion = [decode_rational(v, 8192) for v in checked["head_expansion_checkpoint"]]
        assert expansion == [lo*Fraction(2*m+1, 2), hi*Fraction(2*m+1, 2)]
        public = [decode_rational(v, 8192) for v in checked["publication"]]
        assert public[0] < lo <= hi < public[1]
        radius = decode_rational(checked["endpoint_payment"]["selected_physical_radius_upper"], 8192)
        assert radius == (public[1]-public[0])/2*max(Fraction(2*m+1, 2), Fraction(2*n+1, 2))
        assert radius < problem.numerical_goal


def test_independent_outside_endpoint_rejected_after_valid_positive(problem):
    source, independent = candidates(problem)
    check_entries(problem, source, independent)
    bad = deepcopy(independent)
    bad[-1]["upper"] = encode_rational(decode_rational(source[-1]["upper"], 8192)+Fraction(1, 1<<512), 8192)
    with pytest.raises(ContractError, match="containment failed"):
        check_entries(problem, source, bad)


@pytest.mark.parametrize("fault", ["mass", "expansion", "node", "window", "mode", "width"])
def test_complete_gate_rejects_wrong_physical_math(problem, fault):
    source, independent = candidates(problem)
    check_entries(problem, source, independent)
    bad = deepcopy(source)
    m, n = selected_pairs(problem)[-1]
    if fault == "mass":
        bad[-1]["mass"] = encode_rational(Fraction(2, 2*n+1), 8192)
    elif fault == "expansion":
        bad[-1]["expansion"] = [encode_rational(decode_rational(bad[-1][k], 8192)*Fraction(2*n+1, 2), 8192)
                                  for k in ("lower", "upper")]
    elif fault == "node":
        bad[-1]["covered"] -= 1
    elif fault == "window":
        bad[-1]["covered"] //= 2
    elif fault == "mode":
        bad[-1]["quantity"]["entry"] = [n, m]
    else:
        bad[-1]["lower"] = encode_rational(Fraction(-100), 8192)
        bad[-1]["upper"] = encode_rational(Fraction(100), 8192)
    with pytest.raises(ContractError):
        check_entries(problem, bad, independent)
