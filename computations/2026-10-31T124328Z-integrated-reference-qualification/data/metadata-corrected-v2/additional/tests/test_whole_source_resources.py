"""Capacity selection and qualification of real, bounded owned stages."""
from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import json
import os
from types import SimpleNamespace

import pytest

from scripts.whole_source.contract import ArtifactRef, ContractError, canonical_bytes
from scripts.whole_source.execution import (
    MIB, ExecutionPlan, WorkloadExecution, admit_task, detect_budget, neutral_helpers,
)
from scripts.whole_source.resources import auto_plan, current_allowance


def template(**changes):
    ref = ArtifactRef("controls/program.py", "1" * 64, 1)
    plan = ExecutionPlan("2" * 64, "3" * 64, "producer", 1, 1, 1,
        memory_mib=1536, reserve_mib=64, root_mib=128, worker_base_mib=80,
        worker_private_mib=64, native_workspace_mib=32, conversion_mib=16,
        codec_mib=64, queue_mib=8, supervisor_increment_mib=32,
        repository_mib=128, temporary_mib=16, minimum_free_mib=16,
        max_tasks=32, task_bytes=8192, result_bytes=8192, log_bytes=MIB,
        task_program=ref, task_function="evaluate", precision_bits=25600,
        backend="integer-rational", backend_version="stdlib-v1", provenance=ref)
    return replace(plan, **changes)


def detected(**changes):
    return {"platform": "synthetic", "logical_cpus": 64, "affinity_cpus": 6,
        "effective_cpu_budget": 6, "quota_cpu_limit": None,
        "available_memory_bytes": 32 * 1024 * MIB,
        "cpu_detection_complete": True, "memory_detection_complete": True, **changes}


def test_legacy_plan_serialization_and_identity_are_unchanged():
    plan = template()
    value = asdict(plan)
    value.pop("resource_policy")
    assert plan.to_dict() == {"format": "whole-source-owned-execution-plan-v1", **value}
    assert plan.execution_id == hashlib.sha256(canonical_bytes(value)).hexdigest()
    for key in ("pool_measurement", "provenance"):
        value.pop(key)
    assert plan.pool_context == hashlib.sha256(canonical_bytes(value)).hexdigest()




def test_all_effective_cpus_and_capacity_derived_cap_without_environment(monkeypatch):
    for name in ("CPUS", "WORKERS", "THREADS", "MEMORY_MIB", "RESERVE_MIB"):
        monkeypatch.setenv("T081_" + name, "1")
    base = template()
    parallel = auto_plan(base, parallel=True, detected=detected())
    singleton = auto_plan(base, parallel=False, detected=detected())
    assert (parallel.cpus, parallel.workers, parallel.threads) == (6, 6, 1)
    assert (singleton.cpus, singleton.workers, singleton.threads) == (6, 1, 6)
    assert parallel.memory_mib == singleton.memory_mib == 32768 - 3277 - 32
    assert parallel.memory_mib > 1536
    assert parallel.codec_mib == 6 * base.codec_mib
    assert singleton.native_workspace_mib == 6 * base.native_workspace_mib
    assert parallel.owned_required_bytes <= parallel.memory_mib * MIB
    assert parallel.resource_policy["supervisor_increment_subtractions"] == 1
    assert ExecutionPlan.from_dict(parallel.to_dict()) == parallel
    assert replace(singleton, collection_sha256="4" * 64).threads == 6
    assert parallel.precision_bits == singleton.precision_bits == base.precision_bits
    assert parallel.backend == singleton.backend == "integer-rational"


@pytest.mark.parametrize("evidence,expected", [
    ({"affinity_cpus": 3}, 3),
    ({"quota_cpu_limit": "5/2"}, 2),
    ({"logical_cpus": 4}, 4),
    ({"effective_cpu_budget": 2}, 2),
])
def test_affinity_quota_and_effective_allowance_are_upper_bounds(evidence, expected):
    plan = auto_plan(template(), parallel=True, detected=detected(**evidence))
    assert plan.cpus == plan.workers == expected and plan.threads == 1
    with pytest.raises(ContractError, match="CPU budget exceeds"):
        auto_plan(template(), parallel=True, cpus=expected + 1, detected=detected(**evidence))


