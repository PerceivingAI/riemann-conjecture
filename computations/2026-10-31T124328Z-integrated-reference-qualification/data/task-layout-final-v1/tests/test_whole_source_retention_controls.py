"""Mathematical rejection semantics. Small fixtures here never qualify a full run."""
from dataclasses import asdict, replace
from fractions import Fraction
import hashlib
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace

import pytest
from flint import arb, ctx, fmpq, fmpz_mat

from scripts.whole_source import controls
from scripts.whole_source.artifacts import (
    CollectionLock, CollectionSpec, _publication_header, _raw, _task, decode_integer,
    decode_rational, publication_integers,
)
from scripts.whole_source.contract import ArtifactRef, ContractError, ROOT, bind_problem, canonical_bytes, QuantityKey
from scripts.whole_source.execution import _json, _write
from scripts.whole_source.pipeline import _bind, _tiles, prepare_source_inputs, scientific_manifest, write_source_execution, SourceReader
from scripts.whole_source.exact import IntegerTiles, integer_bounds, integer_congruence, paid_parameters
from scripts.whole_source.exact_global import assess, full_modular_nonsingularity, mass_trace


@pytest.fixture(scope='module')
def operands():
    cache = ROOT/'.pytest_cache'
    cache.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='mathematical-controls-', dir=cache) as temporary:
        directory = Path(temporary)
        inputs = prepare_source_inputs(bind_problem('retained-t081'), directory/'inputs',
            origin_git_commit='0'*40, origin_git_dirty=True, control=True, tile_modes=6)
        problem, _, roles = _bind(inputs['problem'], inputs['execution'], ROOT)
        spec = roles['producer'][0]
        original = directory/'original'
        with CollectionLock.acquire(original, spec):
            pass
        tiles = []
        bits = problem.arithmetic.publication_bits
        scale = 1 << bits
        for family, name in (('A_model', 'A_model'), ('weighted_head', 'head_complete'),
                             ('weighted_complete_tail', 'tail_complete')):
            for parity in (0, 1):
                domain = next(_tiles(spec, QuantityKey(name, parity)))
                records = [[m, n, hex(scale-1), hex(scale+1)] for m in domain.rows
                           for n in domain.columns if m <= n]
                raw = canonical_bytes({'header': _publication_header(spec, domain, bits), 'records': records})
                path = family+'-'+str(parity)+'.json'
                ref = _write(original/path, raw)
                tiles.append({'family': family, 'parity': parity, 'task': domain.to_dict(), 'artifact': asdict(ref)})
        document = scientific_manifest(spec, True, tiles)
        source_path = original/'source-manifest.json'
        _write(source_path, canonical_bytes(document))
        write_source_execution(source_path, spec, {'kind':'DECLARED_CONTROL'})
        reader = SourceReader(source_path, spec, control=True)
        yield directory, inputs, problem, reader


def test_variant_copies_only_verified_dependencies_without_aliasing_originals(operands, tmp_path):
    _, _, _, original = operands
    source = tmp_path/'original'
    shutil.copytree(original.path.parent, source)
    extra = b'unreferenced snapshot'
    (source/'snapshots'/hashlib.sha256(extra).hexdigest()).write_bytes(extra)
    reader = SourceReader(source/'source-manifest.json', original.spec, control=True)
    before = {p.relative_to(source): p.read_bytes() for p in source.rglob('*') if p.is_file()}
    path, _ = controls._variant(reader, tmp_path/'variant', 'wrong-low-constant', 'A_model')
    closure = {r.path: r for r in reader.spec.problem.evidence + reader.spec.code_refs}
    assert {p.name for p in (path.parent/'snapshots').iterdir()} == {r.sha256 for r in closure.values()}
    for ref in closure.values():
        local = ArtifactRef('snapshots/'+ref.sha256, ref.sha256, ref.size)
        assert _raw(path.parent, local, 8*1024*1024) == _raw(source, local, 8*1024*1024)
        assert not (path.parent/local.path).samefile(source/local.path)
    assert {p.relative_to(source): p.read_bytes() for p in source.rglob('*') if p.is_file()} == before


