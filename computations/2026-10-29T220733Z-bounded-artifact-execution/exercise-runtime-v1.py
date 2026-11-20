"""Executed exact-polynomial storage/owned-runtime control, not Weil evaluation."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from dataclasses import asdict
from fractions import Fraction
import hashlib,importlib.metadata,json,shutil
from scripts.whole_source.contract import ArtifactRef,ContractError,ModeRange,QuantityKey,bind_problem,canonical_bytes,problem_id
from scripts.whole_source.artifacts import Axis,CodecBounds,CollectionLock,CollectionSpec,QuantitySpec,ChunkStore,ContributionTask,StagedChunk
from scripts.whole_source.execution import BUNDLE,MIB,ExecutionPlan,WorkloadExecution,_HELPERS,_RUNTIME
PROGRAM=(Path(__file__).parent/'polynomial-worker-v1.py').read_text(encoding='utf-8')
def ref(root, path):
    raw = (root / path).read_bytes()
    return ArtifactRef(path, hashlib.sha256(raw).hexdigest(), len(raw))

def case(tmp_path, problem, *, workers=1, backend="python-flint"):
    captured = tmp_path / "captured"
    captured.mkdir()
    # Actual complete metadata/code input closure, no Git checkout or fresh oracles.
    paths = set(_RUNTIME) | {BUNDLE + "/" + name for name in _HELPERS}
    paths.update(item.path for item in problem.evidence)
    for path in sorted(paths):
        destination = captured / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, destination)
    program = "controls/polynomial.py"
    (captured / "controls").mkdir()
    (captured / program).write_text(PROGRAM, encoding="utf-8", newline="\n")
    code = tuple(sorted((ref(captured, path) for path in (*_RUNTIME, program)), key=lambda r: r.path))
    origin = {"format": "whole-source-code-origin-v1", "origin_git_commit": "a7d43f501cd7cf6ea74360c4092ecaa11392dbef",
              "origin_git_dirty": True, "files": [asdict(item) for item in code]}
    (captured / "origin.json").write_bytes(canonical_bytes(origin))
    bounds = CodecBounds(8*MIB, 256*1024, MIB, 64, 4096, 256*1024, 64*1024, 256*MIB, 32*MIB, 64*MIB)
    quantity = QuantitySpec(QuantityKey("F_H", 0), ModeRange(problem.N, problem.N+4),
        ModeRange(0, 4), False, (Axis("node", 0, 3),))
    version = importlib.metadata.version("python-flint") if backend == "python-flint" else "stdlib-v1"
    spec = CollectionSpec.create(problem, role="producer", quantities=(quantity,),
        partition=(("columns", 2), ("node", 1), ("rows", 2)), backend=backend, backend_version=version,
        native_threads=1, code_refs=code, bounds=bounds, code_root=captured)
    plan = ExecutionPlan(problem_id(problem), spec.collection_id, "producer", max(1, workers), workers, 1,
        memory_mib=768, reserve_mib=64, root_mib=128, worker_base_mib=80, worker_private_mib=64,
        native_workspace_mib=32, conversion_mib=16, codec_mib=64, queue_mib=8,
        supervisor_increment_mib=32, repository_mib=128, temporary_mib=16, minimum_free_mib=16,
        max_tasks=16, task_bytes=8192, result_bytes=8192, log_bytes=MIB,
        task_program=ref(captured, program), task_function="evaluate", precision_bits=problem.arithmetic.source_bits,
        backend=backend, backend_version=version, provenance=ref(captured, "origin.json"))
    return captured, spec, plan

def request(index,**values):
    return {"task_id":hashlib.sha256(canonical_bytes({"index":index,**values})).hexdigest(),**values}

def publish_images(execution,store,problem,contributions):
    name='images_'+''.join(map(str,contributions))
    execution.run_stage(name,[request(c,mode='stage',contribution=c,row=problem.N) for c in contributions])
    refs={}
    for row in execution.read_results(name):
        result=row['result'];wire=result['task']
        task=ContributionTask(QuantityKey(**wire['quantity']),ModeRange(**wire['rows']),ModeRange(**wire['columns']),tuple(Axis(**a) for a in wire['axes']))
        staged=StagedChunk(Path(result['path']),task,ArtifactRef(**result['ref']),result['generation'],result['attempt_id'])
        refs[task.axes[0].start]=store.publish_chunk(task,staged)
    return refs

def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--profile',choices=('retained-t081','selected-t1'),required=True)
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=False)
    problem=bind_problem(args.profile)
    captured,spec,plan=case(args.output_dir,problem)
    assert not (captured/'.git').exists()
    (args.output_dir/'execution.json').write_bytes(canonical_bytes(plan.to_dict()))
    binding=problem.to_dict();binding['problem_id']=problem_id(problem)
    (args.output_dir/'problem.json').write_bytes(canonical_bytes(binding))
    full=ContributionTask(QuantityKey('F_H',0),ModeRange(problem.N,problem.N+4),ModeRange(0,4),(Axis('node',0,3),))
    stage_receipts=[]
    with CollectionLock.acquire(args.output_dir/'uninterrupted',spec) as lock:
        with WorkloadExecution(lock,spec,plan,code_root=captured) as execution:
            store=ChunkStore(lock,spec,attempt_id=execution.attempt_id)
            refs=publish_images(execution,store,problem,[2,0,1])
            final=execution.reduce_prefix(store,full,None,[refs[c] for c in (2,0,1)])
            native=execution.run_stage('native',[request(99,mode='native',x=-3)])
            native_result=next(execution.read_results('native'))['result']
            assert native_result['native_product_verified'] and native_result['precision']==problem.arithmetic.source_bits
            seal=store.seal_quantity(full.quantity)
            baseline=json.loads((lock.root/final.path).read_bytes())['records']
            stage_receipts.extend(execution.receipts)
            baseline_seal=seal.sha256
    first_ref=None
    with CollectionLock.acquire(args.output_dir/'resumed',spec) as lock:
        with WorkloadExecution(lock,spec,plan,code_root=captured) as execution:
            store=ChunkStore(lock,spec,attempt_id=execution.attempt_id)
            refs=publish_images(execution,store,problem,[0])
            first_ref=execution.reduce_prefix(store,full,None,[refs[0]])
            first_attempt=execution.attempt_id
            stage_receipts.extend(execution.receipts)
    with CollectionLock.acquire(args.output_dir/'resumed',spec,resume=True) as lock:
        with WorkloadExecution(lock,spec,plan,code_root=captured) as execution:
            assert execution.attempt_id!=first_attempt
            store=ChunkStore(lock,spec,attempt_id=execution.attempt_id)
            refs=publish_images(execution,store,problem,[2,1])
            final=execution.reduce_prefix(store,full,first_ref,[refs[2],refs[1]])
            actual=json.loads((lock.root/final.path).read_bytes())['records']
            assert actual==baseline
            for row,column,lower,upper in actual:
                exact=2*(row+1)*(column+2)*(1<<spec.grid_bits)
                assert int(lower,16)==exact-6 and int(upper,16)==exact+6
            seal=store.seal_quantity(full.quantity)
            assert seal.sha256==baseline_seal
            try:store.seal_source()
            except ContractError:full_source_rejected=True
            else:raise AssertionError('selected slice claimed full source')
            stage_receipts.extend(execution.receipts)
    report={'format':'bounded-runtime-exercise-v1','scope':'CONTROL_ONLY_NONZERO_POLYNOMIAL_AND_NATIVE_2X2',
        'problem_id':problem_id(problem),'collection_id':spec.collection_id,'profile':args.profile,
        'all_owned_cleanup_verified':all(r['worker_cleanup_verified'] for r in stage_receipts),
        'owned_stages':len(stage_receipts),'owned_peaks_bytes':[r['peak_budgeted_memory_bytes'] for r in stage_receipts],
        'job_hard_cap_bytes':plan.memory_mib*MIB,'owned_required_bytes':plan.owned_required_bytes,
        'resume_endpoints_equal':actual==baseline,'scientific_slice_seal_equal':seal.sha256==baseline_seal,
        'slice_seal_sha256':seal.sha256,'full_source_refused':full_source_rejected,
        'native_control':native_result,'full_mathematical_source':False,'target_positivity_proved':False}
    (args.output_dir/'exercise.json').write_bytes(canonical_bytes(report))
    print(json.dumps(report,sort_keys=True))
    return 0

if __name__=='__main__':raise SystemExit(main())
