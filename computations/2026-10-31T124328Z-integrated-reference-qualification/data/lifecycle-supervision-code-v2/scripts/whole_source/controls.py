"""Owned mathematical rejection controls over fresh, complete source expressions.

The analytical audit remains a prerequisite. Selected false-enclosure probes reuse
its independent raw reconstruction, not a report's asserted mathematical values.
Artificial exact operands never assert analytic truth or Weil negativity.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from fractions import Fraction
import hashlib
import os
from pathlib import Path

from scripts.whole_source.contract import ROOT, ArtifactRef, ContractError, canonical_bytes, problem_id
from scripts.whole_source.artifacts import (
    CollectionLock, CollectionSpec, _raw, _safe, _task, publication_integers,
    encode_integer, decode_integer,
)
from scripts.whole_source.execution import MIB, WorkloadExecution, _bytes, _json, _write, exact_telemetry
from scripts.whole_source.pipeline import SourceReader, _bind, _require, write_source_execution, verify_source_execution
from scripts.whole_source.slice import _ref, _request

SOURCE_CASES = (
    ('wrong-low-constant', 'A_model'),
    ('underpaid-weighted-head', 'weighted_head'),
    ('omitted-complete-physical-exterior', 'weighted_complete_tail'),
    ('wrong-terminal-inverse-weight', None),
    ('omitted-prime5-low-term', 'A_model'),
    ('omitted-prime5-mixed-square', 'weighted_complete_tail'),
)
EXACT_CASES = (
    ('singular-full-U', 'UNRESOLVED_MODULAR_NONSINGULARITY'),
    ('selected-paid-lower-negative', 'SELECTED_PAID_LOWER_NEGATIVE_NOT_WEIL_NEGATIVITY'),
    ('excessive-numerical-width', 'WIDTH_GOAL_FAILED'),
)
SCOPE = 'SELECTION_ONLY'


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _record(path):
    path = Path(path).resolve()
    raw = _bytes(path)
    return {'directory': str(path.parent), 'artifact': asdict(ArtifactRef(path.name, _digest(raw), len(raw)))}


def _bound_record(value):
    return _raw(Path(value['directory']), ArtifactRef(**value['artifact']), 8*1024*1024)


def _tile(reader, family, parity=0):
    for row in reader.document['tiles']:
        if row['family'] == family and row['parity'] == parity:
            domain = _task(row['task'])
            if 0 in domain.rows and 0 in domain.columns:
                raw = _raw(reader.path.parent, ArtifactRef(**row['artifact']), reader.spec.bounds.max_raw_bytes)
                return row, raw, publication_integers(reader.spec, raw, domain, reader.bits)
    raise ContractError('selected mathematical witness is absent')


def _prime5_shifts(problem):
    """Independent signed P0 edge-window formulas, outward at publication bits."""
    from flint import arb, fmpq
    from scripts.whole_source.pipeline import _fixed_bounds
    t = arb(fmpq(problem.support.numerator, problem.support.denominator))
    tau = arb(5).log()/t
    delta = 2-tau
    c5 = arb(5).log()/arb(5).sqrt()
    other = arb(2).log()/arb(2).sqrt()+arb(3).log()/arb(3).sqrt()+arb(2).log()/arb(4).sqrt()
    _require(delta > 0 and tau > 1, 'prime-five edge windows are not disjoint positive windows')
    for m in (2, 3, 4):
        shift = arb(m).log()/t
        _require(tau+shift > 2 and tau > shift, 'prime-five mixed overlap formula is not qualified')
    kappa = arb(fmpq(problem.kappa.numerator, problem.kappa.denominator))
    return {
        'omitted-prime5-low-term': _fixed_bounds(2*c5*delta, problem.arithmetic.publication_bits),
        'omitted-prime5-mixed-square': _fixed_bounds(-kappa*4*delta*c5*other, problem.arithmetic.publication_bits),
    }


def _change(case, lo, hi, bits, shifts):
    scale = 1 << bits
    if case == 'wrong-low-constant':
        return lo+2*scale, hi+2*scale
    if case == 'underpaid-weighted-head':
        return lo//2, -(-hi//2)
    if case == 'omitted-complete-physical-exterior':
        return 0, 0
    if case in shifts:
        lower, upper = shifts[case]
        return lo+lower, hi+upper
    if case == 'excessive-numerical-width':
        return lo-scale, hi+scale
    raise ContractError('unknown false mathematical value')


def _copy_variant_snapshots(reader, directory):
    """Copy the exact consumer's closure from stored source bytes, never the checkout."""
    closure = {}
    for ref in reader.spec.problem.evidence + reader.spec.code_refs:
        _require(ref.path not in closure or closure[ref.path] == ref, 'conflicting source snapshot')
        closure[ref.path] = ref
    cap = min(8*MIB, reader.spec.bounds.max_raw_bytes)
    _require(sum(ref.size for ref in closure.values()) <= min(32*MIB, reader.spec.bounds.max_snapshot_bytes),
             'source snapshot closure exceeds cap')
    _require(all(ref.size <= cap for ref in closure.values()), 'raw artifact exceeds cap')
    _safe(directory, 'snapshots', missing=True).mkdir()
    written = set()
    for ref in closure.values():
        local = ArtifactRef('snapshots/'+ref.sha256, ref.sha256, ref.size)
        raw = _raw(reader.path.parent, local, cap)
        if ref.sha256 not in written:
            _write(_safe(directory, local.path, missing=True), raw)
            _require(_raw(directory, local, cap) == raw, 'variant snapshot differs')
            written.add(ref.sha256)


