"""Capacity-derived owned-job plans; no arithmetic backend is imported here.

The reserve is the larger of the declared reserve, 64 MiB and ten percent
of measured availability. Supervisor growth is outside the owned hard cap.
"""
from dataclasses import replace
from fractions import Fraction

from scripts.whole_source.contract import ROOT, canonical_bytes
from scripts.whole_source.execution import (
    MIB, ExecutionPlan, _positive, _require, exact_telemetry, neutral_helpers,
)

_FORMAT = "whole-source-automatic-resource-policy-v1"
_FIELDS = ("cpus", "workers", "threads", "memory_mib", "reserve_mib",
           "native_workspace_mib", "codec_mib", "queue_mib")
_REQUIREMENTS = ("root_mib", "worker_base_mib", "worker_private_mib", "conversion_mib",
                 "supervisor_increment_mib", "task_bytes", "result_bytes")


def _ceil_mib(value):
    return (value + MIB - 1) // MIB


def _cpu_limit(detected):
    limits = []
    names = ("affinity_cpus", "logical_cpus")
    if detected.get("cpu_detection_complete") is True:
        names += ("effective_cpu_budget",)
    for name in names:
        if detected.get(name) is not None:
            limits.append(_positive(detected[name], name))
    quota = detected.get("quota_cpu_limit")
    if quota is not None:
        value = Fraction(quota)
        _require(value > 0, "invalid detected CPU quota")
        limits.append(max(1, value.numerator // value.denominator))
    if not limits and detected.get("effective_cpu_budget") is not None:
        limits.append(_positive(detected["effective_cpu_budget"], "effective_cpu_budget"))
    _require(limits, "CPU allowance is unknown")
    return min(limits)


def _select(requirements, baseline, detected, parallel, cpus, memory_mib):
    _require(type(parallel) is bool and type(detected) is dict, "invalid automatic resource selection")
    _require(detected.get("cpu_detection_complete") is True or cpus is not None,
             "CPU discovery is incomplete; explicit cpus required")
    _require(detected.get("memory_detection_complete") is True or memory_mib is not None,
             "memory discovery is incomplete; explicit memory_mib required")
    cpu_limit = _cpu_limit(detected)
    cpu = cpu_limit if cpus is None else _positive(cpus, "cpus")
    _require(cpu <= cpu_limit, "CPU budget exceeds detected CPU allowance")
    available = detected.get("available_memory_bytes")
    if available is not None:
        _positive(available, "available memory", maximum=1 << 80)
    reserve = max(baseline["reserve_mib"], 64,
                  _ceil_mib(available // 10) if available is not None else 0)
    external = requirements["supervisor_increment_mib"]
    capacity = None if available is None else available // MIB - reserve - external
    memory = capacity if memory_mib is None else _positive(memory_mib, "memory_mib")
    _require(memory is not None and memory > 0 and (capacity is None or memory <= capacity),
             "memory cap exceeds availability after reserve and supervisor increment")
    best = None
    # CPython's Windows process pool reserves two wait handles in its 63-handle limit.
    worker_limit = min(cpu, 61) if detected.get("platform") == "win32" else cpu
    for workers in range(1, worker_limit + 1) if parallel else (1,):
        for threads in range(1, cpu // workers + 1):
            native = baseline["native_per_thread_mib"] * threads
            codec = baseline["codec_per_worker_mib"] * workers
            queue = max(baseline["queue_mib"],
                        _ceil_mib(2 * workers * requirements["result_bytes"] + MIB))
            required = requirements["root_mib"] + codec + queue + workers * (
                requirements["worker_base_mib"] + requirements["worker_private_mib"] +
                native + requirements["conversion_mib"])
            if required <= memory:
                rank = (workers, workers * threads)
                if best is None or rank > best[0]:
                    best = (rank, {"cpus": cpu, "workers": workers, "threads": threads,
                        "memory_mib": memory, "reserve_mib": reserve,
                        "native_workspace_mib": native, "codec_mib": codec, "queue_mib": queue}, required)
    _require(best is not None, "aggregate bounded task working set exceeds available RAM")
    return best[1], best[2] * MIB


def auto_plan(template: ExecutionPlan, *, parallel: bool, memory_mib: int | None = None,
              cpus: int | None = None, detected: dict | None = None, helper_root=ROOT) -> ExecutionPlan:
    """Fill effective CPU capacity with bounded tasks, subject to aggregate RAM.

    Explicit caps are caller overrides, never inherited environment defaults.
    Parallel plans first preserve the largest affordable independent worker
    count, then fill spare native threads without reducing that count. A
    singleton uses native threads; its workspace grows with those threads,
    not a matrix reconstruction for each CPU. Collection identity may be rebound.
    """
    _require(type(template) is ExecutionPlan, "automatic selection requires an execution template")
    if template.resource_policy is not None:
        validate_policy(template)
    detection = exact_telemetry(neutral_helpers(helper_root)[0].detect_resources()
                                if detected is None else detected)
    requirements = {name: getattr(template, name) for name in _REQUIREMENTS}
    if template.resource_policy is None:
        baseline = {"reserve_mib": template.reserve_mib,
            "native_per_thread_mib": (template.native_workspace_mib + template.threads - 1) // template.threads,
            "codec_per_worker_mib": (template.codec_mib + template.workers - 1) // template.workers,
            "queue_mib": template.queue_mib}
    else:
        baseline = dict(template.resource_policy["baseline"])
    selected, required = _select(requirements, baseline, detection, parallel, cpus, memory_mib)
    policy = {"format": _FORMAT, "parallel": parallel, "overrides": {"cpus": cpus, "memory_mib": memory_mib},
        "detection": detection, "baseline": baseline, "requirements": requirements,
        "selected": selected, "owned_required_bytes": required,
        "reserve_basis": "max(declared,64MiB,ceil(available/10/MiB))",
        "supervisor_increment_subtractions": 1}
    return replace(template, **selected, pool_measurement=None, resource_policy=policy)


def validate_policy(plan):
    """Recompute the closed policy, including every selected resource field."""
    policy = plan.resource_policy
    _require(type(policy) is dict and set(policy) == {
        "format", "parallel", "overrides", "detection", "baseline", "requirements", "selected",
        "owned_required_bytes", "reserve_basis", "supervisor_increment_subtractions"},
        "invalid automatic resource policy fields")
    _require(policy["format"] == _FORMAT and policy["reserve_basis"] ==
             "max(declared,64MiB,ceil(available/10/MiB))" and
             type(policy["supervisor_increment_subtractions"]) is int and
             policy["supervisor_increment_subtractions"] == 1, "invalid automatic resource policy identity")
    _require(type(policy["overrides"]) is dict and set(policy["overrides"]) == {"cpus", "memory_mib"} and
             type(policy["baseline"]) is dict and set(policy["baseline"]) == {
                 "reserve_mib", "native_per_thread_mib", "codec_per_worker_mib", "queue_mib"},
             "invalid automatic resource policy baseline")
    for name, value in policy["baseline"].items():
        _positive(value, name, 0)
    _require(policy["requirements"] == {name: getattr(plan, name) for name in _REQUIREMENTS},
             "automatic resource requirements changed")
    selected, required = _select(policy["requirements"], policy["baseline"], policy["detection"],
                                policy["parallel"], **policy["overrides"])
    _require(canonical_bytes(policy["selected"]) == canonical_bytes(selected) and
             selected == {name: getattr(plan, name) for name in _FIELDS} and
             type(policy["owned_required_bytes"]) is int and policy["owned_required_bytes"] == required and
             required == plan.owned_required_bytes and plan.pool_measurement is None,
             "automatic resource policy does not match selected plan")


def current_allowance(plan, detected, *, existing_owned_bytes=0):
    """Admit only future growth; availability already excludes the live job."""
    validate_policy(plan)
    overrides = plan.resource_policy["overrides"]
    _require(detected.get("cpu_detection_complete") is True or overrides["cpus"] is not None,
             "CPU discovery is incomplete before growth")
    _require(detected.get("memory_detection_complete") is True or overrides["memory_mib"] is not None,
             "memory discovery is incomplete before growth")
    _require(_cpu_limit(detected) >= plan.cpus, "CPU allowance reduced before growth")
    available = detected.get("available_memory_bytes")
    future = plan.owned_required_bytes - existing_owned_bytes + plan.supervisor_increment_mib * MIB
    _require(available is not None or overrides["memory_mib"] is not None, "available memory is unknown")
    _require(available is None or available >= future + plan.reserve_mib * MIB,
             "future owned growth/reserve exceeds current availability")
    return future


def admit_worker_growth(plan, detected, future):
    """Keep the host reserve outside an already-installed owned memory cap."""
    sources = detected.get("memory_sources")
    if not sources:
        available = detected.get("available_memory_bytes")
        _require(available is not None or plan.resource_policy["overrides"]["memory_mib"] is not None,
                 "available memory is unknown")
        _require(available is None or available >= future + plan.reserve_mib*MIB,
                 "future task growth/reserve exceeds current availability")
        return
    for source in sources:
        available = source["available_bytes"]
        _require(type(available) is int and available >= 0, "invalid current memory constraint")
        name = source["source"]
        own_cap = (name in ("windows.job_memory_remaining", "RLIMIT_AS remaining") and
                   source.get("limit_bytes") == plan.memory_mib*MIB)
        address_space = name in ("windows.available_virtual", "RLIMIT_AS remaining",
                                 "RLIMIT_AS limit only", "windows.job_process_memory_remaining",
                                 "windows.job_process_memory_limit_only")
        reserve = 0 if own_cap or address_space else plan.reserve_mib*MIB
        _require(available >= future + reserve,
                 "future task growth/reserve exceeds current availability: "+name)
