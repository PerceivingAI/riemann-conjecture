"""Fresh blocked congruence proposals. Every output is NONPROOF_ONLY."""
from __future__ import annotations

from dataclasses import asdict
from bisect import bisect_left
from fractions import Fraction
import hashlib
import importlib.metadata
from pathlib import Path
import re
import sys
import uuid

from scripts.whole_source.contract import (
    ArtifactRef, ContractError, ROOT, QuantityKey, bind_problem, canonical_bytes, problem_id,
)
from scripts.whole_source.artifacts import (
    CollectionLock, CollectionSpec, _check_quota, _raw, _safe, _volume_gate,
    decode_integer, encode_integer,
)
from scripts.whole_source.execution import (
    MIB, ExecutionPlan, WorkloadExecution, _RUNTIME, _bytes, _json, _write, exact_telemetry,
)
from scripts.whole_source.pipeline import SourceReader, _fixed_bounds, _quantities, _partition, source_execution_document
from scripts.whole_source.slice import _ref, _slice_writer
from scripts.whole_source.reuse import PANEL_DECODED_BYTES, WorkingSet, python_bytes
from scripts.whole_source.task_groups import group_tasks, read_group, seal_group

BITS = 1024
TRANSFORM_BITS = 80
SCOPE = "NONPROOF_PROPOSAL_ONLY"
_NAMES = re.compile(r"(L|X_A|X_H|X_E|A|H|E|V|W|Z)/([0-9]+)/([0-9]+)\Z")


def _require(value, message):
    if not value:
        raise ContractError(message)


def _shape(context, i, j):
    n, b = context['dimension'], context['panel_size']
    _require(type(i) is int and type(j) is int and 0 <= i < n and 0 <= j < n and
             i % b == j % b == 0, 'invalid proposal panel coordinates')
    return min(b, n-i), min(b, n-j)