def _variant(reader, directory, case, family=None, shifts=None):
    """Copy dependencies and change tiles. Unchanged scientific payloads share their inode."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    _copy_variant_snapshots(reader, directory)
    document = _json(canonical_bytes(reader.document))
    mutations = []
    for row in document['tiles']:
        ref = ArtifactRef(**row['artifact'])
        target = directory/ref.path
        target.parent.mkdir(parents=True, exist_ok=True)
        domain = _task(row['task'])
        selected = (case == 'selected-paid-lower-negative' and row['family'] == 'A_model') or (
            row['family'] == family and row['parity'] == 0 and 0 in domain.rows and 0 in domain.columns)
        if not selected:
            if not target.exists():
                from scripts.whole_source.storage import current_budget
                budget = current_budget(target)
                if budget is None:
                    os.link(reader.path.parent/ref.path, target)
                else:
                    budget.link(reader.path.parent/ref.path, target)
            continue
        raw = _raw(reader.path.parent, ref, reader.spec.bounds.max_raw_bytes)
        payload = _json(raw)
        changed = []
        changed_count = 0
        for entry in payload['records']:
            m, n = entry[:2]
            if case != 'selected-paid-lower-negative' and (m, n) != (0, 0):
                continue
            lo, hi = (decode_integer(x, reader.spec.bounds.max_endpoint_bits) for x in entry[2:])
            if case == 'selected-paid-lower-negative':
                value = -Fraction(2*(1 << reader.bits), 2*m+1) if m == n else Fraction(0)
                lower = value.numerator//value.denominator-1
                upper = -((-value.numerator)//value.denominator)+1
            else:
                lower, upper = _change(case, lo, hi, reader.bits, shifts or {})
            if case != 'selected-paid-lower-negative':
                _require((lower, upper) != (lo, hi), 'control did not change mathematical values')
            entry[2:] = [encode_integer(lower, reader.spec.bounds.max_endpoint_bits),
                         encode_integer(upper, reader.spec.bounds.max_endpoint_bits)]
            changed_count += int((lower, upper) != (lo, hi))
            if len(changed) < 4:
                changed.append({'row': m, 'column': n, 'before': [hex(lo), hex(hi)], 'after': entry[2:]})
        new_raw = canonical_bytes(payload)
        # Never replace a linked original payload.
        relative = 'variants/'+ref.sha256+'.json'
        new_ref = _write(directory/relative, new_raw)
        row['artifact'] = {**asdict(new_ref), 'path': relative}
        mutations.append({'family': row['family'], 'parity': row['parity'],
                          'original': asdict(ref), 'modified': row['artifact'],
                          'changed_cells': changed_count, 'sample_cells': changed})
    _require(mutations, 'empty mathematical variant')
    manifest = directory/'source-manifest.json'
    _write(manifest, canonical_bytes(document))
    write_source_execution(manifest, reader.spec, {
        'kind':'MATHEMATICAL_VARIANT','original_source':_record(reader.path),
        'original_execution':_record(reader.execution_path)})
    return manifest, mutations


def _positive(problem, source, independent, audit_path):
    """Recheck all raw analytical enclosures before admitting any false input."""
    audit = _json(_bytes(audit_path))
    expected = 3*(problem.N//2)*(problem.N//2+1)
    _require(audit['format'] == 'whole-source-analytical-receipt-v2' and
             audit['status'] == 'VERIFIED_ALL_DECLARED_SOURCE_ENTRIES' and
             audit['problem_id'] == problem_id(problem) and
             audit['source_manifest'] == asdict(source.ref) and
             audit['source_directory_at_execution'] == str(source.path.parent) and
             audit['source_scientific_id'] == source.spec.scientific_id and
             audit['analytic_scientific_id'] == independent.spec.scientific_id and
             audit['entries_checked'] == expected and audit['full_mathematical_source'] is True and
             audit['scope'] == 'FULL_DECLARED_SOURCE' and audit['production_admission'] is False,
             'fresh complete positive analytical audit is required')
    from scripts.whole_source.pipeline import verify_audit_execution
    verify_audit_execution(audit_path, source, independent)
    count, consumed = 0, hashlib.sha256()
    for (sr, produced), (ar, actual) in zip(source.tiles(), independent.tiles(), strict=True):
        _require((sr['family'], sr['parity'], sr['task']) == (ar['family'], ar['parity'], ar['task']),
                 'independent source domain differs')
        consumed.update(canonical_bytes(sr))
        for x, y in zip(produced, actual, strict=True):
            _require((x.row, x.column) == (y.row, y.column) and
                     x.lower <= y.lower <= y.upper <= x.upper,
                     'positive-first analytical containment failed')
            count += 1
    _require(count == expected and consumed.hexdigest() == audit['consumed_source_tiles_sha256'],
             'positive analytical raw inventory differs')
    return {'entries_checked': count, 'source_sha256': source.ref.sha256,
            'independent_manifest': _record(independent.path), 'audit': _record(audit_path)}


def _native_contains(proposed, proposed_bits, actual, actual_bits):
    """Apply Arb containment to exact dyadic endpoint enclosures."""
    from flint import arb, fmpq
    def ball(pair, bits):
        lo, hi = pair
        denominator = 1 << (bits+1)
        return arb(arb(fmpq(lo+hi, denominator)), arb(fmpq(hi-lo, denominator)))
    return bool(ball(proposed, proposed_bits).contains(ball(actual, actual_bits)))


def _terminal_declaration(problem, source_path, directory):
    """Retain the wrong terminal frequency weight without changing matrix bytes."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    weights = [str(value) for value in problem.inverse_weights]
    _require(weights, 'complete frequency inverse-weight declaration required')
    weights[-1] = '0'
    document = {'format': 'whole-source-control-frequency-weights-v1',
                'problem_id': problem_id(problem), 'source': _record(source_path)['artifact'],
                'frequency_inverse_weights': weights, 'production_admission': False}
    path = directory/'frequency-inverse-weights.json'
    _write(path, canonical_bytes(document))
    return path


