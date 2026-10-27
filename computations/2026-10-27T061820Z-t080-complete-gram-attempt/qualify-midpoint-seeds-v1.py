"""Qualify exact-midpoint spherical Bessel seeds with paid input uncertainty."""
import argparse,hashlib,json
from pathlib import Path
from flint import arb,ctx,fmpq
p=argparse.ArgumentParser();p.add_argument('--declaration',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
if args.output.exists():raise FileExistsError(args.output)
raw=args.declaration.read_bytes();decl=json.loads(raw);rows=[]
for edge in decl['frequency_edges'][1:]:
    values=[]
    for n in (644,645):
        ctx.prec=3072;c=arb(fmpq(4,5)*fmpq(edge));mid=c.mid()
        point=mid.bessel_j(arb(fmpq(2*n+1,2)))*(arb.pi()/(2*mid)).sqrt()
        seed=arb(point.mid(),(point.rad()+c.rad()).upper())
        ctx.prec=4096;cc=arb(fmpq(4,5)*fmpq(edge));mm=cc.mid()
        high=mm.bessel_j(arb(fmpq(2*n+1,2)))*(arb.pi()/(2*mm)).sqrt();check=arb(high.mid(),(high.rad()+cc.rad()).upper())
        contained=seed.lower().fmpq()<=check.lower().fmpq()<=check.upper().fmpq()<=seed.upper().fmpq()
        if not contained or seed.rel_accuracy_bits()<2048:raise ValueError('seed qualification failed')
        values.append({'mode':n,'relative_bits':seed.rel_accuracy_bits(),'independent_higher_precision_contained':contained})
    rows.append({'edge':edge,'seeds':values})
out={'format':'t080-native-midpoint-bessel-qualification-v1','declaration_sha256':hashlib.sha256(raw).hexdigest(),'probe_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'derivative_bound':'|j_n prime|<=1/sqrt(3(2n+1))<=1 by DLMF10.54.2, ordinary Legendre mass and Cauchy-Schwarz','source_precision':3072,'higher_precision_check':4096,'guard_2048_retained':True,'minimum_seed_bits':min(v['relative_bits'] for r in rows for v in r['seeds']),'rows':rows,'status':'PASS_ALL_118_SEEDS'}
args.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='rows'}))
