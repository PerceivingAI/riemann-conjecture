from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import sys
import uuid

from scripts.whole_source.contract import ROOT, bind_problem
from scripts.whole_source.pipeline import prepare_source_inputs
from scripts.whole_source.proposal import prepare_proposal_inputs
from scripts.whole_source.exact import prepare_exact_inputs
from scripts.whole_source.retention import prepare_inputs, _bind


def cli(folder, command, arguments, accepted=(0,)):
    result = subprocess.run([sys.executable, '-B', '-m', 'scripts.weil_whole_source_split',
        command, *arguments], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding='utf-8')
    (folder/(command+'-stdout.txt')).write_text(result.stdout, encoding='utf-8')
    if result.returncode not in accepted:
        print(result.stdout)
        raise RuntimeError(command+' exited '+str(result.returncode))
    print(command+': exit='+str(result.returncode), flush=True)


def finite_positive_source(folder, problem, config):
    from fractions import Fraction
    from scripts.whole_source.artifacts import (CollectionSpec, CollectionLock, ChunkStore,
        IntervalRecord, _coordinates, publish_publication, stage_publication)
    from scripts.whole_source.contract import QuantityKey, canonical_bytes, problem_id
    from scripts.whole_source.pipeline import FAMILIES, _tiles
    from dataclasses import asdict
    spec = CollectionSpec.from_dict(problem,config['roles']['producer']['collection'])
    target = folder/'manufactured-positive-source'
    with CollectionLock.acquire(target,spec) as lock:
        (target/'attempts/fixture').mkdir()
        lock.register_attempt('fixture')
        store = ChunkStore(lock,spec,attempt_id='fixture')
        tiles = []
        for family,name in FAMILIES.items():
            for parity in (0,1):
                for domain in _tiles(spec,QuantityKey(name,parity)):
                    records = []
                    for m,n in _coordinates(domain,True):
                        product = (m+1)*(n+1)
                        if family=='A_model':
                            value = Fraction(8*(m==n))+Fraction(product,64)
                        else:
                            shift = 20 if family=='weighted_head' else 24
                            value = Fraction(product+(4 if m==n else 0),1 << shift)
                        records.append(IntervalRecord(m,n,(0,),value,value))
                    staged = stage_publication(store.staging_context(),domain,records)
                    ref = publish_publication(store,domain,staged)
                    tiles.append({'family':family,'parity':parity,'task':domain.to_dict(),'artifact':asdict(ref)})
        document = {'format':'whole-source-scientific-manifest-v1','problem_id':problem_id(problem),
            'collection':spec.to_dict(),'control':True,'geometry':{'N':6,'M':12,'K':2},
            'role':'producer','publication_bits':256,'scope':'CONTROL_ONLY_REDUCED_MODEL',
            'tiles':tiles,'full_mathematical_source':False,'analytical_acceptance':False,
            'matrix_positivity':False,'production_admission':False,
            'residual_model_payment':'Lambda D once in later exact full-space proof'}
        (target/'source-manifest.json').write_bytes(canonical_bytes(document))
    return target/'source-manifest.json'


def main():
    folder = ROOT/'.pytest_cache'/('resource-capacity-'+uuid.uuid4().hex)
    folder.mkdir()
    origin = dict(origin_git_commit='b19905565ace1f4a1b9ea1387ce123377c65a0e0', origin_git_dirty=True)
    problem = bind_problem('retained-t081')
    integrated = prepare_inputs(problem, folder/'integrated-inputs', **origin)
    _, policy = _bind(integrated['problem'], integrated['execution'], ROOT)
    assert policy['resource_policy'] == 'detected-capacity-v1'
    inputs = prepare_source_inputs(problem, folder/'source-inputs', control=True, tile_modes=2, **origin)
    config = json.loads(inputs['execution'].read_bytes())
    plans = {role: row['execution'] for role,row in config['roles'].items()}
    for role, plan in plans.items():
        assert plan['cpus'] == plan['resource_policy']['selected']['cpus']
        assert plan['workers']*plan['threads'] <= plan['cpus']
        assert plan['memory_mib'] > 1536
    source = folder/'source/producer/source-manifest.json'
    cli(folder, 'source', ['--problem',str(inputs['problem']),'--execution',str(inputs['execution']),
        '--output-dir',str(folder/'source')])
    cli(folder, 'audit', ['--problem',str(inputs['problem']),'--execution',str(inputs['execution']),
        '--source',str(source),'--output-dir',str(folder/'audit')])
    source = finite_positive_source(folder,problem,config)
    proposal = prepare_proposal_inputs(problem, source, folder/'proposal-inputs', panel_size=2, **origin)
    proposal_path = folder/'proposal/proposal.json'
    cli(folder, 'propose', ['--problem',str(proposal['problem']),'--execution',str(proposal['execution']),
        '--source',str(source),'--output-dir',str(folder/'proposal')])
    exact = prepare_exact_inputs(problem, source, proposal_path, folder/'exact-inputs', **origin)
    cli(folder, 'exact', ['--problem',str(exact['problem']),'--execution',str(exact['execution']),
        '--source',str(source),'--proposal',str(proposal_path),'--output-dir',str(folder/'exact')])
    observations = [json.loads(p.read_bytes()) for p in folder.rglob('*-pool-observation.json')]
    receipts = [json.loads(p.read_bytes()) for p in folder.rglob('receipt.json')]
    assert observations and receipts
    assert all(row['cleanup_verified'] for row in observations)
    assert all(row['worker_cleanup_verified'] and row['exit_code']==0 for row in receipts)
    assert max(row['concurrent_workers_observed'] for row in observations) == plans['producer']['workers']
    proposal_config = json.loads(proposal['execution'].read_bytes())
    for phase in proposal_config['phases'].values():
        plan = phase['execution']
        assert plan['workers']==1 and plan['threads']==plan['cpus']
    exact_plan = json.loads(exact['execution'].read_bytes())['execution']
    assert exact_plan['workers']==1 and exact_plan['threads']==exact_plan['cpus']
    exact_report = json.loads((folder/'exact/report.json').read_bytes())
    assert exact_report['proof_scope']=='CONTROL_ONLY' and exact_report['assessment']['positive_paid_lower']
    report = {'created_utc':datetime.now(timezone.utc).isoformat(), 'scope':'REDUCED_MODEL_RESOURCE_SMOKE_ONLY',
        'directory':str(folder),'full_reference_restarted':False,'source_workers':plans['producer']['workers'],
        'cpu_budget':plans['producer']['cpus'],'source_threads_per_worker':plans['producer']['threads'],
        'source_memory_cap_mib':plans['producer']['memory_mib'],
        'source_required_bytes':plans['producer']['resource_policy']['owned_required_bytes'],
        'native_singleton_threads':exact_plan['threads'],'owned_stages':len(receipts),
        'maximum_concurrent_workers_observed':max(row['concurrent_workers_observed'] for row in observations),
        'peak_owned_bytes':max(row['peak_committed_bytes'] for row in observations),
        'all_owned_cleanup_verified':True,'production_admission':False}
    (folder/'smoke-result.json').write_text(json.dumps(report,sort_keys=True,indent=2),encoding='utf-8')
    print(json.dumps(report,sort_keys=True))


if __name__=='__main__':
    main()
