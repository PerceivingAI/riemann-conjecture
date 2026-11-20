"""Check full .81 frequency/head contractions on previously qualified role-specific F columns."""
from __future__ import annotations
import argparse
from dataclasses import asdict, replace
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source.contract import ArtifactRef, QuantityKey, bind_problem, canonical_bytes
from scripts.whole_source.artifacts import CollectionLock, CollectionSpec, ChunkStore, IntervalRecord, _raw, _round
from scripts.whole_source.execution import WorkloadExecution, _json, _bytes, _write, exact_telemetry
from scripts.whole_source.pipeline import (prepare_source_inputs, _bind, _tiles, _column_task, _read, _column)
from scripts.whole_source.slice import _parse_staged, _ref, _request
from scripts.whole_source.gram import _stage, _record

UPSTREAM = 'computations/2026-10-30T165153Z-selected-signed-quantities/data/run-v1/collection'
ACCEPTANCE = 'acceptances/032f46fa6a724a1c8f6c432127942352.json'
ACCEPTANCE_SHA = 'f41cfbcabbfeb7c8c163a3c945754f8c8ad2cae1322ba8a017439b0fb85dd23f'


def evaluate_head(task, staging):
    if staging.spec.role == 'producer':
        from scripts.whole_source import producer as role
    else:
        from scripts.whole_source import analytic as role
    if task['operation'] == 'qualified-column-input':
        from scripts.whole_source import execution
        from flint import ctx
        worker = execution._WORKER
        if worker is None or worker[-1] is not staging or ctx.prec != worker[0].precision_bits:
            raise RuntimeError('qualified dependency requires owned role')
        ref = ArtifactRef(**task['input'])
        raw = (ROOT/ref.path).read_bytes()
        if len(raw) != ref.size or hashlib.sha256(raw).hexdigest() != ref.sha256:
            raise ValueError('changed qualified column snapshot')
        data = _json(raw)
        if data['role'] != staging.spec.role or data['upstream_acceptance_sha256'] != ACCEPTANCE_SHA:
            raise ValueError('foreign qualified dependency role')
        chunks = []
        for row in data['columns']:
            n = row['n']
            records = []
            for m, lower, upper in row['entries']:
                records.append(IntervalRecord(m, n, (0,), Fraction(int(lower, 16), 1 << 512),
                                               Fraction(int(upper, 16), 1 << 512)))
            chunks.append(_stage(staging, _column_task(staging.spec, 'F_column', n), records))
        return {'chunks':chunks, 'scope':'SELECTION_ONLY'}
    if task['operation'] == 'selected-head':
        from flint import ctx
        from scripts.whole_source import execution
        if execution._WORKER[-1] is not staging or ctx.prec != execution._WORKER[0].precision_bits:
            raise RuntimeError('selected head requires owned role')
        output = []
        bits = 256 if staging.spec.role == 'producer' else 512
        for pair in task['pairs']:
            m, n = pair['m'], pair['n']
            left = _column(staging, 'head_column', m, pair['C'])
            image = _column(staging, 'head_image', n, pair['Y'])
            record = _record(m, n, role.head_pair(staging.spec.problem, left, image))
            lo, hi = _round(record.lower, record.upper, bits)
            output.append({'m':m,'n':n,'lower':hex(lo),'upper':hex(hi),'bits':bits})
        return {'chunks':[], 'selected':output, 'scope':'SELECTION_ONLY'}
    return role.evaluate_source(task, staging)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    original = ROOT/UPSTREAM
    raw = (original/ACCEPTANCE).read_bytes()
    if hashlib.sha256(raw).hexdigest() != ACCEPTANCE_SHA:
        raise ValueError('changed original independently accepted column evidence')
    acceptance = json.loads(raw)
    problem = bind_problem('retained-t081')
    revision = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    inputs = prepare_source_inputs(problem, output/'inputs', origin_git_commit=revision,
                                  origin_git_dirty=True, control=False, tile_modes=32)
    _, _, bound = _bind(inputs['problem'], inputs['execution'], ROOT)
    roles, summaries = {}, {}
    for role_name in ('producer','analytic'):
        spec, plan = bound[role_name]
        columns = []
        for row in acceptance['roles'][role_name]['column_chunks']:
            ref = ArtifactRef(**row['ref'])
            raw = _raw(original/role_name, ref, 8*1024**2)
            lines = gzip.decompress(raw).splitlines()
            header = json.loads(lines[0])
            if header['grid_bits'] != 512 or header['task']['quantity']['name'] != 'F_column':
                raise ValueError('incorrect upstream F representation')
            entries = []
            for line in lines[1:]:
                m,n,contribution,lo,hi = json.loads(line)
                if n != row['n'] or contribution != [0]:
                    raise ValueError('incorrect upstream F physical mapping')
                entries.append([m,lo,hi])
            if [r[0] for r in entries] != list(range(row['n']%2,problem.M,2)):
                raise ValueError('incomplete upstream F physical domain')
            columns.append({'n':row['n'],'upstream_chunk':asdict(ref),'entries':entries})
        dependency = output/(role_name+'-qualified-columns.json')
        dependency.write_bytes(canonical_bytes({'format':'qualified-physical-column-dependency-v1',
            'role':role_name,'upstream_acceptance_sha256':ACCEPTANCE_SHA,'columns':columns,
            'scope':'QUALIFIED_F_INPUT_ONLY_NOT_NEW_HEAD_RESULTS'}))
        refs = tuple(sorted((*spec.code_refs, _ref(ROOT, Path(__file__).relative_to(ROOT).as_posix()),
                            _ref(ROOT, dependency.relative_to(ROOT).as_posix())), key=lambda r:r.path))
        spec = CollectionSpec.create(problem, role=role_name, quantities=spec.quantities,
            partition=spec.partition, backend=spec.backend, backend_version=spec.backend_version,
            native_threads=1, code_refs=refs, bounds=spec.bounds)
        origin = output/(role_name+'-selection-origin.json')
        origin.write_bytes(canonical_bytes({'format':'whole-source-code-origin-v1',
            'origin_git_commit':revision,'origin_git_dirty':True,'files':[asdict(r) for r in refs]}))
        plan = replace(plan, collection_sha256=spec.collection_id,
            task_program=_ref(ROOT, Path(__file__).relative_to(ROOT).as_posix()),task_function='evaluate_head',
            scope='SELECTION_ONLY',
            provenance=_ref(ROOT, origin.relative_to(ROOT).as_posix()))
        roles[role_name] = spec
        with CollectionLock.acquire(output/role_name, spec) as lock:
            with WorkloadExecution(lock, spec, plan) as execution:
                store = ChunkStore(lock, spec, attempt_id=execution.attempt_id)
                cached, selected, statistics = {}, [], []
                def stage(name, tasks):
                    execution.run_stage(name, tasks)
                    for response in execution.read_results(name):
                        data = response['result']
                        for wire in data['chunks']:
                            task, staged = _parse_staged(wire)
                            cached[canonical_bytes(task.to_dict())] = store.publish_chunk(task, staged)
                        selected.extend(data.get('selected',[]))
                        if 'statistics' in data:
                            statistics.append(data['statistics'])
                def find(name,n):
                    return asdict(cached[canonical_bytes(_column_task(spec,name,n).to_dict())])
                stage('qualified-input', [_request(operation='qualified-column-input', input=asdict(
                    _ref(ROOT, dependency.relative_to(ROOT).as_posix())))])
                for parity in (0,1):
                    stage('kernel-'+str(parity), [_request(operation='kernel',parity=parity,control=False)])
                    kernel = [asdict(cached[canonical_bytes(t.to_dict())]) for t in
                              _tiles(spec, QuantityKey('kernel_complete',parity))]
                    modes = [parity,problem.N-2+parity]
                    stage('head-'+str(parity), [_request(operation='head',parity=parity,control=False,
                         n=n,F=find('F_column',n),kernel=kernel) for n in modes])
                    a,b = modes
                    stage('selected-'+str(parity), [_request(operation='selected-head',pairs=[
                        {'m':m,'n':n,'C':find('head_column',m),'Y':find('head_image',n)}
                        for m,n in ((a,a),(a,b),(b,b))])])
                summaries[role_name] = {'selected':selected,'owned_receipts':exact_telemetry(execution.receipts),
                    'statistics':statistics,'collection':spec.to_dict(),'attempt_id':execution.attempt_id,
                    'cache':{key.hex():asdict(ref) for key,ref in cached.items()}}
                (output/(role_name+'-result.json')).write_bytes(canonical_bytes(summaries[role_name]))
    kernel_checked = 0
    for parity in (0,1):
        for st,at in zip(_tiles(roles['producer'],QuantityKey('kernel_complete',parity)),
                         _tiles(roles['analytic'],QuantityKey('kernel_complete',parity)),strict=True):
            records = []
            for role,task in (('producer',st),('analytic',at)):
                ref = ArtifactRef(**summaries[role]['cache'][canonical_bytes(task.to_dict()).hex()])
                records.append(_read(roles[role],output/role,task,ref))
            for source,actual in zip(*records,strict=True):
                lo,hi = _round(source.lower,source.upper,256)
                if not Fraction(lo,1<<256) <= actual.lower <= actual.upper <= Fraction(hi,1<<256):
                    raise ValueError('independent complete K containment failure')
                kernel_checked += 1
    for source,actual in zip(summaries['producer']['selected'],summaries['analytic']['selected'],strict=True):
        if (source['m'],source['n']) != (actual['m'],actual['n']):
            raise ValueError('changed selected head mapping')
        lo,hi = (Fraction(int(source[k],16),1<<source['bits']) for k in ('lower','upper'))
        alo,ahi = (Fraction(int(actual[k],16),1<<actual['bits']) for k in ('lower','upper'))
        if not lo <= alo <= ahi <= hi:
            raise ValueError('independent full head containment failed')
    result = {'status':'VERIFIED_SELECTED_COMPLETE_FREQUENCY_HEAD','kernel_entries_checked':kernel_checked,
        'head_entries_checked':6,'full_head_dimension_per_parity':413,'frequency_anchors':len(problem.frequency_edges),
        'qualified_F_dependencies_reused':True,'fresh_F_reconstruction':False,
        'matrix_positivity':False,'full_source_run':False,'scope':'SELECTION_ONLY'}
    (output/'verification.json').write_bytes(canonical_bytes(result))
    print(json.dumps(result,sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
