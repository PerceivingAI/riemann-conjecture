"""Fresh blocked congruence proposals. Every output is NONPROOF_ONLY."""
from __future__ import annotations

from dataclasses import asdict
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
from scripts.whole_source.pipeline import SourceReader, _fixed_bounds, _quantities, _partition
from scripts.whole_source.slice import _ref, _slice_writer

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

    def read(self, name, kind):
        ref = ArtifactRef(**self.refs[name])
        value = _json(_raw(self.root, ref, 8*MIB))
        header = self._header(name, kind)
        _require(set(value) == {'header', 'values'} and
                 canonical_bytes(value['header']) == canonical_bytes(header) and
                 type(value['values']) is list and
                 len(value['values']) == header['rows']*header['columns'], 'changed proposal panel')
        return value['values']

    def put_native(self, name, matrix):
        values = []
        for i in range(matrix.nrows()):
            for j in range(matrix.ncols()):
                lo, hi = _fixed_bounds(matrix[i,j], BITS)
                values.append([encode_integer(lo, 8192), encode_integer(hi, 8192)])
        self.put(name, 'interval', values)

    def native(self, name):
        from flint import arb, arb_mat, fmpq
        values = self.read(name, 'interval')
        _, i, j = _NAMES.fullmatch(name).groups()
        rows, columns = _shape(self.context, int(i), int(j))
        result = arb_mat(rows, columns)
        for k, pair in enumerate(values):
            _require(type(pair) is list and len(pair) == 2, 'invalid interval panel value')
            lo, hi = (decode_integer(v, 8192) for v in pair)
            _require(lo <= hi, 'inverted proposal panel interval')
            result[k//columns,k%columns] = arb(fmpq(lo+hi, 1 << (BITS+1)), arb(fmpq(hi-lo, 1 << (BITS+1))))
        return result

    def vectors(self, name):
        from flint import arb, arb_mat, fmpq
        values = self.read(name, 'binary64')
        _, i, j = _NAMES.fullmatch(name).groups()
        rows, columns = _shape(self.context, int(i), int(j))
        result = arb_mat(rows, columns)
        for k, value in enumerate(values):
            _require(type(value) is str, 'noncanonical floating vector')
            x = float.fromhex(value)
            _require(x.hex() == value and x == x and abs(x) != float('inf'), 'nonfinite floating vector')
            result[k//columns,k%columns] = arb(fmpq(*x.as_integer_ratio()))
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


def blocked_cholesky(matrix, store):
    """Factor the actual paid A, persisting only bounded lower-triangular panels."""
    from flint import arb_mat
    n, b = store.context['dimension'], store.context['panel_size']
    smallest = None
    for j in range(0,n,b):
        diagonal = matrix(j,j)
        for k in range(0,j,b):
            panel = store.native(f'L/{j}/{k}')
            diagonal -= panel*panel.transpose()
        width = diagonal.nrows()
        factor = arb_mat(width,width)
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
        store.put_native(f'L/{j}/{j}', factor)
        # Subsequent solves use the same paid persisted diagonal, not a hidden
        # higher-precision factor retained only in this producer process.
        factor = store.native(f'L/{j}/{j}')
        for i in range(j+b,n,b):
            value = matrix(i,j)
            for k in range(0,j,b):
                value -= store.native(f'L/{i}/{k}')*store.native(f'L/{j}/{k}').transpose()
            store.put_native(f'L/{i}/{j}', _dense_solve(factor,value.transpose()).transpose())
    return smallest


def triangular_solve(factor, rhs, output, prefix, *, transpose=False, transpose_output=False):
    """Full panel solve. Earlier panels are never omitted from an update."""
    n, b = output.context['dimension'], output.context['panel_size']
    order = list(range(0,n,b))
    if transpose:
        order.reverse()
    for j in range(0,n,b):
        for index,i in enumerate(order):
            value = rhs(i,j)
            for k in order[:index]:
                panel = factor.native(f'L/{k}/{i}').transpose() if transpose else factor.native(f'L/{i}/{k}')
                prior = (output.native(f'{prefix}/{j}/{k}').transpose() if transpose_output
                         else output.native(f'{prefix}/{k}/{j}'))
                value -= panel*prior
            value = _dense_solve(factor.native(f'L/{i}/{i}'), value, transpose=transpose)
            name = f'{prefix}/{j}/{i}' if transpose_output else f'{prefix}/{i}/{j}'
            output.put_native(name, value.transpose() if transpose_output else value)


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
        for row in reader.document['tiles']:
            task = _task(row['task'])
            self.index[row['family'],row['parity'],task.rows.start,task.columns.start] = row

    def matrix(self, family, i, j):
        from flint import arb, arb_mat, fmpq
        from scripts.whole_source.artifacts import _partition_widths, _task, decode_publication
        p, b = self.context['parity'], self.context['panel_size']
        rows, columns = _shape(self.context,i,j)
        quantity_name = {'A_model':'A_model','weighted_head':'head_complete','weighted_complete_tail':'tail_complete'}[family]
        q = self.reader.spec.quantity(QuantityKey(quantity_name,p))
        widths = _partition_widths(self.reader.spec,q.key)
        result, decoded = arb_mat(rows,columns), {}
        for r in range(rows):
            for c in range(columns):
                m,n = 2*(i+r)+p,2*(j+c)+p
                u,v = min(m,n),max(m,n)
                sr = q.rows.start+((u-q.rows.start)//(2*widths['rows']))*2*widths['rows']
                sc = q.columns.start+((v-q.columns.start)//(2*widths['columns']))*2*widths['columns']
                key = family,p,sr,sc
                if key not in decoded:
                    row = self.index[key]
                    records = decode_publication(self.reader.spec,
                        _raw(self.reader.path.parent,ArtifactRef(**row['artifact']),8*MIB),
                        _task(row['task']),self.reader.bits)
                    decoded[key] = {(entry.row,entry.column):entry for entry in records}
                entry = decoded[key][u,v]
                middle, radius = (entry.lower+entry.upper)/2,(entry.upper-entry.lower)/2
                value = arb(fmpq(middle.numerator,middle.denominator),arb(fmpq(radius.numerator,radius.denominator)))
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
    spec = CollectionSpec.from_dict(problem,document['collection'],code_root=snapshot_root)
    _require(spec.role == 'producer' and type(document['control']) is bool, 'proposal requires a producer source')
    return SourceReader(Path(source['directory'])/source['manifest']['path'],spec,control=document['control'])


def _input_store(value, context):
    root = Path(value['root'])
    document = _json(_raw(root,ArtifactRef(**value['inventory']),8*MIB))
    _require(set(document) == {'format','context','panels'} and document['format'] == 'nonproof-panel-inventory-v1' and
             canonical_bytes(document['context']) == canonical_bytes(context) and
             type(document['panels']) is dict, 'changed proposal panel inventory')
    return PanelStore(root,context,document['panels'])


def evaluate_proposal(task, staging):
    """Owned entry point. Numerical imports follow actual job/BLAS admission."""
    from scripts.whole_source import execution
    worker = execution._WORKER
    _require(worker is not None and worker[-1] is staging and worker[0].role == 'proposal' and
             worker[0].scope == SCOPE, 'proposal requires its owned nonproof context')
    staging._check()
    context = task['context']
    _require(context['precision_bits'] == BITS and context['grid_bits'] == BITS and
             context['transform_bits'] == TRANSFORM_BITS, 'changed proposal precision policy')
    store = PanelStore(staging.root,context,staging=staging)
    n,b = context['dimension'],context['panel_size']
    operation = task['operation']
    diagnostics = {'status':'NONPROOF_ONLY','production_admission':False}
    if operation == 'factor-whiten':
        _require(worker[0].backend == 'python-flint' and 'numpy' not in sys.modules,
                 'native proposal overlaps floating libraries')
        reader = _reader(staging.spec.problem,task['source'],ROOT/task['source_snapshot'])
        _require(reader.ref.sha256 == context['source_sha256'] and
                 reader.document['geometry']['N']//2 == n, 'changed proposal source geometry')
        source = SourcePanels(reader,context)
        smallest = blocked_cholesky(lambda i,j:source.matrix('A_model',i,j),store)
        for family,name in (('A','A_model'),('H','weighted_head'),('E','weighted_complete_tail')):
            whiten_tiles(lambda i,j:source.matrix(name,i,j),store,family)
        diagnostics['minimum_native_pivot_lower'] = str(smallest)
        diagnostics['native_bits'] = BITS
    elif operation == 'float-optimize':
        _require(worker[0].backend == 'numpy-scipy' and 'flint' not in sys.modules,
                 'floating proposal overlaps native arithmetic')
        # Explicit global exception: input arrays, residual/Gram copies, full
        # eigenvectors and conservative dense LAPACK workspace, before imports.
        dense_account = 16*n*n*8+32*n*8+8*MIB
        _require(dense_account <= worker[0].worker_private_mib*MIB,
                 'dense float proposal exceeds its admitted global-array account')
        native = _input_store(task['input'],context)
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
        _require(worker[0].backend == 'python-flint' and 'numpy' not in sys.modules,
                 'native backsolve overlaps floating libraries')
        native = _input_store(task['native'],context)
        floating = _input_store(task['floating'],context)
        triangular_solve(native,lambda i,j:floating.vectors(f'V/{i}/{j}'),store,'W',transpose=True)
        for i in range(0,n,b):
            for j in range(0,n,b):
                matrix = store.native(f'W/{i}/{j}')
                values = []
                for r in range(matrix.nrows()):
                    for c in range(matrix.ncols()):
                        midpoint = Fraction(str(matrix[r,c].mid().fmpq()))*(1 << TRANSFORM_BITS)
                        integer = (2*midpoint.numerator+midpoint.denominator)//(2*midpoint.denominator)
                        values.append(encode_integer(integer,8192))
                store.put(f'Z/{i}/{j}','integer',values)
        diagnostics['transform_entries'] = n*n
        diagnostics['native_bits'] = BITS
    else:
        raise ContractError('unknown proposal operation')
    return {'panels':store.created,'diagnostics':diagnostics,'scope':SCOPE}


def prepare_proposal_inputs(problem, source_path, directory, *, origin_git_commit,
                            origin_git_dirty, code_root=ROOT, panel_size=32, memory_mib=1536):
    """Bind source snapshots and proposal policy without importing numerical libraries."""
    _require(problem.profile == 'retained-t081', 'target proposal execution is not qualified')
    _require(type(panel_size) is int and 1 <= panel_size <= 32, 'invalid proposal panel width')
    root, directory, source_path = Path(code_root).resolve(), Path(directory).resolve(), Path(source_path).resolve()
    directory.relative_to(root)
    directory.mkdir(parents=True,exist_ok=False)
    source_raw = _bytes(source_path)
    source_document = _json(source_raw)
    _require(source_document['problem_id'] == problem_id(problem), 'proposal source/problem mismatch')
    snapshot_root = directory/'source-context'
    closure = {ref.path:ref for ref in problem.evidence}
    for value in source_document['collection']['code_refs']:
        ref = ArtifactRef(**value)
        _require(ref.path not in closure or closure[ref.path] == ref, 'conflicting frozen source dependency')
        closure[ref.path] = ref
    _require(sum(ref.size for ref in closure.values()) <= 32*MIB, 'source metadata closure exceeds cap')
    for ref in closure.values():
        raw = _raw(source_path.parent,ArtifactRef('snapshots/'+ref.sha256,ref.sha256,ref.size),8*MIB)
        _write(snapshot_root/ref.path,raw)
    source = {'directory':str(source_path.parent),
              'manifest':asdict(ArtifactRef(source_path.name,hashlib.sha256(source_raw).hexdigest(),len(source_raw)))}
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
    refs = tuple(refs[p] for p in sorted(refs))
    policy = {'native_bits':BITS,'working_grid_bits':BITS,'transform_bits':TRANSFORM_BITS,
              'theta_bits':40,'panel_size':panel_size,'logtheta_bounds':[-20,20]}
    proposal_id = hashlib.sha256(canonical_bytes({'problem_id':problem_id(problem),
        'source':source['manifest'],'policy':policy,'code':[asdict(ref) for ref in refs]})).hexdigest()
    context = {'proposal_id':proposal_id,'problem_id':problem_id(problem),
               'source_sha256':reader.ref.sha256,'dimension':reader.document['geometry']['N']//2,
               'panel_size':panel_size,'precision_bits':BITS,'grid_bits':BITS,'transform_bits':TRANSFORM_BITS}
    phases = {}
    for phase,backend in (('native','python-flint'),('floating','numpy-scipy')):
        version = (importlib.metadata.version('python-flint') if phase == 'native' else
                   '/'.join(importlib.metadata.version(name) for name in ('numpy','scipy')))
        origin = directory/(phase+'-origin.json')
        _write(origin,canonical_bytes({'format':'whole-source-code-origin-v1',
            'origin_git_commit':origin_git_commit,'origin_git_dirty':origin_git_dirty,
            'files':[asdict(ref) for ref in refs]}))
        from scripts.whole_source.artifacts import CodecBounds
        bounds = CodecBounds(8*MIB,8*MIB,8*MIB,16384,8192,256*1024,64*1024,
                             8*1024*MIB,128*MIB,64*MIB)
        quantities = tuple(q for q in _quantities(problem,reader.document['control']) if q.key.name == 'A_model')
        spec = CollectionSpec.create(problem,role='proposal',quantities=quantities,
            partition=_partition(problem,reader.document['control'],panel_size),
            backend=backend,backend_version=version,native_threads=1,code_refs=refs,
            bounds=bounds,code_root=root,grid_bits=BITS)
        plan = ExecutionPlan(problem_id(problem),spec.collection_id,'proposal',1,1,1,
            memory_mib=memory_mib,reserve_mib=128,root_mib=128,worker_base_mib=80,
            worker_private_mib=128,native_workspace_mib=128,conversion_mib=64,
            codec_mib=256,queue_mib=8,supervisor_increment_mib=256,
            repository_mib=8192,temporary_mib=128,minimum_free_mib=64,
            max_tasks=32,task_bytes=128*1024,result_bytes=MIB,log_bytes=4*MIB,
            task_program=_ref(root,'scripts/whole_source/proposal.py'),task_function='evaluate_proposal',
            precision_bits=BITS,backend=backend,backend_version=version,
            provenance=_ref(root,origin.relative_to(root).as_posix()),scope=SCOPE)
        phases[phase] = {'collection':spec.to_dict(),'execution':plan.to_dict()}
    config = {'format':'whole-source-proposal-execution-v1','source':source,
              'source_snapshot':snapshot_root.relative_to(root).as_posix(),'context':context,
              'policy':policy,'phases':phases,'control':reader.document['control']}
    _write(directory/'execution.json',canonical_bytes(config))
    return {'problem':directory/'problem.json','execution':directory/'execution.json'}


def _bind_proposal(problem_path, source_path, execution_path, root):
    document,config = (_json(_bytes(Path(p))) for p in (problem_path,execution_path))
    problem = bind_problem(document['parameters']['profile'],root=root)
    expected = problem.to_dict()
    expected['problem_id'] = problem_id(problem)
    _require(canonical_bytes(expected) == canonical_bytes(document) and problem.profile == 'retained-t081',
             'changed or unqualified proposal problem')
    _require(set(config) == {'format','source','source_snapshot','context','policy','phases','control'} and
             config['format'] == 'whole-source-proposal-execution-v1' and type(config['control']) is bool and
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
                 spec.grid_bits == BITS and plan.precision_bits == BITS and plan.scope == SCOPE and
                 plan.task_program.path == 'scripts/whole_source/proposal.py' and
                 plan.task_function == 'evaluate_proposal' and plan.workers == plan.threads == 1,
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
    n,b = context['dimension'],context['panel_size']
    blocks = (n+b-1)//b
    # Native factor plus three full left/whitened stores; inventory/result and
    # factor/solve/codec overlap are bounded before importing FLINT or NumPy.
    panels = blocks*(blocks+1)//2+6*blocks*blocks
    _require(panels*512+65536 <= bound['native'][1].result_bytes,
             'full proposal panel inventory exceeds result transport')
    native_account = 24*b*b*((BITS+7)//8+128)+8*MIB
    float_account = 16*n*n*8+32*n*8+8*MIB
    _require(native_account <= bound['native'][1].worker_private_mib*MIB and
             float_account <= bound['floating'][1].worker_private_mib*MIB,
             'proposal buffers exceed their admitted account')
    return problem,config,bound


def _commit_panels(lock, execution, result, context):
    _require(result['scope'] == SCOPE and type(result['panels']) is dict,
             'changed proposal task scope')
    staging = 'attempts/'+execution.attempt_id+'/staging/'
    panels = {}
    for name,value in result['panels'].items():
        ref = ArtifactRef(**value)
        _require(ref.path.startswith(staging), 'foreign proposal scratch')
        raw = _raw(lock.root,ref,8*MIB)
        data = _json(raw)
        checker = PanelStore(lock.root,context,{name:value})
        _require(canonical_bytes(data['header']) == canonical_bytes(checker._header(name,data['header']['kind'])),
                 'changed staged proposal panel context')
        checker.read(name,data['header']['kind'])
        published = lock._immutable('seals',raw)
        panels[name] = asdict(published)
        _safe(lock.root,ref.path).unlink()
    raw = canonical_bytes({'format':'nonproof-panel-inventory-v1','context':context,'panels':panels})
    inventory = lock._immutable('seals',raw)
    return {'root':str(lock.root),'inventory':asdict(inventory)}


def _run_proposal_stage(output, spec, plan, task, *, code_root):
    with CollectionLock.acquire(output,spec) as lock:
        with WorkloadExecution(lock,spec,plan,code_root=code_root) as execution:
            task['task_id'] = hashlib.sha256(canonical_bytes(task)).hexdigest()
            execution.run_stage(task['operation'],[task])
            rows = list(execution.read_results(task['operation']))
            _require(len(rows) == 1, 'incomplete proposal stage result')
            result = rows[0]['result']
            inventory = _commit_panels(lock,execution,result,task['context'])
            report = {'status':'NONPROOF_ONLY','scope':SCOPE,'attempt_id':execution.attempt_id,
                'inventory':inventory,'diagnostics':result['diagnostics'],
                'owned_receipts':exact_telemetry(execution.receipts),'production_admission':False}
            _write(output/'stage-result.json',canonical_bytes(report))
            return report


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
                native = _run_proposal_stage(output/('native-'+str(parity)),*bound['native'],
                    {'operation':'factor-whiten','context':context,'source':config['source'],
                     'source_snapshot':config['source_snapshot']},code_root=root)
                floating = _run_proposal_stage(output/('floating-'+str(parity)),*bound['floating'],
                    {'operation':'float-optimize','context':context,'input':native['inventory']},code_root=root)
                solved = _run_proposal_stage(output/('solve-'+str(parity)),*bound['native'],
                    {'operation':'backsolve-quantize','context':context,'native':native['inventory'],
                     'floating':floating['inventory']},code_root=root)
                inventory = _input_store(solved['inventory'],context)
                panels = []
                for i in range(0,n,b):
                    for j in range(0,n,b):
                        name = f'Z/{i}/{j}'
                        inventory.read(name,'integer')
                        ref = ArtifactRef(**inventory.refs[name])
                        panels.append({'row':i,'column':j,'artifact':asdict(ArtifactRef(
                            (Path(solved['inventory']['root'])/ref.path).relative_to(output).as_posix(),
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
