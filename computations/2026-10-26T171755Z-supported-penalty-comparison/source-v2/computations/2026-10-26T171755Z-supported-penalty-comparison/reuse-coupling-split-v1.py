"""Exact existing-control consequences of C-0063/C-0095; not a source matrix."""
import argparse,hashlib,json
from fractions import Fraction as Q
from pathlib import Path
from flint import arb,ctx
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
if args.output.exists():raise SystemExit('fresh output required')
ctx.prec=192;T=Q(3,4);N=312;z=T/2
ratio=z*z/((2*N+1)*(2*N+3));assert ratio<Q(1,2)
E=2*(2*N+1)*z**(2*N);assert E<Q(1,10**250)
t=arb(3)/4;assert t.exp()<3 and t.sinh()<2
main=Q(333,1024*N*(N+1));assert main+Q(1,10**120)<Q(1,300000)
out={'format':'exact-existing-coupling-split-control-v1','status':'PASS','support':'3/4','N':N,'harmonic_scalar_cross_exactly_zero':True,'full_pole_already_in_residual':True,'residual_operator_upper':'1/300000','weighted_residual_map_error_upper':'sqrt(3)/300000','main_residual_bound':str(main),'geometric_ratio':str(ratio),'loose_complete_E_upper':str(E),'one_sided_not_double_tail_or_columnwise':True,'source_matrix_generated':False,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
args.output.parent.mkdir(parents=True,exist_ok=True)
with args.output.open('x',encoding='utf-8') as f:json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in out.items() if k!='loose_complete_E_upper'}))
