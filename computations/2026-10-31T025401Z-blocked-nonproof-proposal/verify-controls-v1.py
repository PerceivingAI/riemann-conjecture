"""Read-only exact checks of finite manufactured proposal controls and owned receipts."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.whole_source.contract import bind_problem, canonical_bytes
from scripts.whole_source.proposal import PanelStore, read_proposal


def require(value,message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_bytes())


def bound(base,ref):
    path = base/ref['path']
    require(path.resolve().is_relative_to(base.resolve()),'escaping retained control path')
    raw = path.read_bytes()
    require(len(raw)==ref['size'] and hashlib.sha256(raw).hexdigest()==ref['sha256'],'changed control bytes')
    return raw


def transpose(a):
    return [list(row) for row in zip(*a,strict=True)]


def multiply(a,b):
    return [[sum((x*y for x,y in zip(row,col,strict=True)),Q(0)) for col in transpose(b)] for row in a]


def unpack(run,block,prefix,kind,inventory=None):
    n,b = block['context']['dimension'],block['context']['panel_size']
    if inventory is None:
        refs = {f"Z/{r['row']}/{r['column']}":r['artifact'] for r in block['integer_panels']}
        base = run/'proposal'
    else:
        base = Path(inventory['root'])
        refs = json.loads(bound(base,inventory['inventory']))['panels']
    store = PanelStore(base,block['context'],refs)
    result = [[Q(0) for _ in range(n)] for _ in range(n)]
    for i in range(0,n,b):
        for j in range(0,n,b):
            rows,cols = min(b,n-i),min(b,n-j)
            values = store.read(f'{prefix}/{i}/{j}',kind)
            for k,value in enumerate(values):
                result[i+k//cols][j+k%cols] = (Q(int(value,16),1 << 80) if kind=='integer' else
                    Q(*float.fromhex(value).as_integer_ratio()))
    return result


def check_owned(stage_root,report):
    attempt = report['attempt_id']
    count,peak = 0,0
    for value in report['owned_receipts']:
        name = value['stage']
        folder = stage_root/'attempts'/attempt/name
        receipt = read(folder/'receipt.json')
        require(receipt['exit_code']==0 and receipt['worker_cleanup_verified'] is True,'unsuccessful owned stage')
        require(receipt['peak_budgeted_memory_bytes']==value['peak_budgeted_memory_bytes'],'changed owned peak')
        for channel in ('stdout','stderr'):
            raw = (folder/(channel+'.txt')).read_bytes()
            require(hashlib.sha256(raw).hexdigest()==receipt[channel+'_sha256'],'changed owned stream')
        count += 1
        peak = max(peak,receipt['peak_budgeted_memory_bytes'])
    require(count==1,'unexpected controlled stage inventory')
    return count,peak


def check_case(input_root,run,case):
    definition = read(input_root/'control-definition.json')
    require(definition['case']==case and definition['scope']=='FINITE_MANUFACTURED_MATRIX_CONTROL_NOT_EVALUATED_WEIL_SOURCE',
            'wrong controlled source meaning')
    source_raw = (input_root/'source/source-manifest.json').read_bytes()
    require(hashlib.sha256(source_raw).hexdigest()==definition['source_sha256'],'changed control definition source')
    source = json.loads(source_raw)
    problem = bind_problem('retained-t081')
    ref = {'path':'source-manifest.json','sha256':definition['source_sha256'],'size':len(source_raw)}
    core = read_proposal(run/'proposal/proposal.json',problem,ref)
    invocation = read(run/'invocation.json')
    require(invocation['exit_code']==0,'unsuccessful proposal CLI')
    for channel in ('stdout','stderr'):
        bound(run,invocation[channel])
    source_entries = 0
    for tile in source['tiles']:
        records = json.loads(bound(input_root/'source',tile['artifact']))['records']
        exact = definition['exact_matrices'][str(tile['parity'])][tile['family']]
        for m,n,lo,hi in records:
            x = Q(exact[m//2][n//2])
            require(Q(int(lo,16),1 << 256) <= x <= Q(int(hi,16),1 << 256),
                    'control publication does not contain its exact matrix')
            source_entries += 1
    diagnostics = json.loads(bound(run/'proposal',core['diagnostics']))
    stages,peak,entries,max_residual,max_error = 0,0,0,Q(0),Q(0)
    for block,detail in zip(core['blocks'],diagnostics['blocks'],strict=True):
        p = block['parity']
        require(detail['parity']==p,'changed diagnostic parity')
        for phase in ('native','floating','solve'):
            count,observed = check_owned(run/'proposal'/(phase+'-'+str(p)),detail[phase])
            stages,peak = stages+count,max(peak,observed)
        fd = detail['floating']['diagnostics']
        require(fd['native_library_loaded'] is False,'native/float library lifetime overlap')
        theta = Q(block['theta'])
        require(abs(theta-2) < Q(1,1 << 16),'incorrect known Young optimum')
        require(fd['transform_kind']==('positive_whitening' if case=='positive' else 'signed_diagonalization'),
                'incorrect conditional eigensystem branch')
        z = unpack(run,block,'Z','integer')
        vectors = unpack(run,block,'V','binary64',detail['floating']['inventory'])
        factor = [[Q(x) for x in row] for row in definition['exact_factors'][str(p)]]
        residual = multiply(transpose(factor),z)
        for i in range(3):
            for j in range(3):
                error = abs(residual[i][j]-vectors[i][j])
                max_residual = max(max_residual,error)
                require(error < Q(1,1 << 70),'full native backsolve/dyadic rounding residual failed')
        matrices = {k:[[Q(x) for x in row] for row in matrix]
                    for k,matrix in definition['exact_matrices'][str(p)].items()}
        paid = [[matrices['A_model'][i][j]-(problem.model_error*Q(2,2*(2*i+p)+1) if i==j else 0)
                 -(1+theta)*matrices['weighted_head'][i][j]/problem.eta
                 -(1+1/theta)*matrices['weighted_complete_tail'][i][j]/problem.eta
                 for j in range(3)] for i in range(3)]
        actual = multiply(multiply(transpose(z),paid),z)
        hvalues = [Q(1,8),Q(1,4),Q(3,8)]
        eigen = sorted(1-((1+theta)+4*(1+1/theta))*h for h in hvalues)
        for i in range(3):
            for j in range(3):
                expected = (Q(1) if case=='positive' else eigen[i]) if i==j else Q(0)
                error = abs(actual[i][j]-expected)
                max_error = max(max_error,error)
                require(error < Q(1,1 << 35),'full exact manufactured congruence control failed')
                entries += 1
    require(source_entries==36 and entries==18 and stages==6,'incomplete finite control traversal')
    return {'case':case,'source_entries_checked':source_entries,'transform_entries_checked':entries,
            'owned_stages_cleanup_verified':stages,'observed_owned_peak_bytes':peak,
            'maximum_backsolve_residual':max_residual,'maximum_congruence_error':max_error,
            'scope':'FINITE_MANUFACTURED_MATRIX_CONTROL_ONLY','matrix_positivity_claim':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--positive-input',type=Path,required=True)
    parser.add_argument('--positive-run',type=Path,required=True)
    parser.add_argument('--signed-input',type=Path,required=True)
    parser.add_argument('--signed-run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    require(not args.output.exists(),'fresh control verification output required')
    results = [check_case(args.positive_input,args.positive_run,'positive'),
               check_case(args.signed_input,args.signed_run,'signed')]
    result = {'status':'PASS_EXACT_RETAINED_NONPROOF_PROPOSAL_CONTROLS','cases':results,
              'scope':'READ_ONLY_FINITE_CONTROL_EVIDENCE','fresh_native_reconstruction':False,
              'full_supported_proposal':False,'matrix_positivity':False,'production_admission':False}
    with args.output.open('xb') as stream:
        stream.write(canonical_bytes(result))
    print(json.dumps({'status':result['status'],'transform_entries_checked':36,
        'source_entries_checked':72,'owned_stages_cleanup_verified':12,
        'observed_owned_peak_bytes':max(value['observed_owned_peak_bytes'] for value in results)},sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
