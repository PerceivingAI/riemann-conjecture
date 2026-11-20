"""Independent complete signed quantities and physical projection boundaries."""
from fractions import Fraction
from types import SimpleNamespace

from flint import arb, ctx, fmpq
import pytest

from scripts.whole_source import analytic, producer
from scripts.whole_source.contract import QuantityKey, bind_problem, expected_domain


@pytest.fixture(scope="module")
def original():
    return bind_problem("retained-t081")


@pytest.fixture(scope="module")
def control(original):
    # A complete small algebra/analytic control, not an admissible research profile.
    return SimpleNamespace(N=6, M=12, K=2, support=original.support,
        active_terms=original.active_terms, kernel_coefficients=original.kernel_coefficients[:3],
        source_gauss_order=9, kappa=original.kappa, arithmetic=original.arithmetic,
        numerical_goal=original.numerical_goal)


def agree(source, independent, bits=160):
    difference = source-independent
    assert difference.contains(0)
    assert abs(difference).upper() < arb(2)**-bits


@pytest.mark.parametrize("m,n", [(0, 0), (2, 0), (2, 2), (4, 2), (3, 3), (6, 4), (7, 5), (8, 4), (10, 4)])
def test_full_residual_endpoint_low_and_band_agree(control, m, n):
    assert producer.residual_bilinear(control, m, n) == analytic.residual_bilinear(control, m, n)


@pytest.mark.parametrize("m,n", [(0, 0), (1, 1), (0, 4), (4, 0), (4, 4), (5, 5)])
def test_logarithmic_potential_and_complete_square_agree(m, n):
    with ctx.workprec(512):
        agree(producer.potential_bilinear(m, n), analytic.potential_bilinear(m, n), 350)
        agree(producer.potential_square(m, n), analytic.potential_square(m, n), 350)


def test_constant_logarithmic_integrals_have_closed_values():
    with ctx.workprec(512):
        log2 = arb(2).log()
        agree(producer.potential_bilinear(0, 0), 2-2*log2, 350)
        agree(analytic.potential_square(0, 0), 2*log2**2-4*log2+4-arb.pi()**2/6, 350)


@pytest.mark.parametrize("m,n", [(0, 0), (1, 1), (0, 4), (4, 0), (4, 4), (5, 5)])
def test_complete_signed_square_and_ordered_log_windows(control, m, n):
    with ctx.workprec(512):
        agree(producer.combined_square_entry(control, m, n), analytic.combined_square_entry(control, m, n), 300)
        agree(producer.ordered_vp(control, m, n), analytic.ordered_vp(control, m, n), 300)


def test_ordered_vp_is_not_replaced_by_its_transpose(control):
    with ctx.workprec(512):
        forward = analytic.ordered_vp(control, 0, 4)
        reverse = analytic.ordered_vp(control, 4, 0)
        assert not (forward-reverse).contains(0)


@pytest.mark.parametrize("n", [0, 1, 4, 5])
def test_full_physical_column_includes_head_and_correct_masses(control, n):
    with ctx.workprec(512):
        source, consumer = producer.operator_column(control, n), analytic.operator_column(control, n)
        for m, left, right in zip(range(n % 2, control.M, 2), source, consumer):
            agree(left, right, 300)
            linear = sum((analytic.signed_window_arithmetic(control, m, n, t, w)
                          for t in range(4) for w in range(2)), arb(0)) if m < control.M else arb(0)
            agree(left, linear+analytic.potential_bilinear(m, n), 300)


