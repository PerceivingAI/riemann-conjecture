"""Real false mathematical input controls for the independent full-source audit."""
import argparse,copy,gzip,hashlib,json,subprocess,sys,time
from pathlib import Path
from flint import fmpq
HERE=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    source=json.loads((HERE/'data/whole-source-v4.json').read_text());folder=HERE/'data/false-whole-v1';folder.mkdir(exist_ok=False)
    candidates=[]
    low=copy.deepcopy(source);key='A_model-0';payload=json.loads(gzip.decompress((HERE/low['matrices'][key]['path']).read_bytes()))
    payload['upper_triangle'][0]=[x+(1<<192) for x in payload['upper_triangle'][0]]
    candidates.append(('false_actual_low_constant',low,key,payload,'source enclosure fails at A_model-0 cell (0, 0)'))
    tail=copy.deepcopy(source);key='weighted_complete_tail-0';payload=json.loads(gzip.decompress((HERE/tail['matrices'][key]['path']).read_bytes()))
    payload['upper_triangle']=[[-1,1] for _ in payload['upper_triangle']]
    candidates.append(('discard_infinite_signed_VP_tail',tail,key,payload,'source enclosure fails at weighted_complete_tail-0 cell (0, 0)'))
    frequency=copy.deepcopy(source);frequency['inverse_weight_uppers'][-1]=str(fmpq(frequency['inverse_weight_uppers'][-1])/2)
    candidates.append(('underpay_frequency_exterior',frequency,None,None,'inverse step weight underpays anchor 8192'))
    results=[]
    for name,candidate,key,payload,error in candidates:
        if payload is not None:
            raw=gzip.compress((json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0);path=folder/(name+'.json.gz');path.write_bytes(raw)
            candidate['matrices'][key]={'path':path.relative_to(HERE).as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)}
        packet=folder/(name+'.json');packet.write_text(json.dumps(candidate,sort_keys=True,indent=2)+'\n');audit=folder/(name+'.audit.json')
        argv=[sys.executable,'-B',str(HERE/'verify-whole-v1.py'),'--source',str(packet),'--output',str(audit)];start=time.perf_counter();proc=subprocess.run(argv,text=True,capture_output=True)
        if not audit.exists():raise ValueError('missing real rejection output '+name+' '+proc.stderr[-2000:])
        result=json.loads(audit.read_text())
        if proc.returncode!=1 or result['status']!='REJECT_COMPLETE_SOURCE' or error not in result['error']:raise ValueError('wrong mathematical rejection '+name+' '+str(result))
        receipt={'name':name,'argv':argv,'exit_code':proc.returncode,'elapsed_seconds':time.perf_counter()-start,'stdout':proc.stdout,'stderr':proc.stderr,'packet_sha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'expected_mathematical_error':error,'observed_error':result['error'],'success_claim_emitted':False}
        (folder/(name+'.run.json')).write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');results.append({'name':name,'exit_code':proc.returncode,'mathematical_rejection':True,'error':result['error']})
        print(name,'REJECTED_MATHEMATICALLY',flush=True)
    args.output.write_text(json.dumps({'format':'whole-source-negative-controls-v1','status':'PASS_THREE_MATHEMATICAL_REJECTIONS','cases':results,'hash_and_schema_shortcuts_used':False},sort_keys=True,indent=2)+'\n')
if __name__=='__main__':main()
