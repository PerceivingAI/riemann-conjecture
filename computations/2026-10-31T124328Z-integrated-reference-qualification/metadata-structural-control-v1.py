"""Measure exact structural publications using a separately selected code snapshot."""
from contextlib import contextmanager
from dataclasses import replace
from fractions import Fraction
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import time
import tracemalloc
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--code-root', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--counts', type=int, nargs='+', default=[8, 32, 64])
    args = parser.parse_args()
    root, output = args.code_root.resolve(), args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(root))
    from scripts.whole_source import artifacts as a
    from scripts.whole_source.contract import ArtifactRef, ModeRange, QuantityKey, bind_problem
    problem = bind_problem('retained-t081', root=root)
    refs = []
    for name in ('scripts/run_observability.py','scripts/whole_source/__init__.py',
                 'scripts/whole_source/artifacts.py','scripts/whole_source/contract.py'):
        raw = (root/name).read_bytes()
        refs.append(ArtifactRef(name, hashlib.sha256(raw).hexdigest(), len(raw)))
    results = []
    for count in args.counts:
        assert 1 <= count <= 256
        bounds = a.CodecBounds(8<<20,1<<20,2<<20,512,65536,128<<10,64<<10,256<<20,16<<20,64<<20)
        quantity = a.QuantitySpec(QuantityKey('A_model',0),ModeRange(0,2),ModeRange(0,2*count),
                                  True,(a.Axis('cell',0,1),))
        spec = a.CollectionSpec.create(problem,role='producer',quantities=(quantity,),
            partition=(('cell',1),('columns',1),('rows',1)), backend='CONTROL_ONLY-exact-polynomial',
            backend_version='1',native_threads=1,code_refs=tuple(refs),bounds=bounds,code_root=root)
        directory = output/('count-'+str(count))
        counters = {'index_reads':0,'quota_checks':0,'tree_walks':0,'members_visited':0,
                    'volume_lock_wait_seconds':0.0,'volume_lock_hold_seconds':0.0}
        active = False
        depth = 0
        raw_read,quota,members,gate = a._raw,a._check_quota,a._members,a._volume_gate
        def counted_raw(base, ref, cap):
            if active and ref.path.startswith('index/'):
                counters['index_reads'] += 1
            return raw_read(base,ref,cap)
        def counted_quota(*values,**kwargs):
            if active: counters['quota_checks'] += 1
            return quota(*values,**kwargs)
        def counted_members(base):
            nonlocal depth
            outer = depth == 0
            if active and outer: counters['tree_walks'] += 1
            depth += 1
            try:
                for item in members(base):
                    if active and outer: counters['members_visited'] += 1
                    yield item
            finally:
                depth -= 1
        @contextmanager
        def counted_gate(base):
            before = time.perf_counter()
            with gate(base):
                entered = time.perf_counter()
                if active: counters['volume_lock_wait_seconds'] += entered-before
                try:
                    yield
                finally:
                    if active: counters['volume_lock_hold_seconds'] += time.perf_counter()-entered
        science = hashlib.sha256()
        with a.CollectionLock.acquire(directory,spec) as lock:
            (directory/'attempts/structural').mkdir()
            lock.register_attempt('structural')
            store = a.ChunkStore(lock,spec,attempt_id='structural')
            accepted = []
            per_publish = []
            tracemalloc.start()
            started = time.perf_counter()
            with patch.object(a,'_raw',counted_raw),patch.object(a,'_check_quota',counted_quota),\
                 patch.object(a,'_members',counted_members),patch.object(a,'_volume_gate',counted_gate):
                for column in range(0,2*count,2):
                    task = a.ContributionTask(quantity.key,ModeRange(0,2),ModeRange(column,column+2),quantity.axes)
                    value = Fraction(column+3,8)
                    records = [a.IntervalRecord(0,column,(0,),value-Fraction(1,32),value+Fraction(3,64))]
                    staged = store.stage_chunk(task,records)
                    before = dict(counters)
                    active = True
                    try:
                        ref = store.publish_chunk(task,staged)
                    finally:
                        active = False
                    per_publish.append({key:counters[key]-before[key] for key in counters})
                    snap = store.read_chunk(ref)
                    assert snap.records[0].lower <= records[0].lower <= records[0].upper <= snap.records[0].upper
                    for row in snap.records:
                        science.update(f'{row.row}:{row.column}:{row.contribution}:{row.lower}:{row.upper}\n'.encode())
                    accepted.append((task,ref))
                for task,ref in accepted:
                    store.commit_prefix(task,None,[ref])
                seal = store.seal_quantity(quantity.key)
            current,peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            elapsed = time.perf_counter()-started
        with a.CollectionLock.acquire(directory,spec,resume=True) as reopened:
            (directory/'attempts/reopened').mkdir()
            reopened.register_attempt('reopened')
            check = a.ChunkStore(reopened,spec,attempt_id='reopened')
            assert check.seal_quantity(quantity.key) == seal
        results.append({'chunks':count,'science_sha256':science.hexdigest(),
            'publication_counters':counters,'per_publish':per_publish,'wall_seconds':elapsed,
            'python_traced_current_bytes':current,'python_traced_peak_bytes':peak,
            'memory_scope':'Whole traced Python control interval, including result references; not native memory or total process RSS.',
            'scope':'CONTROL_ONLY_STRUCTURAL_NOT_WEIL_SOURCE','quantity_reopened_unchanged':True})
    report = {'status':'PASS_CONTROL_ONLY_STRUCTURAL_METADATA','code_root':str(root),
        'artifact_program_sha256':hashlib.sha256((root/'scripts/whole_source/artifacts.py').read_bytes()).hexdigest(),
        'environment':{'python':sys.version,'python-flint':importlib.metadata.version('python-flint')},
        'results':results,'counter_scope':'Warm chunk publication only; excludes staging, prefix/seal/reopen and OS physical I/O.',
        'new_weil_source':False,'production_admission':False}
    (output/'result.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'cases':[
        {'chunks':r['chunks'],**r['publication_counters']} for r in results]},sort_keys=True))


if __name__ == '__main__':
    main()
