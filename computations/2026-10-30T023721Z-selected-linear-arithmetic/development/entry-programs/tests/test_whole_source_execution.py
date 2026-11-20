"""Consumer-visible ownership/admission controls using actual captured processes."""
from dataclasses import asdict, replace
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time

import pytest

from scripts.whole_source.contract import ArtifactRef, ContractError, ModeRange, QuantityKey, ROOT, bind_problem, canonical_bytes, problem_id
from scripts.whole_source.artifacts import Axis, CodecBounds, CollectionLock, CollectionSpec, QuantitySpec
from scripts.whole_source.execution import (
    BUNDLE, MIB, ExecutionPlan, WorkloadExecution, _HELPERS, _RUNTIME, admit_task, detect_budget,
)

PROGRAM = '''"""CONTROL_ONLY exact polynomial and native lifecycle workloads."""
from pathlib import Path
from fractions import Fraction
import os,subprocess,sys,time
from flint import ctx
ctx.prec=53
ctx.threads=1

def evaluate(task, staging):
    mode=task.get("mode","polynomial")
    if mode=="memory_error": raise MemoryError("owned deliberate MemoryError")
    if mode=="native_exit": os._exit(91)
    if mode=="native_denied":
        from flint import arb_mat
        value=arb_mat(40000,40000)
        raise RuntimeError("oversized native allocation unexpectedly succeeded")
    if mode=="flood":
        print("x"*200000,flush=True)
        time.sleep(60)
    if mode=="descendant":
        child=subprocess.Popen([sys.executable,"-B","-c","import time;time.sleep(60)"])
        Path(task["ready"]).write_text(str(child.pid))
    native=True
    if mode in ("native","native_wait"):
        from flint import arb_mat
        a=arb_mat([[1,2],[3,4]])
        b=a*a
        native=all(b[i,j]==v for i,j,v in ((0,0,7),(0,1,10),(1,0,15),(1,1,22)))
        retained=bytearray(8*1024*1024)
    if mode in ("wait","native_wait"):
        Path(task["ready"]).write_text(str(os.getpid()))
        while not Path(task["release"]).exists():time.sleep(.02)
    if mode=="stage":
        from scripts.whole_source.artifacts import Axis,ContributionTask,IntervalRecord
        from scripts.whole_source.contract import ModeRange,QuantityKey
        c=task["contribution"]
        domain=ContributionTask(QuantityKey("F_H",0),ModeRange(task["row"],task["row"]+4),
            ModeRange(0,4),(Axis("node",c,c+1),))
        records=[IntervalRecord(r,j,(c,),Fraction((-1)**c*(r+1)*(j+2)*(c+1)),
            Fraction((-1)**c*(r+1)*(j+2)*(c+1))) for r in domain.rows for j in domain.columns]
        staged=staging.stage_chunk(domain,records)
        return {"path":str(staged.path),"task":domain.to_dict(),
            "ref":{"path":staged.ref.path,"sha256":staged.ref.sha256,"size":staged.ref.size},
            "generation":staged.generation,"attempt_id":staged.attempt_id}
    x=task.get("x",2)
    value=1-2*x+3*x*x
    return {"polynomial":hex(value),"native_product_verified":native,
        "precision":ctx.prec,"threads":ctx.threads}
'''


def ref(root, path):
    raw = (root / path).read_bytes()
    return ArtifactRef(path, hashlib.sha256(raw).hexdigest(), len(raw))


@pytest.fixture(scope="module")
def problems():
    return {name: bind_problem(name) for name in ("retained-t081", "selected-t1")}


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


def task(index=0, **values):
    return {"task_id": hashlib.sha256(canonical_bytes({"index": index, **values})).hexdigest(), **values}


