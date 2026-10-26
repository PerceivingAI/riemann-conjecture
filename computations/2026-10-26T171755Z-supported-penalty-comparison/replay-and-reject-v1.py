"""Run frozen-source isolation and actual false-bound rejection controls."""
import argparse,datetime,gzip,hashlib,json,os,subprocess,sys,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--capture',type=Path,required=True);p.add_argument('--data',type=Path,required=True);a=p.parse_args()
root=Path.cwd();here=Path(__file__).resolve().parent;rel=here.relative_to(root);py=Path(sys.executable).relative_to(root).as_posix();data=a.data

def run(label,argv,expected=0):
    receipt=data/(label+'.run.json')
    if receipt.exists():raise ValueError('fresh receipt required')
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic();r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    receipt.write_text(json.dumps({'started':started,'argv':argv,'exit_code':r.returncode,'elapsed_seconds':time.monotonic()-t,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n',encoding='utf-8')
    if r.returncode!=expected:raise ValueError(label+' unexpected exit '+str(r.returncode))
    print(json.dumps({'operation':label,'exit_code':r.returncode}),flush=True)

def captured(name):return (a.capture/rel/name).as_posix()
source=data/'isolated-comparison-v1.json.gz';audit=data/'isolated-audit-v3.json';reuse=data/'isolated-reuse-v1.json'
run('isolated-source',[py,'-I','-B',captured('compare-supported-v1.py'),'--output',source.as_posix()])
run('isolated-audit',[py,'-I','-B',captured('verify-comparison-v3.py'),source.as_posix(),'--output',audit.as_posix()])
run('isolated-reuse',[py,'-I','-B',captured('reuse-coupling-split-v1.py'),'--output',reuse.as_posix()])
replays=[]
for name,orig,new in [('source',data/'comparison-v1.json.gz',source),('audit',data/'independent-audit-v3.json',audit),('reuse',data/'reuse-control-v1.json',reuse)]:
    if orig.read_bytes()!=new.read_bytes():raise ValueError(name+' isolated bytes differ')
    replays.append({'role':name,'sha256':hashlib.sha256(orig.read_bytes()).hexdigest(),'byte_identical':True})
(data/'replay-summary.json').write_text(json.dumps(replays,indent=2)+'\n',encoding='utf-8')
rejections=[]
for label in ['understated-source-error','unpaid-continuum-quadrature','false-residual-work-floor']:
    packet=json.loads(gzip.decompress((data/'comparison-v1.json.gz').read_bytes()))
    if label=='understated-source-error':packet['columns'][0]['error_components']['complete_delta']={'lower':'0','upper':'0'}
    elif label=='unpaid-continuum-quadrature':packet['columns'][0]['full_continuum_quadrature_error_upper']={'lower':'0','upper':'0'}
    else:packet['source_rule_work']['degree311_minimum_M_for_individual_1_over_16']=128
    target=data/(label+'.json.gz');out=data/(label+'-must-not-exist.json')
    with target.open('xb') as f:f.write(gzip.compress((json.dumps(packet,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    run(label,[py,'-I','-B',captured('verify-comparison-v3.py'),target.as_posix(),'--output',out.as_posix()],2)
    if out.exists():raise ValueError('invalid packet produced success output')
    rejections.append({'case':label,'packet_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'exit_code':2,'success_output_exists':False})
(data/'rejection-summary.json').write_text(json.dumps(rejections,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS_ISOLATED_BYTES_AND_THREE_REAL_REJECTIONS','roles':replays,'rejections':3}))
