"""Actual captured-source replay and false-mathematics rejection checks."""
import argparse,datetime,hashlib,json,os,subprocess,sys,time
from pathlib import Path
from flint import fmpq
p=argparse.ArgumentParser();p.add_argument('--capture',type=Path,required=True);p.add_argument('--data',type=Path,required=True);a=p.parse_args();root=Path.cwd();here=Path(__file__).resolve().parent;rel=here.relative_to(root);py=Path(sys.executable).relative_to(root).as_posix();data=a.data

def run(label,argv,expected=0):
    target=data/(label+'.run.json')
    if target.exists():raise ValueError('fresh receipt required')
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic();r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    target.write_text(json.dumps({'started':started,'argv':argv,'exit_code':r.returncode,'elapsed_seconds':time.monotonic()-t,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n',encoding='utf-8')
    if r.returncode!=expected:raise ValueError(label+' unexpected exit '+str(r.returncode))
    print(json.dumps({'operation':label,'exit_code':r.returncode}),flush=True)

def cap(name):return (a.capture/rel/name).as_posix()
source=data/'isolated-structured-source-v1.json';audit=data/'isolated-audit-v1.json'
run('isolated-source',[py,'-I','-B',cap('qualify-structured-v1.py'),'--output',source.as_posix()])
run('isolated-audit',[py,'-I','-B',cap('verify-structured-v1.py'),source.as_posix(),'--output',audit.as_posix()])
replays=[]
for role,old,new in [('source',data/'structured-source-v1.json',source),('audit',data/'independent-audit-v1.json',audit)]:
    if old.read_bytes()!=new.read_bytes():raise ValueError(role+' isolated bytes differ')
    replays.append({'role':role,'sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'byte_identical':True})
(data/'replay-summary.json').write_text(json.dumps(replays,indent=2)+'\n',encoding='utf-8')
rejections=[]
for label in ['altered-signed-band-entry','unpaid-infinite-remainder','forged-whole-low-error']:
    obj=json.loads((data/'structured-source-v1.json').read_text(encoding='utf-8'))
    if label=='altered-signed-band-entry':obj['coefficient_map'][0][0]=str(fmpq(obj['coefficient_map'][0][0])+fmpq(1,2**40))
    elif label=='unpaid-infinite-remainder':obj['complete_remainder_upper']='0'
    else:obj['complete_model_error_upper']='0'
    fixture=data/(label+'.json');out=data/(label+'-must-not-exist.json')
    with fixture.open('x',encoding='utf-8') as f:json.dump(obj,f,sort_keys=True,indent=2);f.write('\n')
    run(label,[py,'-I','-B',cap('verify-structured-v1.py'),fixture.as_posix(),'--output',out.as_posix()],1)
    if out.exists():raise ValueError('false mathematical input wrote success output')
    rejections.append({'case':label,'input_sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),'exit_code':1,'success_output_exists':False})
(data/'rejection-summary.json').write_text(json.dumps(rejections,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS_ISOLATED_SCIENTIFIC_BYTES_AND_THREE_REAL_REJECTIONS','replays':replays,'rejections':3}))
