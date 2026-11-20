"""Compare complete reduced arithmetic and declared fullmode head controls."""
from pathlib import Path
import argparse
import hashlib
import importlib
import importlib.abc
import json
import sys
import time
from unittest.mock import patch


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--code-root',type=Path,required=True)
    parser.add_argument('--role',choices=('producer','analytic'),required=True)
    parser.add_argument('--implementation',choices=('scalar','panels'),required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    root=args.code_root.resolve()
    assert not args.output.exists()
    sys.path.insert(0,str(root))
    opposite='analytic' if args.role=='producer' else 'producer'
    class BlockOpposite(importlib.abc.MetaPathFinder):
        def find_spec(self,fullname,path=None,target=None):
            if fullname=='scripts.whole_source.'+opposite:
                raise RuntimeError('opposite mathematical evaluator is forbidden')
    sys.meta_path.insert(0,BlockOpposite())
    role=importlib.import_module('scripts.whole_source.'+args.role)
    from flint import arb,ctx,fmpq
    from scripts.whole_source.contract import bind_problem
    from scripts.whole_source.pipeline import math_problem,_cache_record,_native
    problem=bind_problem('retained-t081',root=root)
    model=math_problem(problem,True)
    ctx.prec=problem.arithmetic.source_bits if args.role=='producer' else problem.arithmetic.audit_bits
    ctx.threads=1
    science=hashlib.sha256()
    counters={'basis_constructions':0,'recurrence_walks':0,'kernel_tiles_consumed':0}
    basis_name='basis' if args.role=='producer' else 'rodrigues_ratio'
    basis=getattr(role,basis_name)
    def counted_basis(*values,**kwargs):
        counters['basis_constructions']+=1
        return basis(*values,**kwargs)
    def record(value):
        science.update((str(value.mid().fmpq())+':'+str(value.rad().fmpq())+'\n').encode())
    def rounded(m,n,value):
        return _native(_cache_record(m,n,value))
    def tiles(values):
        for value in values:
            counters['kernel_tiles_consumed']+=1
            yield iter(value)
    timings={}
    started=time.perf_counter_ns()
    with patch.object(role,basis_name,counted_basis):
        recurrence=getattr(role,'legendre_values',None)
        def counted_recurrence(*values,**kwargs):
            counters['recurrence_walks']+=1
            return recurrence(*values,**kwargs)
        patches=[]
        if recurrence is not None:
            patches.append(patch.object(role,'legendre_values',counted_recurrence))
        for item in patches: item.start()
        try:
            for parity in (0,1):
                inputs=list(range(parity,model.N,2))
                phase=time.perf_counter_ns()
                columns={}
                if args.implementation=='scalar':
                    columns={n:role.operator_column(model,n) for n in inputs}
                else:
                    for i in range(0,len(inputs),2):
                        columns.update(role.operator_columns(model,inputs[i:i+2]))
                timings['columns-'+str(parity)]=time.perf_counter_ns()-phase
                for n in inputs:
                    for value in columns[n]: record(value)
                    columns[n]=[rounded(m,n,value) for m,value in zip(range(parity,model.M,2),columns[n],strict=True)]
                modes=list(range(model.N+parity,model.M,2))
                kernels={}
                for index in range(len(model.frequency_edges)):
                    contribution=role.frequency_step(model,index)
                    for i,m in enumerate(modes):
                        for n in modes[i:]:
                            kernels[m,n]=kernels.get((m,n),arb(0))+contribution(m,n)
                blocks=[[(m,n,rounded(m,n,value)) for (m,n),value in kernels.items()
                         if m in rs and n in cs] for rs,cs in ((modes[:2],modes[:2]),(modes[:2],modes[2:]),(modes[2:],modes[2:]))]
                phase=time.perf_counter_ns()
                heads={n:role.head_column(model,n,columns[n]) for n in inputs}
                images={}
                if args.implementation=='scalar':
                    images={n:role.head_image(model,heads[n],tiles(blocks)) for n in inputs}
                else:
                    for i in range(0,len(inputs),2):
                        images.update(role.head_images(model,{n:heads[n] for n in inputs[i:i+2]},tiles(blocks)))
                timings['head-'+str(parity)]=time.perf_counter_ns()-phase
                for n in inputs:
                    for value in heads[n]+images[n]: record(value)
                    heads[n]=[rounded(m,n,value) for m,value in zip(modes,heads[n],strict=True)]
                    images[n]=[rounded(m,n,value) for m,value in zip(modes,images[n],strict=True)]
                phase=time.perf_counter_ns()
                for ri in range(0,len(inputs),2):
                    rows=inputs[ri:ri+2]
                    for ci in range(ri,len(inputs),2):
                        cols=inputs[ci:ci+2]
                        result=role.assemble_tile(model,rows,cols,columns)
                        for pair in sorted(result):
                            for key,value in sorted(result[pair].items()):
                                science.update(str(key).encode())
                                record(value)
                            record(role.head_pair(model,heads[pair[0]],images[pair[1]]))
                timings['final-'+str(parity)]=time.perf_counter_ns()-phase
        finally:
            for item in reversed(patches): item.stop()
    full_inputs=[]
    if args.role=='producer':
        # Declared nonzero manufactured F, not an evaluated full mathematical source.
        for n in (0,1,86,87,738,739,740,741,824,825):
            full=[arb(fmpq((i%7)-3,8)) for i in range(problem.M//2)]
            for value in role.head_column(problem,n,full): record(value)
            full_inputs.append(n)
    report={'status':'PASS_CONTROL_ONLY_NUMERICAL_REUSE','role':args.role,
        'implementation':args.implementation,'code_root':str(root),'mathematical_digest':science.hexdigest(),
        'counters':counters,'phase_wall_ns':timings,'total_wall_ns':time.perf_counter_ns()-started,
        'precision_bits':ctx.prec,'native_threads':ctx.threads,'complete_reduced_inputs':6,
        'fullmode_head_inputs':full_inputs,'fullmode_F':'MANUFACTURED_NONZERO_NOT_EVALUATED_SOURCE',
        'opposite_evaluator_blocked':True,'full_source_evaluated':False,'production_admission':False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'role':args.role,'digest':report['mathematical_digest'],
        'counters':counters},sort_keys=True))


if __name__=='__main__':
    main()