def _native_validate_inverse_weights(problem, declaration, source_ref):
    """Check the full ordered declaration with native exact rational arithmetic."""
    from flint import fmpq
    _require(set(declaration) == {'format', 'problem_id', 'source', 'frequency_inverse_weights',
                                 'production_admission'} and
             declaration['format'] == 'whole-source-control-frequency-weights-v1' and
             declaration['problem_id'] == problem_id(problem) and
             declaration['source'] == source_ref and declaration['production_admission'] is False,
             'inverse-weight declaration context mismatch')
    weights = declaration['frequency_inverse_weights']
    _require(type(weights) is list and len(weights) == len(problem.inverse_weights) and
             all(type(value) is str and 0 < len(value) <= 4096 for value in weights),
             'incomplete frequency inverse-weight declaration')
    native = []
    for text in weights:
        value = Fraction(text)
        _require(str(value) == text, 'noncanonical frequency inverse weight')
        native.append(fmpq(value.numerator, value.denominator))
    _require(all(value > 0 for value in native), 'frequency inverse weights must be positive')
    expected = [fmpq(value.numerator, value.denominator) for value in problem.inverse_weights]
    _require(native == expected, 'frequency inverse weights differ from bound declaration')
    return len(native)


def evaluate_control(task, staging):
    """Native worker entry, evaluating serialized false values against independent bytes."""
    from scripts.whole_source import execution
    from flint import ctx
    staging._check()
    _require(execution._WORKER is not None and execution._WORKER[-1] is staging and
             execution._WORKER[0].role == 'analytic' and execution._WORKER[0].scope == SCOPE,
             'mathematical controls require their owned analytic worker')
    ctx.prec = staging.spec.problem.arithmetic.audit_bits
    if task['operation'] == 'prime5-shifts':
        return {'shifts': {key: [hex(x) for x in pair] for key, pair in
                           _prime5_shifts(staging.spec.problem).items()}, 'scope': SCOPE}
    _require(task['operation'] in ('containment', 'inverse-weights'), 'unknown mathematical control operation')
    problem, config, bound = _bind(task['problem_path'], task['execution_path'], ROOT)
    _require(config['control'] is False, 'reduced controls cannot qualify the complete source')
    variant_path = Path(task['variant']['directory'])/task['variant']['artifact']['path']
    _bound_record(task['variant'])
    variant = SourceReader(variant_path, bound['producer'][0], control=False)
    independent_path = Path(task['independent']['directory'])/task['independent']['artifact']['path']
    _bound_record(task['independent'])
    independent = SourceReader(independent_path, bound['analytic'][0], control=False)
    if task['operation'] == 'inverse-weights':
        declaration = _json(_bound_record(task['declaration']))
        try:
            _native_validate_inverse_weights(problem, declaration, asdict(variant.ref))
        except ContractError as error:
            _require(str(error) in ('frequency inverse weights must be positive',
                                    'frequency inverse weights differ from bound declaration'),
                     'terminal control failed outside the mathematical declaration predicate')
            return {'scope': SCOPE, 'status': 'REJECT_FALSE_INVERSE_WEIGHT_DECLARATION',
                    'passed': True, 'error': str(error), 'variant_sha256': variant.ref.sha256,
                    'declaration_sha256': task['declaration']['artifact']['sha256'],
                    'independent_sha256': independent.ref.sha256,
                    'predicate': 'native exact ordered inverse-weight equality and positivity',
                    'matrix_mutations': [], 'production_admission': False}
        return {'scope': SCOPE, 'status': 'FALSE_INVERSE_WEIGHT_DECLARATION_WAS_ACCEPTED',
                'passed': False, 'production_admission': False}
    _, _, proposed = _tile(variant, task['family'])
    _, _, actual = _tile(independent, task['family'])
    x, y = proposed[0], actual[0]
    _require(x[:2] == y[:2] == (0, 0), 'false witness coordinate differs')
    accepted = _native_contains(x[2:], variant.bits, y[2:], independent.bits)
    return {'scope': SCOPE, 'status': 'REJECT_FALSE_SOURCE_ENCLOSURE' if not accepted else
            'FALSE_SOURCE_WAS_ACCEPTED', 'passed': not accepted, 'family': task['family'],
            'cell': [0, 0], 'variant_sha256': variant.ref.sha256,
            'independent_sha256': independent.ref.sha256,
            'proposed': [hex(x[2]), hex(x[3])], 'actual': [hex(y[2]), hex(y[3])],
            'publication_bits': variant.bits, 'independent_bits': independent.bits,
            'reused_fresh_independent_reconstruction': True,
            'fresh_transcendental_reconstruction_per_case': False,
            'complete_source_audit': False, 'production_admission': False}


