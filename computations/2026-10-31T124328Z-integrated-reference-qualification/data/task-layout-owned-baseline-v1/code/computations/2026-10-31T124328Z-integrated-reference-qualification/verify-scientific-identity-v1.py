"""Executed reduced-model replay and separately declared finite proposal control."""
from dataclasses import asdict, replace
from pathlib import Path
import argparse
import hashlib
import json
import runpy
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source import pipeline, resources
from scripts.whole_source.artifacts import CollectionLock, _publication_header
from scripts.whole_source.contract import bind_problem, canonical_bytes, QuantityKey
from scripts.whole_source.execution import MIB, _write
from scripts.whole_source.proposal import prepare_proposal_inputs, run_proposal
from scripts.whole_source.exact import prepare_exact_inputs, run_exact
from scripts.whole_source.retention import _scientific_exact


def prepare(problem, directory, cpus, scratch):
    original = resources.auto_plan
    def capped(template, **kwargs):
        return original(template, **kwargs, cpus=cpus)
    with patch.object(resources, 'auto_plan', capped):
        paths = pipeline.prepare_source_inputs(problem, directory,
            origin_git_commit='0'*40, origin_git_dirty=True,
            control=True, tile_modes=2, memory_mib=4096)
    _, config, bound = pipeline._bind(paths['problem'], paths['execution'], ROOT)
    for role, (spec, plan) in bound.items():
        assert (plan.workers, plan.threads) == (cpus, 1)
        spec = replace(spec, bounds=replace(spec.bounds, max_temporary_bytes=scratch*MIB))
        plan = replace(plan, collection_sha256=spec.collection_id, temporary_mib=scratch)
        spec._validate()
        config['roles'][role] = {'collection':spec.to_dict(), 'execution':plan.to_dict()}
    paths['execution'].write_bytes(canonical_bytes(config))
    return paths


def manufactured(problem, spec, directory):
    helper = runpy.run_path(str(ROOT/'computations/2026-10-31T025401Z-blocked-nonproof-proposal/prepare-controls-v2.py'))
    matrices = {p:helper['matrices'](problem, 'positive', p)[1] for p in (0,1)}
    with CollectionLock.acquire(directory, spec) as lock:
        tiles = []
        for family, name in pipeline.FAMILIES.items():
            for parity in (0,1):
                for task in pipeline._tiles(spec, QuantityKey(name, parity)):
                    records = []
                    for row in task.rows:
                        for column in task.columns:
                            if row > column:
                                continue
                            value = matrices[parity][family][row//2][column//2]*(1 << 256)
                            lo = value.numerator//value.denominator-1
                            hi = -((-value.numerator)//value.denominator)+1
                            records.append([row,column,hex(lo),hex(hi)])
                    ref = lock._immutable('seals', canonical_bytes({
                        'header':_publication_header(spec,task,256), 'records':records}))
                    tiles.append({'family':family,'parity':parity,'task':task.to_dict(),'artifact':asdict(ref)})
        path = directory/'source-manifest.json'
        _write(path, canonical_bytes(pipeline.scientific_manifest(spec, True, tiles)))
        pipeline.write_source_execution(path, spec, {'kind':'DECLARED_CONTROL'})
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    problem = bind_problem('retained-t081')
    prepared, sources, audits, specs = [], [], [], []
    for workers, scratch in ((1,128),(2,192)):
        directory = output/('workers-'+str(workers))
        paths = prepare(problem, directory/'inputs', workers, scratch)
        _, _, bound = pipeline._bind(paths['problem'], paths['execution'], ROOT)
        spec = bound['producer'][0]
        prepared.append(paths)
        specs.append(spec)
        pipeline.run_source(paths['problem'], paths['execution'], directory/'source')
        source = directory/'source/producer/source-manifest.json'
        pipeline.run_audit(paths['problem'], source, paths['execution'], directory/'audit')
        sources.append(source)
        audits.append(directory/'audit/analytical-receipt.json')
    assert specs[0].collection_id != specs[1].collection_id
    assert specs[0].scientific_id == specs[1].scientific_id
    comparison = pipeline.compare_source_audits(sources[0], audits[0], sources[1], audits[1])
    assert comparison['entries_compared'] == 36
    controlled = [manufactured(problem, spec, output/('finite-'+str(i))) for i,spec in enumerate(specs)]
    assert controlled[0].read_bytes() == controlled[1].read_bytes()
    proposal_inputs = prepare_proposal_inputs(problem, controlled[0], output/'proposal-inputs',
        origin_git_commit='0'*40, origin_git_dirty=True, panel_size=2, memory_mib=4096)
    run_proposal(proposal_inputs['problem'], controlled[0], proposal_inputs['execution'], output/'proposal')
    proposal = output/'proposal/proposal.json'
    original_proposal = proposal.read_bytes()
    exact = []
    for i,source in enumerate(controlled):
        inputs = prepare_exact_inputs(problem, source, proposal, output/('exact-inputs-'+str(i)),
            origin_git_commit='0'*40, origin_git_dirty=True)
        report = run_exact(inputs['problem'], source, proposal, inputs['execution'], output/('exact-'+str(i)))
        assert report['status'] == 'PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL'
        assert report['proof_scope'] == 'CONTROL_ONLY'
        exact.append(report)
    assert proposal.read_bytes() == original_proposal
    assert _scientific_exact(exact[0]) == _scientific_exact(exact[1])
    report = {'status':'PASS_REDUCED_SCIENTIFIC_IDENTITY_AND_ORIGINAL_PROPOSAL_REUSE',
        'source_audit':comparison,'workers':[1,2],'native_threads':[1,1],
        'scratch_mib':[128,192],'operational_ids':[s.collection_id for s in specs],
        'scientific_id':specs[0].scientific_id,
        'proposal_sha256':hashlib.sha256(original_proposal).hexdigest(),
        'finite_exact_statuses':[r['status'] for r in exact],
        'finite_control':'MANUFACTURED_POSITIVE_MATRIX_NOT_EVALUATED_WEIL_SOURCE',
        'full_qualification_executed':False,'production_admission':False,'RH_proved':False}
    _write(output/'verification.json', canonical_bytes(report))
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
