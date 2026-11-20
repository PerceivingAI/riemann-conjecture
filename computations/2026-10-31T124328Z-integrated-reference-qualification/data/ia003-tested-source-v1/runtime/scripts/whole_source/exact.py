"""Streamed exact paid-lower assessment. No ball or floating mathematical arithmetic."""
from __future__ import annotations

from dataclasses import asdict
from fractions import Fraction
import hashlib
import importlib.metadata
from math import lcm
from pathlib import Path
import sys
import uuid

from scripts.whole_source.contract import ArtifactRef, ContractError, ROOT, canonical_bytes, problem_id, bind_problem
from scripts.whole_source.artifacts import (
    CollectionSpec, CollectionLock, CodecBounds, _raw, _safe, _task, _partition_widths,
    _check_quota, _volume_gate, publication_integers, decode_integer, decode_rational,
)
from scripts.whole_source.execution import (
    MIB, ExecutionPlan, WorkloadExecution, _RUNTIME, _bytes, _json, _write, exact_telemetry,
)
from scripts.whole_source.pipeline import _quantities, _partition
from scripts.whole_source.proposal import _reader, read_proposal, PanelStore
from scripts.whole_source.slice import _ref, _slice_writer
from scripts.whole_source.exact_global import full_modular_nonsingularity, mass_trace, assess

SCOPE = 'EXACT_ASSESSMENT_ONLY'
SCOPES = ('CONTROL_ONLY','SOURCE_CONDITIONAL','REFERENCE_ARITHMETIC_ONLY')


def _require(value,message):
    if not value:
        raise ContractError(message)


def _fraction(value):
    return decode_rational(value,65536)


def _shape(context,i,j):
    n,b = context['dimension'],context['panel_size']
    _require(type(i) is int and type(j) is int and 0 <= i < n and 0 <= j < n and i%b == j%b == 0,
             'invalid exact panel coordinates')
    return min(b,n-i),min(b,n-j)