def _owned_controls(problem, base_spec, base_plan, directory, root):
    refs = {r.path: r for r in base_spec.code_refs}
    refs['scripts/whole_source/controls.py'] = _ref(root, 'scripts/whole_source/controls.py')
    refs['scripts/whole_source/producer.py'] = _ref(root,'scripts/whole_source/producer.py')
    spec = CollectionSpec.create(problem, role='analytic', quantities=base_spec.quantities,
        partition=base_spec.partition, backend=base_spec.backend, backend_version=base_spec.backend_version,
        native_threads=1, code_refs=tuple(refs[p] for p in sorted(refs)), bounds=base_spec.bounds, code_root=root)
    origin = directory/'control-origin.json'
    provenance = _json(_raw(root, base_plan.provenance, 8*1024*1024))
    _write(origin, canonical_bytes({'format': 'whole-source-code-origin-v1',
        'origin_git_commit': provenance['origin_git_commit'],
        'origin_git_dirty': provenance['origin_git_dirty'], 'files': [asdict(r) for r in spec.code_refs]}))
    plan = replace(base_plan, collection_sha256=spec.collection_id, task_program=refs['scripts/whole_source/controls.py'],
                   task_function='evaluate_control', provenance=_ref(root, origin.relative_to(root).as_posix()), scope=SCOPE)
    from scripts.whole_source.resources import auto_plan
    plan = auto_plan(plan, parallel=False, helper_root=root)
    spec = replace(spec, native_threads=plan.threads)
    spec._validate()
    plan = replace(plan, collection_sha256=spec.collection_id)
    return spec, plan


