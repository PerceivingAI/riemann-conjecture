"""Isolated exact-source reproduction and actual invalid-math rejection checks."""
import argparse,datetime,hashlib,json,os,subprocess,sys,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--capture',type=Path,required=True);p.add_argument('--data',type=Path,required=True);a=p.parse_args();root=Path.cwd();here=Path(__file__).resolve().parent;rel=here.relative_to(root);py=Path(sys.executable).relative_to(root).as_posix();data=a.data

def run(label,argv,expected=0):
    target=data/(label+'.run.json')
    if target.exists():raise ValueError('fresh receipt required')
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic();r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    target.write_text(json.dumps({'started':started,'argv':argv,'exit_code':r.returncode,'elapsed_seconds':time.monotonic()-t,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n',encoding='utf-8')
    if r.returncode!=expected:raise ValueError(label+' unexpected exit '+str(r.returncode))
    print(json.dumps({'operation':label,'exit_code':r.returncode}),flush=True)

def cap(name):return (a.capture/rel/name).as_posix()
replays=[]
for v in (1,2):
    source=data/f'isolated-floor-assessment-v{v}.json';audit=data/f'isolated-floor-audit-v{v}.json'
    run(f'isolated-source-v{v}',[py,'-I','-B',cap(f'assess-low-floor-v{v}.py'),cap(f'data/low-proposal-v{v}.json'),'--output',source.as_posix()])
    run(f'isolated-audit-v{v}',[py,'-I','-B',cap('verify-low-floor-v1.py'),source.as_posix(),'--output',audit.as_posix()])
    for role,orig,new in [('source',data/f'floor-assessment-v{v}.json',source),('audit',data/f'independent-floor-audit-v{v}.json',audit)]:
        if orig.read_bytes()!=new.read_bytes():raise ValueError('isolated scientific bytes differ')
        replays.append({'variant':v,'role':role,'sha256':hashlib.sha256(orig.read_bytes()).hexdigest(),'byte_identical':True})
(data/'replay-summary.json').write_text(json.dumps(replays,indent=2)+'\n',encoding='utf-8')
rejections=[]
for label in ['false-physical-mass','unpaid-complete-exterior','fabricated-completion-margin']:
    packet=json.loads((data/'floor-assessment-v2.json').read_text(encoding='utf-8'))
    if label=='false-physical-mass':packet['witnesses'][0]['exact_mass']='2'
    elif label=='unpaid-complete-exterior':packet['witnesses'][0]['complete_exterior_used_upper']='0'
    else:packet['witnesses'][0]['norm_completion_rayleigh_upper']='-1'
    fixture=data/(label+'.json');out=data/(label+'-must-not-exist.json')
    with fixture.open('x',encoding='utf-8') as f:json.dump(packet,f,sort_keys=True,indent=2);f.write('\n')
    run(label,[py,'-I','-B',cap('verify-low-floor-v1.py'),fixture.as_posix(),'--output',out.as_posix()],1)
    if out.exists():raise ValueError('invalid mathematical packet wrote success output')
    rejections.append({'case':label,'packet_sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),'exit_code':1,'success_output_exists':False})
(data/'rejection-summary.json').write_text(json.dumps(rejections,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS_BOTH_EXACT_VERSIONS_ISOLATED_AND_THREE_FALSE_BOUND_REJECTIONS','replays':replays,'rejections':3}))
