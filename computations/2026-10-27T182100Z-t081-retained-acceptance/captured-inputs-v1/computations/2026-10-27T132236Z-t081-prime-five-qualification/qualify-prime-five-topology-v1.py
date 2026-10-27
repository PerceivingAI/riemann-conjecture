"""Four-mode compressed-operator qualification; not the complete target calculation."""
from __future__ import annotations
import argparse,hashlib,json,sys
from fractions import Fraction as Q
from pathlib import Path
from flint import arb,ctx
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.legendre_schur import legendre_polynomials
from scripts.cert.prime_power_terms import assemble_active_prime_power_operator,assemble_combined_prime_power_operator,_exact_polynomials
from scripts.cert.mixed_gram_research import _mixed_by_shifts
BITS=192
def rounded(x):
    lower, upper = arb_to_rational_enclosure(x)
    magnitude = max(abs(lower), abs(upper))
    exponent = magnitude.numerator.bit_length() - magnitude.denominator.bit_length() if magnitude else 0
    scale = 1 << max(0, BITS - exponent)
    return Q((lower * scale).__floor__(), scale), Q((upper * scale).__ceil__(), scale)


def enclosure(x):
    lower, upper = rounded(x)
    return {"lower": str(lower), "upper": str(upper)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module_bindings():
    files, namespaces = {}, {}
    for name, module in sorted(sys.modules.items()):
        if name == "scripts" or name.startswith("scripts."):
            if getattr(module, "__file__", None) is None:
                namespaces[name] = sorted({Path(p).resolve().relative_to(ROOT).as_posix()
                                           for p in module.__path__})
            else:
                path = Path(module.__file__).resolve()
                files[path.relative_to(ROOT).as_posix()] = sha(path)
    return files, namespaces



def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('inputs','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    raw=args.inputs.read_bytes();inputs=json.loads(raw)
    expected={'format':'t081-prime-five-topology-inputs-v1','support':'81/100','diagnostic_dimension':4,'producer_precision_bits':512,'independent_precision_bits':768,'publication_bits':192,'full_target_low_coupling_matrix_permitted':False,'production_admission':False}
    if inputs!=expected:raise ValueError('not declared diagnostic inputs')
    ctx.prec=512
    polys=legendre_polynomials(3)
    combined=assemble_active_prime_power_operator(polys,81,100,prec=512)
    terms=combined.terms
    if [term.m for term in terms]!=[2,3,4,5]:raise ValueError('active powers changed')
    vp=_mixed_by_shifts(_exact_polynomials(polys),(),terms,potential=True)
    pv=[[vp[j][i] for j in range(4)] for i in range(4)]
    only5=assemble_combined_prime_power_operator(polys,(terms[3],),prec=512)
    mixed=[]
    for term in terms[:3]:
        older=assemble_combined_prime_power_operator(polys,(term,),prec=512)
        pair=assemble_combined_prime_power_operator(polys,(term,terms[3]),prec=512)
        value=pair.p_squared_matrix[0][0]-older.p_squared_matrix[0][0]-only5.p_squared_matrix[0][0]
        if not value>0:raise ValueError('mixed constant-mode contribution unresolved')
        mixed.append({'m':term.m,'value':enclosure(value)})
    matrices={'P':combined.p_matrix,'P_squared':combined.p_squared_matrix,'GP':combined.g_p,'VP':vp,'PV':pv}
    modules,_=module_bindings()
    result={'format':'t081-prime-five-topology-qualification-v1','support':'81/100','diagnostic_dimension':4,'producer_precision_bits':512,'publication_bits':192,
            'active_terms':[{'m':x.m,'prime':x.prime,'exponent':x.exponent,'tau':enclosure(x.tau),'coefficient':enclosure(x.coefficient)} for x in terms],
            'breakpoints':[enclosure(x) for x in combined.breakpoints],
            'matrices':{key:[[enclosure(x) for x in row] for row in mat] for key,mat in matrices.items()},
            'prime5_mixed_square_constant_mode':mixed,'new_edge_width_mapped':enclosure(2-terms[3].tau),
            'new_edge_width_physical':enclosure(arb(81)/50-arb(5).log()),
            'inputs_sha256':hashlib.sha256(raw).hexdigest(),'producer_sha256':sha(Path(__file__)),
            'imported_project_module_sha256':modules,'diagnostic_only':True,'full_target_low_coupling_matrix_computed':False,
            'target_positivity_proved':False,'production_admission':False}
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:handle.write(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':'FOUR_MODE_DIAGNOSTIC_ONLY','active_terms':[x.m for x in terms],'translation_cells':len(combined.breakpoints)-1,'mixed_prime5_pairs':len(mixed)}))
if __name__=='__main__':main()