@pytest.mark.parametrize("memory,workers,threads", [(800, 2, 3), (500, 1, 4), (1200, 4, 1)])
def test_aggregate_ram_preserves_independent_workers_then_fills_threads(memory, workers, threads):
    plan = auto_plan(template(), parallel=True, memory_mib=memory, detected=detected())
    assert (plan.workers, plan.threads) == (workers, threads)
    assert plan.owned_required_bytes <= memory * MIB
    assert plan.native_workspace_mib == 32 * threads
    assert plan.codec_mib == 64 * workers
    assert plan.workers * plan.threads <= plan.cpus


def test_memory_capacity_and_no_feasible_working_set_reject():
    with pytest.raises(ContractError, match="aggregate bounded task working set"):
        auto_plan(template(), parallel=True, memory_mib=300, detected=detected())
    with pytest.raises(ContractError, match="memory cap exceeds"):
        auto_plan(template(), parallel=False, memory_mib=32768, detected=detected())
    with pytest.raises(ContractError, match="workers times threads"):
        template(cpus=6, workers=4, threads=2)


def test_codec_and_queue_cover_all_resized_workers():
    plan = auto_plan(template(task_bytes=MIB, result_bytes=2 * MIB),
                     parallel=True, detected=detected())
    assert plan.workers == 6 and plan.codec_mib == 384
    assert plan.queue_mib == 25
    assert plan.queue_mib * MIB >= 2 * plan.workers * plan.result_bytes + MIB
    assert plan.codec_mib * MIB >= plan.workers * (plan.task_bytes + plan.result_bytes)


def test_derived_singleton_reuses_per_worker_costs_and_refreshes_host_reserve():
    parallel = auto_plan(template(), parallel=True, detected=detected())
    singleton = auto_plan(parallel, parallel=False, memory_mib=700,
                          detected=detected(available_memory_bytes=16*1024*MIB))
    assert singleton.workers == 1 and singleton.threads == 6
    assert singleton.codec_mib == template().codec_mib
    assert singleton.owned_required_bytes <= 700*MIB
    assert singleton.reserve_mib < parallel.reserve_mib
    assert singleton.resource_policy["baseline"] == parallel.resource_policy["baseline"]


@pytest.mark.parametrize("field,override", [
    ("cpu_detection_complete", {"cpus": 3}),
    ("memory_detection_complete", {"memory_mib": 768}),
])
def test_incomplete_discovery_requires_relevant_explicit_limit(field, override):
    evidence = detected(**{field: False})
    with pytest.raises(ContractError, match="discovery is incomplete"):
        auto_plan(template(), parallel=True, detected=evidence)
    plan = auto_plan(template(), parallel=True, detected=evidence, **override)
    assert plan.workers * plan.threads <= plan.cpus
    with pytest.raises(ContractError):
        auto_plan(template(), parallel=True, detected=evidence, cpus=7, memory_mib=32768)


def test_explicit_cpu_limit_can_replace_incomplete_discovery_fallback():
    evidence = detected(cpu_detection_complete=False, effective_cpu_budget=1)
    plan = auto_plan(template(), parallel=True, cpus=3, detected=evidence)
    assert plan.cpus == plan.workers == 3
    assert admit_task({"task_id": "8" * 64}, plan, detected=evidence) > 0
    with pytest.raises(ContractError, match="CPU budget exceeds"):
        auto_plan(template(), parallel=True, cpus=7, detected=evidence)


def test_unknown_memory_requires_explicit_cap_and_retains_known_constraints():
    evidence = detected(memory_detection_complete=False, available_memory_bytes=None)
    plan = auto_plan(template(), parallel=False, memory_mib=768, detected=evidence)
    assert plan.memory_mib == 768 and plan.threads == 6
    assert current_allowance(plan, evidence) == plan.owned_required_bytes + 32 * MIB
    limited = detected(memory_detection_complete=False, available_memory_bytes=700 * MIB)
    with pytest.raises(ContractError, match="memory cap exceeds"):
        auto_plan(template(), parallel=True, memory_mib=768, detected=limited)


def test_policy_is_closed_and_cannot_be_used_as_an_unvalidated_pool_bypass(tmp_path):
    plan = auto_plan(template(), parallel=True, detected=detected())
    with pytest.raises(ContractError, match="automatic resource policy"):
        replace(plan, workers=5)
    policy = deepcopy(plan.resource_policy)
    policy["unrecognized"] = True
    with pytest.raises(ContractError, match="policy fields"):
        replace(plan, resource_policy=policy)
    plan.resource_policy["selected"]["workers"] = 1
    with pytest.raises(ContractError, match="automatic resource policy"):
        detect_budget(plan, repository=tmp_path, temporary=tmp_path, qualify_pool=True)
    legacy = template(cpus=2, workers=2)
    with pytest.raises(ContractError, match="pool requires its actual aggregate measurement"):
        detect_budget(legacy, repository=tmp_path, temporary=tmp_path)