def _proposal_variant(problem, original_path, original, manifest, directory, case):
    """Bind all actual proposal integers to the changed source or singular U."""
    from scripts.whole_source.proposal import PanelStore
    directory.mkdir(parents=True, exist_ok=False)
    core = _json(canonical_bytes(original))
    source = _record(manifest)['artifact']
    core['source'] = source
    core['source_directory_at_execution'] = str(Path(manifest).parent)
    identity = _digest(canonical_bytes({'problem_id': problem_id(problem), 'source': source,
        'policy': core['policy'], 'code': core['code']}))
    diagnostics = ArtifactRef(**core['diagnostics'])
    _raw(original_path.parent, diagnostics, 8*1024*1024)
    target = directory/diagnostics.path
    target.parent.mkdir(parents=True, exist_ok=True)
    from scripts.whole_source.storage import current_budget
    budget = current_budget(target)
    if budget is None:
        os.link(original_path.parent/diagnostics.path, target)
    else:
        budget.link(original_path.parent/diagnostics.path, target)
    for block in core['blocks']:
        old = original['blocks'][block['parity']]
        refs = {f"Z/{r['row']}/{r['column']}": r['artifact'] for r in old['integer_panels']}
        prior = PanelStore(original_path.parent, old['context'], refs)
        block['context'].update(proposal_id=identity, source_sha256=source['sha256'])
        store = PanelStore(directory, block['context'])
        for panel in block['integer_panels']:
            i, j = panel['row'], panel['column']
            name = f'Z/{i}/{j}'
            values = list(prior.read(name, 'integer'))
            if case == 'singular-full-U' and block['parity'] == 0 and j == 0:
                b, n = block['context']['panel_size'], block['dimension']
                columns = min(b, n-j)
                for row in range(min(b, n-i)):
                    values[row*columns] = '0x0'
            store.put(name, 'integer', values)
            panel['artifact'] = store.refs[name]
    path = directory/'proposal-core.json'
    _write(path, canonical_bytes(core))
    return path