@pytest.mark.parametrize('damage', ['missing', 'corrupted'])
def test_variant_rejects_bad_stored_snapshot_before_publication(operands, tmp_path, damage):
    _, _, _, original = operands
    source = tmp_path/'original'
    shutil.copytree(original.path.parent, source)
    reader = SourceReader(source/'source-manifest.json', original.spec, control=True)
    ref = reader.spec.problem.evidence[0]
    stored = source/'snapshots'/ref.sha256
    original_raw = stored.read_bytes()
    if damage == 'missing':
        stored.unlink()
    else:
        stored.write_bytes(bytes([original_raw[0] ^ 1])+original_raw[1:])
    target = tmp_path/'variant'
    with pytest.raises(ContractError):
        controls._variant(reader, target, 'selected-paid-lower-negative')
    assert not (target/'source-manifest.json').exists()
    assert not (target/'source-execution.json').exists()
    assert (original.path.parent/'snapshots'/ref.sha256).read_bytes() == original_raw


def test_conflicting_snapshot_declarations_reject_at_collection_binding(operands):
    _, _, _, original = operands
    spec = original.spec
    conflict = replace(spec.problem.evidence[0], sha256='0'*64)
    refs = tuple(sorted((*spec.code_refs, conflict), key=lambda r: r.path))
    with pytest.raises(ContractError, match='conflicting implementation reference'):
        CollectionSpec.create(spec.problem, role=spec.role, quantities=spec.quantities,
            partition=spec.partition, backend=spec.backend, backend_version=spec.backend_version,
            native_threads=spec.native_threads, code_refs=refs, bounds=spec.bounds, grid_bits=spec.grid_bits)


@pytest.mark.parametrize('case', ['selected-paid-lower-negative', 'excessive-numerical-width'])
def test_source_variant_reaches_real_owned_exact_outcome(operands, proposal, monkeypatch, case):
    from scripts.whole_source import resources
    from scripts.whole_source.receipts import verify_stage
    directory, _, problem, source = operands
    path, core = proposal
    allocator = resources.auto_plan
    def allocate(template, *, parallel, memory_mib=None, helper_root=ROOT):
        return allocator(template, parallel=parallel, cpus=1, memory_mib=1536, helper_root=helper_root)
    monkeypatch.setattr(resources, 'auto_plan', allocate)
    output = directory/('exact-regression-'+case)
    result = controls._exact_case(problem, source, path, core, output, case, ROOT,
                                  {'origin_git_commit': '0'*40, 'origin_git_dirty': True})
    report = _json((output/'run/report.json').read_bytes())
    assert report['status'] == dict(controls.EXACT_CASES)[case]
    assert report['proof_scope'] == 'CONTROL_ONLY'
    assert report['assessment']['smooth_test_consequence_conditional'] is False
    assert report['production_admission'] is False
    if case == 'selected-paid-lower-negative':
        assert any(decode_rational(b['direction_upper'], 65536) < 0 and
                   decode_rational(b['direction_mass'], 65536) > 0 for b in report['blocks'])
    else:
        assert any(decode_rational(b['width'], 65536) > decode_rational(b['goal'], 65536)
                   for b in report['blocks'])
    assert result['passed'] is True
    for ref in result['receipt_bindings']:
        verify_stage(output/'run'/ref['path'])


def test_native_inclusive_containment_rejects_wrong_raw_enclosures():
    with ctx.workprec(1024):
        assert controls._native_contains((0, 8), 3, (0, 32), 5)
        assert controls._native_contains((0, 8), 3, (4, 28), 5)
        assert not controls._native_contains((0, 8), 3, (-1, 28), 5)
        assert not controls._native_contains((0, 8), 3, (4, 33), 5)
        # Hash correctness cannot make a false mathematical enclosure true.
        raw = canonical_bytes({'false': [hex(8), hex(9)]})
        assert len(hashlib.sha256(raw).hexdigest()) == 64
        assert not controls._native_contains((8, 9), 3, (0, 1), 5)


