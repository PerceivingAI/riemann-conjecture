"""Scalar native Bessel seed precision diagnosis, not a positivity calculation."""
import argparse,hashlib,json
from pathlib import Path
from flint import arb,ctx,fmpq
p=argparse.ArgumentParser();p.add_argument('--declaration',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
if args.output.exists():raise FileExistsError(args.output)
raw=args.declaration.read_bytes();decl=json.loads(raw);out={'format':'t080-native-bessel-seed-diagnosis-v1','declaration_sha256':hashlib.sha256(raw).hexdigest(),'probe_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'profiles':{}}
for precision in (3072,4096):
    ctx.prec=precision;rows=[]
    for edge in decl['frequency_edges'][1:]:
        c=arb(fmpq(4,5)*fmpq(edge));values=[]
        for n in (644,645):
            seed=c.bessel_j(arb(fmpq(2*n+1,2)))*(arb.pi()/(2*c)).sqrt()
            values.append({'mode':n,'relative_bits':seed.rel_accuracy_bits(),'absolute_radius_upper':str(seed.rad().upper().fmpq()),'finite':seed.is_finite()})
        rows.append({'edge':edge,'seeds':values})
    out['profiles'][str(precision)]=rows
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n',encoding='utf-8')
for precision,rows in out['profiles'].items():
    bad=[{'edge':r['edge'],'minimum_seed_bits':min(v['relative_bits'] for v in r['seeds'])} for r in rows if any(v['relative_bits']<2048 for v in r['seeds'])]
    print(json.dumps({'precision':precision,'failed_guard_anchors':bad,'minimum_seed_bits':min(v['relative_bits'] for r in rows for v in r['seeds'])}))
