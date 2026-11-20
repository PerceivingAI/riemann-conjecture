"""Exercise exact context, witness-source and owned-receipt rejection predicates.

These are bounded contract controls on real completed inputs/receipts. They do
not replace the nine full-reference mathematical controls or final assessment.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.whole_source.contract import ContractError,bind_problem,canonical_bytes
from scripts.whole_source.retention import _bind,_verify_receipts,_record
from scripts.whole_source.proposal import read_proposal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--problem',type=Path,required=True)
    parser.add_argument('--execution',type=Path,required=True)
    parser.add_argument('--scalar-run',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=False)
    _bind(args.problem,args.execution,ROOT)
    problem = json.loads(args.problem.read_bytes())
    execution = json.loads(args.execution.read_bytes())
    cases = []
    for name in ('changed-full-dimension','loosened-numerical-goal','changed-code-bytes','ignored-mathematical-replay-output'):
        p,e = deepcopy(problem),deepcopy(execution)
        if name=='changed-full-dimension':
            p['parameters']['N']-=2
        elif name=='loosened-numerical-goal':
            value = p['parameters']['numerical_goal']
            value['numerator']=hex(2*int(value['numerator'],16))
        elif name=='changed-code-bytes':
            e['code'][0]['sha256']='0'*64
        else:
            e['replay_exclusions']['exact'].append('blocks')
        directory = output/name
        directory.mkdir()
        (directory/'problem.json').write_bytes(canonical_bytes(p))
        (directory/'execution.json').write_bytes(canonical_bytes(e))
        try:
            _bind(directory/'problem.json',directory/'execution.json',ROOT)
        except ContractError as error:
            cases.append({'case':name,'rejected':True,'error':str(error),
                'problem':_record(directory/'problem.json'),'execution':_record(directory/'execution.json')})
        else:
            raise ValueError('changed context was accepted: '+name)
    source_root = ROOT/'computations/2026-10-31T025401Z-blocked-nonproof-proposal/data'
    core_path = source_root/'positive-run-v3/proposal/proposal.json'
    core = json.loads(core_path.read_bytes())
    bound = bind_problem('retained-t081')
    read_proposal(core_path,bound,core['source'])
    wrong_source = {**core['source'],'sha256':'0'*64}
    try:
        read_proposal(core_path,bound,wrong_source)
    except ContractError as error:
        cases.append({'case':'proposal-bound-to-another-source','rejected':True,'error':str(error),
            'proposal':_record(core_path),'scope':'CONTROL_ONLY_EXISTING_FINITE_NONPROOF_CORE'})
    else:
        raise ValueError('proposal/source identity was ignored')
    successful = _verify_receipts(args.scalar_run)
    first = successful[0]
    path = Path(first['directory'])/first['artifact']['path']
    shadow = output/'misplaced-receipt'
    shadow.mkdir()
    (shadow/'receipt.json').write_bytes(path.read_bytes())
    try:
        _verify_receipts(shadow)
    except ContractError as error:
        cases.append({'case':'owned-receipt-from-another-stage','rejected':True,'error':str(error),
            'original_receipt':first,'misplaced_receipt':_record(shadow/'receipt.json')})
    else:
        raise ValueError('receipt moved to another stage was accepted')
    result = {'format':'whole-source-context-control-qualification-v1','status':'PASS_BOUND_CONTEXT_CONTROLS',
        'positive_owned_scalar_stages_verified':len(successful),'cases':cases,
        'original_inputs':{'problem':_record(args.problem),'execution':_record(args.execution)},
        'argv':[sys.executable,*sys.argv],
        'program_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'full_reference_acceptance':False,'production_admission':False}
    (output/'context-controls.json').write_bytes(canonical_bytes(result))
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':
    main()