def test_prime5_omissions_have_independently_derived_signed_effects(operands):
    _, _, problem, _ = operands
    with ctx.workprec(problem.arithmetic.audit_bits):
        shifts = controls._prime5_shifts(problem)
        low = shifts['omitted-prime5-low-term']
        mixed = shifts['omitted-prime5-mixed-square']
        assert 0 < low[0] <= low[1]
        assert mixed[0] <= mixed[1] < 0
        t = arb(fmpq(81, 100))
        c5 = arb(5).log()/arb(5).sqrt()
        delta = 2-arb(5).log()/t
        scale = 1 << problem.arithmetic.publication_bits
        assert arb(fmpq(low[0], scale)) <= 2*c5*delta
        assert arb(fmpq(low[1], scale)) >= 2*c5*delta
        kappa = arb(fmpq(problem.kappa.numerator, problem.kappa.denominator))
        other = sum((arb(m).log()/arb(m).sqrt() for m in (2, 3)), arb(0)) + arb(2).log()/2
        expected = -4*kappa*delta*c5*other
        assert arb(fmpq(mixed[0], scale)) <= expected <= arb(fmpq(mixed[1], scale))


@pytest.mark.parametrize('case,family', [case for case in controls.SOURCE_CASES if case[1] is not None])
def test_rehashed_false_tiles_reach_native_consumer_and_reuse_unchanged_payloads(operands, case, family):
    directory, _, problem, original = operands
    with ctx.workprec(problem.arithmetic.audit_bits):
        shifts = controls._prime5_shifts(problem)
        path, mutations = controls._variant(original, directory/case, case, family, shifts)
        value = _json(path.read_bytes())
        assert len(mutations) == 1
        assert mutations[0]['changed_cells'] == 1
        selected = next(row for row in value['tiles'] if row['family'] == family and row['parity'] == 0)
        ref = ArtifactRef(**selected['artifact'])
        raw = _raw(path.parent, ref, original.spec.bounds.max_raw_bytes)
        integers = publication_integers(original.spec, raw, _task(selected['task']), original.bits)
        assert integers[0][:2] == (0, 0)
        assert not controls._native_contains(integers[0][2:], original.bits,
                                            ((1 << original.bits)-1, (1 << original.bits)+1), original.bits)
        original_rows = {(row['family'], row['parity']): row for row in original.document['tiles']}
        for row in value['tiles']:
            if row is selected:
                continue
            prior = original_rows[(row['family'], row['parity'])]
            assert row['artifact'] == prior['artifact']
            old = original.path.parent/row['artifact']['path']
            new = path.parent/row['artifact']['path']
            assert old.stat().st_ino == new.stat().st_ino
            assert old.read_bytes() == new.read_bytes()