class PanelStore:
    """Bounded closed panels; workers stage, the collection owner publishes."""
    def __init__(self, root, context, inventory=None, staging=None):
        self.root, self.context, self.staging = Path(root), context, staging
        self.refs = {} if inventory is None else dict(inventory)
        self.created = {}
        self.decoded = WorkingSet(PANEL_DECODED_BYTES)

    def _header(self, name, kind):
        match = _NAMES.fullmatch(name)
        _require(match is not None and kind in ('interval', 'binary64', 'integer'), 'invalid panel kind/name')
        i, j = int(match[2]), int(match[3])
        rows, columns = _shape(self.context, i, j)
        _require((kind == 'integer') == (match[1] == 'Z') and
                 (kind == 'binary64') == (match[1] == 'V'), 'panel arithmetic/name mismatch')
        return {'format': 'whole-source-nonproof-panel-v1', 'context': self.context,
                'name': name, 'kind': kind, 'rows': rows, 'columns': columns,
                'grid_bits': TRANSFORM_BITS if kind == 'integer' else (BITS if kind == 'interval' else None),
                'status': 'NONPROOF_ONLY', 'production_admission': False}

    def put(self, name, kind, values):
        _require(name not in self.refs, 'duplicate proposal panel')
        header = self._header(name, kind)
        _require(len(values) == header['rows']*header['columns'], 'incomplete proposal panel')
        raw = canonical_bytes({'header': header, 'values': values})
        _require(len(raw) <= 8*MIB, 'proposal panel exceeds bounded codec')
        if self.staging is not None:
            self.staging._check()
            relative = 'attempts/'+self.staging.attempt_id+'/staging/'+uuid.uuid4().hex
            path = _safe(self.root, relative, missing=True)
            with _volume_gate(self.root):
                _check_quota(self.root, self.staging.spec.bounds, len(raw), len(raw))
                _write(path, raw)
            self.staging._check()
        else:
            relative = uuid.uuid4().hex
            path = self.root/relative
            _write(path, raw)
        ref = ArtifactRef(relative, hashlib.sha256(raw).hexdigest(), len(raw))
        self.refs[name] = asdict(ref)
        self.created[name] = asdict(ref)

    def _read(self, name, kind):
        ref = ArtifactRef(**self.refs[name])
        raw = _raw(self.root, ref, 8*MIB)
        header = self._header(name, kind)
        return ref, raw, header

    def _values(self, raw, header):
        value = _json(raw)
        _require(set(value) == {'header', 'values'} and
                 canonical_bytes(value['header']) == canonical_bytes(header) and
                 type(value['values']) is list and
                 len(value['values']) == header['rows']*header['columns'], 'changed proposal panel')
        return value['values']

    def read(self, name, kind):
        _, raw, header = self._read(name, kind)
        return self._values(raw, header)

    def _integers(self, name, kind):
        ref, raw, header = self._read(name, kind)
        policy = canonical_bytes(self.context)
        cache = self.decoded.bind(policy)
        key = (str(self.root.absolute()), ref.path, ref.sha256, ref.size, canonical_bytes(header))
        result = cache.get(key)
        if result is not None:
            return result
        # Include tuple slots, integer objects and temporary conversion results.
        admitted = cache.reserve(key, 4*len(raw)+256*header['rows']*header['columns']+4096)
        values = self._values(raw, header)
        result = []
        for value in values:
            if kind == 'interval':
                _require(type(value) is list and len(value) == 2, 'invalid interval panel value')
                lo, hi = (decode_integer(v, 8192) for v in value)
                _require(lo <= hi, 'inverted proposal panel interval')
                result.append((lo, hi))
            else:
                _require(type(value) is str, 'noncanonical floating vector')
                x = float.fromhex(value)
                _require(x.hex() == value and x == x and abs(x) != float('inf'), 'nonfinite floating vector')
                result.append(x.as_integer_ratio())
        result = tuple(result)
        if admitted:
            cache.put(key, result, python_bytes(result))
        return result

    def put_native(self, name, matrix):
        values = []
        for i in range(matrix.nrows()):
            for j in range(matrix.ncols()):
                lo, hi = _fixed_bounds(matrix[i,j], BITS)
                values.append([encode_integer(lo, 8192), encode_integer(hi, 8192)])
        self.put(name, 'interval', values)

    def native(self, name):
        from flint import arb, arb_mat, fmpq
        values = self._integers(name, 'interval')
        _, i, j = _NAMES.fullmatch(name).groups()
        rows, columns = _shape(self.context, int(i), int(j))
        result = arb_mat(rows, columns)
        for k, (lo, hi) in enumerate(values):
            result[k//columns,k%columns] = arb(fmpq(lo+hi, 1 << (BITS+1)), arb(fmpq(hi-lo, 1 << (BITS+1))))
        return result

    def vectors(self, name):
        from flint import arb, arb_mat, fmpq
        values = self._integers(name, 'binary64')
        _, i, j = _NAMES.fullmatch(name).groups()
        rows, columns = _shape(self.context, int(i), int(j))
        result = arb_mat(rows, columns)
        for k, (numerator, denominator) in enumerate(values):
            result[k//columns,k%columns] = arb(fmpq(numerator, denominator))
        return result


def _dense_solve(lower, rhs, *, transpose=False):
    """Solve one diagonal triangular panel, including every within-panel index."""
    from flint import arb, arb_mat
    n = lower.nrows()
    _require(lower.ncols() == n and rhs.nrows() == n, 'triangular solve shape mismatch')
    result = arb_mat(n, rhs.ncols())
    order = range(n-1,-1,-1) if transpose else range(n)
    for i in order:
        pivot = lower[i,i]
        _require(pivot > 0, 'NONPROOF_PROPOSAL_UNRESOLVED: uncertain triangular pivot')
        for j in range(rhs.ncols()):
            value = rhs[i,j]
            for k in (range(i+1,n) if transpose else range(i)):
                value -= (lower[k,i] if transpose else lower[i,k])*result[k,j]
            result[i,j] = value/pivot
    return result


def _factor_diagonal(matrix, store, j, *, predecessors=None):
    """Keep the literal diagonal arithmetic and its paid publication boundary."""
    from flint import arb_mat
    b = store.context['panel_size']
    predecessors = store if predecessors is None else predecessors
    diagonal = matrix(j,j)
    for k in range(0,j,b):
        panel = predecessors.native(f'L/{j}/{k}')
        diagonal -= panel*panel.transpose()
    width = diagonal.nrows()
    factor = arb_mat(width,width)
    smallest = None
    for row in range(width):
        for column in range(row+1):
            value = diagonal[row,column]
            for k in range(column):
                value -= factor[row,k]*factor[column,k]
            if row == column:
                _require(value > 0, 'NONPROOF_PROPOSAL_UNRESOLVED: nonpositive or uncertain Cholesky pivot')
                lower = Fraction(str(value.lower().fmpq()))
                smallest = lower if smallest is None else min(smallest,lower)
                factor[row,column] = value.sqrt()
            else:
                factor[row,column] = value/factor[column,column]
    store.put_native(f'L/{j}/{j}',factor)
    return smallest


def _factor_below(matrix, factor, output, i, j, *, paid_diagonal=None):
    b = output.context['panel_size']
    diagonal = factor.native(f'L/{j}/{j}') if paid_diagonal is None else paid_diagonal
    value = matrix(i,j)
    for k in range(0,j,b):
        value -= factor.native(f'L/{i}/{k}')*factor.native(f'L/{j}/{k}').transpose()
    output.put_native(f'L/{i}/{j}',_dense_solve(diagonal,value.transpose()).transpose())


def blocked_cholesky(matrix, store):
    """Literal full-factor control, also used by persisted arithmetic comparisons."""
    n,b = store.context['dimension'],store.context['panel_size']
    smallest = None
    for j in range(0,n,b):
        lower = _factor_diagonal(matrix,store,j)
        smallest = lower if smallest is None else min(smallest,lower)
        diagonal = store.native(f'L/{j}/{j}')
        for i in range(j+b,n,b):
            _factor_below(matrix,store,store,i,j,paid_diagonal=diagonal)
    return smallest


def _solve_column(factor, rhs, output, prefix, j, *, transpose=False, transpose_output=False):
    n,b = output.context['dimension'],output.context['panel_size']
    order = list(range(0,n,b))
    if transpose:
        order.reverse()
    for index,i in enumerate(order):
        value = rhs(i,j)
        for k in order[:index]:
            panel = factor.native(f'L/{k}/{i}').transpose() if transpose else factor.native(f'L/{i}/{k}')
            prior = (output.native(f'{prefix}/{j}/{k}').transpose() if transpose_output
                     else output.native(f'{prefix}/{k}/{j}'))
            value -= panel*prior
        value = _dense_solve(factor.native(f'L/{i}/{i}'),value,transpose=transpose)
        name = f'{prefix}/{j}/{i}' if transpose_output else f'{prefix}/{i}/{j}'
        output.put_native(name,value.transpose() if transpose_output else value)


def triangular_solve(factor, rhs, output, prefix, *, transpose=False, transpose_output=False):
    """Full literal control with complete, ordered column chains."""
    n,b = output.context['dimension'],output.context['panel_size']
    for j in range(0,n,b):
        _solve_column(factor,rhs,output,prefix,j,transpose=transpose,transpose_output=transpose_output)


def whiten_tiles(matrix, store, family):
    triangular_solve(store, matrix, store, 'X_'+family)
    triangular_solve(store, lambda i,j: store.native(f'X_{family}/{j}/{i}').transpose(),
                     store, family, transpose_output=True)


class SourcePanels:
    """Read only the source tiles intersecting the current physical panel."""
    def __init__(self, reader, context):
        from scripts.whole_source.artifacts import _task
        self.reader, self.context = reader, context
        self.index = {}
        self.decoded = WorkingSet(PANEL_DECODED_BYTES)
        for row in reader.document['tiles']:
            task = _task(row['task'])
            self.index[row['family'],row['parity'],task.rows.start,task.columns.start] = row

    def _integers(self, row):
        from scripts.whole_source.artifacts import _publication_header, _task, publication_integers
        task = _task(row['task'])
        ref = ArtifactRef(**row['artifact'])
        raw = _raw(self.reader.path.parent, ref, 8*MIB)
        header = canonical_bytes(_publication_header(self.reader.spec, task, self.reader.bits))
        cache = self.decoded.bind((canonical_bytes(self.context), self.reader.spec.collection_id, self.reader.bits))
        key = (str(self.reader.path.parent.absolute()), ref.path, ref.sha256, ref.size, header)
        result = cache.get(key)
        if result is not None:
            return result
        admitted = cache.reserve(key, 4*len(raw)+256*len(task.rows)*len(task.columns)+4096)
        result = publication_integers(self.reader.spec, raw, task, self.reader.bits)
        if admitted:
            cache.put(key, result, python_bytes(result))
        return result

    def matrix(self, family, i, j):
        from flint import arb, arb_mat, fmpq
        from scripts.whole_source.artifacts import _partition_widths
        p, b = self.context['parity'], self.context['panel_size']
        rows, columns = _shape(self.context,i,j)
        quantity_name = {'A_model':'A_model','weighted_head':'head_complete','weighted_complete_tail':'tail_complete'}[family]
        q = self.reader.spec.quantity(QuantityKey(quantity_name,p))
        widths = _partition_widths(self.reader.spec,q.key)
        result, locations = arb_mat(rows,columns), {}
        for r in range(rows):
            for c in range(columns):
                m,n = 2*(i+r)+p,2*(j+c)+p
                u,v = min(m,n),max(m,n)
                sr = q.rows.start+((u-q.rows.start)//(2*widths['rows']))*2*widths['rows']
                sc = q.columns.start+((v-q.columns.start)//(2*widths['columns']))*2*widths['columns']
                key = family,p,sr,sc
                locations.setdefault(key, []).append((r,c,m,n,u,v))
        for key, cells in locations.items():
            records = self._integers(self.index[key])
            for r,c,m,n,u,v in cells:
                index = bisect_left(records, (u,v))
                _require(index < len(records) and records[index][:2] == (u,v), 'missing proposal source coordinate')
                _, _, lo, hi = records[index]
                value = arb(fmpq(lo+hi,1 << (self.reader.bits+1)),
                            arb(fmpq(hi-lo,1 << (self.reader.bits+1))))
                if family == 'A_model':
                    if m == n:
                        paid = self.reader.spec.problem.model_error*Fraction(2,2*m+1)
                        value -= arb(fmpq(paid.numerator,paid.denominator))
                else:
                    eta = self.reader.spec.problem.eta
                    value /= arb(fmpq(eta.numerator,eta.denominator))
                result[r,c] = value
        return result


def _reader(problem, source, snapshot_root):
    raw = _raw(Path(source['directory']),ArtifactRef(**source['manifest']),8*MIB)
    document = _json(raw)
    execution_ref = ArtifactRef(**source['execution'])
    _raw(snapshot_root,execution_ref,8*MIB)
    execution = source_execution_document(Path(source['directory'])/source['manifest']['path'],
                                         snapshot_root/execution_ref.path)
    spec = CollectionSpec.from_dict(problem,execution['collection'],code_root=snapshot_root)
    _require(spec.role == 'producer' and type(document['control']) is bool, 'proposal requires a producer source')
    return SourceReader(Path(source['directory'])/source['manifest']['path'],spec,
                        control=document['control'],execution_path=snapshot_root/execution_ref.path)


_OPERATIONS = ('factor-diagonal','factor-below','whiten-forward','whiten-transpose',
               'float-optimize','backsolve-quantize')
_FAMILIES = {'A':'A_model','H':'weighted_head','E':'weighted_complete_tail'}


def _grid(context):
    _require(type(context) is dict and set(context) == {
        'proposal_id','problem_id','source_sha256','dimension','panel_size',
        'precision_bits','grid_bits','transform_bits','parity'},'invalid proposal task context')
    _require(all(type(context[k]) is str and re.fullmatch('[0-9a-f]{64}',context[k])
                 for k in ('proposal_id','problem_id','source_sha256')) and
             type(context['parity']) is int and context['parity'] in (0,1) and
             type(context['dimension']) is int and context['dimension'] > 0 and
             type(context['panel_size']) is int and 1 <= context['panel_size'] <= 32 and
             context['precision_bits'] == context['grid_bits'] == BITS and
             context['transform_bits'] == TRANSFORM_BITS,'changed proposal task geometry/policy')
    return range(0,context['dimension'],context['panel_size'])


def _task_panels(task):
    context,operation = task['context'],task['operation']
    grid = _grid(context)
    _require(operation in _OPERATIONS,'unknown proposal operation')
    fields = {'operation','context','source','source_snapshot','dependencies','task_id'}
    if operation != 'float-optimize':
        fields.add('column')
        _require(type(task.get('column')) is int and task['column'] in grid,'invalid proposal task column')
    if operation == 'factor-below':
        fields.add('row')
        _require(type(task.get('row')) is int and task['row'] in grid and
                 task['row'] > task['column'],'invalid below-diagonal task row')
    if operation.startswith('whiten-'):
        fields.add('family')
        _require(task.get('family') in _FAMILIES,'invalid whitening task family')
    _require(set(task) == fields and type(task['dependencies']) is dict,'invalid closed proposal task')
    identity = {k:v for k,v in task.items() if k != 'task_id'}
    _require(task['task_id'] == hashlib.sha256(canonical_bytes(identity)).hexdigest(),
             'changed proposal task identity')
    j = task.get('column')
    if operation == 'factor-diagonal':
        return {f'L/{j}/{j}'}
    if operation == 'factor-below':
        return {f"L/{task['row']}/{j}"}
    if operation == 'whiten-forward':
        return {f"X_{task['family']}/{i}/{j}" for i in grid}
    if operation == 'whiten-transpose':
        return {f"{task['family']}/{j}/{i}" for i in grid}
    if operation == 'float-optimize':
        return {f'V/{i}/{k}' for i in grid for k in grid}
    return {f'{prefix}/{i}/{j}' for prefix in ('W','Z') for i in grid}


def _wave_context(context, operation, column=None):
    return {'format':'whole-source-proposal-task-group-v1','context':context,
            'operation':operation,'column':column}


def _wave_names(context, operation, column=None):
    grid = _grid(context)
    if operation == 'factor-diagonal':
        return {f'L/{column}/{column}'}
    if operation == 'factor-below':
        return {f'L/{i}/{column}' for i in grid if i > column}
    if operation in ('whiten-forward','whiten-transpose'):
        prefixes = ('X_A','X_H','X_E') if operation == 'whiten-forward' else ('A','H','E')
    else:
        _require(operation in ('float-optimize','backsolve-quantize'),'unknown proposal dependency operation')
        prefixes = ('V',) if operation == 'float-optimize' else ('W','Z')
    return {f'{prefix}/{i}/{j}' for prefix in prefixes for i in grid for j in grid}


def _factor_waves(context, stop=None, *, diagonal=None):
    grid = _grid(context)
    stop = context['dimension'] if stop is None else stop
    result = []
    for j in grid:
        if j >= stop:
            break
        result.append(('factor-diagonal',j))
        if j != grid[-1]:
            result.append(('factor-below',j))
    if diagonal is not None:
        result.append(('factor-diagonal',diagonal))
    return result


def _verify_group_tasks(record, context, operation, column, outputs, binding):
    expected,seen = None,set()
    wave_context = _wave_context(context,operation,column)
    for task,result in group_tasks(record,wave_context):
        _require(task.get('operation') == operation and task.get('context') == context,
                 'unrelated proposal dependency task')
        names = _task_panels(task)
        if expected is None:
            base = {'context':context,'source':binding['source'],
                    'source_snapshot':binding['source_snapshot']}
            expected = {row['task_id']:row for row in
                        _make_tasks(base,operation,task['dependencies'],column)}
        identity = task['task_id']
        _require(identity in expected and identity not in seen and
                 canonical_bytes(task) == canonical_bytes(expected[identity]),
                 'wrong or repeated proposal dependency request')
        _require(type(result) is dict and set(result) == {'scope','panels','diagnostics'} and
                 result['scope'] == SCOPE and type(result['panels']) is dict and
                 set(result['panels']) == names and type(result['diagnostics']) is dict,
                 'wrong proposal dependency task result')
        for name in names:
            published = ArtifactRef(**outputs[name])
            actual = ArtifactRef(**result['panels'][name])
            _require((published.sha256,published.size) == (actual.sha256,actual.size),
                     'swapped proposal dependency output attribution')
        seen.add(identity)
    _require(expected is not None and seen == set(expected),
             'incomplete proposal dependency task cover')


def _dependency_store(values, context, expected, *, binding):
    _require(type(values) is list and len(values) == len(expected),'incomplete proposal dependency groups')
    root,panels = None,{}
    for value,(operation,column) in zip(values,expected):
        _require(type(value) is dict and set(value) == {'operation','column','record'} and
                 value['operation'] == operation and type(value['column']) is type(column) and
                 value['column'] == column,'wrong proposal dependency wave')
        current,outputs = read_group(value['record'],_wave_context(context,operation,column))
        _require(type(outputs) is dict and set(outputs) == _wave_names(context,operation,column) and
                 not (set(panels) & set(outputs)),'incomplete or repeated proposal dependency panels')
        _verify_group_tasks(value['record'],context,operation,column,outputs,binding)
        _require(root is None or root == current,'mixed proposal dependency collections')
        root = current
        panels.update(outputs)
    return PanelStore(root if root is not None else Path('.'),context,panels)


def _dependencies(task):
    context,operation = task['context'],task['operation']
    deps = task['dependencies']
    binding = {'source':task['source'],'source_snapshot':task['source_snapshot']}
    if operation.startswith('factor-'):
        expected = _factor_waves(context,task['column'],
                                 diagonal=task['column'] if operation == 'factor-below' else None)
        _require(set(deps) == {'factor'},'wrong factor task dependencies')
        return {'factor':_dependency_store(deps['factor'],context,expected,binding=binding)}
    if operation.startswith('whiten-'):
        _require(set(deps) == ({'factor','forward'} if operation == 'whiten-transpose' else {'factor'}),
                 'wrong whitening task dependencies')
        result = {'factor':_dependency_store(deps['factor'],context,_factor_waves(context),binding=binding)}
        if operation == 'whiten-transpose':
            result['forward'] = _dependency_store(deps['forward'],context,[('whiten-forward',None)],binding=binding)
        return result
    if operation == 'float-optimize':
        _require(set(deps) == {'whitened'},'wrong floating task dependencies')
        return {'whitened':_dependency_store(deps['whitened'],context,[('whiten-transpose',None)],binding=binding)}
    _require(set(deps) == {'factor','floating'},'wrong backsolve task dependencies')
    return {'factor':_dependency_store(deps['factor'],context,_factor_waves(context),binding=binding),
            'floating':_dependency_store(deps['floating'],context,[('float-optimize',None)],binding=binding)}


def evaluate_proposal(task, staging):
    """Owned entry point. Numerical imports follow actual job/BLAS admission."""
    from scripts.whole_source import execution
    worker = execution._WORKER
    _require(worker is not None and worker[-1] is staging and worker[0].role == 'proposal' and
             worker[0].scope == SCOPE, 'proposal requires its owned nonproof context')
    staging._check()
    context = task['context']
    n,b = context['dimension'],context['panel_size']
    operation = task['operation']
    phase = 'floating' if operation == 'float-optimize' else 'native'
    accounts = _proposal_accounts(n,b)
    _require(accounts[phase+'_working_bytes'] <= worker[0].worker_private_mib*MIB,
             'proposal buffers exceed their admitted account')
    _require(accounts['task_bytes'] <= 128*1024 and
             max(accounts['native_result_bytes'],accounts['floating_result_bytes']) <= MIB,
             'proposal task geometry exceeds bounded transport')
    expected = _task_panels(task)
    _require(worker[0].backend == ('numpy-scipy' if phase == 'floating' else 'python-flint') and
             ('flint' if phase == 'floating' else 'numpy') not in sys.modules,
             'proposal arithmetic backends overlap')
    # Each independently scheduled callback revalidates the bound source.
    reader = _reader(staging.spec.problem,task['source'],ROOT/task['source_snapshot'])
    _require(reader.ref.sha256 == context['source_sha256'] and
             reader.document['geometry']['N']//2 == n and
             problem_id(staging.spec.problem) == context['problem_id'],'changed proposal source geometry/context')
    deps = _dependencies(task)
    store = PanelStore(staging.root,context,staging=staging)
    diagnostics = {'status':'NONPROOF_ONLY','production_admission':False}
    j = task.get('column')
    if operation == 'factor-diagonal':
        source = SourcePanels(reader,context)
        smallest = _factor_diagonal(lambda i,k:source.matrix('A_model',i,k),store,j,
                                    predecessors=deps['factor'])
        diagnostics['minimum_native_pivot_lower'] = str(smallest)
    elif operation == 'factor-below':
        source = SourcePanels(reader,context)
        _factor_below(lambda i,k:source.matrix('A_model',i,k),deps['factor'],store,task['row'],j)
    elif operation == 'whiten-forward':
        source = SourcePanels(reader,context)
        family = task['family']
        _solve_column(deps['factor'],lambda i,k:source.matrix(_FAMILIES[family],i,k),
                      store,'X_'+family,j)
    elif operation == 'whiten-transpose':
        family = task['family']
        _solve_column(deps['factor'],lambda i,k:deps['forward'].native(f'X_{family}/{k}/{i}').transpose(),
                      store,family,j,transpose_output=True)
    elif operation == 'float-optimize':
        dense_account = _proposal_accounts(n,b)['floating_working_bytes']
        native = deps['whitened']
        import numpy as np
        from scripts.whole_source.proposal_float import optimize_theta
        arrays = []
        for family in ('A','H','E'):
            matrix = np.empty((n,n),dtype=np.float64)
            for i in range(0,n,b):
                for j in range(0,n,b):
                    rows,columns = _shape(context,i,j)
                    values = native.read(f'{family}/{i}/{j}','interval')
                    for k,pair in enumerate(values):
                        lo,hi = (decode_integer(v,8192) for v in pair)
                        _require(lo <= hi, 'inverted floating input panel')
                        matrix[i+k//columns,j+k%columns] = float(Fraction(lo+hi,1 << (BITS+1)))
            arrays.append(matrix)
        theta,vectors,diagnostics = optimize_theta(*arrays)
        diagnostics['dense_array_account_bytes'] = dense_account
        diagnostics['native_library_loaded'] = 'flint' in sys.modules
        for i in range(0,n,b):
            for j in range(0,n,b):
                rows,columns = _shape(context,i,j)
                store.put(f'V/{i}/{j}','binary64',
                          [float(vectors[i+r,j+c]).hex() for r in range(rows) for c in range(columns)])
        diagnostics['theta'] = str(theta)
    elif operation == 'backsolve-quantize':
        floating = deps['floating']
        _solve_column(deps['factor'],lambda i,k:floating.vectors(f'V/{i}/{k}'),
                      store,'W',j,transpose=True)
        for i in range(0,n,b):
            # Quantization consumes the paid persisted W, never a hidden solve.
            matrix = store.native(f'W/{i}/{j}')
            values = []
            for r in range(matrix.nrows()):
                for c in range(matrix.ncols()):
                    midpoint = Fraction(str(matrix[r,c].mid().fmpq()))*(1 << TRANSFORM_BITS)
                    integer = (2*midpoint.numerator+midpoint.denominator)//(2*midpoint.denominator)
                    values.append(encode_integer(integer,8192))
            store.put(f'Z/{i}/{j}','integer',values)
        diagnostics['transform_entries'] = n*min(b,n-j)
    _require(set(store.created) == expected,'incomplete proposal task output')
    if phase == 'native':
        diagnostics['native_bits'] = BITS
    return {'panels':store.created,'diagnostics':diagnostics,'scope':SCOPE}


def _proposal_layout(n, b):
    q = (n+b-1)//b
    return {'format':'whole-source-proposal-task-layout-v1',
            'operations':list(_OPERATIONS),'panel_columns':q,
            'factor_diagonal_tasks':q,'factor_below_tasks':q*(q-1)//2,
            'forward_tasks':3*q,'transpose_tasks':3*q,'floating_tasks':1,'backsolve_tasks':q,
            'stages_per_parity':2*q+3,'native_max_tasks':3*q,'floating_max_tasks':1,
            'task_bytes':65536+2048*q,
            'native_result_bytes':65536+1024*q,
            'floating_result_bytes':65536+512*q*q}


def _proposal_accounts(n, b):
    """Conservative component/transport/disk counts, not a measured process peak."""
    _require(type(n) is int and n > 0 and type(b) is int and 1 <= b <= 32,
             'invalid proposal account geometry')
    blocks = (n+b-1)//b
    panels = blocks*(blocks+1)//2+6*blocks*blocks
    layout = _proposal_layout(n,b)
    # Original full retained lifetime remains paid, including duplicate staging
    # until publication, dense diagonal zeros, and every W/Z coordinate.
    # put_native's _fixed_bounds guard limits scaled endpoints to BITS+32
    # bits before the outward unit.560 bytes covers both signed JSON endpoints.
    # Paid W therefore has magnitude <=2**32 plus rounding; its80-bit
    # quantization fits64 bytes per signed integer.8192 is a read/codec cap,
    # not an attainable native writer magnitude.
    factor_bytes = 7*n*n*560+panels*4096
    solve_bytes = n*n*(560+64)+2*blocks*blocks*4096
    reuse_bytes = 3*PANEL_DECODED_BYTES
    decode_scratch_bytes = 32*MIB
    native_tasks = blocks*(blocks+1)//2+7*blocks
    # Task/result spools survive every barrier. Group authority includes task
    # and output refs; receipts/profiles/streams keep their original log headroom.
    native_envelope = native_tasks*(layout['task_bytes']+layout['native_result_bytes']+4096)
    native_envelope += (2*blocks+2)*(4*MIB+65536)+panels*2048
    floating_envelope = layout['task_bytes']+layout['floating_result_bytes']+8*MIB
    return {'native_working_bytes':24*b*b*((BITS+7)//8+128)+8*MIB+reuse_bytes+decode_scratch_bytes,
            'floating_working_bytes':16*n*n*8+32*n*8+8*MIB+reuse_bytes+decode_scratch_bytes,
            'native_staging_bytes':max(factor_bytes,solve_bytes)+8*MIB+native_envelope,
            'floating_staging_bytes':n*n*48+blocks*blocks*4096+8*MIB+floating_envelope,
            'native_result_bytes':layout['native_result_bytes'],
            'floating_result_bytes':layout['floating_result_bytes'],
            'task_bytes':layout['task_bytes'],
            'native_max_tasks':layout['native_max_tasks'],'floating_max_tasks':1,
            'per_parity_panel_disk_bytes':factor_bytes+solve_bytes+n*n*48+blocks*blocks*4096,
            'retained_graph_bytes':native_envelope+floating_envelope}


def prepare_proposal_inputs(problem, source_path, directory, *, origin_git_commit,
                            origin_git_dirty, code_root=ROOT, panel_size=32, memory_mib=None):
    """Bind source snapshots and proposal policy without importing numerical libraries."""
    _require(problem.profile == 'retained-t081', 'target proposal execution is not qualified')
    _require(type(panel_size) is int and 1 <= panel_size <= 32, 'invalid proposal panel width')
    root, directory, source_path = Path(code_root).resolve(), Path(directory).resolve(), Path(source_path).resolve()
    directory.relative_to(root)
    directory.mkdir(parents=True,exist_ok=False)
    source_raw = _bytes(source_path)
    source_document = _json(source_raw)
    _require(source_document['problem_id'] == problem_id(problem), 'proposal source/problem mismatch')
    execution_path = source_path.parent/'source-execution.json'
    execution_document = source_execution_document(source_path)
    snapshot_root = directory/'source-context'
    closure = {ref.path:ref for ref in problem.evidence}
    for value in execution_document['collection']['code_refs']:
        ref = ArtifactRef(**value)
        _require(ref.path not in closure or closure[ref.path] == ref, 'conflicting frozen source dependency')
        closure[ref.path] = ref
    _require(sum(ref.size for ref in closure.values()) <= 32*MIB, 'source metadata closure exceeds cap')
    for ref in closure.values():
        raw = _raw(source_path.parent,ArtifactRef('snapshots/'+ref.sha256,ref.sha256,ref.size),8*MIB)
        _write(snapshot_root/ref.path,raw)
    _write(snapshot_root/'source-execution.json',_bytes(execution_path))
    source = {'directory':str(source_path.parent),
              'manifest':asdict(ArtifactRef(source_path.name,hashlib.sha256(source_raw).hexdigest(),len(source_raw))),
              'execution':asdict(_ref(snapshot_root,'source-execution.json'))}
    reader = _reader(problem,source,snapshot_root)
    document = problem.to_dict()
    document['problem_id'] = problem_id(problem)
    _write(directory/'problem.json',canonical_bytes(document))
    paths = (*_RUNTIME,'scripts/whole_source/slice.py','scripts/whole_source/gram.py',
             'scripts/whole_source/pipeline.py','scripts/whole_source/proposal.py',
             'scripts/whole_source/proposal_float.py','scripts/weil_whole_source_split.py')
    refs = {_ref(root,p).path:_ref(root,p) for p in paths}
    for name in closure:
        path = (snapshot_root/name).relative_to(root).as_posix()
        refs[path] = _ref(root,path)
    path = (snapshot_root/'source-execution.json').relative_to(root).as_posix()
    refs[path] = _ref(root,path)
    refs = tuple(refs[p] for p in sorted(refs))
    policy = {'native_bits':BITS,'working_grid_bits':BITS,'transform_bits':TRANSFORM_BITS,
              'theta_bits':40,'panel_size':panel_size,'logtheta_bounds':[-20,20]}
    proposal_id = hashlib.sha256(canonical_bytes({'problem_id':problem_id(problem),
        'source':source['manifest'],'policy':policy,'code':[asdict(ref) for ref in refs]})).hexdigest()
    context = {'proposal_id':proposal_id,'problem_id':problem_id(problem),
               'source_sha256':reader.ref.sha256,'dimension':reader.document['geometry']['N']//2,
               'panel_size':panel_size,'precision_bits':BITS,'grid_bits':BITS,'transform_bits':TRANSFORM_BITS}
    accounts = _proposal_accounts(context['dimension'],panel_size)
    _require(accounts['task_bytes'] <= 128*1024 and
             max(accounts['native_result_bytes'],accounts['floating_result_bytes']) <= MIB,
             'proposal task geometry exceeds bounded transport')
    phases = {}
    for phase,backend in (('native','python-flint'),('floating','numpy-scipy')):
        version = (importlib.metadata.version('python-flint') if phase == 'native' else
                   '/'.join(importlib.metadata.version(name) for name in ('numpy','scipy')))
        origin = directory/(phase+'-origin.json')
        _write(origin,canonical_bytes({'format':'whole-source-code-origin-v1',
            'origin_git_commit':origin_git_commit,'origin_git_dirty':origin_git_dirty,
            'reader_contexts':[snapshot_root.relative_to(root).as_posix()],
            'files':[asdict(ref) for ref in refs]}))
        scratch_mib = (accounts[phase+'_staging_bytes']+MIB-1)//MIB+16
        from scripts.whole_source.artifacts import CodecBounds
        bounds = CodecBounds(8*MIB,8*MIB,8*MIB,16384,8192,256*1024,64*1024,
                             8*1024*MIB,scratch_mib*MIB,64*MIB)
        quantities = tuple(q for q in _quantities(problem,reader.document['control']) if q.key.name == 'A_model')
        spec = CollectionSpec.create(problem,role='proposal',quantities=quantities,
            partition=_partition(problem,reader.document['control'],panel_size),
            backend=backend,backend_version=version,native_threads=1,code_refs=refs,
            bounds=bounds,code_root=root,grid_bits=BITS)
        plan = ExecutionPlan(problem_id(problem),spec.collection_id,'proposal',1,1,1,
            memory_mib=memory_mib or 1,reserve_mib=128,root_mib=128,worker_base_mib=80,
            worker_private_mib=128,native_workspace_mib=128,conversion_mib=64,
            codec_mib=256,queue_mib=8,supervisor_increment_mib=256,
            repository_mib=8192,temporary_mib=scratch_mib,minimum_free_mib=64,
            max_tasks=accounts[phase+'_max_tasks'],task_bytes=accounts['task_bytes'],
            result_bytes=accounts[phase+'_result_bytes'],log_bytes=4*MIB,
            task_program=_ref(root,'scripts/whole_source/proposal.py'),task_function='evaluate_proposal',
            precision_bits=BITS,backend=backend,backend_version=version,
            provenance=_ref(root,origin.relative_to(root).as_posix()),scope=SCOPE)
        from dataclasses import replace
        from scripts.whole_source.resources import auto_plan
        plan = auto_plan(plan,parallel=phase == 'native',memory_mib=memory_mib,helper_root=root)
        spec = replace(spec,native_threads=plan.threads)
        spec._validate()
        plan = replace(plan,collection_sha256=spec.collection_id)
        _require(accounts[phase+'_working_bytes'] <= plan.worker_private_mib*MIB,
                 'proposal buffers exceed their admitted account')
        phases[phase] = {'collection':spec.to_dict(),'execution':plan.to_dict()}
    config = {'format':'whole-source-proposal-execution-v3','source':source,
              'source_snapshot':snapshot_root.relative_to(root).as_posix(),'context':context,
              'policy':policy,'phases':phases,'control':reader.document['control'],
              'layout':_proposal_layout(context['dimension'],panel_size)}
    _write(directory/'execution.json',canonical_bytes(config))
    return {'problem':directory/'problem.json','execution':directory/'execution.json'}


def _bind_proposal(problem_path, source_path, execution_path, root):
    document,config = (_json(_bytes(Path(p))) for p in (problem_path,execution_path))
    problem = bind_problem(document['parameters']['profile'],root=root)
    expected = problem.to_dict()
    expected['problem_id'] = problem_id(problem)
    _require(canonical_bytes(expected) == canonical_bytes(document) and problem.profile == 'retained-t081',
             'changed or unqualified proposal problem')
    _require(set(config) == {'format','source','source_snapshot','context','policy','phases','control','layout'} and
             config['format'] == 'whole-source-proposal-execution-v3' and type(config['control']) is bool and
             set(config['phases']) == {'native','floating'}, 'invalid proposal execution contract')
    _require(Path(config['source']['directory'])/config['source']['manifest']['path'] == Path(source_path).resolve(),
             'proposal source locator differs from its binding')
    snapshot_ref = ArtifactRef(config['source_snapshot'],'0'*64,0)
    reader = _reader(problem,config['source'],root/snapshot_ref.path)
    context,policy = config['context'],config['policy']
    _require(type(policy['panel_size']) is int and 1 <= policy['panel_size'] <= 32 and
             canonical_bytes(policy) == canonical_bytes({'native_bits':BITS,'working_grid_bits':BITS,
                'transform_bits':TRANSFORM_BITS,'theta_bits':40,'panel_size':policy['panel_size'],
                'logtheta_bounds':[-20,20]}), 'changed proposal numerical policy')
    bound = {}
    for name,backend in (('native','python-flint'),('floating','numpy-scipy')):
        spec = CollectionSpec.from_dict(problem,config['phases'][name]['collection'],code_root=root)
        plan = ExecutionPlan.from_dict(config['phases'][name]['execution'])
        _require(spec.role == plan.role == 'proposal' and plan.backend == spec.backend == backend and
                 plan.problem_sha256 == problem_id(problem) and plan.collection_sha256 == spec.collection_id and
                 plan.backend_version == spec.backend_version and plan.threads == spec.native_threads and
                 spec.grid_bits == BITS and plan.precision_bits == BITS and plan.scope == SCOPE and
                 plan.task_program.path == 'scripts/whole_source/proposal.py' and
                 plan.task_function == 'evaluate_proposal' and
                 plan.repository_mib == 8192 and spec.bounds.max_total_bytes == 8192*MIB and
                 (name != 'floating' or plan.workers == 1) and
                 type(plan.resource_policy) is dict and plan.resource_policy['parallel'] is (name == 'native'),
                 'changed proposal execution role/policy')
        bound[name] = spec,plan
    _require(bound['native'][0].code_refs == bound['floating'][0].code_refs,'proposal phases have different code closures')
    identity = hashlib.sha256(canonical_bytes({'problem_id':problem_id(problem),
        'source':config['source']['manifest'],'policy':policy,
        'code':[asdict(ref) for ref in bound['native'][0].code_refs]})).hexdigest()
    expected_context = {'proposal_id':identity,'problem_id':problem_id(problem),
        'source_sha256':reader.ref.sha256,'dimension':reader.document['geometry']['N']//2,
        'panel_size':policy['panel_size'],'precision_bits':BITS,'grid_bits':BITS,'transform_bits':TRANSFORM_BITS}
    _require(canonical_bytes(context) == canonical_bytes(expected_context) and
             reader.document['control'] is config['control'], 'changed proposal context or geometry')
    accounts = _proposal_accounts(context['dimension'],context['panel_size'])
    _require(canonical_bytes(config['layout']) == canonical_bytes(
                 _proposal_layout(context['dimension'],context['panel_size'])),
             'changed proposal task layout')
    _require(accounts['task_bytes'] <= 128*1024 and
             max(accounts['native_result_bytes'],accounts['floating_result_bytes']) <= MIB,
             'proposal task geometry exceeds bounded transport')
    for phase,(spec,plan) in bound.items():
        _require(plan.max_tasks == accounts[phase+'_max_tasks'] and
                 plan.task_bytes == accounts['task_bytes'] and
                 plan.result_bytes == accounts[phase+'_result_bytes'],
                 'changed proposal task transport geometry')
        _require(accounts[phase+'_working_bytes'] <= plan.worker_private_mib*MIB,
                 'proposal buffers exceed their admitted account')
        _require(accounts[phase+'_staging_bytes'] <= spec.bounds.max_temporary_bytes and
                 accounts[phase+'_staging_bytes'] <= plan.temporary_mib*MIB,
                 'complete proposal stage scratch exceeds its admitted disk allowance')
        retained = accounts['per_parity_panel_disk_bytes']+accounts['retained_graph_bytes']+64*MIB
        _require(retained <= spec.bounds.max_total_bytes and retained <= plan.repository_mib*MIB,
                 'complete proposal panel stores exceed repository allowance')
    return problem,config,bound


def _make_tasks(base, operation, dependencies, column=None):
    grid = _grid(base['context'])
    if operation == 'factor-diagonal':
        geometry = [{'column':column}]
    elif operation == 'factor-below':
        geometry = [{'column':column,'row':i} for i in grid if i > column]
    elif operation.startswith('whiten-'):
        geometry = [{'family':family,'column':j} for family in _FAMILIES for j in grid]
    elif operation == 'float-optimize':
        geometry = [{}]
    else:
        _require(operation == 'backsolve-quantize','unknown proposal task factory operation')
        geometry = [{'column':j} for j in grid]
    tasks = []
    for coordinates in geometry:
        task = {**base,'operation':operation,'dependencies':dependencies,**coordinates}
        task['task_id'] = hashlib.sha256(canonical_bytes(task)).hexdigest()
        _task_panels(task)
        tasks.append(task)
    return tasks


def _validate_result(result, task, root, attempt_id):
    expected = _task_panels(task)
    _require(type(result) is dict and set(result) == {'scope','panels','diagnostics'} and
             result['scope'] == SCOPE and type(result['panels']) is dict and
             set(result['panels']) == expected and type(result['diagnostics']) is dict,
             'changed proposal task scope or output coverage')
    staging = 'attempts/'+attempt_id+'/staging/'
    for name in sorted(expected):
        ref = ArtifactRef(**result['panels'][name])
        _require(ref.path.startswith(staging),'foreign proposal scratch')
        checker = PanelStore(root,task['context'],{name:asdict(ref)})
        kind = 'integer' if name.startswith('Z/') else ('binary64' if name.startswith('V/') else 'interval')
        if kind == 'integer':
            for value in checker.read(name,kind):
                decode_integer(value,8192)
        else:
            checker._integers(name,kind)


def _commit_panels(lock, result):
    panels = {}
    for name in sorted(result['panels']):
        ref = ArtifactRef(**result['panels'][name])
        raw = _raw(lock.root,ref,8*MIB)
        panels[name] = asdict(lock._immutable('seals',raw))
        # The immutable copy is the dependency, not worker scratch. Failed
        # publications retain prior immutable copies without a committed group.
        _safe(lock.root,ref.path).unlink()
    return panels


def _run_wave(lock, execution, tasks, operation, column=None):
    _require(tasks,'empty proposal wave')
    context = tasks[0]['context']
    expected,cover = {},set()
    for task in tasks:
        names = _task_panels(task)
        _require(task['operation'] == operation and task['context'] == context and
                 task['task_id'] not in expected and not (cover & names),
                 'repeated or mixed proposal wave task')
        if operation.startswith('factor-'):
            _require(task['column'] == column,'mixed factor columns')
        expected[task['task_id']] = task
        cover.update(names)
    _require(cover == _wave_names(context,operation,column),'incomplete proposal wave geometry')
    stage = operation+('_'+str(column) if column is not None else '')
    execution.run_stage(stage,tasks)
    results = {}
    for row in execution.read_results(stage):
        task_id = row['task_id']
        _require(task_id in expected and task_id not in results and row['scope'] == SCOPE,
                 'foreign or repeated proposal result')
        result = row['result']
        _validate_result(result,expected[task_id],lock.root,execution.attempt_id)
        results[task_id] = result
    _require(set(results) == set(expected),'incomplete proposal stage result')
    panels,diagnostics = {},[]
    # Canonical task order, not pool completion order, owns publication.
    for task in tasks:
        result = results[task['task_id']]
        panels.update(_commit_panels(lock,result))
        diagnostics.append({'task_id':task['task_id'],'diagnostics':result['diagnostics']})
    record = seal_group(lock,execution,stage,_wave_context(context,operation,column),panels)
    report = {'status':'NONPROOF_ONLY','scope':SCOPE,'attempt_id':execution.attempt_id,
              'dependency':{'operation':operation,'column':column,'record':record},
              'diagnostics':diagnostics[0]['diagnostics'] if len(tasks) == 1 else {},
              'tasks':diagnostics,'owned_receipts':exact_telemetry(execution.receipts[-1:]),
              'production_admission':False}
    _write(lock.root/(stage+'-result.json'),canonical_bytes(report))
    return report


def _run_proposal_stage(output, spec, plan, tasks, operation, *, code_root):
    with CollectionLock.acquire(output,spec) as lock:
        with WorkloadExecution(lock,spec,plan,code_root=code_root) as execution:
            return _run_wave(lock,execution,tasks,operation)


def _run_native_graph(output, spec, plan, base, *, code_root):
    factors,stages = [],[]
    with CollectionLock.acquire(output,spec) as lock:
        with WorkloadExecution(lock,spec,plan,code_root=code_root) as execution:
            for j in _grid(base['context']):
                diagonal = _run_wave(lock,execution,
                    _make_tasks(base,'factor-diagonal',{'factor':list(factors)},j),'factor-diagonal',j)
                factors.append(diagonal['dependency'])
                stages.append(diagonal)
                tasks = _make_tasks(base,'factor-below',{'factor':list(factors)},j)
                if tasks:
                    below = _run_wave(lock,execution,tasks,'factor-below',j)
                    factors.append(below['dependency'])
                    stages.append(below)
            forward = _run_wave(lock,execution,
                _make_tasks(base,'whiten-forward',{'factor':factors}),'whiten-forward')
            stages.append(forward)
            transpose = _run_wave(lock,execution,_make_tasks(base,'whiten-transpose',
                {'factor':factors,'forward':[forward['dependency']]}),'whiten-transpose')
            stages.append(transpose)
    return {'factors':factors,'whitened':transpose['dependency'],'stages':stages}


def run_proposal(problem_path, source_path, execution_path, output_dir, *, code_root=ROOT):
    root,output = Path(code_root).resolve(),Path(output_dir).absolute()
    problem,config,bound = _bind_proposal(problem_path,source_path,execution_path,root)
    n,b = config['context']['dimension'],config['context']['panel_size']
    # Use the existing operation-wide OS lock, not independent phase locks alone.
    with _slice_writer(output,resume=False):
        try:
            blocks,diagnostics = [],[]
            for parity in (0,1):
                context = {**config['context'],'parity':parity}
                base = {'context':context,'source':config['source'],'source_snapshot':config['source_snapshot']}
                native = _run_native_graph(output/('native-'+str(parity)),*bound['native'],base,code_root=root)
                floating = _run_proposal_stage(output/('floating-'+str(parity)),*bound['floating'],
                    _make_tasks(base,'float-optimize',{'whitened':[native['whitened']]}),
                    'float-optimize',code_root=root)
                solved = _run_proposal_stage(output/('solve-'+str(parity)),*bound['native'],
                    _make_tasks(base,'backsolve-quantize',
                                {'factor':native['factors'],'floating':[floating['dependency']]}),
                    'backsolve-quantize',code_root=root)
                inventory = _dependency_store([solved['dependency']],context,[('backsolve-quantize',None)],binding=base)
                panels = []
                for i in range(0,n,b):
                    for j in range(0,n,b):
                        name = f'Z/{i}/{j}'
                        inventory.read(name,'integer')
                        ref = ArtifactRef(**inventory.refs[name])
                        panels.append({'row':i,'column':j,'artifact':asdict(ArtifactRef(
                            (inventory.root/ref.path).relative_to(output).as_posix(),
                            ref.sha256,ref.size))})
                theta = Fraction(floating['diagnostics']['theta'])
                _require(theta > 0 and (theta*(1 << 40)).denominator == 1,'invalid dyadic Young proposal')
                blocks.append({'parity':parity,'dimension':n,'u':TRANSFORM_BITS,'theta':str(theta),
                               'context':context,'integer_panels':panels,'inherited_coordinates_used':False})
                diagnostics.append({'parity':parity,'native':native,'floating':floating,'solve':solved})
            diagnostic_ref = _write(output/'proposal-diagnostics.json',canonical_bytes({
                'format':'whole-source-proposal-diagnostics-v1','status':'NONPROOF_ONLY','blocks':diagnostics}))
            core = {'format':'whole-source-congruence-proposal-v1','status':'NONPROOF_ONLY',
                'scope':SCOPE,'problem_id':problem_id(problem),'source':config['source']['manifest'],
                'source_directory_at_execution':config['source']['directory'],
                'source_control':config['control'],'policy':config['policy'],
                'code':[asdict(ref) for ref in bound['native'][0].code_refs],
                'backend_versions':{name:plan.backend_version for name,(_,plan) in bound.items()},
                'diagnostics':asdict(diagnostic_ref),'blocks':blocks,
                'analytical_acceptance':False,'matrix_positivity':False,'production_admission':False}
            pending = output/'proposal-pending.json'
            _write(pending,canonical_bytes(core))
            read_proposal(pending,problem,config['source']['manifest'])
            _write(output/'proposal.json',canonical_bytes(core))
            pending.unlink()
            return core
        except BaseException as exc:
            _write(output/'proposal-state.json',canonical_bytes({
                'status':'NONPROOF_PROPOSAL_UNRESOLVED','scope':SCOPE,
                'error_type':type(exc).__name__,'error':str(exc),
                'matrix_positivity':False,'production_admission':False}))
            raise


def read_proposal(path, problem, source_ref):
    """Read every integer coordinate; this is structural, never exact-sign acceptance."""
    from scripts.whole_source.pipeline import math_problem
    path = Path(path).resolve()
    value = _json(_bytes(path))
    _require(set(value) == {'format','status','scope','problem_id','source','source_directory_at_execution',
                'source_control','policy','code','backend_versions','diagnostics','blocks',
                'analytical_acceptance','matrix_positivity','production_admission'} and
             value['format'] == 'whole-source-congruence-proposal-v1' and value['status'] == 'NONPROOF_ONLY' and
             value['scope'] == SCOPE and value['problem_id'] == problem_id(problem) and
             canonical_bytes(value['source']) == canonical_bytes(source_ref) and
             type(value['source_control']) is bool and
             value['analytical_acceptance'] is False and value['matrix_positivity'] is False and
             value['production_admission'] is False and type(value['blocks']) is list and len(value['blocks']) == 2,
             'invalid nonproof proposal core')
    policy = value['policy']
    b = policy['panel_size']
    _require(type(b) is int and 1 <= b <= 32 and
             canonical_bytes(policy) == canonical_bytes({'native_bits':BITS,'working_grid_bits':BITS,
                'transform_bits':TRANSFORM_BITS,'theta_bits':40,'panel_size':b,'logtheta_bounds':[-20,20]}),
             'changed proposal core numerical policy')
    code = [ArtifactRef(**ref) for ref in value['code']]
    _require([ref.path for ref in code] == sorted({ref.path for ref in code}) and
             set(_RUNTIME) | {'scripts/whole_source/proposal.py','scripts/whole_source/proposal_float.py'} <=
             {ref.path for ref in code}, 'invalid proposal code closure')
    _require(type(value['backend_versions']) is dict and set(value['backend_versions']) == {'native','floating'} and
             all(type(v) is str and 0 < len(v) <= 256 for v in value['backend_versions'].values()),
             'missing proposal backend version bindings')
    identity = hashlib.sha256(canonical_bytes({'problem_id':problem_id(problem),
        'source':source_ref,'policy':policy,'code':value['code']})).hexdigest()
    n = math_problem(problem,value['source_control']).N//2
    _raw(path.parent,ArtifactRef(**value['diagnostics']),8*MIB)
    for parity,block in enumerate(value['blocks']):
        context = {'proposal_id':identity,'problem_id':problem_id(problem),'source_sha256':source_ref['sha256'],
            'dimension':n,'panel_size':b,'precision_bits':BITS,'grid_bits':BITS,
            'transform_bits':TRANSFORM_BITS,'parity':parity}
        theta = Fraction(block['theta'])
        _require(set(block) == {'parity','dimension','u','theta','context','integer_panels','inherited_coordinates_used'} and
                 type(block['parity']) is int and block['parity'] == parity and
                 type(block['dimension']) is int and block['dimension'] == n and
                 type(block['u']) is int and block['u'] == TRANSFORM_BITS and theta > 0 and
                 canonical_bytes(block['context']) == canonical_bytes(context) and
                 str(theta) == block['theta'] and (theta*(1 << 40)).denominator == 1 and
                 block['inherited_coordinates_used'] is False, 'invalid complete proposal block')
        expected = [(i,j) for i in range(0,n,b) for j in range(0,n,b)]
        _require(type(block['integer_panels']) is list and
                 [(r['row'],r['column']) for r in block['integer_panels']] == expected and
                 all(type(r['row']) is int and type(r['column']) is int and
                     set(r) == {'row','column','artifact'} for r in block['integer_panels']),
                 'incomplete proposal coordinate panels')
        count,refs = 0,{}
        for row in block['integer_panels']:
            name = f"Z/{row['row']}/{row['column']}"
            refs[name] = row['artifact']
        store = PanelStore(path.parent,context,refs)
        for name in refs:
            for integer in store.read(name,'integer'):
                decode_integer(integer,8192)
                count += 1
        _require(count == n*n,'incomplete full rational transform')
    return value