def _exact_case(problem, source, proposal_path, core, directory, name, root, provenance):
    from scripts.whole_source.exact import prepare_exact_inputs, run_exact_operands
    directory.mkdir(parents=True, exist_ok=False)
    manifest, mutations = (source.path, [])
    if name != 'singular-full-U':
        manifest, mutations = _variant(source, directory/'source', name,
                                       'A_model' if name == 'excessive-numerical-width' else None)
    variant_proposal = _proposal_variant(problem, proposal_path, core, manifest, directory/'proposal', name)
    raw = _bytes(variant_proposal)
    origin = {'kind': 'FRESH_NONPROOF', 'directory': str(variant_proposal.parent),
              'artifact': asdict(ArtifactRef(variant_proposal.name, _digest(raw), len(raw)))}
    inputs = prepare_exact_inputs(problem, manifest, variant_proposal, directory/'inputs',
        origin_git_commit=provenance['origin_git_commit'],
        origin_git_dirty=provenance['origin_git_dirty'], code_root=root)
    report = run_exact_operands(inputs['problem'], inputs['execution'], directory/'run', code_root=root)
    expected = dict(EXACT_CASES)[name]
    # A singular transform must have no positive margin. The exact assessment may
    # prioritize width, so bind its full modular result rather than infer singularity from status.
    if name == 'singular-full-U':
        passed = (report['blocks'][0]['modular']['residue'] == 0 and
                  report['blocks'][0]['modular']['nonsingular'] is False and
                  report['assessment']['positive_paid_lower'] is False)
    elif name == 'selected-paid-lower-negative':
        from scripts.whole_source.artifacts import decode_rational
        passed = (report['status'] == expected and any(
            decode_rational(row['direction_upper'], 65536) < 0 and
            decode_rational(row['direction_mass'], 65536) > 0 for row in report['blocks']))
    else:
        from scripts.whole_source.artifacts import decode_rational
        passed = (report['status'] == expected and any(
            decode_rational(row['width'], 65536) > decode_rational(row['goal'], 65536)
            for row in report['blocks']))
    return {'case': name, 'passed': passed, 'expected': expected, 'status': report['status'],
            'source': _record(manifest), 'proposal': origin, 'mutations': mutations,
            'operands': _record(inputs['operands']), 'report': _record(directory/'run/report.json'),
            'owned_receipts': report['owned_receipts'], 'receipt_bindings': report['receipt_bindings'],
            'artificial_mathematical_input': True, 'weil_negativity_claimed': False,
            'production_admission': False}


