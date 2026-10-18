"""Fail-closed controls for research-only independent analytic entry checking."""
from __future__ import annotations

import gzip
import json
from fractions import Fraction
from pathlib import Path

import pytest
from flint import arb, ctx

from scripts.verify_combined_schur_analytic_entries import (
    bound_tail, cell_v_moments, current_packet, endpoints, is_inside,
    run,
)


def test_containment_rejects_wrong_or_reversed_interval():
    with ctx.workprec(512):
        exact=arb(1)
        assert is_inside(exact,[1<<352,1<<352],352)
        assert not is_inside(exact,[0,0],352)
        assert not is_inside(exact,[1<<352,(1<<352)-1],352)
        assert not is_inside(arb(1)/3,[0,0],352)


def test_logarithmic_cell_rejects_uncertain_domain():
    with ctx.workprec(512):
        with pytest.raises(ValueError):
            cell_v_moments(arb(-1),arb(1,1),6)
        with pytest.raises(ValueError):
            cell_v_moments(arb(0),arb(0),6)


def test_residual_radius_rejects_bad_support():
    with ctx.workprec(512):
        with pytest.raises(ValueError):
            bound_tail(arb(2),[],32)


def test_packet_metadata_fails_closed(tmp_path:Path):
    source=Path("computations/2026-10-17T150153Z-combined-schur-bounded-test/data/matrix-N192.json.gz")
    p=json.loads(gzip.decompress(source.read_bytes()))
    p["active_terms"]=[2]
    path=tmp_path/"wrong.json.gz"
    path.write_bytes(gzip.compress(json.dumps(p).encode(),mtime=0))
    with pytest.raises(ValueError,match="support/terms"):
        current_packet(path)


def test_separate_complete_small_gram_agrees_with_generator():
    result=run(8,768,None,False)
    assert result["source_independent_analytic_reconstruction"]
    assert result["dimension"]==8