def test_full_exterior_pays_low_and_head_projection(control):
    with ctx.workprec(512):
        source_columns = {n: producer.operator_column(control, n) for n in (0, 4)}
        analytic_columns = {n: analytic.operator_column(control, n) for n in (0, 4)}
        source = producer.assemble_entry(control, 0, 4, source_columns)
        consumer = analytic.assemble_entry(control, 0, 4, analytic_columns)
        columns = analytic_columns
        for key in source:
            agree(source[key], consumer[key], 280)
        joint = consumer[("J_F", 0, 4)]
        low = sum((columns[0][k//2]*columns[4][k//2]*fmpq(2*k+1, 2)
                   for k in range(0, control.N, 2)), arb(0))
        head = sum((columns[0][k//2]*columns[4][k//2]*fmpq(2*k+1, 2)
                    for k in range(control.N, control.M, 2)), arb(0))
        agree(consumer[("G_exterior", 0, 4)], joint-low-head, 280)
        assert not head.contains(0)
        assert not low.contains(0)
        agree(consumer[("weighted_complete_tail", 0, 4)],
              consumer[("G_exterior", 0, 4)]*fmpq(control.kappa.numerator, control.kappa.denominator), 280)


def test_selected_component_domains_preserve_order_and_projection_extent(original):
    ordered = QuantityKey("VP", 0, entry=(original.N-2, 0))
    domain = expected_domain(original, ordered)
    assert tuple(domain.rows) == (original.N-2,) and tuple(domain.columns) == (0,)
    assert domain.symmetric_upper is False
    column = expected_domain(original, QuantityKey("F_column", 1))
    assert tuple(column.rows)[-1] == original.M-1
    assert tuple(column.columns)[-1] == original.N-1


def test_full_kernel_constant_integral_includes_every_endpoint_and_polar_term(original):
    expected = sum((fmpq(c.numerator, c.denominator)*fmpq(2**(d+3), (d+1)*(d+2))
                    for d, c in enumerate(original.kernel_coefficients)), fmpq(0))
    assert producer.residual_bilinear(original, 0, 0) == expected
    assert analytic.residual_bilinear(original, 0, 0) == expected


@pytest.mark.parametrize("m,n", [(86, 86), (88, 86), (87, 87), (826, 738), (826, 740),
                                (826, 824), (827, 825), (910, 824), (912, 824), (1650, 824)])
def test_declared_residual_boundary_and_exact_band(original, m, n):
    value = producer.residual_bilinear(original, m, n)
    assert value == analytic.residual_bilinear(original, m, n)
    if (m, n) in ((826, 738), (912, 824), (1650, 824)):
        assert value == 0
    if (m, n) in ((826, 740), (910, 824)):
        assert value != 0


def test_constant_combined_square_matches_all_ordered_signed_intersections(control):
    with ctx.workprec(512):
        support = arb(fmpq(control.support.numerator, control.support.denominator))
        images = []
        for term in control.active_terms:
            tau = arb(term.m).log()/support
            coefficient = -arb(term.prime).log()/arb(term.m).sqrt()
            for shift in (-tau, tau):
                images.append((shift, coefficient))
        total, same_power = arb(0), arb(0)
        for i, (left_shift, left_coefficient) in enumerate(images):
            for j, (right_shift, right_coefficient) in enumerate(images):
                lower = max(arb(-1), -1-left_shift, -1-right_shift)
                upper = min(arb(1), 1-left_shift, 1-right_shift)
                if lower < upper:
                    contribution = left_coefficient*right_coefficient*(upper-lower)
                    total += contribution
                    if i//2 == j//2:
                        same_power += contribution
        agree(producer.combined_square_entry(control, 0, 0), total, 300)
        assert not (total-same_power).contains(0)


@pytest.fixture(scope="module")
def complete_control(control):
    from scripts.whole_source.gram import residual_pairs, selected_pairs
    with ctx.workprec(768):
        modes = sorted({n for pair in selected_pairs(control) for n in pair})
        source_columns = {n: producer.operator_column(control, n) for n in modes}
        consumer_columns = {n: analytic.operator_column(control, n) for n in modes}
        source, consumer = {}, {}
        for m, n in selected_pairs(control):
            source.update(producer.assemble_entry(control, m, n, source_columns))
            consumer.update(analytic.assemble_entry(control, m, n, consumer_columns))
        for m, n in residual_pairs(control):
            source[("R_action", m, n)] = arb(producer.residual_bilinear(control, m, n))
            consumer[("R_action", m, n)] = arb(analytic.residual_bilinear(control, m, n))
        return source, consumer, source_columns


@pytest.mark.parametrize("omission", ["mixed_power", "vp_orientation", "low_projection",
                                     "head_projection", "inverse_mass", "low_endpoint", "band_terminal"])
def test_incomplete_expression_fails_after_structural_publication(tmp_path, original, control,
                                                                 complete_control, omission):
    from copy import deepcopy
    import hashlib
    from scripts.whole_source.artifacts import (
        Axis, ChunkStore, CodecBounds, CollectionLock, CollectionSpec, ContributionTask,
        QuantitySpec, encode_rational,
    )
    from scripts.whole_source.contract import ArtifactRef, ContractError, ROOT, quantity_document
    from scripts.whole_source.execution import _RUNTIME
    from scripts.whole_source.gram import COMPLETE, _record, check_entries, selected_keys
    source, independent, columns = complete_control
    keys = selected_keys(control)
    def rows(values):
        result = []
        for key in keys:
            m, n = key.entry
            record = _record(m, n, values[(key.name, m, n)])
            result.append({"quantity": quantity_document(key),
                           "lower": encode_rational(record.lower, 8192),
                           "upper": encode_rational(record.upper, 8192)})
        return result
    with ctx.workprec(768):
        positive, consumer = rows(source), rows(independent)
        check_entries(control, positive, consumer)
        changed = dict(source)
        pair = (0, control.N-2)
        key = ("G_exterior", *pair)
        if omission == "mixed_power":
            key = ("P_squared", 0, 0)
            separate = arb(0)
            for term in control.active_terms:
                one = SimpleNamespace(N=control.N, active_terms=(term,), support=control.support)
                separate += producer.combined_square_entry(one, 0, 0)
            changed[key] = separate
        elif omission == "vp_orientation":
            key = ("J_F", *pair)
            changed[key] = source[key]-source[("VP", pair[1], pair[0])]
        elif omission in ("low_projection", "head_projection"):
            indices = range(0, control.N, 2) if omission == "low_projection" else range(control.N, control.M, 2)
            changed[key] = source[key]+sum((columns[0][k//2]*columns[pair[1]][k//2]*fmpq(2*k+1, 2)
                                            for k in indices), arb(0))
        elif omission == "inverse_mass":
            changed[key] = source[("J_F", *pair)]-sum((a*b for a, b in zip(columns[0], columns[pair[1]])), arb(0))
        elif omission == "low_endpoint":
            key = ("R_action", 0, 0)
            c = control.kernel_coefficients[0]
            changed[key] = source[key]-4*arb(fmpq(c.numerator, c.denominator))
        else:
            key = ("R_action", control.N, control.N-2)
            assert not source[key].contains(0)
            changed[key] = arb(0)
        selected = QuantityKey(key[0], key[1] % 2, entry=key[1:])
        domain = expected_domain(original, selected)
        refs = []
        for name in sorted(_RUNTIME):
            raw = (ROOT/name).read_bytes()
            refs.append(ArtifactRef(name, hashlib.sha256(raw).hexdigest(), len(raw)))
        spec = CollectionSpec.create(original, role="producer",
            quantities=(QuantitySpec(selected, domain.rows, domain.columns, domain.symmetric_upper, COMPLETE),),
            partition=(("columns", 1), ("complete", 1), ("rows", 1)),
            backend="CONTROL_ONLY-exact-polynomial", backend_version="1", native_threads=1,
            code_refs=tuple(refs), bounds=CodecBounds(8*1024**2, 1024**2, 2*1024**2,
                512, 8192, 128*1024, 64*1024, 256*1024**2, 16*1024**2, 64*1024**2))
        with CollectionLock.acquire(tmp_path/"control", spec) as lock:
            (lock.root/"attempts/check").mkdir()
            lock.register_attempt("check")
            store = ChunkStore(lock, spec, attempt_id="check")
            task = ContributionTask(selected, domain.rows, domain.columns, COMPLETE)
            # This is a reduced, non-admissible mathematical control. Structural
            # validity is deliberately insufficient for analytical acceptance.
            staged = store.stage_chunk(task, (_record(*key[1:], changed[key]),))
            ref = store.publish_chunk(task, staged)
            record = store.read_chunk(ref).records[0]
            candidate = deepcopy(positive)
            for row in candidate:
                if row["quantity"] == quantity_document(selected):
                    row["lower"] = encode_rational(record.lower, 8192)
                    row["upper"] = encode_rational(record.upper, 8192)
            with pytest.raises(ContractError, match="containment failed"):
                check_entries(control, candidate, consumer)
