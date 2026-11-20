"""Prepare declared finite matrix controls, not an evaluated Weil source."""
from __future__ import annotations
import argparse
from dataclasses import asdict
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.whole_source.contract import bind_problem, canonical_bytes, problem_id
from scripts.whole_source.artifacts import CollectionSpec, CollectionLock, CodecBounds, _publication_header, _round
from scripts.whole_source.pipeline import _quantities, _partition, _tiles, FAMILIES
from scripts.whole_source.execution import _RUNTIME, MIB
from scripts.whole_source.slice import _ref


def transpose(a):
    return [list(row) for row in zip(*a,strict=True)]


def multiply(a,b):
    return [[sum((x*y for x,y in zip(row,col,strict=True)),Q(0)) for col in transpose(b)] for row in a]


def matrices(problem,case,parity):
    factor = [[Q(0) for _ in range(3)] for _ in range(3)]
    for i in range(3):
        scale = Q(1,1 << (3*i+parity))
        factor[i][i] = scale*(i+2)
        for j in range(i):
            factor[i][j] = scale*Q((-1)**(i+j)*(i+j+1),8)
    rotation = [[Q(3,5),Q(-4,5),Q(0)],[Q(4,5),Q(3,5),Q(0)],[Q(0),Q(0),Q(1)]]
    values = [Q(1,64),Q(1,32),Q(3,64)] if case == 'positive' else [Q(1,8),Q(1,4),Q(3,8)]
    diagonal = [[values[i] if i==j else Q(0) for j in range(3)] for i in range(3)]
    hw = multiply(multiply(rotation,diagonal),transpose(rotation))
    paid = multiply(factor,transpose(factor))
    h = multiply(multiply(factor,hw),transpose(factor))
    a = [[paid[i][j]+(problem.model_error*Q(2,2*(2*i+parity)+1) if i==j else 0)
          for j in range(3)] for i in range(3)]
    h = [[problem.eta*x for x in row] for row in h]
    return factor,{'A_model':a,'weighted_head':h,'weighted_complete_tail':[[4*x for x in row] for row in h]}


def diagnose(source_path,output):
    source = json.loads(source_path.read_bytes())
    problem = bind_problem('retained-t081')
    diagonals = []
    for row in source['tiles']:
        if row['family'] != 'A_model':
            continue
        raw = (source_path.parent/row['artifact']['path']).read_bytes()
        if len(raw) != row['artifact']['size'] or hashlib.sha256(raw).hexdigest() != row['artifact']['sha256']:
            raise ValueError('changed reduced-source tile')
        for m,n,lo,hi in json.loads(raw)['records']:
            if m != n:
                continue
            payment = problem.model_error*Q(2,2*m+1)
            diagonals.append({'parity':row['parity'],'physical_mode':m,
                'paid_lower':str(Q(int(lo,16),1 << 256)-payment),
                'paid_upper':str(Q(int(hi,16),1 << 256)-payment)})
    negative = [row for row in diagonals if Q(row['paid_upper']) < 0]
    if not negative:
        raise ValueError('diagonal bounds alone do not diagnose the observed pivot refusal')
    value = {'status':'EXACT_NEGATIVE_DIAGONAL_IN_REDUCED_CONTROL',
             'source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),
             'negative_diagonals':negative,'scope':'REDUCED_CONTROL_ONLY_NOT_WEIL_NEGATIVITY',
             'matrix_positivity':False,'production_admission':False}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('xb') as stream:
        stream.write(canonical_bytes(value))
    print(json.dumps(value,sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--case',choices=('positive','signed'))
    parser.add_argument('--diagnose-source',type=Path)
    parser.add_argument('--diagnosis-output',type=Path)
    args = parser.parse_args()
    if args.diagnose_source:
        if not args.diagnosis_output:
            parser.error('--diagnosis-output required')
        diagnose(args.diagnose_source,args.diagnosis_output)
        return 0
    if args.output_dir is None or args.case is None:
        parser.error('--output-dir and --case required')
    output = args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=False)
    problem = bind_problem('retained-t081')
    paths = (*_RUNTIME,'scripts/whole_source/slice.py','scripts/whole_source/gram.py',
             'scripts/whole_source/pipeline.py',Path(__file__).relative_to(ROOT).as_posix())
    refs = tuple(sorted((_ref(ROOT,p) for p in paths),key=lambda ref:ref.path))
    quantities = tuple(q for q in _quantities(problem,True) if q.key.name in FAMILIES.values())
    spec = CollectionSpec.create(problem,role='producer',quantities=quantities,
        partition=_partition(problem,True,2),backend='integer-rational',backend_version='stdlib-v1',
        native_threads=1,code_refs=refs,bounds=CodecBounds(8*MIB,8*MIB,8*MIB,16384,8192,
            256*1024,64*1024,1024*MIB,128*MIB,64*MIB))
    cases = {p:matrices(problem,args.case,p) for p in (0,1)}
    with CollectionLock.acquire(output/'source',spec) as lock:
        tiles = []
        for family,name in FAMILIES.items():
            for p in (0,1):
                for task in _tiles(spec,next(q.key for q in spec.quantities if q.key.name==name and q.key.parity==p)):
                    records = []
                    for m in task.rows:
                        for n in task.columns:
                            if m>n:
                                continue
                            x = cases[p][1][family][m//2][n//2]
                            lo,hi = _round(x,x,256)
                            records.append([m,n,hex(lo),hex(hi)])
                    ref = lock._immutable('seals',canonical_bytes({
                        'header':_publication_header(spec,task,256),'records':records}))
                    tiles.append({'family':family,'parity':p,'task':task.to_dict(),'artifact':asdict(ref)})
        source = {'format':'whole-source-scientific-manifest-v1','problem_id':problem_id(problem),
            'collection':spec.to_dict(),'control':True,'geometry':{'N':6,'M':12,'K':2},
            'role':'producer','publication_bits':256,'scope':'CONTROL_ONLY_REDUCED_MODEL','tiles':tiles,
            'full_mathematical_source':False,'analytical_acceptance':False,'matrix_positivity':False,
            'production_admission':False,'residual_model_payment':'Lambda D once in later exact full-space proof'}
        raw = canonical_bytes(source)
        (lock.root/'source-manifest.json').write_bytes(raw)
    definition = {'format':'exact-known-factor-proposal-control-v1','case':args.case,
        'scope':'FINITE_MANUFACTURED_MATRIX_CONTROL_NOT_EVALUATED_WEIL_SOURCE',
        'source_sha256':hashlib.sha256(raw).hexdigest(),
        'exact_factors':{str(p):[[str(x) for x in row] for row in cases[p][0]] for p in (0,1)},
        'exact_matrices':{str(p):{k:[[str(x) for x in row] for row in matrix]
            for k,matrix in cases[p][1].items()} for p in (0,1)},
        'expected_theta':'2','matrix_positivity':False,'production_admission':False}
    (output/'control-definition.json').write_bytes(canonical_bytes(definition))
    print(json.dumps({'status':'PREPARED_EXACT_NONPROOF_MATRIX_CONTROL','case':args.case,
                      'source':str(output/'source/source-manifest.json')},sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
