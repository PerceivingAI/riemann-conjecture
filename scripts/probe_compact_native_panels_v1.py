"""Full-inner synthetic interval multiplication with exact endpoint controls."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,os,random,sys,time
from pathlib import Path
from flint import arb,arb_mat,ctx,fmpq
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'computations/2026-10-28T034134Z-t081-resource-execution';sys.path.insert(0,str(BASE))
from resource_limits_v1 import windows_resource_snapshot

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path);p.add_argument('--output-dir',type=Path);p.add_argument('--memory-mib',type=int,default=2048);args=p.parse_args()
    if args.output_dir is not None:
        if args.output_dir.exists():raise FileExistsError(args.output_dir)
        runner=module(ROOT/'computations/2026-10-29T013929Z-t1-execution-allocation/run-probes-v1.py','panel_probe_supervision')
        budget=runner.policy.resolve_resources(memory_mib=args.memory_mib,required_bytes=512*runner.policy.MIB)
        with runner.ProbeExecution(args.output_dir,budget) as execution:
            execution.run('panels',Path(__file__).resolve(),['--inputs',args.inputs.resolve(),'--output',(args.output_dir/'result.json').resolve()],kind='fixture')
        return 0
    if args.output is None:p.error('--output or --output-dir required')
    if args.output.exists():raise FileExistsError(args.output)
    cfg=json.loads(args.inputs.read_bytes())
    for b in cfg['bindings'].values():
        if hashlib.sha256((ROOT/b['path']).read_bytes()).hexdigest()!=b['sha256']:raise ValueError('changed dependency')
    ctx.prec=cfg['audit_bits'];n=cfg['source_gauss_order'];b=32;q=cfg['checkpoint_bits'];scale=1<<q;rng=random.Random(cfg['seed']);phases=[]
    def phase(name,fn):
        before=windows_resource_snapshot()['process'];w,c=time.monotonic(),time.process_time();print('T081_EVENT '+json.dumps({'event':'phase_started','phase':name}),flush=True)
        value=fn();phases.append({'phase':name,'wall_seconds':time.monotonic()-w,'cpu_seconds':time.process_time()-c,'before':before,'after':windows_resource_snapshot()['process']})
        print('T081_EVENT '+json.dumps({'event':'phase_finished','phase':name,'wall_seconds':phases[-1]['wall_seconds']}),flush=True);return value
    selected=[(0,0),(0,b-1),(b-1,0),(b-1,b-1)]
    def construct():
        A=arb_mat(b,n);B=arb_mat(n,b);aa={};bb={}
        for i in range(b):
            for k in range(n):
                z=rng.getrandbits(q);z=-z if rng.getrandbits(1) else z
                A[i,k]=arb(fmpq(z,scale),arb(fmpq(1,scale)))
                if i in (0,b-1):aa[i,k]=z
        for k in range(n):
            for j in range(b):
                z=rng.getrandbits(q);z=-z if rng.getrandbits(1) else z
                B[k,j]=arb(fmpq(z,scale),arb(fmpq(1,scale)))
                if j in (0,b-1):bb[k,j]=z
        return A,B,aa,bb
    A,B,aa,bb=phase('compact_interval_operand_construction',construct)
    C=phase('native_complete_inner_matrix_product',lambda:A*B)
    def verify():
        rows=[]
        for i,j in selected:
            lower=upper=0
            for k in range(n):
                x,y=aa[i,k],bb[k,j];products=[(x+s)*(y+t) for s in (-1,1) for t in (-1,1)]
                lower+=min(products);upper+=max(products)
            if not C[i,j].contains(fmpq(lower,scale*scale)) or not C[i,j].contains(fmpq(upper,scale*scale)):raise ArithmeticError('complete endpoint-domain enclosure mismatch')
            # Last complete inner contribution must not be silently omitted.
            midpoint=sum(aa[i,k]*bb[k,j] for k in range(n));missing=sum(aa[i,k]*bb[k,j] for k in range(n-1))
            if midpoint==missing or C[i,j].contains(fmpq(missing,scale*scale)):raise ArithmeticError('missing-final-inner control inconclusive')
            mantissa,exponent=C[i,j].mid().man_exp();rows.append({'row':i,'column':j,'midpoint_mantissa_bits':abs(int(mantissa)).bit_length(),'midpoint_exponent':int(exponent),'complete_endpoint_range_contained':True,'omitted_final_inner_rejected':True})
        return rows
    checked=phase('independent_all_inner_integer_endpoint_controls',verify)
    out={'format':'compact-operand-native-observation-v1','status':'PASS_COMPLETE_SYNTHETIC_INNER_PRODUCT','inputs_sha256':hashlib.sha256(args.inputs.read_bytes()).hexdigest(),'program_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'native_threads':ctx.threads,'native_precision':ctx.prec,'checkpoint_grid':q,'left_shape':[b,n],'right_shape':[n,b],'full_inner_count':n,'phases':phases,'checks':checked,'scope':'synthetic completed-operand intervals, not source or target conditioning','full_target_matrices_computed':False,'target_positivity_proved':False,'production_admission':False}
    with args.output.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(out,indent=2,sort_keys=True)+'\n')
    return 0
if __name__=='__main__':raise SystemExit(main())