def run_controls(problem_path, execution_path, source_path, audit_path, proposal_path, exact_path,
                 output_dir, *, code_root=ROOT):
    """Require the complete positive audit, then retain nine owned rejection probes."""
    from scripts.whole_source.proposal import read_proposal
    root, output = Path(code_root).resolve(), Path(output_dir).resolve()
    output.relative_to(root)
    problem, config, bound = _bind(problem_path, execution_path, root)
    _require(config['control'] is False and (problem.N, problem.K, problem.M, problem.support) ==
             (826, 86, 1652, Fraction(81, 100)), 'full retained mathematical target required')
    output.mkdir(parents=True, exist_ok=False)
    from scripts.whole_source.retention import _capture_implementation, _complete_implementation
    _capture_implementation(problem,output,root,'controls')
    receipt = {'format': 'whole-source-mathematical-controls-v1', 'status': 'FAILED_REQUIRED_MATHEMATICAL_CONTROLS',
               'problem_id': problem_id(problem), 'cases': [], 'production_admission': False,
               'weil_negativity_claimed': False}
    try:
        source = SourceReader(source_path, bound['producer'][0], control=False)
        independent = SourceReader(Path(audit_path).parent/'analytic/source-manifest.json', bound['analytic'][0], control=False)
        receipt['positive_first'] = _positive(problem, source, independent, audit_path)
        core = read_proposal(proposal_path, problem, asdict(source.ref))
        _require(core['source_control'] is False, 'fresh full proposal required')
        full_exact = _json(_bytes(exact_path))
        proposal_path = Path(proposal_path).resolve()
        _require(full_exact['format'] == 'whole-source-exact-assessment-v1' and
                 full_exact['proof_scope'] == 'SOURCE_CONDITIONAL' and
                 full_exact['source']['manifest'] == asdict(source.ref) and
                 full_exact['source']['directory'] == str(source.path.parent) and
                 full_exact['proposal']['kind'] == 'FRESH_NONPROOF' and
                 _bound_record(full_exact['proposal']) == _bytes(proposal_path) and
                 len(full_exact['blocks']) == 2 and all(row['dimension'] == 413 for row in full_exact['blocks']) and
                 full_exact['production_admission'] is False, 'fresh full exact assessment binding differs')
        _require(full_exact['receipt_bindings'] and full_exact['owned_receipts'],
                 'full exact owned execution receipts are required')
        for ref in full_exact['receipt_bindings']:
            _raw(Path(exact_path).resolve().parent, ArtifactRef(**ref), 8*1024*1024)
        _raw(root, ArtifactRef(**full_exact['operands']), 8*1024*1024)
        receipt.update({'source': _record(source.path), 'proposal': _record(proposal_path),
                        'audit': _record(audit_path), 'exact': _record(exact_path),
                        'source_sha256': source.ref.sha256, 'proposal_sha256': _digest(_bytes(proposal_path)),
                        'audit_sha256': _digest(_bytes(audit_path)), 'exact_sha256': _digest(_bytes(exact_path))})
        spec, plan = _owned_controls(problem, *bound['analytic'], output, root)
        with CollectionLock.acquire(output/'native', spec) as lock:
            with WorkloadExecution(lock, spec, plan, code_root=root) as execution:
                execution.run_stage('prime5', [_request(operation='prime5-shifts')])
                result = next(execution.read_results('prime5'))['result']
                shifts = {key: tuple(int(x, 16) for x in pair) for key, pair in result['shifts'].items()}
                for name, family in SOURCE_CASES:
                    declaration = None
                    if name == 'wrong-terminal-inverse-weight':
                        declaration = _terminal_declaration(problem, source.path, output/name)
                        manifest, mutations = source.path, []
                    else:
                        manifest, mutations = _variant(source, output/name, name, family, shifts)
                    request = {'operation': 'inverse-weights' if declaration else 'containment', 'family': family,
                        'problem_path': str(Path(problem_path).resolve()), 'execution_path': str(Path(execution_path).resolve()),
                        'variant': _record(manifest), 'independent': _record(independent.path)}
                    if declaration:
                        request['declaration'] = _record(declaration)
                    task = _request(**request)
                    execution.run_stage(name, [task])
                    result = next(execution.read_results(name))['result']
                    expected = 'REJECT_FALSE_INVERSE_WEIGHT_DECLARATION' if declaration else 'REJECT_FALSE_SOURCE_ENCLOSURE'
                    case = {'case': name, 'passed': result['passed'], 'expected': expected,
                            'source': _record(manifest), 'mutations': mutations, 'result': result,
                            'owned_receipts': exact_telemetry(execution.receipts[-1:]),
                            'receipt': _record(execution.output/name/'receipt.json'), 'production_admission': False}
                    if declaration:
                        case['declaration'] = _record(declaration)
                        case['weight_mutation'] = {'index': len(problem.inverse_weights)-1,
                            'declared': str(problem.inverse_weights[-1]), 'false': '0',
                            'field': 'frequency_inverse_weights'}
                    _write(output/name/'case-result.json', canonical_bytes(case))
                    receipt['cases'].append(case)
                receipt['native_owned_receipts'] = exact_telemetry(execution.receipts)
        provenance = _json(_raw(root, bound['analytic'][1].provenance, 8*1024*1024))
        for name, _ in EXACT_CASES:
            case = _exact_case(problem, source, proposal_path, core, output/name, name, root, provenance)
            _write(output/name/'case-result.json', canonical_bytes(case))
            receipt['cases'].append(case)
        _require(len(receipt['cases']) == 9 and all(row['passed'] for row in receipt['cases']),
                 'required mathematical control did not produce its expected semantic outcome')
        receipt['status'] = 'PASS_REQUIRED_MATHEMATICAL_CONTROLS'
    except BaseException as error:
        receipt['error_type'], receipt['error'] = type(error).__name__, str(error)
        _write(output/'controls-receipt.json', canonical_bytes(receipt))
        raise
    _write(output/'controls-receipt.json', canonical_bytes(receipt))
    _complete_implementation(output,root,{'controls':_record(output/'controls-receipt.json')})
    return receipt
