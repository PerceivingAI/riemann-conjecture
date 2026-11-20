"""Frozen resource identities stay deterministic; actual growth still checks live limits."""
import pytest
from scripts.whole_source import resources, supervision
from scripts.whole_source.execution import ExecutionPlan, MIB
from tests.test_whole_source_resources import detected, template


def test_frozen_policy_retains_constrained_snapshot_and_validates_without_live_queries(monkeypatch):
    def constrained(value):
        return {**value, 'available_memory_bytes': 2048*MIB, 'lifecycle_upstream_cpus': 2}
    monkeypatch.setattr(supervision, 'constrain_detection', constrained)
    plan = resources.auto_plan(template(), parallel=True, detected=detected())
    assert plan.resource_policy['detection']['available_memory_bytes'] == 2048*MIB
    assert plan.cpus == plan.workers == 2
    raw = plan.to_dict()
    def unavailable(*args, **kwargs):
        raise ValueError('required live query unavailable')
    monkeypatch.setattr(supervision, 'constrain_detection', unavailable)
    monkeypatch.setattr(supervision, 'upstream_cpu_limit', unavailable)
    assert ExecutionPlan.from_dict(raw) == plan
    with pytest.raises(ValueError, match='required live query unavailable'):
        resources.current_allowance(plan, detected())


def test_later_lower_memory_refuses_growth_without_invalidating_frozen_identity(monkeypatch):
    monkeypatch.setattr(supervision, 'constrain_detection', lambda value: value)
    plan = resources.auto_plan(template(), parallel=True, detected=detected(available_memory_bytes=2048*MIB))
    before = plan.to_dict()
    resources.validate_policy(plan)
    with pytest.raises(ValueError, match='current availability'):
        resources.current_allowance(plan, detected(available_memory_bytes=1))
    assert plan.to_dict() == before