def test_current_admission_counts_only_future_growth_and_external_increment_once(tmp_path, monkeypatch):
    import scripts.whole_source.execution as runtime
    plan = auto_plan(template(), parallel=True, detected=detected())
    existing = 128 * MIB
    remaining = plan.owned_required_bytes - existing + (plan.supervisor_increment_mib + plan.reserve_mib) * MIB
    evidence = detected(available_memory_bytes=remaining)
    monkeypatch.setattr(runtime, "neutral_helpers", lambda root: (
        SimpleNamespace(detect_resources=lambda: evidence), None, None, {}))
    budget = detect_budget(plan, repository=tmp_path, temporary=tmp_path,
                           existing_owned_bytes=existing)
    assert budget.future_owned_bytes == plan.owned_required_bytes - existing
    assert budget.external_increment_bytes == 32 * MIB
    assert budget.owned_hard_cap_bytes == plan.memory_mib * MIB
    assert budget.single_root_resolver["required_bytes"] == plan.owned_required_bytes - existing + 32 * MIB
    evidence["available_memory_bytes"] -= 1
    with pytest.raises(ContractError, match="future owned growth"):
        detect_budget(plan, repository=tmp_path, temporary=tmp_path, existing_owned_bytes=existing)


def test_worker_admission_rechecks_current_cpu_memory_and_discovery():
    plan = auto_plan(template(), parallel=True, detected=detected())
    task = {"task_id": "9" * 64}
    assert admit_task(task, plan, detected=detected()) > 0
    with pytest.raises(ContractError, match="CPU allowance reduced"):
        admit_task(task, plan, detected=detected(effective_cpu_budget=5))
    with pytest.raises(ContractError, match="future task growth"):
        admit_task(task, plan, detected=detected(available_memory_bytes=MIB))
    with pytest.raises(ContractError, match="discovery is incomplete"):
        admit_task(task, plan, detected=detected(memory_detection_complete=False))


def test_worker_reserve_stays_outside_owned_job_cap_and_preserves_host_headroom():
    plan = auto_plan(template(), parallel=True, cpus=2, memory_mib=768, detected=detected())
    task = {"task_id": "9"*64}
    own = {"source": "windows.job_memory_remaining", "limit_bytes": 768*MIB,
           "usage_bytes": 200*MIB, "available_bytes": 568*MIB}
    host = {"source": "windows.available_physical", "available_bytes": 10*1024*MIB}
    current = detected(available_memory_bytes=568*MIB, memory_sources=[own, host])
    future = admit_task(task, plan, detected=current)
    assert future < own["available_bytes"] < plan.reserve_mib*MIB
    host["available_bytes"] = future + plan.reserve_mib*MIB - 1
    with pytest.raises(ContractError, match="windows.available_physical"):
        admit_task(task, plan, detected=current)
    host["available_bytes"] = 10*1024*MIB
    own["available_bytes"] = future - 1
    with pytest.raises(ContractError, match="windows.job_memory_remaining"):
        admit_task(task, plan, detected=current)




def test_readiness_requires_owned_concurrent_pids_and_aggregate_memory(tmp_path, monkeypatch):
    import scripts.whole_source.execution as execution_module
    monkeypatch.setattr(execution_module, "neutral_helpers", lambda root: (
        SimpleNamespace(detect_resources=lambda: detected()), None, None, {}))
    plan = auto_plan(template(), parallel=True, cpus=2, memory_mib=768, detected=detected())
    runtime = object.__new__(WorkloadExecution)
    runtime.plan = plan
    runtime.code_root = tmp_path
    runtime._job_samples = []
    runtime._pool_folder = tmp_path
    runtime._expected_workers = 2
    (tmp_path / "pool-ready.json").write_bytes(canonical_bytes({
        "execution_id": plan.execution_id, "worker_pids": [101, 102]}))
    runtime._observe_pool({"active_process_ids": [101], "peak_committed_bytes": MIB})
    assert not (tmp_path / "pool-go.json").exists()
    with pytest.raises(ContractError, match="aggregate profile"):
        runtime._observe_pool({"active_process_ids": [101, 102],
                               "peak_committed_bytes": plan.owned_required_bytes + 1})
    assert not (tmp_path / "pool-go.json").exists()
    runtime._observe_pool({"active_process_ids": [101, 102], "peak_committed_bytes": 128 * MIB,
                           "current_committed_bytes": 128 * MIB})
    assert json.loads((tmp_path / "pool-go.json").read_bytes())["owned_concurrency_verified"] is True