def wait_for(predicate, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(.02)
    raise AssertionError("real lifecycle condition not observed")


def result_rows(output, name="control"):
    folder = output / (name + "-results")
    for line in (folder / "completed.jsonl").read_text().splitlines():
        item = json.loads(line)
        raw = (folder / item["path"]).read_bytes()
        assert len(raw) == item["size"] and hashlib.sha256(raw).hexdigest() == item["sha256"]
        yield json.loads(raw)


def test_native_task_and_t1_identity_in_captured_root_without_git(tmp_path, problems):
    captured, spec, plan = case(tmp_path, problems["selected-t1"])
    assert not (captured / ".git").exists()
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        with WorkloadExecution(lock, spec, plan, code_root=captured) as execution:
            complete = execution.run_stage("control", [task(mode="native", x=-3)])
            output = execution.output
            assert complete["task_count"] == 1 and complete["peak_inflight"] == 1
            assert execution.receipts[-1]["worker_cleanup_verified"]
        rows = list(result_rows(output))
        assert rows[0]["result"] == {"polynomial": "0x22", "native_product_verified": True,
                                     "precision": 25600, "threads": 1}
        identity = json.loads((output / ".live/run.json").read_bytes())
        assert identity["support"] == "1" and identity["dimensions"] == [5564, 11128, 132]
        context = json.loads((output / "attempt-context.json").read_bytes())
        assert context["problem_id"] == problem_id(spec.problem)
        assert context["collection_id"] == spec.collection_id
        assert context["execution_id"] == plan.execution_id
        assert not (tmp_path / "collection/source.json").exists()


def test_legacy_environment_cannot_select_resource_policy(tmp_path, problems, monkeypatch):
    captured, spec, plan = case(tmp_path, problems["retained-t081"])
    for name in ("CPUS", "WORKERS", "THREADS", "MEMORY_MIB", "RESERVE_MIB"):
        monkeypatch.setenv("T081_" + name, "not-an-integer")
    budget = detect_budget(plan, repository=tmp_path, temporary=tmp_path, helper_root=captured)
    assert budget.cpu_budget == 1 and budget.workers == 1
    assert budget.owned_hard_cap_bytes == 768*MIB
    assert budget.future_owned_bytes + budget.existing_owned_bytes == budget.owned_required_bytes
    assert budget.external_increment_bytes == 32*MIB


def test_job_cap_and_future_increment_are_separate(tmp_path, problems):
    captured, spec, plan = case(tmp_path, problems["retained-t081"])
    base = 64*MIB
    budget = detect_budget(plan, repository=tmp_path, temporary=tmp_path, helper_root=captured,
                           existing_owned_bytes=base)
    assert budget.owned_hard_cap_bytes == 768*MIB
    assert budget.future_owned_bytes == plan.owned_required_bytes-base
    assert budget.single_root_resolver["workers"] == 1
    assert budget.single_root_resolver["required_bytes"] == budget.future_owned_bytes + budget.external_increment_bytes


@pytest.mark.parametrize("change", ["memory", "threads", "volume", "pool"])
def test_bad_resource_plan_refuses_before_attempt(tmp_path, problems, change):
    captured, spec, plan = case(tmp_path, problems["retained-t081"])
    if change == "threads":
        with pytest.raises(ContractError):
            replace(plan, workers=2)
        return
    plan = replace(plan, memory_mib=1) if change == "memory" else (
        replace(plan, repository_mib=1 << 39) if change == "volume" else replace(plan, cpus=2, workers=2))
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        with pytest.raises(ContractError):
            with WorkloadExecution(lock, spec, plan, code_root=captured):
                pytest.fail("unadmitted execution entered")
        assert not (lock.root / "attempts").exists() or not any((lock.root / "attempts").iterdir())


def test_actual_resource_inspection_cli_and_low_cap_refusal(tmp_path, problems):
    from scripts.weil_whole_source_split import inspect_profile
    captured, spec, plan = case(tmp_path, problems["selected-t1"])
    inspect_profile("selected-t1", tmp_path / "binding")
    execution_path = tmp_path / "execution.json"
    # The CLI uses repository code; install a source-root-relative capture in an owned temporary test directory.
    from scripts.weil_whole_source_split import inspect_resources
    execution_path.write_bytes(canonical_bytes(plan.to_dict()))
    report = inspect_resources(tmp_path / "binding/problem.json", execution_path, tmp_path / "admitted", root=captured)
    assert report["status"] == "RESOURCE_ENVELOPE_ADMITTED" and report["execution_authorized"] is False
    with pytest.raises(ContractError):
        inspect_resources(tmp_path / "binding/problem.json", execution_path, tmp_path / "refused", root=captured,
                          overrides={"memory_mib": 1})
    assert not (tmp_path / "refused").exists()


@pytest.mark.parametrize("mode,code", [("memory_error", 75), ("native_exit", None), ("native_denied", None)])
def test_real_worker_failure_never_publishes_stage_success(tmp_path, problems, mode, code):
    captured, spec, plan = case(tmp_path, problems["retained-t081"])
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        execution = WorkloadExecution(lock, spec, plan, code_root=captured)
        with pytest.raises((RuntimeError, MemoryError)):
            with execution:
                execution.run_stage("control", [task(mode=mode)])
        receipt = json.loads((execution.output / "control/receipt.json").read_bytes())
        assert receipt["worker_cleanup_verified"] and receipt["exit_code"] != 0
        if code is not None:
            assert receipt["exit_code"] == code
        assert not (execution.output / "control-results/complete.json").exists()
        assert not (lock.root / "source.json").exists()


def test_reduced_task_resources_reject_before_callback(tmp_path, problems):
    captured, spec, plan = case(tmp_path, problems["retained-t081"])
    with pytest.raises(ContractError, match="CPU allowance reduced"):
        admit_task(task(), plan, detected={"effective_cpu_budget": 0, "available_memory_bytes": 1 << 40})
    with pytest.raises(ContractError, match="future task growth"):
        admit_task(task(), plan, detected={"effective_cpu_budget": 1, "available_memory_bytes": MIB})


@pytest.mark.skipif(sys.platform != "win32", reason="actual Windows job attachment failure")
def test_attach_failure_prevents_program_import(tmp_path, problems, monkeypatch):
    captured, spec, plan = case(tmp_path, problems["retained-t081"])
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        with WorkloadExecution(lock, spec, plan, code_root=captured) as execution:
            job = execution.backend.run.__func__.__globals__["WindowsJob"]
            def denied(self, pid):
                raise RuntimeError("deliberate owned attachment refusal")
            monkeypatch.setattr(job, "attach_worker_pid", denied)
            with pytest.raises(RuntimeError, match="attachment refusal"):
                execution.run_stage("control", [task(mode="native")])
            receipt = json.loads((execution.output / "control/receipt.json").read_bytes())
            assert receipt["worker_cleanup_verified"]
            assert not (execution.output / "control/profile.json").exists()
            assert not (execution.output / "control-results").exists()


def test_cancellation_reaps_only_owned_tree(tmp_path, problems):
    captured, spec, plan = case(tmp_path, problems["retained-t081"])
    unrelated = subprocess.Popen([getattr(sys, "_base_executable", sys.executable), "-B", "-c", "import time;time.sleep(120)"])
    ready, release = tmp_path / "ready", tmp_path / "release"
    outcomes = {}
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        execution = WorkloadExecution(lock, spec, plan, code_root=captured)
        def run():
            try:
                with execution:
                    execution.run_stage("control", [task(mode="wait", ready=str(ready), release=str(release))])
            except BaseException as exc:
                outcomes["error"] = exc
        thread = threading.Thread(target=run)
        thread.start()
        try:
            wait_for(lambda: ready.exists() or outcomes)
            assert ready.exists(), outcomes
            with pytest.raises(ContractError, match="only one owned stage"):
                execution.run_stage("overlap", [task(2, mode="native")])
            assert not (execution.output / "overlap").exists()
            execution.cancel_owned()
            thread.join(30)
            assert not thread.is_alive() and isinstance(outcomes.get("error"), KeyboardInterrupt)
            assert unrelated.poll() is None
            receipt = json.loads((execution.output / "control/receipt.json").read_bytes())
            assert receipt["worker_cleanup_verified"]
        finally:
            release.touch()
            if thread.is_alive():
                execution.cancel_owned()
            thread.join(30)
            unrelated.kill()
            unrelated.wait()


def test_descendant_holding_pipe_is_reaped_before_eof(tmp_path, problems):
    captured, spec, plan = case(tmp_path, problems["retained-t081"])
    ready = tmp_path / "descendant"
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        with WorkloadExecution(lock, spec, plan, code_root=captured) as execution:
            execution.run_stage("control", [task(mode="descendant", ready=str(ready))])
            assert ready.exists() and execution.receipts[-1]["worker_cleanup_verified"]


def test_unbounded_stdout_is_refused_without_reader_deadlock(tmp_path, problems):
    captured, spec, plan = case(tmp_path, problems["retained-t081"])
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        with WorkloadExecution(lock, spec, plan, code_root=captured) as execution:
            with pytest.raises(RuntimeError, match="line/log allowance"):
                execution.run_stage("control", [task(mode="flood")])
            assert json.loads((execution.output / "control/receipt.json").read_bytes())["worker_cleanup_verified"]
            assert not (execution.output / "control-results/complete.json").exists()


def test_real_two_worker_pool_requires_and_records_aggregate_observation(tmp_path, problems):
    captured, spec, plan = case(tmp_path, problems["retained-t081"], workers=2)
    allowed = detect_budget(replace(plan, cpus=1, workers=1), repository=tmp_path, temporary=tmp_path, helper_root=captured)
    if allowed.detected["effective_cpu_budget"] < 2:
        pytest.skip("host exposes fewer than two CPU slots")
    release = tmp_path / "release"
    ready = [tmp_path / ("ready"+str(i)) for i in range(2)]
    result = {}
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        execution = WorkloadExecution(lock, spec, plan, code_root=captured, qualify_pool=True)
        def run():
            try:
                with execution:
                    result["complete"] = execution.run_stage("control", [task(i, mode="native_wait", ready=str(path), release=str(release)) for i, path in enumerate(ready)])
            except BaseException as exc:
                result["error"] = exc
        thread = threading.Thread(target=run)
        thread.start()
        try:
            wait_for(lambda: all(p.exists() for p in ready) or result)
            assert all(p.exists() for p in ready), result
            assert len({p.read_text() for p in ready}) == 2
            live = wait_for(lambda: json.loads((execution.output / ".live/run-status.json").read_bytes())["current_operation"].get("resources"))
            assert live["active_process_count"] >= 3
        finally:
            release.touch()
            thread.join(45)
        assert not thread.is_alive() and "error" not in result, result
        observation_path = execution.output / "control-pool-observation.json"
        observation = json.loads(observation_path.read_bytes())
        assert observation["workers_observed"] == 2 and observation["cleanup_verified"]
        assert observation["peak_committed_bytes"] <= plan.owned_required_bytes
        assert result["complete"]["peak_inflight"] == 2
        # Reuse only this exact code/arithmetic/resource-context measurement.
        shutil.copyfile(observation_path, captured / "pool-observation.json")
        measured = replace(plan, pool_measurement=ref(captured, "pool-observation.json"))
        detect_budget(measured, repository=tmp_path, temporary=tmp_path, helper_root=captured)
        with pytest.raises(ContractError, match="incompatible/unqualified"):
            detect_budget(replace(measured, native_workspace_mib=33), repository=tmp_path, temporary=tmp_path, helper_root=captured)


def test_actual_owned_worker_stages_and_reduces_nonzero_quantity(tmp_path, problems):
    from scripts.whole_source.artifacts import ChunkStore, ContributionTask, StagedChunk
    captured, spec, plan = case(tmp_path, problems["retained-t081"])
    full = ContributionTask(QuantityKey("F_H", 0), ModeRange(spec.problem.N, spec.problem.N+4),
                            ModeRange(0, 4), (Axis("node", 0, 3),))
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        with WorkloadExecution(lock, spec, plan, code_root=captured) as execution:
            store = ChunkStore(lock, spec, attempt_id=execution.attempt_id)
            execution.run_stage("images", [task(c, mode="stage", contribution=c, row=spec.problem.N)
                                          for c in (2, 0, 1)])
            refs = []
            for record in execution.read_results("images"):
                item = record["result"]
                wire = item["task"]
                domain = ContributionTask(QuantityKey(**wire["quantity"]), ModeRange(**wire["rows"]),
                    ModeRange(**wire["columns"]), tuple(Axis(**a) for a in wire["axes"]))
                staged = StagedChunk(Path(item["path"]), domain, ArtifactRef(**item["ref"]),
                                     item["generation"], item["attempt_id"])
                refs.append(store.publish_chunk(domain, staged))
            prefix = execution.reduce_prefix(store, full, None, refs)
            document = json.loads((lock.root / prefix.path).read_bytes())
            for row, column, lower, upper in document["records"]:
                exact = 2*(row+1)*(column+2)*(1 << spec.grid_bits)
                assert int(lower, 16) == exact-6 and int(upper, 16) == exact+6
            assert document["covered"] == 3 and document["rounds"] == 3
            assert all(r["worker_cleanup_verified"] for r in execution.receipts)
            with pytest.raises(ContractError, match="every real family"):
                store.seal_source()


@pytest.mark.parametrize("logical", [6, 12, 128])
def test_only_exact_owned_windows_rate_rounding_is_eligible(tmp_path, problems, logical):
    from fractions import Fraction
    captured, spec, plan = case(tmp_path, problems["retained-t081"], workers=2)
    quota = Fraction((2*10000//logical)*logical, 10000)
    snapshot = {"platform": "win32", "logical_cpus": logical, "affinity_cpus": logical,
                "cpu_detection_complete": True, "effective_cpu_budget": 1,
                "quota_cpu_limit": str(quota), "available_memory_bytes": 4*1024**3}
    assert admit_task(task(), plan, detected=snapshot) > 0
    for changed in (dict(quota_cpu_limit="1"), dict(affinity_cpus=1),
                    dict(cpu_detection_complete=False)):
        with pytest.raises(ContractError, match="CPU allowance reduced"):
            admit_task(task(), plan, detected={**snapshot, **changed})


def test_scheduler_budget_alone_cannot_launch_uncontained_workers(tmp_path, problems):
    from scripts.whole_source.execution import TaskScheduler
    captured, spec, plan = case(tmp_path, problems["retained-t081"])
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        with WorkloadExecution(lock, spec, plan, code_root=captured) as execution:
            scheduler = TaskScheduler(plan, execution.budget.to_dict(), root=captured,
                result_dir=tmp_path / "uncontained", attempt_id=execution.attempt_id,
                generation=lock.generation, collection=spec.to_dict(),
                profile=spec.problem.profile, artifact_context={})
            with pytest.raises(ContractError, match="owned memory"):
                list(scheduler.run([task(mode="native")]))
            assert not (tmp_path / "uncontained").exists()