def test_terminal_weight_control_retains_false_declaration_without_matrix_mutation(operands):
    directory, _, problem, original = operands
    originals = {row['artifact']['path']: (original.path.parent/row['artifact']['path']).read_bytes()
                 for row in original.document['tiles']}
    path = controls._terminal_declaration(problem, original.path, directory/'terminal-weight-declaration')
    retained = controls._record(path)
    declaration = _json(controls._bound_record(retained))
    assert declaration['frequency_inverse_weights'][:-1] == [str(x) for x in problem.inverse_weights[:-1]]
    assert declaration['frequency_inverse_weights'][-1] == '0'
    assert declaration['source'] == controls._record(original.path)['artifact']
    assert retained['artifact']['sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ContractError, match='frequency inverse weights must be positive'):
        controls._native_validate_inverse_weights(problem, declaration, declaration['source'])
    for relative, raw in originals.items():
        assert (original.path.parent/relative).read_bytes() == raw
    assert {entry.name for entry in path.parent.iterdir()} == {'frequency-inverse-weights.json'}
    with pytest.raises(ContractError, match='unknown false mathematical value'):
        controls._change('wrong-terminal-inverse-weight', 1, 2, original.bits, {})
    assert controls._change('omitted-complete-physical-exterior', 1, 2, original.bits, {}) == (0, 0)


def test_native_inverse_weight_predicate_accepts_only_complete_ordered_positive_declaration(operands):
    _, _, problem, original = operands
    source = controls._record(original.path)['artifact']
    document = {'format': 'whole-source-control-frequency-weights-v1',
                'problem_id': controls.problem_id(problem), 'source': source,
                'frequency_inverse_weights': [str(x) for x in problem.inverse_weights],
                'production_admission': False}
    assert problem.inverse_weights[-1] > 0
    assert controls._native_validate_inverse_weights(problem, document, source) == len(problem.inverse_weights)
    for terminal in ('0', '-1'):
        changed = {**document, 'frequency_inverse_weights': document['frequency_inverse_weights'][:-1]+[terminal]}
        with pytest.raises(ContractError, match='frequency inverse weights must be positive'):
            controls._native_validate_inverse_weights(problem, changed, source)
    reordered = list(document['frequency_inverse_weights'])
    different = next(i for i, weight in enumerate(reordered) if weight != reordered[-1])
    reordered[different], reordered[-1] = reordered[-1], reordered[different]
    with pytest.raises(ContractError, match='frequency inverse weights differ from bound declaration'):
        controls._native_validate_inverse_weights(problem, {**document, 'frequency_inverse_weights': reordered}, source)
    with pytest.raises(ContractError, match='incomplete frequency inverse-weight declaration'):
        controls._native_validate_inverse_weights(problem, {**document, 'frequency_inverse_weights': reordered[:-1]}, source)


def test_selected_negative_changes_actual_source_diagonals_not_just_report_status(operands):
    directory, _, _, original = operands
    path, mutations = controls._variant(original, directory/'negative-source', 'selected-paid-lower-negative')
    value = _json(path.read_bytes())
    assert len(mutations) == 2
    for row in value['tiles']:
        if row['family'] != 'A_model':
            continue
        raw = _raw(path.parent, ArtifactRef(**row['artifact']), original.spec.bounds.max_raw_bytes)
        entries = publication_integers(original.spec, raw, _task(row['task']), original.bits)
        for m, n, lo, hi in entries:
            expected = -Fraction(2, 2*m+1) if m == n else Fraction(0)
            assert Fraction(lo, 1 << original.bits) <= expected <= Fraction(hi, 1 << original.bits)
            if m == n:
                assert hi < 0


def test_reduced_model_cannot_obtain_required_controls_pass(operands):
    directory, inputs, _, original = operands
    with pytest.raises(ContractError, match='full retained mathematical target'):
        controls.run_controls(inputs['problem'], inputs['execution'], original.path,
            directory/'missing-audit.json', directory/'missing-proposal.json', directory/'missing-exact.json',
            directory/'forbidden-reduced-run')
    assert not (directory/'forbidden-reduced-run').exists()


def test_full_413_transform_zero_column_is_rejected_by_global_native_check():
    n, b = 413, 32
    def tile(i, j):
        return fmpz_mat([[int(i+r == j+c and j+c != 0)
                          for c in range(min(b, n-j))] for r in range(min(b, n-i))])
    report = full_modular_nonsingularity(n, b, tile, workspace_bytes=32*n*n+256*n+16384)
    assert report['global_input_entries'] == 413**2
    assert report['residue'] == 0
    assert report['nonsingular'] is False


class _Source:
    bits = 256
    def __init__(self, width):
        self.width = width
    def bounds(self, family, i, j):
        scale = 1 << self.bits
        if family == 'A_model':
            return (fmpz_mat([[-2*scale-self.width]]), fmpz_mat([[-2*scale+self.width]]))
        return fmpz_mat([[0]]), fmpz_mat([[0]])


@pytest.mark.parametrize('wide,expected', [(False, 'SELECTED_PAID_LOWER_NEGATIVE_NOT_WEIL_NEGATIVITY'),
                                          (True, 'WIDTH_GOAL_FAILED')])
def test_exact_outcomes_come_from_actual_congruence_arithmetic(tmp_path, wide, expected):
    """A scalar unit of the real full-transform consumer, not full qualification."""
    parameters = paid_parameters(256, Fraction(1), Fraction(1))
    context = {'problem_id': 'a'*64, 'source_sha256': 'b'*64, 'proposal_sha256': 'c'*64,
               'parity': 0, 'dimension': 1, 'panel_size': 1, 'u': 0, 'endpoint_bits': 259, 'z_bits': 1}
    context['product_bits'] = integer_bounds(context, parameters, Fraction(0))['product_bits']
    transform = IntegerTiles(tmp_path/'U', context)
    transform.put_values('Z', 0, 0, [1])
    masses = mass_trace(1, 0, 0, 1, transform.tile)
    products = IntegerTiles(tmp_path/'products', context)
    report = integer_congruence(_Source(1 << 256 if wide else 1), transform, products,
                               parameters, masses, Fraction(0))
    block = {key: report[key] for key in ('width', 'margin', 'tau', 'direction_upper', 'direction_mass', 'direction_index')}
    block.update(goal=Fraction(1, 1000), modular_nonsingular=True)
    result = assess([block, block], eta=Fraction(1), m=Fraction(1), b_K=Fraction(0), delta=Fraction(0))
    assert report['direction_upper'] < 0
    assert result['status'] == expected
    assert result['positive_paid_lower'] is False
    assert result['production_admission'] is False


@pytest.fixture(scope='module')
def proposal(operands):
    from scripts.whole_source.proposal import PanelStore, read_proposal, BITS, TRANSFORM_BITS, SCOPE
    from scripts.whole_source.execution import _RUNTIME
    from scripts.whole_source.slice import _ref
    from scripts.whole_source.contract import problem_id
    directory, _, problem, reader = operands
    original_dir = directory/'proposal-original'
    original_dir.mkdir()
    source = controls._record(reader.path)['artifact']
    policy = {'native_bits': BITS, 'working_grid_bits': BITS, 'transform_bits': TRANSFORM_BITS,
              'theta_bits': 40, 'panel_size': 2, 'logtheta_bounds': [-20, 20]}
    paths = sorted(set(_RUNTIME) | {'scripts/whole_source/proposal.py', 'scripts/whole_source/proposal_float.py'})
    code = [asdict(_ref(ROOT, path)) for path in paths]
    identity = controls._digest(canonical_bytes({'problem_id': problem_id(problem), 'source': source,
                                               'policy': policy, 'code': code}))
    diagnostics = _write(original_dir/'diagnostics.json', canonical_bytes({'purpose': 'unit fixture'}))
    blocks = []
    for p in (0, 1):
        context = {'proposal_id': identity, 'problem_id': problem_id(problem), 'source_sha256': source['sha256'],
                   'dimension': 3, 'panel_size': 2, 'precision_bits': BITS, 'grid_bits': BITS,
                   'transform_bits': TRANSFORM_BITS, 'parity': p}
        store = PanelStore(original_dir, context)
        panels = []
        for i in (0, 2):
            for j in (0, 2):
                name = f'Z/{i}/{j}'
                store.put(name, 'integer', [hex((1 << TRANSFORM_BITS)*int(r == c))
                          for r in range(i, min(i+2, 3)) for c in range(j, min(j+2, 3))])
                panels.append({'row': i, 'column': j, 'artifact': store.refs[name]})
        blocks.append({'parity': p, 'dimension': 3, 'u': TRANSFORM_BITS, 'theta': '1',
                       'context': context, 'integer_panels': panels, 'inherited_coordinates_used': False})
    core = {'format': 'whole-source-congruence-proposal-v1', 'status': 'NONPROOF_ONLY', 'scope': SCOPE,
            'problem_id': problem_id(problem), 'source': source, 'source_directory_at_execution': str(reader.path.parent),
            'source_control': True, 'policy': policy, 'code': code,
            'backend_versions': {'native': 'unit-fixture', 'floating': 'unit-fixture'},
            'diagnostics': asdict(diagnostics), 'blocks': blocks, 'analytical_acceptance': False,
            'matrix_positivity': False, 'production_admission': False}
    path = original_dir/'core.json'
    _write(path, canonical_bytes(core))
    read_proposal(path, problem, source)
    return path, core


def test_singular_proposal_rebinds_every_integer_panel_and_passes_real_consumer(operands, proposal):
    from scripts.whole_source.proposal import PanelStore, read_proposal, TRANSFORM_BITS
    directory, _, problem, reader = operands
    path, core = proposal
    source = controls._record(reader.path)['artifact']
    changed_source = directory/'rebound-source.json'
    _write(changed_source, canonical_bytes({'different': 'raw source identity'}))
    variant = controls._proposal_variant(problem, path, core, changed_source,
                                          directory/'singular-proposal', 'singular-full-U')
    checked = read_proposal(variant, problem, controls._record(changed_source)['artifact'])
    for block in checked['blocks']:
        store = PanelStore(variant.parent, block['context'],
                           {f"Z/{r['row']}/{r['column']}": r['artifact'] for r in block['integer_panels']})
        for i in (0, 2):
            values = [decode_integer(v, 8192) for v in store.read(f'Z/{i}/0', 'integer')]
            assert values[0] == (0 if block['parity'] == 0 or i != 0 else 1 << TRANSFORM_BITS)
    assert core['source'] == source