class IntegerTiles:
    """One bounded integer tile at a time, with exact context/shape/bit checks."""
    def __init__(self,root,context,refs=None,*,staging=None):
        self.root,self.context,self.staging = Path(root),context,staging
        self.refs = {} if refs is None else dict(refs)
        self.created = {}

    def _header(self,family,i,j):
        _require(family in ('Z','J','S'),'unknown exact panel family')
        rows,columns = _shape(self.context,i,j)
        return {'format':'whole-source-exact-integer-panel-v1','context':self.context,
                'family':family,'row':i,'column':j,'rows':rows,'columns':columns,
                'integer_bits':self.context['z_bits'] if family=='Z' else self.context['product_bits']}

    def put(self,family,i,j,matrix):
        header = self._header(family,i,j)
        _require(matrix.nrows()==header['rows'] and matrix.ncols()==header['columns'],'wrong integer panel shape')
        self.put_values(family,i,j,[int(matrix[r,c]) for r in range(matrix.nrows()) for c in range(matrix.ncols())])

    def put_values(self,family,i,j,integers):
        name = f'{family}/{i}/{j}'
        _require(name not in self.refs,'duplicate exact integer panel')
        header = self._header(family,i,j)
        _require(len(integers)==header['rows']*header['columns'] and
                 all(type(v) is int and abs(v).bit_length()<=header['integer_bits'] for v in integers),
                 'wrong integer panel shape/type/bit account')
        values = [hex(v) for v in integers]
        raw = canonical_bytes({'header':header,'values':values})
        _require(len(raw) <= 8*MIB,'integer panel exceeds bounded codec')
        if self.staging is None:
            relative = uuid.uuid4().hex
            _write(self.root/relative,raw)
        else:
            self.staging._check()
            relative = 'attempts/'+self.staging.attempt_id+'/staging/'+uuid.uuid4().hex
            path = _safe(self.root,relative,missing=True)
            with _volume_gate(self.root):
                _check_quota(self.root,self.staging.spec.bounds,len(raw),len(raw))
                _write(path,raw)
            self.staging._check()
        ref = ArtifactRef(relative,hashlib.sha256(raw).hexdigest(),len(raw))
        self.refs[name] = asdict(ref)
        self.created[name] = asdict(ref)

    def tile(self,i,j,family='Z'):
        from flint import fmpz_mat
        name = f'{family}/{i}/{j}'
        header = self._header(family,i,j)
        value = _json(_raw(self.root,ArtifactRef(**self.refs[name]),8*MIB))
        _require(set(value)=={'header','values'} and
                 canonical_bytes(value['header'])==canonical_bytes(header) and
                 type(value['values']) is list and len(value['values'])==header['rows']*header['columns'],
                 'invalid exact integer panel context/cover')
        result = fmpz_mat(header['rows'],header['columns'])
        for index,text in enumerate(value['values']):
            result[index//header['columns'],index%header['columns']] = decode_integer(text,header['integer_bits'])
        return result


class SourceIntegers:
    """Bounded source decoding; no ball conversion and no full C/R family."""
    def __init__(self,reader,context):
        self.reader,self.context = reader,context
        self.bits = reader.bits
        self.index = {}
        for row in reader.document['tiles']:
            task = _task(row['task'])
            self.index[row['family'],row['parity'],task.rows.start,task.columns.start] = row
        self.consumed = set()

    def bounds(self,family,i,j):
        from flint import fmpz_mat
        from scripts.whole_source.contract import QuantityKey
        p = self.context['parity']
        rows,columns = _shape(self.context,i,j)
        component = {'A_model':'A_model','weighted_head':'head_complete','weighted_complete_tail':'tail_complete'}[family]
        q = self.reader.spec.quantity(QuantityKey(component,p))
        widths = _partition_widths(self.reader.spec,q.key)
        lower,upper = fmpz_mat(rows,columns),fmpz_mat(rows,columns)
        decoded = {}
        for r in range(rows):
            for c in range(columns):
                m,n = 2*(i+r)+p,2*(j+c)+p
                u,v = min(m,n),max(m,n)
                sr = q.rows.start+((u-q.rows.start)//(2*widths['rows']))*2*widths['rows']
                sc = q.columns.start+((v-q.columns.start)//(2*widths['columns']))*2*widths['columns']
                key = family,p,sr,sc
                if key not in decoded:
                    row = self.index[key]
                    ref = ArtifactRef(**row['artifact'])
                    raw = _raw(self.reader.path.parent,ref,8*MIB)
                    records = publication_integers(self.reader.spec,raw,_task(row['task']),self.bits)
                    decoded[key] = {(a,b):(lo,hi) for a,b,lo,hi in records}
                    self.consumed.add((ref.path,ref.sha256,ref.size))
                lo,hi = decoded[key][u,v]
                _require(max(abs(lo).bit_length(),abs(hi).bit_length()) <= self.context['endpoint_bits'],
                         'source endpoint exceeds admitted bit bound')
                lower[r,c],upper[r,c] = lo,hi
        return lower,upper


def paid_parameters(bits,theta,eta):
    _require(type(bits) is int and bits > 0 and type(theta) is Fraction and type(eta) is Fraction and
             theta > 0 and eta > 0,'invalid exact Young/source parameters')
    head,tail = (1+theta)/eta,(1+1/theta)/eta
    scale = lcm(head.denominator,tail.denominator)
    return {'Q':(1 << (bits+1))*scale,'scale':scale,
            'head':head.numerator*(scale//head.denominator),
            'tail':tail.numerator*(scale//tail.denominator)}


def paid_integer_tiles(source,i,j,parameters):
    al,au = source.bounds('A_model',i,j)
    hl,hu = source.bounds('weighted_head',i,j)
    el,eu = source.bounds('weighted_complete_tail',i,j)
    lower = al*parameters['scale']-hu*parameters['head']-eu*parameters['tail']
    upper = au*parameters['scale']-hl*parameters['head']-el*parameters['tail']
    center,radius = lower+upper,upper-lower
    _require(all(radius[r,c]>=0 for r in range(radius.nrows()) for c in range(radius.ncols())),
             'negative exact source radius')
    return center,radius


def integer_bounds(context,parameters,lam):
    n,b = context['dimension'],context['panel_size']
    _require(type(n) is int and n > 0 and type(b) is int and 1 <= b <= 32 and
             type(context['endpoint_bits']) is int and 1 <= context['endpoint_bits'] <= 8192 and
             type(context['z_bits']) is int and 1 <= context['z_bits'] <= 8192 and
             type(lam) is Fraction and lam >= 0,'invalid exact bit-bound inputs')
    L = 1
    for i in range(n):
        L = lcm(L,2*(2*i+context['parity'])+1)
    logn = (n-1).bit_length()
    coefficient = 2*(parameters['scale']+parameters['head']+parameters['tail'])
    c_bits = context['endpoint_bits']+coefficient.bit_length()+1
    product_bits = c_bits+context['z_bits']+logn+1
    transformed_bits = product_bits+context['z_bits']+logn+1
    mass_bits = (2*L).bit_length()+2*context['z_bits']+logn+1
    paid_bits = max(lam.denominator.bit_length()+L.bit_length()+transformed_bits,
                    abs(lam.numerator).bit_length()+parameters['Q'].bit_length()+mass_bits)+1
    # Current source row C/R, old/new native operands/products, mass/transformed
    # tiles, Python/native slots, codec overlap and O(n) row accumulators.
    row_bytes = 2*b*n*((c_bits+7)//8+128)
    tile_bytes = 24*b*b*((max(product_bits,paid_bits,mass_bits)+7)//8+128)
    accumulator_bytes = 12*n*((max(paid_bits,transformed_bits)+7)//8+128)
    blocks = (n+b-1)//b
    staged_bytes = 2*n*n*((product_bits+3)//4+8)+2*blocks*blocks*4096+8*MIB
    return {'mass_lcm':L,'center_bits':c_bits,'product_bits':product_bits,
            'transformed_bits':transformed_bits,'mass_bits':mass_bits,'paid_bits':paid_bits,
            'private_bytes':row_bytes+tile_bytes+accumulator_bytes+16*MIB,
            'staged_bytes':staged_bytes,'result_bytes':2*blocks*blocks*512+2*MIB,
            'modular_workspace_bytes':32*n*n+256*n+16384}


def numerical_width(row_sums,Q,minimum_mass):
    _require(row_sums and all(type(v) is int and v >= 0 for v in row_sums) and
             type(Q) is int and Q > 0 and minimum_mass > 0,'invalid physical radius sum')
    return Fraction(max(row_sums),Q)/minimum_mass


def _absolute(matrix):
    from flint import fmpz_mat
    result = fmpz_mat(matrix.nrows(),matrix.ncols())
    for i in range(matrix.nrows()):
        for j in range(matrix.ncols()):
            result[i,j] = abs(matrix[i,j])
    return result


def complete_rows(diagonal,off_diagonal,radius_sums,directional_radius,i,j,Bn,En):
    """Both global rows receive every symmetric upper off-diagonal contribution."""
    for r in range(Bn.nrows()):
        for c in range(Bn.ncols()):
            a,b = i+r,j+c
            if a>b:
                continue
            center,radius = int(Bn[r,c]),int(En[r,c])
            _require(radius >= 0,'negative transformed exact radius')
            if a==b:
                diagonal[a] = center
                directional_radius[a] = radius
                radius_sums[a] += radius
            else:
                off_diagonal[a] += abs(center)
                off_diagonal[b] += abs(center)
                radius_sums[a] += radius
                radius_sums[b] += radius


def integer_congruence(source,transform,store,parameters,masses,lam):
    from flint import fmpz_mat
    context = store.context
    n,b = context['dimension'],context['panel_size']
    source_rows = [0]*n
    Q,L,u = parameters['Q'],masses['mass_lcm'],context['u']
    for i in range(0,n,b):
        rows = min(b,n-i)
        c_row,r_row = [],[]
        for k in range(0,n,b):
            center,radius = paid_integer_tiles(source,i,k,parameters)
            c_row.append(center)
            r_row.append(radius)
            for r in range(rows):
                source_rows[i+r] += sum(int(radius[r,c]) for c in range(radius.ncols()))
        for j in range(0,n,b):
            cols = min(b,n-j)
            J,S = fmpz_mat(rows,cols),fmpz_mat(rows,cols)
            for index,k in enumerate(range(0,n,b)):
                Z = transform.tile(k,j)
                J += c_row[index]*Z
                S += r_row[index]*_absolute(Z)
            store.put('J',i,j,J)
            store.put('S',i,j,S)
        del c_row,r_row
    diagonal,off,radii,directional_radius = ([0]*n for _ in range(4))
    transformed_digest = hashlib.sha256()
    for i in range(0,n,b):
        for j in range(i,n,b):
            rows,cols = min(b,n-i),min(b,n-j)
            B0,En,G = (fmpz_mat(rows,cols) for _ in range(3))
            for k in range(0,n,b):
                Zi,Zj = transform.tile(k,i),transform.tile(k,j)
                B0 += Zi.transpose()*store.tile(k,j,'J')
                En += _absolute(Zi).transpose()*store.tile(k,j,'S')
                weighted = fmpz_mat(Zj.nrows(),Zj.ncols())
                for r in range(Zj.nrows()):
                    for c in range(Zj.ncols()):
                        weighted[r,c] = masses['mass_weights'][k+r]*Zj[r,c]
                G += Zi.transpose()*weighted
            Bn = B0*(lam.denominator*L)-G*(lam.numerator*Q)
            complete_rows(diagonal,off,radii,directional_radius,i,j,Bn,En)
            transformed_digest.update(canonical_bytes({'row':i,'column':j,
                'center':[hex(int(Bn[r,c])) for r in range(rows) for c in range(cols)],
                'radius':[hex(int(En[r,c])) for r in range(rows) for c in range(cols)]}))
    BD = Q*L*lam.denominator*(1 << (2*u))
    ED = Q*(1 << (2*u))
    factor = L*lam.denominator
    margins = [Fraction(diagonal[i]-off[i]-factor*radii[i],BD) for i in range(n)]
    upper = [Fraction(diagonal[i]+factor*directional_radius[i],BD) for i in range(n)]
    worst = min(range(n),key=lambda i:upper[i])
    return {'width':numerical_width(source_rows,Q,masses['minimum_mass']),
            'margin':min(margins),'row_margins':margins,'direction_index':worst,
            'direction_upper':upper[worst],'direction_mass':masses['direction_masses'][worst],
            'tau':masses['tau'],'Q':hex(Q),'L':hex(L),'center_denominator':hex(BD),'radius_denominator':hex(ED),
            'transformed_upper_entries':n*(n+1)//2,'complete_source_row_sums':[hex(x) for x in source_rows],
            'transformed_digest':transformed_digest.hexdigest()}


def evaluate_exact(task,staging):
    from scripts.whole_source import execution
    worker = execution._WORKER
    _require(worker is not None and worker[-1] is staging and worker[0].role=='exact' and
             worker[0].backend=='python-flint-exact' and worker[0].scope==SCOPE and
             'numpy' not in sys.modules and 'scipy' not in sys.modules,
             'exact arithmetic requires its owned integer-only context')
    staging._check()
    descriptor = _json(_raw(ROOT,ArtifactRef(**task['operands']),8*MIB))
    _validate_operands(staging.spec.problem,descriptor,ROOT)
    if task['operation']=='assess':
        reports = [_json(_raw(staging.root,ArtifactRef(**ref),8*MIB)) for ref in task['blocks']]
        _require(len(reports)==2,'both complete parity reports required')
        for p,report in enumerate(reports):
            context = descriptor['blocks'][p]['context']
            modular = report['modular']
            _require(type(report['parity']) is int and report['parity']==p and
                     report['dimension']==context['dimension'] and report['scope']==descriptor['proof_scope'] and
                     report['source_sha256']==context['source_sha256'] and
                     report['proposal_sha256']==context['proposal_sha256'] and
                     _fraction(report['goal'])==staging.spec.problem.numerical_goal and
                     len(report['row_margins'])==context['dimension'] and
                     min(_fraction(x) for x in report['row_margins'])==_fraction(report['margin']) and
                     modular['prime']==65521 and type(modular['residue']) is int and
                     0<=modular['residue']<65521 and modular['nonsingular'] is (modular['residue']!=0) and
                     modular['global_input_entries']==context['dimension']**2,
                     'changed global exact report context/coverage')
        fields = ('width','goal','margin','tau','direction_upper','direction_mass')
        blocks = [{**{name:_fraction(report[name]) for name in fields},
                   'modular_nonsingular':report['modular']['nonsingular'],
                   'direction_index':report['direction_index']} for report in reports]
        problem = staging.spec.problem
        result = assess(blocks,eta=problem.eta,m=problem.m,b_K=problem.b_K,delta=problem.delta,
                        control=descriptor['proof_scope']!='SOURCE_CONDITIONAL')
        result['proof_scope'] = descriptor['proof_scope']
        result['smooth_test_consequence_conditional'] = (result['positive_paid_lower'] and
                                                        descriptor['proof_scope']=='SOURCE_CONDITIONAL')
        return {'assessment':result,'scope':SCOPE}
    _require(task['operation']=='parity' and type(task['parity']) is int and task['parity'] in (0,1),
             'unknown exact operation/parity')
    p = task['parity']
    block = descriptor['blocks'][p]
    context = block['context']
    _require(context['parity']==p and context['problem_id']==problem_id(staging.spec.problem),
             'changed exact operand identity')
    reader = _reader(staging.spec.problem,descriptor['source'],ROOT/descriptor['source_snapshot'])
    _require(reader.ref.sha256==context['source_sha256'] and reader.document['geometry']['N']//2==context['dimension'],
             'exact source geometry/bytes mismatch')
    source = SourceIntegers(reader,context)
    parameters = paid_parameters(reader.bits,Fraction(block['theta']),staging.spec.problem.eta)
    bounds = integer_bounds(context,parameters,staging.spec.problem.model_error)
    _require(bounds['product_bits']==context['product_bits'] and bounds['private_bytes']<=worker[0].worker_private_mib*MIB and
             bounds['modular_workspace_bytes']<=worker[0].native_workspace_mib*MIB and
             bounds['staged_bytes']<=staging.spec.bounds.max_temporary_bytes,
             'exact operands exceed admitted bit/workspace/disk account')
    transform = IntegerTiles(ROOT,context,block['panels'])
    n,b = context['dimension'],context['panel_size']
    masses = mass_trace(n,p,context['u'],b,transform.tile)
    _require(masses['mass_lcm']==bounds['mass_lcm'],'physical mass account mismatch')
    modular = full_modular_nonsingularity(n,b,transform.tile,
                                          workspace_bytes=worker[0].native_workspace_mib*MIB)
    store = IntegerTiles(staging.root,context,staging=staging)
    report = integer_congruence(source,transform,store,parameters,masses,staging.spec.problem.model_error)
    report.update({'parity':p,'dimension':n,'goal':staging.spec.problem.numerical_goal,
                   'source_sha256':context['source_sha256'],'proposal_sha256':context['proposal_sha256'],
                   'modular':modular,'bit_account':bounds,'source_tiles_consumed':len(source.consumed),
                   'source_consumed_digest':hashlib.sha256(canonical_bytes(sorted(source.consumed))).hexdigest(),
                   'scope':descriptor['proof_scope'],'analytical_source_acceptance':False,
                   'production_admission':False})
    return {'report':report,'panels':store.created,'scope':SCOPE}


def _freeze_source(problem,source_path,directory,root):
    raw = _bytes(source_path)
    document = _json(raw)
    closure = {ref.path:ref for ref in problem.evidence}
    for value in document['collection']['code_refs']:
        ref = ArtifactRef(**value)
        _require(ref.path not in closure or closure[ref.path]==ref,'conflicting source snapshot')
        closure[ref.path] = ref
    _require(sum(ref.size for ref in closure.values()) <= 32*MIB,'source snapshot closure exceeds cap')
    snapshot = directory/'source-context'
    for ref in closure.values():
        value = _raw(source_path.parent,ArtifactRef('snapshots/'+ref.sha256,ref.sha256,ref.size),8*MIB)
        _write(snapshot/ref.path,value)
    source = {'directory':str(source_path.parent),'manifest':asdict(ArtifactRef(
        source_path.name,hashlib.sha256(raw).hexdigest(),len(raw)))}
    reader = _reader(problem,source,snapshot)
    return source,snapshot,reader,[(snapshot/name).relative_to(root).as_posix() for name in closure]


def prepare_exact_operands(problem,source_path,directory,blocks,origin,*,origin_git_commit,
                           origin_git_dirty,code_root=ROOT,proof_scope='REFERENCE_ARITHMETIC_ONLY',
                           memory_mib=None):
    """Normalize only new typed operands; legacy transcription belongs to control adapters."""
    _require(problem.profile=='retained-t081' and proof_scope in SCOPES,'unqualified exact profile/scope')
    root,directory,source_path = Path(code_root).resolve(),Path(directory).resolve(),Path(source_path).resolve()
    directory.relative_to(root)
    directory.mkdir(parents=True,exist_ok=False)
    source,snapshot,reader,paths = _freeze_source(problem,source_path,directory,root)
    _require((origin['kind']=='REFERENCE_TRANSCRIPTION' and proof_scope=='REFERENCE_ARITHMETIC_ONLY') or
             (origin['kind']=='FRESH_NONPROOF' and proof_scope==
              ('CONTROL_ONLY' if reader.document['control'] else 'SOURCE_CONDITIONAL')),
             'origin cannot release a different proof scope')
    origin_raw = _raw(Path(origin['directory']),ArtifactRef(**origin['artifact']),8*MIB)
    _write(directory/'origin-document.json',origin_raw)
    paths.append((directory/'origin-document.json').relative_to(root).as_posix())
    endpoint_bits = [1,1]
    for row in reader.document['tiles']:
        task,ref = _task(row['task']),ArtifactRef(**row['artifact'])
        for _,_,lo,hi in publication_integers(reader.spec,_raw(reader.path.parent,ref,8*MIB),task,reader.bits):
            endpoint_bits[row['parity']] = max(endpoint_bits[row['parity']],abs(lo).bit_length(),abs(hi).bit_length())
    _require(type(blocks) in (list,tuple) and len(blocks)==2,'both exact parity operands required')
    normalized,accounts = [],[]
    for p,block in enumerate(blocks):
        n,b,u = block['dimension'],block['panel_size'],block['u']
        theta = block['theta']
        _require(type(block['parity']) is int and block['parity']==p and type(n) is int and
                 n==reader.document['geometry']['N']//2 and type(b) is int and 1<=b<=32 and
                 type(u) is int and 0<=u<=4096 and type(theta) is Fraction and theta>0,
                 'invalid complete exact transform geometry/parameters')
        z_bits = 1
        for i in range(0,n,b):
            for j in range(0,n,b):
                values = block['read_values'](i,j)
                _require(len(values)==min(b,n-i)*min(b,n-j) and all(type(v) is int for v in values),
                         'incomplete/noninteger transform input')
                z_bits = max(z_bits,max(abs(v).bit_length() for v in values))
        context = {'problem_id':problem_id(problem),'source_sha256':reader.ref.sha256,
            'proposal_sha256':origin['artifact']['sha256'],'parity':p,'dimension':n,'panel_size':b,
            'u':u,'endpoint_bits':endpoint_bits[p],'z_bits':z_bits}
        parameters = paid_parameters(reader.bits,theta,problem.eta)
        account = integer_bounds(context,parameters,problem.model_error)
        _require(max(account['paid_bits'],account['product_bits'],account['mass_bits'])<=65536,
                 'exact operands exceed the integer bit cap')
        context['product_bits'] = account['product_bits']
        target = directory/('transform-'+str(p))
        target.mkdir()
        store = IntegerTiles(target,context)
        for i in range(0,n,b):
            for j in range(0,n,b):
                store.put_values('Z',i,j,block['read_values'](i,j))
        refs = {}
        for name,value in store.refs.items():
            ref = ArtifactRef(**value)
            path = (target/ref.path).relative_to(root).as_posix()
            paths.append(path)
            refs[name] = asdict(ArtifactRef(path,ref.sha256,ref.size))
        normalized.append({'context':context,'theta':str(theta),'panels':refs})
        accounts.append(account)
    descriptor = {'format':'whole-source-exact-operands-v1','problem_id':problem_id(problem),
        'source':source,'source_snapshot':snapshot.relative_to(root).as_posix(),
        'origin':origin,'proof_scope':proof_scope,'blocks':normalized}
    operands_path = directory/'operands.json'
    _write(operands_path,canonical_bytes(descriptor))
    paths.append(operands_path.relative_to(root).as_posix())
    paths.extend((*_RUNTIME,'scripts/whole_source/slice.py','scripts/whole_source/gram.py',
        'scripts/whole_source/pipeline.py','scripts/whole_source/proposal.py',
        'scripts/whole_source/proposal_float.py','scripts/whole_source/exact.py',
        'scripts/whole_source/exact_global.py','scripts/weil_whole_source_split.py'))
    refs = tuple(_ref(root,path) for path in sorted(set(paths)))
    code_origin = directory/'exact-origin.json'
    _write(code_origin,canonical_bytes({'format':'whole-source-code-origin-v1',
        'origin_git_commit':origin_git_commit,'origin_git_dirty':origin_git_dirty,
        'reader_contexts':[snapshot.relative_to(root).as_posix()],'files':[asdict(r) for r in refs]}))
    scratch_mib = (max(a['staged_bytes'] for a in accounts)+MIB-1)//MIB+16
    bounds = CodecBounds(8*MIB,8*MIB,8*MIB,2048,65536,256*1024,64*1024,
                         8*1024*MIB,scratch_mib*MIB,64*MIB)
    quantities = tuple(q for q in _quantities(problem,reader.document['control']) if q.key.name=='A_model')
    spec = CollectionSpec.create(problem,role='exact',quantities=quantities,
        partition=_partition(problem,reader.document['control'],normalized[0]['context']['panel_size']),
        backend='python-flint-exact',backend_version=importlib.metadata.version('python-flint'),
        native_threads=1,code_refs=refs,bounds=bounds,code_root=root)
    plan = ExecutionPlan(problem_id(problem),spec.collection_id,'exact',1,1,1,
        memory_mib=memory_mib or 1,reserve_mib=128,root_mib=128,worker_base_mib=80,worker_private_mib=128,
        native_workspace_mib=128,conversion_mib=64,codec_mib=256,queue_mib=16,
        supervisor_increment_mib=256,repository_mib=8192,temporary_mib=scratch_mib,minimum_free_mib=64,
        max_tasks=32,task_bytes=128*1024,result_bytes=4*MIB,log_bytes=4*MIB,
        task_program=_ref(root,'scripts/whole_source/exact.py'),task_function='evaluate_exact',
        precision_bits=65536,backend='python-flint-exact',backend_version=spec.backend_version,
        provenance=_ref(root,code_origin.relative_to(root).as_posix()),scope=SCOPE)
    from dataclasses import replace
    from scripts.whole_source.resources import auto_plan
    plan = auto_plan(plan,parallel=False,memory_mib=memory_mib,helper_root=root)
    spec = replace(spec,native_threads=plan.threads)
    spec._validate()
    plan = replace(plan,collection_sha256=spec.collection_id)
    for account in accounts:
        _require(account['private_bytes']<=plan.worker_private_mib*MIB and
                 account['modular_workspace_bytes']<=plan.native_workspace_mib*MIB and
                 account['result_bytes']<=plan.result_bytes,'exact geometry exceeds admitted working/transport account')
    execution = {'format':'whole-source-exact-execution-v1','collection':spec.to_dict(),
                 'execution':plan.to_dict(),'operands':asdict(_ref(root,operands_path.relative_to(root).as_posix()))}
    document = problem.to_dict()
    document['problem_id'] = problem_id(problem)
    _write(directory/'problem.json',canonical_bytes(document))
    _write(directory/'execution.json',canonical_bytes(execution))
    return {'problem':directory/'problem.json','execution':directory/'execution.json','operands':operands_path}


def prepare_exact_inputs(problem,source_path,proposal_path,directory,*,origin_git_commit,
                         origin_git_dirty,code_root=ROOT):
    source_path,proposal_path = Path(source_path).resolve(),Path(proposal_path).resolve()
    raw = _bytes(source_path)
    source_ref = asdict(ArtifactRef(source_path.name,hashlib.sha256(raw).hexdigest(),len(raw)))
    core = read_proposal(proposal_path,problem,source_ref)
    proposal_raw = _bytes(proposal_path)
    origin = {'kind':'FRESH_NONPROOF','directory':str(proposal_path.parent),
              'artifact':asdict(ArtifactRef(proposal_path.name,hashlib.sha256(proposal_raw).hexdigest(),len(proposal_raw)))}
    blocks = []
    for block in core['blocks']:
        refs = {f"Z/{r['row']}/{r['column']}":r['artifact'] for r in block['integer_panels']}
        store = PanelStore(proposal_path.parent,block['context'],refs)
        def read_values(i,j,store=store):
            return [decode_integer(v,8192) for v in store.read(f'Z/{i}/{j}','integer')]
        blocks.append({'parity':block['parity'],'dimension':block['dimension'],'u':block['u'],
            'theta':Fraction(block['theta']),'panel_size':block['context']['panel_size'],'read_values':read_values})
    return prepare_exact_operands(problem,source_path,directory,blocks,origin,
        origin_git_commit=origin_git_commit,origin_git_dirty=origin_git_dirty,code_root=code_root,
        proof_scope='CONTROL_ONLY' if core['source_control'] else 'SOURCE_CONDITIONAL')


def _validate_operands(problem,descriptor,root):
    _require(set(descriptor)=={'format','problem_id','source','source_snapshot','origin','proof_scope','blocks'} and
             descriptor['format']=='whole-source-exact-operands-v1' and descriptor['problem_id']==problem_id(problem) and
             descriptor['proof_scope'] in SCOPES and type(descriptor['blocks']) is list and
             len(descriptor['blocks'])==2,'invalid exact operands contract')
    snapshot = ArtifactRef(descriptor['source_snapshot'],'0'*64,0)
    reader = _reader(problem,descriptor['source'],root/snapshot.path)
    origin = descriptor['origin']
    raw = _raw(Path(origin['directory']),ArtifactRef(**origin['artifact']),8*MIB)
    _require((origin['kind']=='REFERENCE_TRANSCRIPTION' and descriptor['proof_scope']=='REFERENCE_ARITHMETIC_ONLY') or
             (origin['kind']=='FRESH_NONPROOF' and descriptor['proof_scope']==
              ('CONTROL_ONLY' if reader.document['control'] else 'SOURCE_CONDITIONAL')),
             'exact origin/proof scope mismatch')
    original = None
    if origin['kind']=='FRESH_NONPROOF':
        original = read_proposal(Path(origin['directory'])/origin['artifact']['path'],problem,descriptor['source']['manifest'])
    for p,block in enumerate(descriptor['blocks']):
        context = block['context']
        _require(set(block)=={'context','theta','panels'} and
                 set(context)=={'problem_id','source_sha256','proposal_sha256','parity','dimension','panel_size','u',
                               'endpoint_bits','z_bits','product_bits'} and
                 context['problem_id']==problem_id(problem) and context['source_sha256']==reader.ref.sha256 and
                 context['proposal_sha256']==origin['artifact']['sha256'] and type(context['parity']) is int and
                 context['parity']==p and type(context['dimension']) is int and
                 context['dimension']==reader.document['geometry']['N']//2 and
                 type(context['u']) is int and 0<=context['u']<=4096,'changed exact physical/proposal context')
        theta = Fraction(block['theta'])
        _require(str(theta)==block['theta'],'noncanonical exact theta')
        account = integer_bounds(context,paid_parameters(reader.bits,theta,problem.eta),problem.model_error)
        _require(type(context['product_bits']) is int and context['product_bits']==account['product_bits'],
                 'changed exact integer product cap')
        n,b = context['dimension'],context['panel_size']
        expected = [f'Z/{i}/{j}' for i in range(0,n,b) for j in range(0,n,b)]
        _require(type(block['panels']) is dict and set(block['panels'])==set(expected),
                 'incomplete normalized transform coordinates')
        if original is not None:
            prior = original['blocks'][p]
            _require(prior['u']==context['u'] and Fraction(prior['theta'])==theta and
                     prior['context']['panel_size']==b,'normalized proposal parameters changed')
            refs = {f"Z/{r['row']}/{r['column']}":r['artifact'] for r in prior['integer_panels']}
            prior_store = PanelStore(Path(origin['directory']),prior['context'],refs)
            # This is a byte/integer transport check, not proof arithmetic.
            for name in expected:
                ref = ArtifactRef(**block['panels'][name])
                current = _json(_raw(root,ref,8*MIB))
                i,j = map(int,name.split('/')[1:])
                checker = IntegerTiles(root,context,block['panels'])
                _require(canonical_bytes(current['header'])==canonical_bytes(checker._header('Z',i,j)) and
                         current['values']==prior_store.read(name,'integer'),
                         'normalized integer transform differs from bound proposal')
    return reader


def _bind_exact(problem_path,execution_path,root):
    document,config = (_json(_bytes(Path(p))) for p in (problem_path,execution_path))
    problem = bind_problem(document['parameters']['profile'],root=root)
    expected = problem.to_dict()
    expected['problem_id'] = problem_id(problem)
    _require(canonical_bytes(document)==canonical_bytes(expected) and problem.profile=='retained-t081',
             'changed/unqualified exact problem')
    _require(set(config)=={'format','collection','execution','operands'} and
             config['format']=='whole-source-exact-execution-v1','invalid exact execution contract')
    spec = CollectionSpec.from_dict(problem,config['collection'],code_root=root)
    plan = ExecutionPlan.from_dict(config['execution'])
    descriptor = _json(_raw(root,ArtifactRef(**config['operands']),8*MIB))
    _validate_operands(problem,descriptor,root)
    _require(spec.role==plan.role=='exact' and plan.scope==SCOPE and
             plan.backend==spec.backend=='python-flint-exact' and plan.precision_bits==65536 and
             plan.task_program.path=='scripts/whole_source/exact.py' and plan.task_function=='evaluate_exact' and
             plan.workers==1 and ArtifactRef(**config['operands']) in spec.code_refs,
             'changed exact role/arithmetic/entry binding')
    for block in descriptor['blocks']:
        context = block['context']
        account = integer_bounds(context,paid_parameters(256,Fraction(block['theta']),problem.eta),problem.model_error)
        _require(account['private_bytes']<=plan.worker_private_mib*MIB and
                 account['modular_workspace_bytes']<=plan.native_workspace_mib*MIB and
                 account['staged_bytes']<=spec.bounds.max_temporary_bytes and
                 account['staged_bytes']<=plan.temporary_mib*MIB and account['result_bytes']<=plan.result_bytes,
                 'exact integer buffers/workspace/storage exceed admitted account')
    return problem,config,descriptor,spec,plan


def _publish_exact(lock,execution,result,context):
    n,b = context['dimension'],context['panel_size']
    expected = {f'{family}/{i}/{j}' for family in ('J','S') for i in range(0,n,b) for j in range(0,n,b)}
    _require(type(result['panels']) is dict and set(result['panels'])==expected,
             'incomplete exact first-contraction panels')
    refs = {}
    for name,value in result['panels'].items():
        ref = ArtifactRef(**value)
        _require(ref.path.startswith('attempts/'+execution.attempt_id+'/staging/'),'foreign exact scratch')
        family,i,j = name.split('/')
        raw = _raw(lock.root,ref,8*MIB)
        data = _json(raw)
        checker = IntegerTiles(lock.root,context)
        _require(canonical_bytes(data['header'])==canonical_bytes(checker._header(family,int(i),int(j))) and
                 len(data['values'])==data['header']['rows']*data['header']['columns'],'changed exact staged panel')
        for value in data['values']:
            decode_integer(value,data['header']['integer_bits'])
        refs[name] = asdict(lock._immutable('seals',raw))
        _safe(lock.root,ref.path).unlink()
    inventory = {'format':'whole-source-exact-product-inventory-v1','context':context,'panels':refs}
    return lock._immutable('seals',canonical_bytes(inventory))


def run_exact_operands(problem_path,execution_path,output_dir,*,code_root=ROOT):
    root,output = Path(code_root).resolve(),Path(output_dir).absolute()
    problem,config,descriptor,spec,plan = _bind_exact(problem_path,execution_path,root)
    with _slice_writer(output,resume=False):
        try:
            with CollectionLock.acquire(output/'collection',spec) as lock:
                with WorkloadExecution(lock,spec,plan,code_root=root) as execution:
                    reports,report_refs,products = [],[],[]
                    for p in (0,1):
                        task = {'operation':'parity','parity':p,'operands':config['operands']}
                        task['task_id'] = hashlib.sha256(canonical_bytes(task)).hexdigest()
                        name = 'parity-'+str(p)
                        execution.run_stage(name,[task])
                        result = next(execution.read_results(name))['result']
                        _require(result['scope']==SCOPE,'changed exact task scope')
                        products.append(asdict(_publish_exact(lock,execution,result,descriptor['blocks'][p]['context'])))
                        report_ref = lock._immutable('seals',canonical_bytes(result['report']))
                        report_refs.append(asdict(report_ref))
                        reports.append(result['report'])
                    task = {'operation':'assess','operands':config['operands'],'blocks':report_refs}
                    task['task_id'] = hashlib.sha256(canonical_bytes(task)).hexdigest()
                    execution.run_stage('assess',[task])
                    assessment = next(execution.read_results('assess'))['result']['assessment']
                    report = {'format':'whole-source-exact-assessment-v1','status':assessment['status'],
                        'proof_scope':descriptor['proof_scope'],'source':descriptor['source'],
                        'proposal':descriptor['origin'],'problem_id':problem_id(problem),'blocks':reports,
                        'assessment':assessment,'product_inventories':products,
                        'operands':config['operands'],'attempt_id':execution.attempt_id,
                        'owned_receipts':exact_telemetry(execution.receipts),
                        'receipt_bindings':[asdict(_ref(output,(execution.output/r['stage']/'receipt.json')
                            .relative_to(output).as_posix())) for r in execution.receipts],
                        'analytical_source_acceptance':False,'production_admission':False}
                    _write(output/'report.json',canonical_bytes(report))
                    return report
        except BaseException as exc:
            status = ('EXACT_INTERRUPTED' if isinstance(exc,KeyboardInterrupt) else
                      'EXACT_CONTRACT_FAILURE' if isinstance(exc,(ContractError,ValueError,TypeError,KeyError)) else
                      'EXACT_OPERATIONAL_FAILURE')
            _write(output/'failure.json',canonical_bytes({'status':status,
                'error_type':type(exc).__name__,'error':str(exc),'production_admission':False}))
            raise


def run_exact(problem_path,source_path,proposal_path,execution_path,output_dir,*,code_root=ROOT):
    root = Path(code_root).resolve()
    _,_,descriptor,_,_ = _bind_exact(problem_path,execution_path,root)
    _require(descriptor['origin']['kind']=='FRESH_NONPROOF' and
             Path(descriptor['source']['directory'])/descriptor['source']['manifest']['path']==Path(source_path).resolve() and
             Path(descriptor['origin']['directory'])/descriptor['origin']['artifact']['path']==Path(proposal_path).resolve(),
             'exact CLI requires the bound new proposal/source, not a legacy reference adapter')
    return run_exact_operands(problem_path,execution_path,output_dir,code_root=root)
