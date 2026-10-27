"""Conjunctive retained research acceptance and exact full source-norm consequence."""
import argparse,hashlib,json
from pathlib import Path
from flint import fmpq
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SOURCE_SHA='f50d8a194bf4d13ad4cd65ccbcf5762c403d8f5e26d384cbdb38be5ccb807fe6'
CASES={'wrongactual-lowconstant','underpaidweightedhead','omitted-complete-physicalexterior','underpaid-terminal-inverseweight','singular-fullspace-witness','synthetic-selected-negative','numerical-width-uncertainty'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def require(ok,message):
    if not ok:raise ValueError(message)

def pinned(path,expected):
    raw=path.read_bytes();require(sha(raw)==expected,'changed bound file '+str(path));return raw

def q(value):
    require(type(value) is str,'rational string required');number=fmpq(value);require(str(number)==value,'canonical rational required');return number

def main():
    p=argparse.ArgumentParser();p.add_argument('--replay',type=Path,required=True);p.add_argument('--negative-controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();require(not args.output.exists(),'fresh output required')
    inputs=load(HERE/'acceptance-inputs-v1.json');base=ROOT/inputs['candidate_bundle'];manifest=load(base/'manifest.json')
    pinned(base/'manifest.json',inputs['candidate_manifest_sha256']);members={x['path']:x for x in manifest['members']}
    for item in members.values():
        raw=pinned(base/item['path'],item['sha256']);require(len(raw)==item['bytes'],'candidate byte size')
    source=load(base/'data/whole-source-v2.json');require(sha((base/'data/whole-source-v2.json').read_bytes())==SOURCE_SHA,'source fingerprint')
    native=load(base/'data/whole-source-audit-v2.json');proof=load(base/'data/whole-exact-sign-v2.json')
    require(native['status']=='PASS_COMPLETE_SOURCE' and native['checked_triangular_entries']==78246 and native['source_sha256']==SOURCE_SHA,'canonical full native gate')
    require(proof['status']=='PASS_COMPLETE_SOURCE_CONDITIONAL_CANDIDATE' and proof['source_sha256']==SOURCE_SHA and set(proof['blocks'])=={'even','odd'},'canonical full exact gate')
    require(source['producer_sha256']==members['build-whole-source-v2.py']['sha256'] and native['consumer_sha256']==members['verify-whole-source-v2.py']['sha256'] and proof['verifier_sha256']==members['verify-whole-sign-v1.py']['sha256'],'mathematical program fingerprints')
    replay=load(args.replay);capture_path=HERE/'captured-source-inputs-v2.json';capture=load(capture_path)
    require(replay['status']=='PASS_COMPLETE_CAPTURED_REFERENCE_SOURCE_AND_EXACT_REPLAY' and replay['source_sha256']==SOURCE_SHA,'isolated replay status/source')
    require(replay['driver_sha256']==sha((HERE/'replay-acceptance-v2.py').read_bytes()) and replay['captured_manifest_sha256']==sha(capture_path.read_bytes()),'replay driver/capture binding')
    require(replay['original_tree_scientific_execution'] is False and replay['own_isolated_tree_removed'] is True,'execution isolation/cleanup')
    require(len({x['destination'] for x in capture['files']})==len(capture['files'])==replay['captured_files'],'complete unique captured files')
    require(capture['extends_capture_sha256']==sha((HERE/'captured-source-inputs-v1.json').read_bytes()),'preserved first capture binding')
    for item in capture['files']:
        raw=pinned(HERE/item['stored'],item['sha256']);require(len(raw)==item['bytes'],'captured size')
    require(len(replay['steps'])==4 and all(s['exit_code']==0 for s in replay['steps']),'all isolated mathematical processes')
    qualification=replay['qualification_replay'];require(qualification['status']=='PASS_CAPTURED_QUALIFICATION_REPLAY' and len(qualification['checks'])==14 and qualification['own_isolated_tree_removed'] is True,'full scalar/reference qualification replay')
    require(set(replay['checks'])=={'complete_source','complete_native_audit','complete_exact_sign'}|set(source['matrices']),'all target scientific replay checks')
    require(replay['checks']['complete_source']=={'byte_identical':True,'sha256':SOURCE_SHA},'complete source byte check')
    require(replay['checks']['complete_exact_sign']=={'byte_identical':True,'sha256':members['data/whole-exact-sign-v2.json']['sha256']},'complete exact report byte check')
    require(replay['checks']['complete_native_audit']=={'identical_except_explicit_paths':['source','inputs'],'all_other_fields_identical':True},'only two native execution-path exclusions')
    for name,descriptor in source['matrices'].items():require(replay['checks'][name]=={'byte_identical':True,'sha256':descriptor['sha256']},'complete matrix byte check '+name)
    negatives=load(args.negative_controls)
    require(negatives['status']=='PASS_NEGATIVE_CONTROLS' and negatives['candidate_source_sha256']==SOURCE_SHA and negatives['candidate_manifest_sha256']==inputs['candidate_manifest_sha256'],'false mathematics gate')
    require(len(negatives['cases'])==7 and {c['case'] for c in negatives['cases']}==CASES and all(c['passed'] is True for c in negatives['cases']),'seven distinct substantive countercases')
    case_root=(HERE/negatives['case_directory']).resolve();require(case_root.is_relative_to(HERE),'case inventory path')
    for case in negatives['cases']:
        for item in case['files']:
            path=(case_root/item['path']).resolve();require(path.is_relative_to(case_root),'case path escape');raw=pinned(path,item['sha256']);require(len(raw)==item['bytes'],'case byte size')
    low=[]
    for label in ('even','odd'):
        block=proof['blocks'][label]
        require(block['dimension']==161 and block['exact_nonsingularity'] is True and block['positive_complete_paid_lower'] is True and block['numerical_width_goal_passed'] is True,'complete positive parity '+label)
        require(q(block['minimum_complete_congruence_margin'])>0 and q(block['numerical_radius_physical_upper'])<=q(block['numerical_radius_physical_goal']),'strict exact sign and physical error budget')
        low.append(q(block['complete_physical_lower_if_positive']))
    candidate_inputs=load(base/'whole-inputs-v1.json')
    declaration=json.loads(pinned(ROOT/candidate_inputs['target_declaration'],candidate_inputs['target_declaration_sha256']))
    sigma=min(low);eta=q(declaration['eta']);m=q(declaration['m']);delta=q(declaration['complete_remainder_upper']);b=q(declaration['combined_model_cross_norm_upper'])+delta
    require(sigma>0 and 0<eta<=1 and m>0 and delta>=0 and b>0,'positive full consequence inputs')
    factor=1+2*b*b/(eta*eta*m*m);gamma=min(sigma/factor,eta*m/2);published=fmpq(1,10**20)
    require(gamma>=published>0,'published full source-norm lower does not follow')
    result={'format':'t080-retained-full-smooth-test-acceptance-v1','status':'PASS_RETAINED_SOURCE_CONDITIONAL_SMOOTH_TEST_POSITIVITY','support':'4/5','N':322,'K':76,'M':644,'source_sha256':SOURCE_SHA,'candidate_manifest_sha256':inputs['candidate_manifest_sha256'],'acceptance_program_sha256':sha(Path(__file__).read_bytes()),'replay_report_sha256':sha(args.replay.read_bytes()),'negative_controls_report_sha256':sha(args.negative_controls.read_bytes()),'captured_closure_sha256':sha(capture_path.read_bytes()),'source_analytic_entries_reconstructed':78246,'qualification_byte_checks':14,'target_replay_checks':9,'adversarial_cases':7,'full_parity_dimensions':[161,161],'ordinary_physical_mass':'2/(2n+1)','sigma_selected_low_Schur':str(sigma),'true_complete_cross_norm_upper':str(b),'eta':str(eta),'m':str(m),'full_norm_comparison_factor':str(factor),'complete_source_norm_gap_lower':str(gamma),'published_rational_source_norm_gap_lower':str(published),'source_norm':'L2(-1,1), equivalently unitary f(t)=T^-1/2u(t/T) on(-T,T)','smooth_test_consequence':'strict positivity for every nonzero complex Suzuki admissible smooth test at fixed support, conditional on source/form/Arb premises','whole_operator_domain_identity_claimed':False,'external_coercivity_comparison_claimed':False,'production_admission':False,'RH_status':'UNRESOLVED'}
    with args.output.open('x',encoding='utf-8',newline='\n') as stream:stream.write(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'source_sha256':SOURCE_SHA,'published_rational_source_norm_gap_lower':str(published),'production_admission':False}),flush=True)
if __name__=='__main__':main()
