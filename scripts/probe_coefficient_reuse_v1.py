"""Exact coefficient-construction observations with unchanged reference comparisons."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,sys,time
from pathlib import Path
from flint import arb,arb_mat,ctx,fmpq,fmpq_poly
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'computations/2026-10-28T034134Z-t081-resource-execution'
sys.path.insert(0,str(BASE))
from resource_limits_v1 import windows_resource_snapshot

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);out=importlib.util.module_from_spec(spec);sys.modules[name]=out;spec.loader.exec_module(out);return out

def ratio_polynomial(n):
    # Rodrigues integer coefficients A_k/2^n. The ratio follows by cancelling
    # factorials in binom(n,k)*binom(2*n-2*k,n); each division must be exact.
    coefficients=[0]*(n+1);value=math.comb(2*n,n);divisions=0
    for k in range(n//2+1):
        coefficients[n-2*k]=value
        if k<n//2:
            numerator=-value*(n-2*k)*(n-2*k-1);denominator=2*(k+1)*(2*n-2*k-1)
            value,remainder=divmod(numerator,denominator)
            if remainder:raise ArithmeticError('nonexact coefficient ratio')
            divisions+=1
    return fmpq_poly(coefficients)*fmpq(1,1<<n),divisions

def measure(name,call):
    before=windows_resource_snapshot()['process'];wall,cpu=time.monotonic(),time.process_time()
    print('T081_EVENT '+json.dumps({'event':'phase_started','phase':name}),flush=True)
    value=call();entry={'phase':name,'wall_seconds':time.monotonic()-wall,'cpu_seconds':time.process_time()-cpu,'before':before,'after':windows_resource_snapshot()['process']}
    print('T081_EVENT '+json.dumps({'event':'phase_finished','phase':name,'wall_seconds':entry['wall_seconds']}),flush=True)
    return value,entry

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path);p.add_argument('--output-dir',type=Path);p.add_argument('--memory-mib',type=int,default=2048);args=p.parse_args()
    if args.output_dir is not None:
        if args.output_dir.exists():raise FileExistsError(args.output_dir)
        runner=module(ROOT/'computations/2026-10-29T013929Z-t1-execution-allocation/run-probes-v1.py','coefficient_probe_supervision')
        budget=runner.policy.resolve_resources(memory_mib=args.memory_mib,threads=1,required_bytes=512*runner.policy.MIB)
        with runner.ProbeExecution(args.output_dir,budget) as execution:
            execution.run('coefficients',Path(__file__).resolve(),['--inputs',args.inputs.resolve(),'--output',(args.output_dir/'result.json').resolve()],kind='fixture')
        return 0
    if args.output is None:p.error('--output or --output-dir required')
    if args.output.exists():raise FileExistsError(args.output)
    config=json.loads(args.inputs.read_bytes())
    for b in config['bindings'].values():
        if hashlib.sha256((ROOT/b['path']).read_bytes()).hexdigest()!=b['sha256']:raise ValueError('changed bound dependency')
    helper=module(BASE/'verify-whole-source-v2.py','coefficient_reference_rodrigues')
    ctx.prec=config['audit_bits'];rows=[];phases=[];degrees=[0,1,2,132,config['basis_dimension']-1,config['extent']-1]
    for n in degrees:
        native,pn=measure('native_exact_'+str(n),lambda:fmpq_poly.legendre_p(n));phases.append(pn)
        (ratio,divisions),pr=measure('integer_ratio_'+str(n),lambda:ratio_polynomial(n));phases.append(pr)
        reference,po=measure('closed_Rodrigues_'+str(n),lambda:helper.rodrigues(n));phases.append(po)
        if native!=ratio or ratio!=reference:raise ArithmeticError('full exact coefficient mismatch at '+str(n))
        # Omit a genuine leading coefficient, not a metadata flag.
        bad=ratio.coeffs();bad[n]=0
        if fmpq_poly(bad)==reference:raise ArithmeticError('omitted leading coefficient not detected')
        rows.append({'degree':n,'all_coefficients_checked':n+1,'exact_integer_divisions':divisions,'native_wall_seconds':pn['wall_seconds'],'ratio_wall_seconds':pr['wall_seconds'],'closed_Rodrigues_wall_seconds':po['wall_seconds'],'all_exact_equal':True,'omitted_leading_coefficient_detected':True})
        if n==degrees[-1]:
            def convert():
                values=[arb(c) for c in ratio.coeffs()]
                if not all(x.is_exact() for x in values):raise ArithmeticError('nonexact dyadic conversion')
                matrix=arb_mat([values]);return windows_resource_snapshot()['process']
            native_row,pc=measure('highest_exact_native_conversion',convert);phases.append(pc)
        del native,ratio,reference,bad
    out={'format':'exact-coefficient-observations-v1','status':'PASS_EXACT_SELECTED_COEFFICIENTS','inputs_sha256':hashlib.sha256(args.inputs.read_bytes()).hexdigest(),'program_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'native_threads':ctx.threads,'precision':ctx.prec,'rows':rows,'phases':phases,'highest_native_row_live':native_row,'scope':'exact selected full coefficient domains; not complete source, global resource or target conditioning','target_positivity_proved':False,'full_target_matrices_computed':False,'production_admission':False}
    with args.output.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(out,indent=2,sort_keys=True)+'\n')
    return 0
if __name__=='__main__':raise SystemExit(main())