@pytest.mark.parametrize("task_count", [1, 2, 5])
def test_real_automatic_stage_qualifies_its_actual_pool_before_publishing_completion(tmp_path, task_count):
    pytest.importorskip("flint")
    from tests.test_whole_source_execution import case, task
    from scripts.whole_source.contract import bind_problem
    from scripts.whole_source.artifacts import CollectionLock
    evidence = neutral_helpers()[0].detect_resources()
    if evidence["effective_cpu_budget"] < 2 or not evidence["cpu_detection_complete"] or not evidence["memory_detection_complete"]:
        pytest.skip("two fully detected effective CPUs and memory required for owned pool lifecycle")
    captured, spec, base = case(tmp_path, bind_problem("retained-t081"), backend="integer-rational")
    plan = auto_plan(base, parallel=True, cpus=2, memory_mib=768, detected=evidence)
    assert plan.workers == 2 and plan.pool_measurement is None
    x = 1 << 512
    with CollectionLock.acquire(tmp_path / "collection", spec) as lock:
        with WorkloadExecution(lock, spec, plan, code_root=captured) as execution:
            complete = execution.run_stage("automatic", [task(i, x=x + i) for i in range(task_count)])
            assert complete["task_count"] == task_count
            assert complete["peak_inflight"] == min(2, task_count)
            assert len(complete["pool_worker_pids"]) == min(2, task_count)
            observation = json.loads((execution.output / "automatic-pool-observation.json").read_bytes())
            assert observation["workers_observed"] == observation["concurrent_workers_observed"] == min(2, task_count)
            assert observation["cleanup_verified"]
            assert 0 < observation["peak_committed_bytes"] <= plan.owned_required_bytes
            assert (execution.output / "automatic-results/complete.json").exists()
            assert execution.receipts[-1]["worker_cleanup_verified"]
            results = {row["task_id"]: row["result"]["polynomial"] for row in execution.read_results("automatic")}
            expected = {task(i, x=x+i)["task_id"]: hex(1 - 2*(x+i) + 3*(x+i)*(x+i)) for i in range(task_count)}
            assert results == expected


@pytest.mark.skipif(os.name != "nt", reason="Windows readers deny atomic replacement")
def test_owned_work_completes_while_live_status_snapshot_is_locked(tmp_path, capsys):
    from tests.test_whole_source_execution import case, task
    from scripts.whole_source.contract import bind_problem
    from scripts.whole_source.artifacts import CollectionLock
    evidence = neutral_helpers()[0].detect_resources()
    if not evidence["cpu_detection_complete"] or not evidence["memory_detection_complete"]:
        pytest.skip("complete resource detection required")
    captured, spec, base = case(tmp_path, bind_problem("retained-t081"), backend="integer-rational")
    plan = auto_plan(base, parallel=False, cpus=1, memory_mib=768, detected=evidence)
    x = 1 << 512
    requests = [task(i, x=x+i) for i in range(3)]
    with CollectionLock.acquire(tmp_path/"collection", spec) as lock:
        with WorkloadExecution(lock, spec, plan, code_root=captured) as execution:
            with execution.writer.path.open("rb") as reader:
                initial = json.load(reader)
                execution.run_stage("locked-status", requests)
                assert json.loads(execution.writer.path.read_bytes()) == initial
            results = {row["task_id"]:row["result"]["polynomial"]
                       for row in execution.read_results("locked-status")}
            assert results == {task(i, x=x+i)["task_id"]:hex(1-2*(x+i)+3*(x+i)*(x+i))
                               for i in range(3)}
            assert execution.receipts[-1]["exit_code"] == 0
            assert execution.receipts[-1]["worker_cleanup_verified"] is True
            status_path = execution.writer.path
        status = json.loads(status_path.read_bytes())
        assert status["workflow_state"] == "RUN_COMPLETED" and status["terminal"] is True
    assert "computation continues" in capsys.readouterr().err
