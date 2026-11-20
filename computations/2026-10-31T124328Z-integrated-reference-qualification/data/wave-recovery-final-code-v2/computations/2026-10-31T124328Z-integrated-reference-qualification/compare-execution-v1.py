"""Summarize completed owned work against the retained pre-change reference.

Operational counters and source interval comparisons are not proof admission.
The caller supplies an existing completed run and a fresh report filename.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def require(value, message):
    if not value:
        raise ValueError(message)


def load(path):
    return json.loads(Path(path).read_bytes())


def binding(path):
    path = Path(path).resolve(strict=True)
    digest = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
            size += len(block)
    return {'path': str(path), 'sha256': digest.hexdigest(), 'size': size}


def phase(relative):
    first = relative.parts[0]
    return {'source':'source', 'audit':'independent-audit', 'proposal':'fresh-proposal',
            'exact':'exact-sign', 'premises':'scalar-premises', 'controls':'mathematical-controls',
            'replay':'captured-scientific-replay'}.get(first, 'other-owned-work')


def footprint(directory):
    result = subprocess.run(['dirrake','info',str(directory),'relative','json'],
        check=True, stdout=subprocess.PIPE, text=True, encoding='utf-8')
    value = json.loads(result.stdout)
    require(value['schema_version'] == 1 and value['type'] == 'info', 'unknown census contract')
    return value


def source_operand_passes(stage):
    """Count source-reader passes from executed, SHA-verified task inventories.

    Head/final/reduction callbacks read each listed operand once. This is a
    logical encoded-byte account, not physical disk traffic or all runtime I/O.
    """
    result = defaultdict(lambda: {'tasks':0,'operand_read_passes':0,'encoded_operand_bytes':0})
    with Path(stage['task_file']).open('rb') as stream:
        for line in stream:
            task = json.loads(line)
            operation = task.get('operation')
            if operation == 'kernel-reduce':
                refs = [group['artifact'] for group in task['groups']]
            elif operation == 'head':
                refs = [task['F'],*task['kernel']]
            elif operation == 'final':
                refs = [column[key] for column in task['columns'] for key in ('F','C','Y')]
            else:
                continue
            values = result[operation]
            values['tasks'] += 1
            for ref in refs:
                require(type(ref) is dict and set(ref)=={'path','sha256','size'} and
                        type(ref['size']) is int and ref['size']>0, 'invalid source operand reference')
                values['operand_read_passes'] += 1
                values['encoded_operand_bytes'] += ref['size']
    return dict(result)


def resources(directory):
    from scripts.whole_source.retention import _verify_receipts
    verified = _verify_receipts(directory)
    groups = defaultdict(lambda: {'stages':0, 'stage_elapsed_seconds':0.0,
        'owned_cpu_seconds':0.0, 'cpu_counter_missing':0, 'peak_owned_committed_bytes':0,
        'peak_sampled_external_increment_bytes':0, 'attempts':set(),
        'configured_cpu_budgets':set(), 'configured_worker_budgets':set(),
        'configured_native_threads_per_worker':set(), 'max_concurrently_observed_workers':0})
    rows = []
    logical_passes = defaultdict(lambda: defaultdict(lambda: {
        'tasks':0,'operand_read_passes':0,'encoded_operand_bytes':0}))
    for record in verified:
        path = Path(record['directory'])/record['artifact']['path']
        receipt = load(path)
        attempt = path.parent.parent
        stage = load(attempt/(receipt['stage']+'-stage.json'))
        group = phase(path.relative_to(directory))
        summary = load(attempt/(receipt['stage']+'-resources.json'))
        observation = load(attempt/(receipt['stage']+'-pool-observation.json'))
        cpu = receipt['last_metrics'].get('cpu_seconds')
        values = groups[group]
        for operation, account in source_operand_passes(stage).items():
            for key,value in account.items():
                logical_passes[group][operation][key] += value
        values['stages'] += 1
        values['stage_elapsed_seconds'] += receipt['elapsed_seconds']
        if cpu is None:
            values['cpu_counter_missing'] += 1
        else:
            values['owned_cpu_seconds'] += cpu
        values['peak_owned_committed_bytes'] = max(values['peak_owned_committed_bytes'],
            receipt['peak_budgeted_memory_bytes'])
        values['peak_sampled_external_increment_bytes'] = max(
            values['peak_sampled_external_increment_bytes'], summary['sampled_external_increment_bytes'])
        values['attempts'].add(attempt)
        values['configured_cpu_budgets'].add(stage['plan']['cpus'])
        values['configured_worker_budgets'].add(stage['plan']['workers'])
        values['configured_native_threads_per_worker'].add(stage['plan']['threads'])
        values['max_concurrently_observed_workers'] = max(values['max_concurrently_observed_workers'],
            observation['concurrent_workers_observed'])
        rows.append({'phase':group, 'receipt':binding(path),
            'elapsed_seconds':receipt['elapsed_seconds'], 'aggregate_owned_cpu_seconds':cpu,
            'peak_owned_committed_bytes':receipt['peak_budgeted_memory_bytes'],
            'sampled_external_increment_bytes':summary['sampled_external_increment_bytes'],
            'cleanup_verified':receipt['worker_cleanup_verified']})
    output = {}
    for name, values in sorted(groups.items()):
        attempts = values.pop('attempts')
        owner_seconds = 0.0
        for attempt in attempts:
            status = load(attempt/'.live/run-status.json')
            require(status.get('terminal') is True or status.get('workflow_state') == 'RUN_COMPLETED',
                    'attempt has not finished')
            owner_seconds += status['elapsed_seconds']
        values['collection_owner_elapsed_seconds'] = owner_seconds
        values['collection_owners'] = len(attempts)
        for key in ('configured_cpu_budgets','configured_worker_budgets','configured_native_threads_per_worker'):
            values[key] = sorted(values[key])
        values['aggregate_cpu_per_owner_wall'] = (values['owned_cpu_seconds']/owner_seconds
            if owner_seconds and not values['cpu_counter_missing'] else None)
        output[name] = values
    source_reads = {name:dict(operations) for name,operations in logical_passes.items()}
    return {'phases':output, 'stages':rows, 'owned_receipts_verified':len(verified),
        'source_logical_operand_passes':source_reads,
        'source_read_scope':'Derived from executed task references and callback read loops; excludes metadata, proposal/exact operand passes, writes and physical OS/device traffic.',
        'all_owned_cleanup_verified':all(row['cleanup_verified'] for row in rows),
        'counter_scope':'Owned job cumulative CPU includes descendants. Owner wall includes inter-stage publication; final caller read-through and unowned CPU are not included.'}


def baseline(directory):
    rows = []
    for name in ('source','independent-audit','exact-sign'):
        path = directory/name/'receipt.json'
        value = load(path)
        profile = load(directory/name/'profile.json')
        require(value['exit_code'] == 0 and value['worker_cleanup_verified'] is True,
                'baseline stage did not succeed')
        rows.append({'phase':name,'receipt':binding(path),'profile':binding(directory/name/'profile.json'),
            'stage_elapsed_seconds':value['elapsed_seconds'],
            'aggregate_owned_cpu_seconds':value['last_metrics'].get('cpu_seconds'),
            'numerical_process_cpu_seconds':profile['cpu_seconds'],
            'peak_owned_committed_bytes':value['peak_budgeted_memory_bytes'],
            'native_threads':profile['native_threads'],
            'memory_limit_bytes':value['budget']['memory_budget_bytes']})
    qualification = load(directory/'qualification.json')
    require(qualification['status']=='PASS_CAPTURED_SOURCE_ANALYTICAL_EXACT_AND_NINE_CONTROLS',
            'unqualified baseline')
    return {'qualification':binding(directory/'qualification.json'),'stages':rows,
        'scope':{'source':'All six source matrices; no fresh proposal search.',
            'independent-audit':'All512946 entries plus six native false-source subset probes and scalar/declaration checks.',
            'exact-sign':'Both413-dimensional signs/widths/nonsingularity using the retained untrusted proposal.',
            'not_in_three_phase_total':['fresh proposal construction','new workflow scalar reconstruction',
                'all separate exact controls','second scientific replay','reviewed final acceptance']}}


def compare_sources(run, retained):
    from scripts.whole_source.contract import ArtifactRef
    from scripts.whole_source.artifacts import _raw, _task, publication_integers
    from scripts.whole_source.pipeline import _bind, SourceReader
    result = load(run/'pipeline-result.json')
    problem_path = Path(result['problem']['directory'])/result['problem']['artifact']['path']
    execution_path = Path(result['source_execution']['directory'])/result['source_execution']['artifact']['path']
    problem,config,bound = _bind(problem_path, execution_path, ROOT)
    require(config['control'] is False, 'full source comparison refuses reduced models')
    source_path = Path(result['source']['directory'])/result['source']['artifact']['path']
    source = SourceReader(source_path,bound['producer'][0],control=False)
    old_path = retained/'results/source.json'
    old = load(old_path)
    require((old['support'],old['N'],old['order'],old['physical_extent'],old['bits'],old['precision']) ==
        ('81/100',problem.N,problem.K,problem.M,source.bits,problem.arithmetic.source_bits),
        'baseline mathematical parameters differ')
    indexed = defaultdict(list)
    for row in source.document['tiles']:
        indexed[row['family'],row['parity']].append(row)
    counts = []
    for family in ('A_model','weighted_head','weighted_complete_tail'):
        for parity in (0,1):
            ref = old['matrices'][family+'-'+str(parity)]
            raw = (old_path.parent/ref['path']).read_bytes()
            require(hashlib.sha256(raw).hexdigest()==ref['sha256'] and len(raw)==ref['size'],
                    'baseline packet integrity differs')
            packet = json.loads(gzip.decompress(raw))
            require(packet['dimension']==413 and packet['bits']==source.bits and
                    packet['kind']==family and packet['parity']==parity, 'baseline packet domain differs')
            endpoints = packet['upper_triangle']
            checked = identical = disjoint = 0
            old_width = new_width = 0
            for row in indexed[family,parity]:
                task = _task(row['task'])
                payload = _raw(source.path.parent,ArtifactRef(**row['artifact']),source.spec.bounds.max_raw_bytes)
                for m,n,lo,hi in publication_integers(source.spec,payload,task,source.bits):
                    i,j = (m-parity)//2,(n-parity)//2
                    index = i*413-i*(i-1)//2+j-i
                    a,b = (int(x,16) for x in endpoints[index])
                    checked += 1
                    identical += (a,b)==(lo,hi)
                    disjoint += max(a,lo)>min(b,hi)
                    old_width = max(old_width,b-a)
                    new_width = max(new_width,hi-lo)
            require(checked==413*414//2, 'incomplete common source domain')
            counts.append({'family':family,'parity':parity,'entries':checked,'identical_endpoint_pairs':identical,
                'disjoint_enclosures':disjoint,'old_max_width_grid_units':hex(old_width),
                'new_max_width_grid_units':hex(new_width)})
    require(sum(row['entries'] for row in counts)==512946, 'incomplete source comparison')
    return {'source':binding(source_path),'baseline_source':binding(old_path),'families':counts,
        'meaning':'Diagnostic comparison of independently validated enclosures of the same mathematical quantities; overlap is not a substitute for either analytical audit.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir',type=Path,required=True)
    parser.add_argument('--baseline-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--compare-source',action='store_true')
    args = parser.parse_args()
    run,old = args.run_dir.resolve(strict=True),args.baseline_dir.resolve(strict=True)
    require(not args.output.exists(), 'report output must be fresh')
    report = {'format':'whole-source-retained-execution-comparison-v1',
        'created_utc':datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),
        'status':'OPERATIONAL_AND_DIAGNOSTIC_COMPARISON_ONLY','program':binding(Path(__file__)),
        'new':resources(run),'baseline':baseline(old),
        'disk':{'new':footprint(run),'baseline':footprint(old)},
        'limits':['No matched full-pipeline speedup: baseline reuses a proposal and stage/control/replay boundaries differ.',
            'Native stage sums exclude inter-stage owner work; owner wall excludes final caller read-through.',
            'Unowned supervisor CPU is not captured by job CPU counters.',
            'Disk census is retained logical file bytes, not transient write traffic or physical device I/O; OS I/O counters were not retained.',
            'One execution per implementation is not a statistical scaling study.'],
        'production_admission':False}
    if (run/'elapsed.json').is_file():
        report['new']['coordinator_elapsed'] = load(run/'elapsed.json')
    if args.compare_source:
        report['source_comparison'] = compare_sources(run,old)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(report,stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps({'report':str(args.output),'verified_owned_stages':report['new']['owned_receipts_verified'],
        'all_owned_cleanup_verified':report['new']['all_owned_cleanup_verified'],'scope':report['status']},sort_keys=True))


if __name__ == '__main__':
    main()
