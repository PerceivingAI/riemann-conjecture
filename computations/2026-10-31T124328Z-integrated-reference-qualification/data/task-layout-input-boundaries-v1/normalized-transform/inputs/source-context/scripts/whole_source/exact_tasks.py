"""Complete integer contractions split at owned dependency-wave seams."""
from dataclasses import asdict
from fractions import Fraction
import hashlib
from pathlib import Path
import uuid

from scripts.whole_source.contract import ArtifactRef, ContractError, canonical_bytes
from scripts.whole_source.artifacts import _raw, _safe, _check_quota, _volume_gate, decode_integer
from scripts.whole_source.execution import MIB, _json, _write
from scripts.whole_source.task_groups import read_group, seal_group, group_tasks

LAYOUT = 'whole-source-exact-dependency-layout-v1'


def _require(value, message):
    if not value:
        raise ContractError(message)


def layout(descriptor):
    blocks = [{'parity': p, 'dimension': block['context']['dimension'],
               'panel_size': block['context']['panel_size']} for p, block in enumerate(descriptor['blocks'])]
    counts = [(row['dimension']+row['panel_size']-1)//row['panel_size'] for row in blocks]
    return {'format': LAYOUT, 'blocks': blocks,
            'max_wave_tasks': max(2, sum(counts), sum(q*(q+1)//2 for q in counts))}


def _context(descriptor, operands, operation):
    return {'format': LAYOUT, 'operands': operands, 'operation': operation,
            'contexts': [block['context'] for block in descriptor['blocks']]}


def _expected(descriptor, operation):
    names = set()
    for p, block in enumerate(descriptor['blocks']):
        n, b = block['context']['dimension'], block['context']['panel_size']
        if operation in ('global', 'reduce'):
            names.add(f'{operation}/{p}')
        elif operation == 'first':
            for i in range(0, n, b):
                names.add(f'row/{p}/{i}')
                names.update(f'{p}/{family}/{i}/{j}' for family in ('J', 'S') for j in range(0, n, b))
        elif operation == 'second':
            names.update(f'block/{p}/{i}/{j}' for i in range(0, n, b) for j in range(i, n, b))
        else:
            raise ContractError('unknown exact dependency operation')
    return names

def _wave(task, descriptor, operation, *, expected_root, expected_attempt):
    context = _context(descriptor, task['operands'], operation)
    record = task['groups'][operation]
    root, outputs = read_group(record, context, expected_root=expected_root, expected_attempt=expected_attempt)
    _require(set(outputs) == _expected(descriptor, operation), 'incomplete exact dependency wave cover')
    seen, covered = set(), set()
    expected = set()
    for p, block in enumerate(descriptor['blocks']):
        n, b = block['context']['dimension'], block['context']['panel_size']
        coordinates = ([()] if operation in ('global', 'reduce') else
                       [(i,) for i in range(0, n, b)] if operation == 'first' else
                       [(i, j) for i in range(0, n, b) for j in range(i, n, b)])
        expected.update((p, *coordinates_) for coordinates_ in coordinates)
    for original, result in group_tasks(record, context, expected_root=expected_root, expected_attempt=expected_attempt):
        _validate_task(original, operation)
        _require(original['operands'] == task['operands'], 'foreign exact dependency operands')
        for name, dependency in original['groups'].items():
            if name in task['groups']:
                _require(dependency == task['groups'][name], 'foreign exact predecessor wave')
        key = (original['parity'], *(original[name] for name in ('row', 'column') if name in original))
        _require(key in expected and key not in seen, 'repeated or foreign exact dependency task')
        seen.add(key)
        named = _result_outputs(original, result, descriptor)
        for name, authority in named.items():
            _require(name in outputs and name not in covered, 'repeated exact output attribution')
            ref = ArtifactRef(**outputs[name])
            _require((ref.sha256, ref.size) == authority, 'exact output differs from its assigned task')
            covered.add(name)
    _require(seen == expected and covered == set(outputs), 'incomplete exact task/output provenance')
    return root, outputs


def _validate_task(task, operation):
    fields = {'global': set(), 'first': {'row'}, 'second': {'row', 'column'}, 'reduce': set()}
    dependencies = {'global': set(), 'first': {'global'}, 'second': {'global', 'first'},
                    'reduce': {'global', 'first', 'second'}}
    _require(operation in fields and type(task) is dict and
             set(task) == {'task_id', 'operation', 'parity', 'operands', 'groups'} | fields[operation] and
             task['operation'] == operation and type(task['groups']) is dict and
             set(task['groups']) == dependencies[operation] and
             type(task['parity']) is int and task['parity'] in (0, 1) and
             all(type(task[name]) is int for name in fields[operation]),
             'unknown exact dependency task fields')
    identity = {key: value for key, value in task.items() if key != 'task_id'}
    _require(task['task_id'] == hashlib.sha256(canonical_bytes(identity)).hexdigest(), 'changed exact task identity')


def _result_outputs(task, result, descriptor):
    from scripts.whole_source.exact import SCOPE
    operation, p = task['operation'], task['parity']
    _require(type(result) is dict and result.get('scope') == SCOPE, 'changed exact task scope')
    def scalar(value):
        raw = canonical_bytes(value)
        return hashlib.sha256(raw).hexdigest(), len(raw)
    def artifact(value):
        ref = ArtifactRef(**value)
        return ref.sha256, ref.size
    if operation in ('global', 'reduce'):
        field = 'metadata' if operation == 'global' else 'report'
        _require(set(result) == {field, 'scope'}, 'unexpected exact global/reduction output')
        return {f'{operation}/{p}': scalar(result[field])}
    if operation == 'first':
        context = descriptor['blocks'][p]['context']
        i, n, b = task['row'], context['dimension'], context['panel_size']
        expected = {f'{family}/{i}/{j}' for family in ('J', 'S') for j in range(0, n, b)}
        _require(set(result) == {'panels', 'metadata', 'scope'} and type(result['panels']) is dict and
                 set(result['panels']) == expected, 'incomplete exact row panel cover')
        return {f'row/{p}/{i}': scalar(result['metadata']),
                **{f'{p}/{name}': artifact(value) for name, value in result['panels'].items()}}
    _require(set(result) == {'block', 'scope'}, 'unexpected exact block outputs')
    return {f"block/{p}/{task['row']}/{task['column']}": artifact(result['block'])}


def _metadata(root, outputs, name):
    return _json(_raw(root, ArtifactRef(**outputs[name]), 8*MIB))


def _globals(task, descriptor, staging):
    from scripts.whole_source.exact import _fraction
    root, outputs = _wave(task, descriptor, 'global', expected_root=staging.root, expected_attempt=staging.attempt_id)
    p = task['parity']
    value = _metadata(root, outputs, f'global/{p}')
    _require(set(value) == {'context', 'masses', 'modular'} and
             canonical_bytes(value['context']) == canonical_bytes(descriptor['blocks'][p]['context']), 'changed exact global context')
    masses = dict(value['masses'])
    for key in ('minimum_mass', 'tau'):
        masses[key] = _fraction(masses[key])
    masses['direction_masses'] = [_fraction(item) for item in masses['direction_masses']]
    return masses, value['modular']


def _stage_document(staging, document):
    raw = canonical_bytes(document)
    _require(len(raw) <= 8*MIB, 'exact output block exceeds codec')
    staging._check()
    name = 'attempts/'+staging.attempt_id+'/staging/'+uuid.uuid4().hex
    with _volume_gate(staging.root):
        _check_quota(staging.root, staging.spec.bounds, len(raw), len(raw))
        _write(_safe(staging.root, name, missing=True), raw)
    staging._check()
    return asdict(ArtifactRef(name, hashlib.sha256(raw).hexdigest(), len(raw)))


def _block_values(raw, context, i, j, account):
    from scripts.whole_source.exact import _shape
    rows, columns = _shape(context, i, j)
    data = _json(raw)
    _require(set(data) == {'format', 'context', 'row', 'column', 'center', 'radius'} and
             data['format'] == 'whole-source-exact-output-block-v1' and
             canonical_bytes(data['context']) == canonical_bytes(context) and
             type(data['row']) is type(data['column']) is int and data['row'] == i and data['column'] == j and i <= j,
             'changed exact output block context')
    _require(type(data['center']) is type(data['radius']) is list and
             len(data['center']) == len(data['radius']) == rows*columns, 'incomplete exact output block')
    center = [decode_integer(item, account['paid_bits']) for item in data['center']]
    radius = [decode_integer(item, account['transformed_bits']) for item in data['radius']]
    _require(all(value >= 0 for value in radius), 'negative exact transformed radius')
    return data, center, radius


def evaluate(task, staging, descriptor, reader, worker):
    from scripts.whole_source import exact as e
    operation = task['operation']
    _validate_task(task, operation)
    p = task['parity']
    block = descriptor['blocks'][p]
    context = block['context']
    n, b = context['dimension'], context['panel_size']
    parameters = e.paid_parameters(reader.bits, Fraction(block['theta']), staging.spec.problem.eta)
    account = e.integer_bounds(context, parameters, staging.spec.problem.model_error)
    _require(account['private_bytes'] <= worker[0].worker_private_mib*MIB and
             account['modular_workspace_bytes'] <= worker[0].native_workspace_mib*MIB and
             account['staged_bytes'] <= staging.spec.bounds.max_temporary_bytes,
             'exact dependency task exceeds admitted account')
    transform = e.IntegerTiles(e.ROOT, context, block['panels'])
    if operation == 'global':
        masses = e.mass_trace(n, p, context['u'], b, transform.tile)
        _require(masses['mass_lcm'] == account['mass_lcm'], 'physical mass account mismatch')
        modular = e.full_modular_nonsingularity(n, b, transform.tile,
                                               workspace_bytes=worker[0].native_workspace_mib*MIB)
        return {'metadata': {'context': context, 'masses': masses, 'modular': modular}, 'scope': e.SCOPE}
    masses, modular = _globals(task, descriptor, staging)
    if operation == 'first':
        from flint import fmpz_mat
        i = task['row']
        rows, _ = e._shape(context, i, 0)
        source = e.SourceIntegers(reader, context)
        store = e.IntegerTiles(staging.root, context, staging=staging)
        source_rows = [0]*rows
        centers, radii = [], []
        for k in range(0, n, b):
            center, radius = e.paid_integer_tiles(source, i, k, parameters)
            centers.append(center)
            radii.append(radius)
            for r in range(rows):
                source_rows[r] += sum(int(radius[r, c]) for c in range(radius.ncols()))
        for j in range(0, n, b):
            J, S = fmpz_mat(rows, min(b, n-j)), fmpz_mat(rows, min(b, n-j))
            for index, k in enumerate(range(0, n, b)):
                Z = transform.tile(k, j)
                J += centers[index]*Z
                S += radii[index]*e._absolute(Z)
            store.put('J', i, j, J)
            store.put('S', i, j, S)
        return {'panels': store.created, 'metadata': {'context': context, 'row': i,
                'row_sums': [hex(value) for value in source_rows], 'consumed': sorted(source.consumed)}, 'scope': e.SCOPE}
    first_root, first = _wave(task, descriptor, 'first', expected_root=staging.root, expected_attempt=staging.attempt_id)
    if operation == 'second':
        from flint import fmpz_mat
        i, j = task['row'], task['column']
        rows, cols = e._shape(context, i, j)
        _require(i <= j, 'lower exact output block is not assigned')
        refs = {name.split('/', 1)[1]: value for name, value in first.items() if name.startswith(str(p)+'/')}
        products = e.IntegerTiles(first_root, context, refs)
        B0, En, G = (fmpz_mat(rows, cols) for _ in range(3))
        for k in range(0, n, b):
            Zi, Zj = transform.tile(k, i), transform.tile(k, j)
            B0 += Zi.transpose()*products.tile(k, j, 'J')
            En += e._absolute(Zi).transpose()*products.tile(k, j, 'S')
            weighted = fmpz_mat(Zj.nrows(), Zj.ncols())
            for r in range(Zj.nrows()):
                for c in range(Zj.ncols()):
                    weighted[r, c] = masses['mass_weights'][k+r]*Zj[r, c]
            G += Zi.transpose()*weighted
        lam = staging.spec.problem.model_error
        Bn = B0*(lam.denominator*masses['mass_lcm'])-G*(lam.numerator*parameters['Q'])
        data = {'format': 'whole-source-exact-output-block-v1', 'context': context, 'row': i, 'column': j,
                'center': [hex(int(Bn[r, c])) for r in range(rows) for c in range(cols)],
                'radius': [hex(int(En[r, c])) for r in range(rows) for c in range(cols)]}
        _block_values(canonical_bytes(data), context, i, j, account)
        return {'block': _stage_document(staging, data), 'scope': e.SCOPE}
    from flint import fmpz_mat
    second_root, second = _wave(task, descriptor, 'second', expected_root=staging.root, expected_attempt=staging.attempt_id)
    source_rows, consumed = [], set()
    expected_consumed = {(row['artifact']['path'], row['artifact']['sha256'], row['artifact']['size'])
                         for row in reader.document['tiles'] if row['parity'] == p}
    for i in range(0, n, b):
        value = _metadata(first_root, first, f'row/{p}/{i}')
        _require(set(value) == {'context', 'row', 'row_sums', 'consumed'} and
                 canonical_bytes(value['context']) == canonical_bytes(context) and
                 type(value['row']) is int and value['row'] == i and
                 type(value['row_sums']) is list and len(value['row_sums']) == min(b, n-i) and
                 type(value['consumed']) is list and
                 all(type(item) in (list, tuple) and len(item) == 3 for item in value['consumed']),
                 'changed exact first-contraction metadata')
        row_sums = [decode_integer(item, account['center_bits']+(n-1).bit_length()+1) for item in value['row_sums']]
        _require(all(item >= 0 for item in row_sums), 'negative original source radius sum')
        source_rows.extend(row_sums)
        for item in value['consumed']:
            ref = ArtifactRef(*item)
            _require(tuple(item) in expected_consumed, 'foreign exact consumed source')
            _raw(reader.path.parent, ref, 8*MIB)
            consumed.add(tuple(item))
        _require([tuple(item) for item in value['consumed']] == sorted(set(map(tuple, value['consumed']))),
                 'repeated or noncanonical exact consumed source cover')
    _require(consumed == expected_consumed, 'incomplete exact consumed source cover')
    diagonal, off, radii, directional = ([0]*n for _ in range(4))
    digest = hashlib.sha256()
    for i in range(0, n, b):
        for j in range(i, n, b):
            rows, cols = e._shape(context, i, j)
            data, center, radius = _block_values(_raw(second_root, ArtifactRef(**second[f'block/{p}/{i}/{j}']), 8*MIB),
                                                  context, i, j, account)
            Bn, En = fmpz_mat(rows, cols, center), fmpz_mat(rows, cols, radius)
            e.complete_rows(diagonal, off, radii, directional, i, j, Bn, En)
            digest.update(canonical_bytes({'row': i, 'column': j, 'center': data['center'], 'radius': data['radius']}))
    lam, Q, L = staging.spec.problem.model_error, parameters['Q'], masses['mass_lcm']
    BD, ED = Q*L*lam.denominator*(1 << (2*context['u'])), Q*(1 << (2*context['u']))
    factor = L*lam.denominator
    margins = [Fraction(diagonal[i]-off[i]-factor*radii[i], BD) for i in range(n)]
    upper = [Fraction(diagonal[i]+factor*directional[i], BD) for i in range(n)]
    worst = min(range(n), key=lambda i: upper[i])
    report = {'width': e.numerical_width(source_rows, Q, masses['minimum_mass']), 'margin': min(margins),
              'row_margins': margins, 'direction_index': worst, 'direction_upper': upper[worst],
              'direction_mass': masses['direction_masses'][worst], 'tau': masses['tau'], 'Q': hex(Q), 'L': hex(L),
              'center_denominator': hex(BD), 'radius_denominator': hex(ED), 'transformed_upper_entries': n*(n+1)//2,
              'transformed_digest': digest.hexdigest(), 'parity': p, 'dimension': n,
              'goal': staging.spec.problem.numerical_goal, 'source_sha256': context['source_sha256'],
              'proposal_sha256': context['proposal_sha256'], 'modular': modular, 'bit_account': account,
              'source_tiles_consumed': len(consumed),
              'source_consumed_digest': hashlib.sha256(canonical_bytes(sorted(consumed))).hexdigest(),
              'complete_source_row_sums': [hex(value) for value in source_rows],
              'scope': descriptor['proof_scope'], 'analytical_source_acceptance': False, 'production_admission': False}
    return {'report': report, 'scope': e.SCOPE}


def assessment_reports(task, descriptor, root, attempt_id):
    _require(set(task) == {'task_id', 'operation', 'operands', 'blocks', 'groups'} and
             set(task['groups']) == {'reduce'}, 'changed final exact dependency task')
    identity = {key: value for key, value in task.items() if key != 'task_id'}
    _require(task['operation'] == 'assess' and
             task['task_id'] == hashlib.sha256(canonical_bytes(identity)).hexdigest(), 'changed exact task identity')
    group_root, outputs = _wave(task, descriptor, 'reduce', expected_root=root, expected_attempt=attempt_id)
    _require(group_root == Path(root).resolve() and task['blocks'] == [outputs[f'reduce/{p}'] for p in (0, 1)],
             'final assessment reports differ from complete parity wave')
    return task['blocks']


def _request(operation, operands, groups, **fields):
    task = {'operation': operation, 'operands': operands, 'groups': groups, **fields}
    task['task_id'] = hashlib.sha256(canonical_bytes(task)).hexdigest()
    return task


def run_waves(lock, execution, descriptor, operands):
    from scripts.whole_source import exact as e
    groups, reports, product_inventories = {}, [], []
    for operation in ('global', 'first', 'second', 'reduce'):
        deps = dict(groups)
        tasks = []
        for p, block in enumerate(descriptor['blocks']):
            n, b = block['context']['dimension'], block['context']['panel_size']
            coordinates = ([{}] if operation in ('global', 'reduce') else
                           [{'row': i} for i in range(0, n, b)] if operation == 'first' else
                           [{'row': i, 'column': j} for i in range(0, n, b) for j in range(i, n, b)])
            for values in coordinates:
                tasks.append(_request(operation, operands, deps, parity=p, **values))
        execution.run_stage(operation, tasks)
        results = {}
        for row in execution.read_results(operation):
            _require(row['task_id'] not in results, 'repeated exact task wave result')
            results[row['task_id']] = row['result']
        _require(set(results) == {task['task_id'] for task in tasks}, 'incomplete exact task wave results')
        outputs, staged = {}, []
        for task in tasks:
            result = results[task['task_id']]
            _result_outputs(task, result, descriptor)
            p = task['parity']
            context = descriptor['blocks'][p]['context']
            n, b = context['dimension'], context['panel_size']
            if operation in ('global', 'reduce'):
                key = 'metadata' if operation == 'global' else 'report'
                _require(set(result) == {key, 'scope'}, 'unexpected exact global/reduction output')
                outputs[f'{operation}/{p}'] = asdict(lock._immutable('seals', canonical_bytes(result[key])))
                if operation == 'reduce':
                    reports.append(result[key])
            elif operation == 'first':
                i = task['row']
                expected = {f'{family}/{i}/{j}' for family in ('J', 'S') for j in range(0, n, b)}
                _require(set(result) == {'panels', 'metadata', 'scope'} and set(result['panels']) == expected,
                         'incomplete exact row panel cover')
                checker = e.IntegerTiles(lock.root, context)
                for name, value in result['panels'].items():
                    ref = ArtifactRef(**value)
                    _require(ref.path.startswith('attempts/'+execution.attempt_id+'/staging/'), 'foreign exact scratch')
                    raw = _raw(lock.root, ref, 8*MIB)
                    data = _json(raw)
                    family, row, column = name.split('/')
                    _require(set(data) == {'header', 'values'} and data['header'] == checker._header(family, int(row), int(column)),
                             'changed staged exact row panel context')
                    _require(type(data['values']) is list and len(data['values']) == data['header']['rows']*data['header']['columns'],
                             'incomplete staged exact row panel')
                    for item in data['values']:
                        decode_integer(item, data['header']['integer_bits'])
                    outputs[f'{p}/{name}'] = asdict(lock._immutable('seals', raw))
                    staged.append(ref)
                outputs[f'row/{p}/{i}'] = asdict(lock._immutable('seals', canonical_bytes(result['metadata'])))
            else:
                _require(set(result) == {'block', 'scope'}, 'unexpected exact block outputs')
                ref = ArtifactRef(**result['block'])
                _require(ref.path.startswith('attempts/'+execution.attempt_id+'/staging/'), 'foreign exact block scratch')
                raw = _raw(lock.root, ref, 8*MIB)
                account = e.integer_bounds(context, e.paid_parameters(256, Fraction(descriptor['blocks'][p]['theta']),
                                           execution.spec.problem.eta), execution.spec.problem.model_error)
                _block_values(raw, context, task['row'], task['column'], account)
                outputs[f"block/{p}/{task['row']}/{task['column']}"] = asdict(lock._immutable('seals', raw))
                staged.append(ref)
        _require(set(outputs) == _expected(descriptor, operation), 'incomplete exact committed wave cover')
        groups[operation] = seal_group(lock, execution, operation, _context(descriptor, operands, operation), outputs)
        if operation == 'first':
            for p, block in enumerate(descriptor['blocks']):
                panels = {name.split('/', 1)[1]: ref for name, ref in outputs.items() if name.startswith(str(p)+'/')}
                product_inventories.append(asdict(lock._immutable('seals', canonical_bytes({
                    'format': 'whole-source-exact-product-inventory-v1', 'context': block['context'], 'panels': panels}))))
        for ref in staged:
            _safe(lock.root, ref.path).unlink()
    group_root, outputs = read_group(groups['reduce'], _context(descriptor, operands, 'reduce'),
                                     expected_root=lock.root, expected_attempt=execution.attempt_id)
    refs = [outputs[f'reduce/{p}'] for p in (0, 1)]
    return reports, refs, product_inventories, groups
