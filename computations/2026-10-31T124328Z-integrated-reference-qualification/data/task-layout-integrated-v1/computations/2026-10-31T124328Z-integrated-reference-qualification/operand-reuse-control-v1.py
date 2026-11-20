"""Compare real persisted panel consumers on declared signed finite controls."""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import json
import sys
from unittest.mock import patch


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--code-root',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    root,output=args.code_root.resolve(),args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(root))
    from flint import arb_mat,ctx,fmpq,fmpz_mat
    from scripts.whole_source import proposal as p,exact as e
    from scripts.whole_source.contract import canonical_bytes
    from scripts.whole_source.exact_global import mass_trace,full_modular_nonsingularity
    ctx.prec=1024
    ctx.threads=1
    counters={name:{'json_parses':0,'integer_decodes':0,'raw_reads':0,'logical_bytes_read':0} for name in ('proposal','exact')}
    science=hashlib.sha256()
    def wrappers(module,label):
        original_json,original_int,original_raw=module._json,module.decode_integer,module._raw
        def decoded(raw):
            counters[label]['json_parses']+=1
            return original_json(raw)
        def integer(*args,**kwargs):
            counters[label]['integer_decodes']+=1
            return original_int(*args,**kwargs)
        def raw(directory,ref,cap):
            counters[label]['raw_reads']+=1
            counters[label]['logical_bytes_read']+=ref.size
            return original_raw(directory,ref,cap)
        return [patch.object(module,'_json',decoded),patch.object(module,'decode_integer',integer),patch.object(module,'_raw',raw)]
    patches=wrappers(p,'proposal')+wrappers(e,'exact')
    for item in patches:item.start()
    try:
        for parity in (0,1):
            n,b=7,2
            context={'dimension':n,'panel_size':b,'parity':parity,'precision_bits':1024,
                'grid_bits':1024,'transform_bits':80,'proposal_id':'1'*64,'problem_id':'2'*64,'source_sha256':'3'*64}
            lower=[[Fraction(i+2) if i==j else Fraction((i+j)%3-1,8) if i>j else Fraction(0)
                    for j in range(n)] for i in range(n)]
            a=[[sum(lower[i][k]*lower[j][k] for k in range(n)) for j in range(n)] for i in range(n)]
            rhs=[[Fraction((i*3+j)%7-3,8) for j in range(n)] for i in range(n)]
            def panel(values,i,j):
                return arb_mat([[fmpq(x.numerator,x.denominator) for x in row[j:min(j+b,n)]]
                    for row in values[i:min(i+b,n)]])
            store=p.PanelStore(output/f'proposal-{parity}',context)
            p.blocked_cholesky(lambda i,j:panel(a,i,j),store)
            p.triangular_solve(store,lambda i,j:panel(rhs,i,j),store,'X_A')
            p.triangular_solve(store,lambda i,j:store.native(f'X_A/{i}/{j}'),store,'W',transpose=True)
            for name in sorted(store.refs):
                science.update(name.encode())
                science.update(canonical_bytes({'values':store.read(name,'interval')}))
            exact_context={'dimension':n,'panel_size':b,'parity':parity,'u':3,'endpoint_bits':12,'z_bits':8,
                'problem_id':'2'*64,'source_sha256':'3'*64,'proposal_sha256':'1'*64}
            parameters=e.paid_parameters(8,Fraction(3,2),Fraction(7,8))
            lam=Fraction(1,1024)
            exact_context['product_bits']=e.integer_bounds(exact_context,parameters,lam)['product_bits']
            transform=e.IntegerTiles(output/f'transform-{parity}',exact_context)
            for i in range(0,n,b):
                for j in range(0,n,b):
                    transform.put_values('Z',i,j,[8*(r+2) if r==c else (r+c)%3-1
                        for r in range(i,min(i+b,n)) for c in range(j,min(j+b,n))])
            class Source:
                def bounds(self,family,i,j):
                    centers={'A_model':2048,'weighted_head':16,'weighted_complete_tail':24}
                    values=[[centers[family]*(r+1) if r==c else (r+c)%5-2
                        for c in range(j,min(j+b,n))] for r in range(i,min(i+b,n))]
                    return fmpz_mat([[x-1 for x in row] for row in values]),fmpz_mat([[x+1 for x in row] for row in values])
            masses=mass_trace(n,parity,3,b,transform.tile)
            modular=full_modular_nonsingularity(n,b,transform.tile,workspace_bytes=128*1024**2)
            assert modular['nonsingular'] is True and modular['global_input_entries']==n*n
            products=e.IntegerTiles(output/f'products-{parity}',exact_context)
            result=e.integer_congruence(Source(),transform,products,parameters,masses,lam)
            def exact_wire(value):
                if isinstance(value,Fraction):return str(value)
                if isinstance(value,dict):return {k:exact_wire(v) for k,v in value.items()}
                if isinstance(value,list):return [exact_wire(v) for v in value]
                return value
            science.update(canonical_bytes(exact_wire(result)))
    finally:
        for item in reversed(patches):item.stop()
    report={'status':'PASS_CONTROL_ONLY_OPERAND_REUSE','mathematical_digest':science.hexdigest(),
        'counters':counters,'code_root':str(root),'dimension':7,'panel_size':2,'parities':[0,1],
        'native_precision_bits':1024,'native_threads':1,'source':'MANUFACTURED_INTEGER_AND_RATIONAL_CONTROL',
        'complete_global_inner_sums_and_mass':True,'physical_device_io_measured':False,
        'full_source_evaluated':False,'production_admission':False}
    (output/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'digest':report['mathematical_digest'],'counters':counters},sort_keys=True))


if __name__=='__main__':main()
