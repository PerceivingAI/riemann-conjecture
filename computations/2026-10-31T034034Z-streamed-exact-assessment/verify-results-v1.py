"""Check completed exact result, raw receipt, program, stream and artifact bindings."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.whole_source.contract import canonical_bytes
from scripts.whole_source.execution import exact_telemetry


def require(value,message):
    if not value:
        raise ValueError(message)


def document(path):
    return json.loads(path.read_bytes())


def checked(root,ref):
    path = (root/ref['path']).resolve(strict=True)
    require(path.is_relative_to(root.resolve()) and not path.is_symlink(),'escaping evidence member')
    raw = path.read_bytes()
    require(len(raw)==ref['size'] and hashlib.sha256(raw).hexdigest()==ref['sha256'],
            'changed bound evidence: '+str(path))
    return raw


def contained(root,path):
    path = Path(path).resolve(strict=True)
    require(path.is_relative_to(root.resolve()),'foreign runtime evidence')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    require(not args.output.exists(),'fresh qualifier output required')
    bundle = args.bundle.resolve(strict=True)
    results,owned_peaks,external_increments = [],[],[]
    for label,scope,status,exit_code in (
        ('positive-v1','CONTROL_ONLY','PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL',0),
        ('signed-v1','CONTROL_ONLY','SELECTED_PAID_LOWER_NEGATIVE_NOT_WEIL_NEGATIVITY',1),
        ('retained-v1','REFERENCE_ARITHMETIC_ONLY','PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL',None)):
        run = bundle/'data'/label
        directory = run/'exact'
        report_raw = (directory/'report.json').read_bytes()
        report = json.loads(report_raw)
        require(report['proof_scope']==scope and report['status']==status and
                report['assessment']['proof_scope']==scope and
                report['assessment']['smooth_test_consequence_conditional'] is False and
                report['production_admission'] is False and report['analytical_source_acceptance'] is False,
                'unexpected exact result scope or consequence')
        require(len(report['receipt_bindings'])==len(report['owned_receipts'])==3,'incomplete stage receipt cover')
        stages = []
        for index,ref in enumerate(report['receipt_bindings']):
            raw = checked(directory,ref)
            receipt = json.loads(raw)
            require(exact_telemetry(receipt)==report['owned_receipts'][index], 'receipt summary differs')
            stage_name = ('parity-0','parity-1','assess')[index]
            require(receipt['stage']==stage_name and receipt['exit_code']==0 and receipt['error'] is None and
                    receipt['worker_cleanup_verified'] is True and
                    receipt['last_metrics']['active_process_count']==0 and
                    receipt['last_metrics']['active_process_ids']==[], 'owned stage did not cleanly succeed')
            argv = receipt['argv']
            runtime_program = contained(run,argv[argv.index('--program')+1])
            require(hashlib.sha256(runtime_program.read_bytes()).hexdigest()==receipt['program_sha256'],
                    'changed runtime program')
            config_path = contained(run,argv[argv.index('--config')+1])
            require(hashlib.sha256(config_path.read_bytes()).hexdigest()==receipt['config_sha256'],
                    'changed resource config')
            stage_path = contained(run,argv[argv.index('--stage')+1])
            require(hashlib.sha256(stage_path.read_bytes()).hexdigest()==argv[argv.index('--stage-sha256')+1],
                    'changed stage descriptor')
            stage = document(stage_path)
            plan = stage['plan']
            require(plan['role']=='exact' and plan['backend']=='python-flint-exact' and
                    plan['scope']=='EXACT_ASSESSMENT_ONLY' and plan['workers']==plan['threads']==1 and
                    plan['task_function']=='evaluate_exact' and plan['task_program']['path']=='scripts/whole_source/exact.py',
                    'wrong exact runtime plan')
            checked(ROOT,plan['task_program'])
            runtime_root = runtime_program.parents[2]
            checked(runtime_root,plan['task_program'])
            task_file = contained(run,stage['task_file'])
            require(hashlib.sha256(task_file.read_bytes()).hexdigest()==stage['task_sha256'] and stage['task_count']==1,
                    'changed exact task file')
            profile_path = contained(run,argv[argv.index('--profile')+1])
            profile = document(profile_path)
            require(profile['exit_code']==0 and profile['error'] is None and
                    profile['native_threads']==1 and profile['program_sha256']==receipt['program_sha256'],
                    'incorrect successful worker profile')
            attempt_root = (directory/ref['path']).parent.parent
            for stream in ('stdout','stderr'):
                member = contained(run,attempt_root/receipt['logs'][stream]['path'])
                require(hashlib.sha256(member.read_bytes()).hexdigest()==receipt['logs'][stream]['sha256'],
                        'changed owned stream')
            resources = document(attempt_root/(stage_name+'-resources.json'))
            require(resources['cleanup_verified'] is True and resources['resource_failure'] is None and
                    resources['transport_failure'] is None and
                    resources['sampled_external_increment_bytes']<=resources['external_increment_allowance_bytes'] and
                    resources['owned_peak_bytes']<=resources['owned_hard_cap_bytes'],
                    'resource or transport account failed')
            external_increments.append(resources['sampled_external_increment_bytes'])
            owned_peaks.append(receipt['peak_budgeted_memory_bytes'])
            stages.append({'stage':stage_name,'receipt_sha256':ref['sha256'],
                'peak_owned_bytes':receipt['peak_budgeted_memory_bytes'],'cleanup_verified':True,
                'elapsed_seconds_hex':float(receipt['elapsed_seconds']).hex(),
                'cpu_seconds_hex':float(receipt['last_metrics']['cpu_seconds']).hex()})
        products = 0
        for parity,ref in enumerate(report['product_inventories']):
            inventory = json.loads(checked(directory/'collection',ref))
            context = inventory['context']
            n,b = context['dimension'],context['panel_size']
            require(context['parity']==parity and set(inventory['panels'])==
                {f'{family}/{i}/{j}' for family in ('J','S') for i in range(0,n,b) for j in range(0,n,b)},
                'incomplete first-contraction inventory')
            for panel in inventory['panels'].values():
                checked(directory/'collection',panel)
                products += 1
        row = {'run':label,'status':status,'proof_scope':scope,'stages':stages,
            'product_panels_bound':products,'report_sha256':hashlib.sha256(report_raw).hexdigest()}
        if exit_code is not None:
            invocation = document(run/'invocation.json')
            require(invocation['exit_code']==exit_code,'incorrect real exact CLI exit')
            for channel in ('stdout','stderr'):
                checked(run,invocation[channel])
            row['cli_exit_code'] = exit_code
            row['cli_elapsed_seconds_hex'] = invocation['elapsed_seconds_hex']
        results.append(row)
    comparison = document(bundle/'data/reference-comparison-v1.json')
    require(comparison['status']=='PASS_EXACT_REFERENCE_COMPARISON' and comparison['row_margins_compared']==826,
            'incomplete retained reference comparison')
    result = {'format':'streamed-exact-execution-qualification-v1','status':'PASS_EXACT_EXECUTION_BINDINGS',
        'scope':'EXECUTION_AND_REFERENCE_BINDINGS_ONLY','results':results,'owned_stages_verified':9,
        'maximum_owned_peak_bytes':max(owned_peaks),'maximum_sampled_external_increment_bytes':max(external_increments),
        'analytical_source_acceptance':False,
        'fresh_source_proposal_qualification':False,'production_admission':False}
    with args.output.open('xb') as stream:
        stream.write(canonical_bytes(result))
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':
    main()
