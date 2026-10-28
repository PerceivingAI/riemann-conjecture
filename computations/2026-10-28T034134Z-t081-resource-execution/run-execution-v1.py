"""Budgeted captured source, independent audit, exact sign and nine countercases.

No production admission or new smooth-test release. Existing proof artifacts
and their retained-acceptance procedure are not modified or substituted.
"""
from __future__ import annotations
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
from execution_resources_v2 import resolve_resources
from execution_supervisor_v1 import Execution
import native_controls_v1 as controls

CAPTURE=ROOT/'computations/2026-10-27T182100Z-t081-retained-acceptance'
OLD='computations/2026-10-27T140745Z-t081-complete-gram-attempt'
SELF=HERE.relative_to(ROOT)
GIB=1024**3
# Planning reservations, not proved analytic bounds. The kernel cap is authoritative.
# The consumer probe's 739647488-byte peak scaled by (826/256)^2 and 25% headroom
# rounds up to 9 GiB; the measured source's 6.17 GiB plus headroom fits below it.
REQUIRED_BYTES=9*GIB


def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
def require(condition,message):
    if not condition:raise ValueError(message)
def fresh(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:stream.write(raw)
def load(path):return json.loads(path.read_bytes())
def confined(base,name):
    require(isinstance(name,str) and name and ':' not in name and '\\' not in name,'portable relative path required')
    require(all(x not in ('','.','..') for x in name.split('/')),'unsafe relative path')
    path=(base/name).resolve();require(path.is_relative_to(base.resolve()),'path escapes capture');return path


def capture_tree(isolated,retained):
    raw=(CAPTURE/'captured-source-inputs-v1.json').read_bytes();capture=json.loads(raw)
    records=[]
    for item in capture['files']:
        data=confined(CAPTURE,item['stored']).read_bytes()
        require(sha(data)==item['sha256'] and len(data)==item['bytes'],'captured premise changed')
        if 'installed' in item['roles']:fresh(confined(isolated,item['destination']),data)
        records.append({'destination':item['destination'],'sha256':sha(data),'roles':item['roles']})
    for item in records:
        if 'expected_target_only' in item['roles']:
            require(not confined(isolated,item['destination']).exists(),'expected target leaked into child')
    programs={}
    for file in HERE.glob('*.py'):
        data=file.read_bytes();target=isolated/SELF/file.name;fresh(target,data)
        fresh(retained/'captured-code-v1'/file.name,data)
        programs[file.name]=sha(data)
    exact=(ROOT/OLD/'verify-whole-sign-v1.py').read_bytes()
    fresh(isolated/SELF/'verify-whole-sign-v1.py',exact)
    fresh(retained/'captured-code-v1'/'verify-whole-sign-v1.py',exact)
    programs['verify-whole-sign-v1.py']=sha(exact)
    return {'original_capture_sha256':sha(raw),'original_capture_files':len(records),
        'records':records,'new_programs':programs,'expected_full_target_outputs_installed':False}


def pipeline(output,budget):
    output=Path(output).resolve()
    with Execution(output,budget) as run:
        with tempfile.TemporaryDirectory(prefix='rh_t081_resource_capture_') as temporary:
            isolated=Path(temporary).resolve();capture=capture_tree(isolated,output)
            fresh(output/'captured-execution-v1.json',encode(capture))
            run.root=isolated;run.worker=isolated/SELF/'stage_worker_v1.py'
            programs=isolated/SELF
            inputs=isolated/OLD/'whole-inputs-v1.json'
            result_dir=output/'results';result_dir.mkdir()
            source=result_dir/'source.json';audit=result_dir/'audit.json';exact=result_dir/'exact.json'
            proposal=result_dir/'proposal.json.gz';native_dir=output/'native-controls'
            run.run('source',programs/'build-whole-source-v4.py',
                ['--inputs',inputs,'--output',source],kind='source')
            source_raw=source.read_bytes();source_data=json.loads(source_raw)
            # Old exact witness is an input proposal, never an inherited sign.
            proposed=json.loads(gzip.decompress((isolated/OLD/'data/proposal-v1.json.gz').read_bytes()))
            proposed['source_sha256']=sha(source_raw)
            fresh(proposal,gzip.compress(encode(proposed),mtime=0))
            run.run('independent-audit',programs/'verify-whole-source-v2.py',
                ['--inputs',inputs,'--source',source,'--output',audit],kind='audit',
                environment={'T081_NATIVE_CONTROLS':str(native_dir)})
            accepted=load(audit)
            require(accepted['status']=='PASS_COMPLETE_SOURCE' and accepted['checked_triangular_entries']==512946
                and accepted['source_sha256']==sha(source_raw),'complete independent analytical gate failed')
            run.run('exact-sign',programs/'verify-whole-sign-v1.py',
                ['--inputs',inputs,'--source',source,'--proposal',proposal,'--output',exact],kind='exact')
            signed=load(exact)
            require(signed['status']=='PASS_COMPLETE_SOURCE_CONDITIONAL_CANDIDATE' and signed['source_sha256']==sha(source_raw)
                and set(signed['blocks'])=={'even','odd'}
                and all(x['dimension']==413 and x['exact_nonsingularity'] and x['positive_complete_paid_lower']
                    and x['numerical_width_goal_passed'] for x in signed['blocks'].values()),'complete zero-float gate failed')
            matrices={key:((result_dir/d['path']).read_bytes(),
                json.loads(gzip.decompress((result_dir/d['path']).read_bytes()))) for key,d in source_data['matrices'].items()}
            cases=[];case_root=output/'exact-controls';case_root.mkdir()
            for name,expected in (('singular-fullspace-witness','singular full congruence'),
                ('synthetic-selected-negative','SELECTED_CONSERVATIVE_SCHUR_NEGATIVE_NOT_WEIL_NEGATIVITY'),
                ('numerical-width-uncertainty','NUMERICAL_WIDTH_GOAL_FAILED')):
                folder=case_root/name;folder.mkdir()
                _,case_sha,_=controls.packet(folder,source_data,matrices,name,{})
                variant=copy.deepcopy(proposed);variant['source_sha256']=case_sha
                if name=='singular-fullspace-witness':
                    for row in variant['blocks']['even']['proposal_transform']:row[0]='0'
                fresh(folder/'proposal.json.gz',gzip.compress(encode(variant),mtime=0))
                stage=run.run(name,programs/'verify-whole-sign-v1.py',
                    ['--inputs',inputs,'--source',folder/'source.json','--proposal',folder/'proposal.json.gz',
                     '--output',folder/'exact.json'],kind='exact',expected_codes=(1,) if name=='singular-fullspace-witness' else (0,))
                if name=='singular-fullspace-witness':
                    require(expected in (output/name/'stderr.txt').read_text(encoding='utf-8'),'singular witness did not reach exact nonsingularity rejection')
                else:require(load(folder/'exact.json')['status']==expected,'exact countercase reached wrong outcome')
                cases.append({'case':name,'passed':True,'expected':expected,'source_sha256':case_sha})
            native=load(native_dir/'native-controls.json')
            require(native['status']=='PASS_SIX_NATIVE_SUBSET_CONTROLS' and native['source_sha256']==sha(source_raw)
                and len(native['cases'])==6 and all(x['passed'] for x in native['cases']),'native countercases incomplete')
            checker=ROOT/'computations/2026-10-28T024305Z-t081-execution-corrections/compare-v3-v1.py'
            spec=importlib.util.spec_from_file_location('t081_strict_identity',checker)
            identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)
            identity_result=identity.compare(source,HERE/'build-whole-source-v4.py')
            fresh(output/'identity.json',encode(identity_result))
            for file,digest in capture['new_programs'].items():
                expected_file=programs/file
                require(sha(expected_file.read_bytes())==digest,'captured execution code changed')
            result={'format':'t081-resource-execution-qualification-v1',
                'status':'PASS_CAPTURED_SOURCE_ANALYTICAL_EXACT_AND_NINE_CONTROLS',
                'source_sha256':sha(source_raw),'budget':budget,'capture':capture,
                'analytical_entries':512946,'native_controls':native,'exact_controls':cases,
                'identity':identity_result,'stages':run.receipts,'production_admission':False,
                'retained_smooth_test_admission_executed':False,'rh_status':'UNRESOLVED'}
        result['captured_tree_removed']=not isolated.exists()
        require(result['captured_tree_removed'],'captured owned tree remains')
        require(all(stage['worker_cleanup_verified'] for stage in run.receipts),'owned workers remain')
        fresh(output/'qualification.json',encode(result))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    for name in ('cpus','workers','threads','memory-mib','reserve-mib'):
        parser.add_argument('--'+name,type=int)
    args=parser.parse_args()
    budget=resolve_resources(cpus=args.cpus,workers=args.workers,threads=args.threads,
        memory_mib=args.memory_mib,reserve_mib=args.reserve_mib,required_bytes=REQUIRED_BYTES)
    result=pipeline(args.output_dir,budget)
    print(json.dumps({'status':result['status'],'captured_tree_removed':result['captured_tree_removed'],
        'analytical_entries':result['analytical_entries']}),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
