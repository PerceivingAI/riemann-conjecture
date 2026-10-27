"""Conjunctive fixed research acceptance and exact full source-norm consequence.

This consumes trusted reviewed local-driver reports and immutable scientific
bytes. It is not a universal verifier for arbitrary untrusted process reports.
"""
import argparse,hashlib,json
from pathlib import Path
from flint import fmpq
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE_SHA='f69fee0feb9c08833ad6a3091718c9a6a301e5b5ddbea96ee5f0f6c0553c8b6e'
INPUTS_SHA='bb19e0fbafa6aff30e0eab92de1951b8c54c0cf380ab8681e0e0c098879b757a'
DECLARATION_SHA='026658a580d6ebe2ff8543d9e94ebbd24ea92d13027c5e43714e876cce353341'
CASES={'wrongactual-lowconstant','underpaidweightedhead','omitted-complete-physicalexterior','underpaid-terminal-inverseweight','omitted-prime5-low-term','omitted-prime5-mixed-square','singular-fullspace-witness','synthetic-selected-negative','numerical-width-uncertainty'}
SCALARS={'fresh_global_source':'data/reference-source-v2.json','fresh_global_native_audit':'data/reference-audit-v2.json','supported_reference_source':'data/supported-reference-source-v1.json','supported_reference_native_audit':'data/supported-reference-audit-v1.json','target_declaration':'data/target-declaration-source-v1.json','target_declaration_native_audit':'data/target-declaration-audit-v1.json','four_mode_topology_source':'data/topology-source-v1.json','four_mode_topology_native_audit':'data/topology-audit-v1.json'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def require(ok,message):
    if not ok:raise ValueError(message)
def confined(base,name):
    require(type(name) is str and name and '\\' not in name and ':' not in name and not name.startswith('/') and all(x not in ('','.','..') for x in name.split('/')),'portable confined path required')
    path=(base/name).resolve();require(path.is_relative_to(base.resolve()),'bound path escape');return path
def pinned(path,expected):
    raw=path.read_bytes();require(sha(raw)==expected,'changed bound file '+str(path));return raw
def q(value):
    require(type(value) is str,'rational string required');number=fmpq(value);require(str(number)==value,'canonical rational required');return number
def inventory(base,items):
    names=set()
    for item in items:
        require(item['path'] not in names,'duplicate inventory path');names.add(item['path'])
        raw=pinned(confined(base,item['path']),item['sha256']);require(len(raw)==item['bytes'],'inventory byte size')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('replay','negative-controls','output'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();require(not args.output.exists(),'fresh output required')
    inputs=json.loads(pinned(HERE/'acceptance-inputs-v1.json',INPUTS_SHA))
    require((inputs['support'],inputs['N'],inputs['K'],inputs['M'])==('81/100',826,86,1652) and inputs['production_admission'] is False,'acceptance tuple/scope')
    base=confined(ROOT,inputs['candidate_bundle']);manifest=json.loads(pinned(base/'manifest.json',inputs['candidate_manifest_sha256']))
    members={m['path']:m for m in manifest['members']};require(len(members)==len(manifest['members'])==33,'complete unique candidate inventory')
    for item in members.values():require(len(pinned(confined(base,item['path']),item['sha256']))==item['size'],'candidate size')
    qualification=confined(ROOT,inputs['qualification_bundle']);qm=json.loads(pinned(qualification/'manifest.json',inputs['qualification_manifest_sha256']))
    for item in qm['members']:require(len(pinned(confined(qualification,item['path']),item['sha256']))==item['size'],'qualification size')
    source=json.loads(pinned(base/'data/source-v1.json',SOURCE_SHA));native=load(base/'data/source-audit-v1.json');proof=load(base/'data/exact-sign-v1.json')
    require(native['status']=='PASS_COMPLETE_SOURCE' and native['checked_triangular_entries']==512946 and native['checked_matrix_files']==6 and native['source_sha256']==SOURCE_SHA,'canonical full native gate')
    require(proof['status']=='PASS_COMPLETE_SOURCE_CONDITIONAL_CANDIDATE' and proof['source_sha256']==SOURCE_SHA and set(proof['blocks'])=={'even','odd'},'canonical full exact gate')
    require(source['producer_sha256']==members['build-whole-source-v1.py']['sha256'] and native['consumer_sha256']==members['verify-whole-source-v1.py']['sha256'] and proof['verifier_sha256']==members['verify-whole-sign-v1.py']['sha256'],'scientific program fingerprints')
    candidate_inputs=load(base/'whole-inputs-v1.json');require(candidate_inputs['target_declaration_sha256']==DECLARATION_SHA,'fixed declaration pin')
    declaration=json.loads(pinned(confined(ROOT,candidate_inputs['target_declaration']),DECLARATION_SHA))
    require(proof['inputs_sha256']==native['inputs_sha256']==source['inputs_sha256']==sha((base/'whole-inputs-v1.json').read_bytes()),'same complete input bytes')
    require(proof['proposal_sha256']==members['data/proposal-v1.json.gz']['sha256'],'raw compressed witness binding')
    replay=load(args.replay);capture_path=HERE/'captured-source-inputs-v1.json';capture=load(capture_path)
    require(replay['status']=='PASS_COMPLETE_CAPTURED_REFERENCE_SOURCE_AND_EXACT_REPLAY' and replay['source_sha256']==SOURCE_SHA,'isolated replay status/source')
    require(replay['driver_sha256']==sha((HERE/'replay-acceptance-v1.py').read_bytes())==capture['driver_sha256'] and replay['captured_manifest_sha256']==sha(capture_path.read_bytes()),'replay driver/capture binding')
    require(replay['original_tree_scientific_execution'] is False and replay['expected_full_target_outputs_installed_in_child'] is False and replay['own_isolated_tree_removed'] is True,'source isolation/output separation/cleanup')
    require(len({m['destination'] for m in capture['files']})==len(capture['files'])==replay['captured_files']==55,'complete unique capture inventory')
    for item in capture['files']:
        require(len(pinned(confined(HERE,item['stored']),item['sha256']))==item['bytes'],'captured size')
        require(len(pinned(confined(ROOT,item['destination']),item['sha256']))==item['bytes'],'capture differs from immutable canonical source/input')
        require(set(item['roles']) in ({'installed'},{'expected_target_only'}),'unknown capture role')
    require(capture['candidate_manifest_sha256']==inputs['candidate_manifest_sha256'] and capture['qualification_manifest_sha256']==inputs['qualification_manifest_sha256'],'captured immutable bundle identities')
    oracle_names={inputs['candidate_bundle']+'/data/'+d['path'] for d in source['matrices'].values()}|{inputs['candidate_bundle']+'/data/'+n for n in ('source-v1.json','source-audit-v1.json','exact-sign-v1.json')}
    require(all('installed' not in item['roles'] for item in capture['files'] if item['destination'] in oracle_names),'expected target output installed as a scientific premise')
    require({item['destination'] for item in capture['files'] if 'expected_target_only' in item['roles']}==oracle_names,'exact expected-target-only inventory')
    require(len(replay['steps'])==11 and all(s['exit_code']==0 for s in replay['steps']),'all isolated scientific processes')
    require(set(replay['qualification_checks'])==set(SCALARS),'all scalar/reference replay outputs')
    for name,path in SCALARS.items():require(replay['qualification_checks'][name]=={'byte_identical':True,'sha256':sha((qualification/path).read_bytes())},'scalar byte reproduction '+name)
    require(set(replay['checks'])=={'complete_source','complete_native_audit','complete_exact_sign'}|set(source['matrices']),'all target scientific comparisons')
    require(replay['checks']['complete_source']=={'byte_identical':True,'sha256':SOURCE_SHA},'source byte reproduction')
    require(replay['checks']['complete_exact_sign']=={'byte_identical':True,'sha256':members['data/exact-sign-v1.json']['sha256']},'exact report byte reproduction')
    require(replay['checks']['complete_native_audit']=={'identical_except_explicit_paths':['source','inputs'],'all_other_fields_identical':True},'only native execution paths excluded')
    for name,d in source['matrices'].items():require(replay['checks'][name]=={'byte_identical':True,'sha256':d['sha256']},'matrix byte reproduction '+name)
    negatives=load(args.negative_controls)
    require(negatives['format']=='t081-retained-negative-controls-v1' and negatives['status']=='PASS_NEGATIVE_CONTROLS' and negatives['candidate_source_sha256']==SOURCE_SHA and negatives['candidate_manifest_sha256']==inputs['candidate_manifest_sha256'],'substantive false mathematics gate')
    require(len(negatives['cases'])==9 and {c['case'] for c in negatives['cases']}==CASES and all(c['passed'] is True for c in negatives['cases']),'nine distinct substantive outcomes')
    case_root=confined(HERE,negatives['case_directory']);inventory(case_root,negatives['files'])
    for case in negatives['cases']:inventory(case_root,case['files'])
    control=negatives['native_batch_proof']
    require(control['status']=='PASS_ORIGINAL_NATIVE_SUBSET_CONTROL' and control['consumer_sha256']==members['verify-whole-source-v1.py']['sha256'] and control['source_sha256']==SOURCE_SHA and control['parity']==0 and control['dimension']==413 and control['independent_precision_bits']==6144 and control['checked_triangular_entries']==256473,'fresh independent even control')
    require(control['successful_original_controls'] is True and control['consumer_predicates_unchanged'] is True and control['producer_imported'] is False and control['fresh_reconstruct_calls']==1,'honest native subset semantics')
    require({r['family'] for r in control['original_families_checked']}=={'A_model-0','weighted_head-0','weighted_complete_tail-0'} and all(r['status']=='PASS_NATIVE_SUBSET_CONTAINMENT' and r['checked_triangular_entries']==85491 for r in control['original_families_checked']),'all original even families')
    review=load(HERE/'review-decision-v1.json');require(review['scope_approved'] is True and review['source_sha256']==SOURCE_SHA and review['published_rational_source_norm_gap_lower']=='1/1000000000000000000000','reviewed consequence scope')
    pinned(HERE/'smooth-test-consequence-v1.md',review['smooth_test_consequence_sha256']);pinned(HERE/'independent-review-v1.md',review['review_text_sha256'])
    low=[]
    for label in ('even','odd'):
        b=proof['blocks'][label]
        require(b['dimension']==413 and b['exact_nonsingularity'] is True and b['positive_complete_paid_lower'] is True and b['numerical_width_goal_passed'] is True,'complete positive parity '+label)
        require(q(b['minimum_complete_congruence_margin'])>0 and q(b['numerical_radius_physical_goal'])==q(declaration['precision']['numerical_error_physical_norm_goal']) and q(b['numerical_radius_physical_upper'])<=q(b['numerical_radius_physical_goal']),'strict exact sign and frozen physical error goal')
        low.append(q(b['complete_physical_lower_if_positive']))
    sigma=min(low);eta=q(declaration['eta']);m=q(declaration['m']);delta=q(declaration['complete_remainder_upper']);b=q(declaration['combined_model_cross_norm_upper'])+delta
    require(sigma>0 and 0<eta<=1 and m>0 and delta>=0 and b>0,'positive full consequence inputs')
    factor=1+2*b*b/(eta*eta*m*m);gamma=min(sigma/factor,eta*m/2);published=fmpq(1,10**21)
    require(gamma>=published>0,'published full source-norm bound does not follow')
    result={'format':'t081-retained-full-smooth-test-acceptance-v1','status':'PASS_RETAINED_SOURCE_CONDITIONAL_SMOOTH_TEST_POSITIVITY','support':'81/100','N':826,'K':86,'M':1652,'source_sha256':SOURCE_SHA,'candidate_manifest_sha256':inputs['candidate_manifest_sha256'],'qualification_manifest_sha256':inputs['qualification_manifest_sha256'],'acceptance_program_sha256':sha(Path(__file__).read_bytes()),'acceptance_inputs_sha256':INPUTS_SHA,'replay_report_sha256':sha(args.replay.read_bytes()),'negative_controls_report_sha256':sha(args.negative_controls.read_bytes()),'captured_closure_sha256':sha(capture_path.read_bytes()),'review_decision_sha256':sha((HERE/'review-decision-v1.json').read_bytes()),'source_analytic_entries_reconstructed':512946,'qualification_byte_checks':8,'target_replay_checks':9,'captured_destinations':55,'adversarial_cases':9,'adversarial_native_original_even_control_entries':256473,'adversarial_native_scope_is_subset_not_complete_source_audit':True,'full_parity_dimensions':[413,413],'ordinary_physical_mass':'2/(2n+1)','sigma_selected_low_Schur':str(sigma),'true_complete_cross_norm_upper':str(b),'eta':str(eta),'m':str(m),'full_norm_comparison_factor':str(factor),'complete_source_norm_gap_lower':str(gamma),'published_rational_source_norm_gap_lower':str(published),'source_norm':'scaled L2(-1,1), equivalent unitary physical L2(-T,T)','smooth_test_consequence':'strict positivity for every nonzero admissible complex smooth test supported in[-81/100,81/100] under the documented source/form/Arb premises','whole_operator_domain_identity_claimed':False,'external_coercivity_comparison_claimed':False,'production_admission':False,'RH_status':'UNRESOLVED','report_trust_boundary':'reviewed trusted local scientific drivers and shared recorded runtime/source premises; not arbitrary untrusted-report proof verification'}
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:handle.write(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'source_sha256':SOURCE_SHA,'published_rational_source_norm_gap_lower':str(published),'production_admission':False}))
if __name__=='__main__':main()
