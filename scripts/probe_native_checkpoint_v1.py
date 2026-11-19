"""Contained native preparation, enclosure and transport observations.

Restricted scientific values and synthetic ownership/I/O controls only. No full
matrix, target positivity or production theorem admission is computed here.
"""
from __future__ import annotations
import argparse, contextlib, gc, gzip, hashlib, importlib.util, json, math, os
from pathlib import Path
import random, subprocess, sys, tempfile, time
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'computations/2026-10-28T034134Z-t081-resource-execution'
sys.path.insert(0,str(BASE))
from resource_limits_v1 import windows_resource_snapshot
from flint import arb, arb_mat, ctx, fmpq, fmpq_poly
PHASES=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def snap():return windows_resource_snapshot()['process'] if os.name=='nt' else {'unmeasured_platform':sys.platform}
def emit(name,**kw):print('T081_EVENT '+json.dumps({'event':'work','phase':name,**kw}),flush=True)
@contextlib.contextmanager
def phase(name):
    before=snap();w,c=time.monotonic(),time.process_time();emit(name,completed=0,total=1)
    try:yield
    finally:
        PHASES.append({'phase':name,'wall_seconds':time.monotonic()-w,'cpu_seconds':time.process_time()-c,'before':before,'after':snap()})
        emit(name,completed=1,total=1)
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);out=importlib.util.module_from_spec(spec);sys.modules[name]=out;spec.loader.exec_module(out);return out
def publish(x,bits):
    if not x.is_finite():raise ValueError('nonfinite enclosure')
    scale=1<<bits
    return [int((x.lower().fmpq()*scale).floor())-1,int((x.upper().fmpq()*scale).ceil())+1]
def restore(pair,bits):
    lo,hi=pair;scale=1<<bits
    if lo>hi:raise ValueError('reversed enclosure')
    return arb(fmpq(lo+hi,2*scale),arb(fmpq(hi-lo,2*scale)))
def inside(x,pair,bits=256):
    return fmpq(pair[0],1<<bits)<=x.lower().fmpq()<=x.upper().fmpq()<=fmpq(pair[1],1<<bits)
def recurrence(x,modes):
    wanted=set(modes);out={};previous,current=arb(1),x
    if 0 in wanted:out[0]=previous
    if 1 in wanted:out[1]=current
    for n in range(1,max(modes)):
        following=((2*n+1)*x*current-n*previous)/(n+1)
        previous,current=current,following
        if n+1 in wanted:out[n+1]=current
    return out

def prepare(cfg):
    M=cfg['extent'];n=M-1;ctx.prec=cfg['audit_bits']
    helper=module(BASE/'verify-whole-source-v2.py','bounded_independent_basis')
    with phase('stream_exact_three_term_basis'):
        previous,current=fmpq_poly([1]),fmpq_poly([0,1]);x=fmpq_poly([0,1])
        for k in range(1,n):
            following=((2*k+1)*x*current-k*previous)*fmpq(1,k+1)
            previous,current=current,following
        last=current;del previous,following
    with phase('independent_highest_Rodrigues'):
        independent=helper.rodrigues(n)
        if last!=independent:raise ValueError('highest exact basis mismatch')
    with phase('one_highest_native_coefficient_batch'):
        coeff=[arb(c) for c in independent.coeffs()]
        native=arb_mat([coeff]);observed=snap()
        max_bits=max(int(abs(independent[i].p).bit_length()) for i in range(n+1))
        del coeff,native
    return {'scope':'one streamed complete degree range, highest independent polynomial and one coefficient row; not all-M storage','highest_degree':n,'exact_coefficients':n+1,'nonzero_coefficients':n//2+1,'maximum_reduced_numerator_bits':max_bits,'native_row_live':observed,'exact_highest_polynomial_agrees':True,'native_precision':ctx.prec}

def image_values(cfg):
    N=cfg['basis_dimension'];M=cfg['extent'];modes=[N-7,N-1];ps=cfg['source_bits'];pa=cfg['audit_bits'];q=cfg['checkpoint_bits']
    powers=[(2,2),(3,3),(4,2),(5,5),(7,7)];node_ids=[0,N//2,N-1]
    store=[];node_checks=[]
    with ctx.workprec(ps):
        terms=[(arb(m).log(),arb(p).log()/arb(m).sqrt()) for m,p in powers]
        left,right=terms[-1][0]-1,arb(1);mid=(left+right)/2;half=(right-left)/2
        with phase('selected_actual_square_roots_and_all_signed_images'):
            for j in node_ids:
                root,weight=arb.legendre_p_root(N,j,weight=True);x=mid+half*root
                images=[arb(0) for _ in modes];active=[]
                for (m,p),(tau,c) in zip(powers,terms):
                    if not arb(-1)<x-tau<arb(1) or not x+tau>1:raise ValueError('strict last-cell topology')
                    vals=recurrence(x-tau,modes);active.append(m)
                    for k,n in enumerate(modes):images[k]-=c*vals[n]
                pairs=[publish(z,q) for z in images]
                restored=[restore(z,q) for z in pairs]
                grams=[publish(half*weight*restored[i]*restored[k],256) for i,k in ((0,0),(0,1),(1,1))]
                store.append({'node':j,'image_pairs_hex':[[hex(v) for v in z] for z in pairs],'partial_Gram_pairs_hex':[[hex(v) for v in z] for z in grams]})
                node_checks.append((pairs,grams))
        # Distinct q=8346 window: highest represented head value, not a full quadrature.
        with phase('selected_arithmetic_order_root_highest_head'):
            root,weight=arb.legendre_p_root(cfg['source_gauss_order'],cfg['source_gauss_order']//2,weight=True)
            tau=terms[0][0];xx=-tau/2+(1-tau/2)*root
            head=recurrence(xx,[M-1])[M-1];head_pair=publish(head,q)
    wrong=0;independent_checks=0
    with ctx.workprec(pa):
        with phase('independent_selected_images_and_checkpoint_containment'):
            terms=[(arb(m).log(),arb(p).log()/arb(m).sqrt()) for m,p in powers]
            left,right=terms[-1][0]-1,arb(1);mid=(left+right)/2;half=(right-left)/2
            for index,j in enumerate(node_ids):
                root,weight=arb.legendre_p_root(N,j,weight=True);x=mid+half*root
                contributions=[[-c*(x-tau).legendre_p(n) for n in modes] for tau,c in terms]
                images=[sum((z[k] for z in contributions),arb(0)) for k in range(len(modes))]
                pairs,grams=node_checks[index]
                for value,pair in zip(images,pairs):
                    if not inside(value,pair,q):raise ValueError('image checkpoint containment')
                    independent_checks+=1
                for v,(i,k) in enumerate(((0,0),(0,1),(1,1))):
                    if not inside(half*weight*images[i]*images[k],grams[v]):raise ValueError('partial signed Gram containment')
                    independent_checks+=1
                bad=half*weight*(images[-1]-contributions[-1][-1])**2
                if not inside(bad,grams[-1]):wrong+=1
            root,weight=arb.legendre_p_root(cfg['source_gauss_order'],cfg['source_gauss_order']//2,weight=True)
            tau=terms[0][0];xx=-tau/2+(1-tau/2)*root
            if not inside(xx.legendre_p(M-1),head_pair,q):raise ValueError('highest head checkpoint containment')
            independent_checks+=1
    if wrong==0:raise ValueError('prime7 omission control inconclusive')
    # A checkpoint-rounding-only uniform bound, not a bound on native/input widths.
    decl=json.loads((ROOT/cfg['bindings']['declaration']['path']).read_bytes())
    S=sum((2*Fraction(t['coefficient']['upper']) for t in decl['active_terms']),Fraction(0));e=Fraction(2,1<<q)
    per_entry=2*(2*S*e+e*e);d=N//2;minmass=Fraction(2,2*N-1)
    bound=d*per_entry/minmass
    return {'scope':'last translation cell, three selected q=N nodes, complete active signed image and selected head value; not complete quadrature/Gram','native_precisions':[ps,pa],'checkpoint_bits':q,'input_modes':modes,'highest_head_mode':M-1,'node_ids':node_ids,'active_powers':[m for m,p in powers],'inactive_opposite_shifts':5,'checked_enclosures':independent_checks,'prime7_omission_rejected_nodes':wrong,'values':store,'checkpoint_only_full_Psquare_physical_rounding_bound':str(bound),'checkpoint_only_bound_below_goal':bound<Fraction(1,1<<80),'all_native_widths_or_full_target_goal_checked':False}

def frequency(cfg):
    source=module(BASE/'build-whole-source-v4.py','bounded_downward_source')
    decl=json.loads((ROOT/cfg['bindings']['declaration']['path']).read_bytes());edges=decl['frequency']['edges'];weights=[fmpq(x) for x in decl['frequency']['inverse_weight_step_uppers']]
    anchors=[1,len(edges)//2,len(edges)-1];M=cfg['extent'];a,b=M-3,M-1;q=cfg['checkpoint_bits'];pairs=[];values=[]
    def band(js,c):
        da=a/c*js[a]-js[a+1];db=b/c*js[b]-js[b+1]
        return 4/arb.pi()*((-1)**((b-a)//2))*c*c*(db*js[a]-da*js[b])/(b*(b+1)-a*(a+1))
    with ctx.workprec(cfg['source_bits']):
        prefix=arb(0)
        for j in anchors:
            with phase('downward_anchor_'+str(j)):
                c=arb(fmpq(edges[j]));js=source.bessel(c,M);v=band(js,c)*arb(weights[j-1]-weights[j]);pair=publish(v,q);pairs.append(pair);prefix+=restore(pair,q);del js
        published=publish(prefix,256)
    with ctx.workprec(cfg['audit_bits']):
        prefix=arb(0)
        for ix,j in enumerate(anchors):
            with phase('upward_anchor_'+str(j)):
                c=arb(fmpq(edges[j]));sine,cosine=c.sin(),c.cos();js=[sine/c,(sine-c*cosine)/(c*c)]
                for n in range(1,M):js.append((2*n+1)/c*js[-1]-js[-2])
                v=band(js,c)*arb(weights[j-1]-weights[j]);del js
                if not inside(v,pairs[ix],q):raise ValueError('independent band checkpoint containment at '+str(j))
                prefix+=v;values.append({'anchor_index':j,'omega':edges[j],'checkpoint_pair_hex':[hex(z) for z in pairs[ix]],'checkpoint_grid_width':pairs[ix][1]-pairs[ix][0]})
        if not inside(prefix,published):raise ValueError('band prefix publication containment')
    return {'scope':'three actual anchors, full M recurrence, one highest offdiagonal band entry; not full kernel/59-anchor sum/diagonal/terminal check','modes':[a,b],'native_precisions':[cfg['source_bits'],cfg['audit_bits']],'anchors':values,'checked_enclosures':4,'prefix_publication_hex':[hex(x) for x in published],'complete_frequency_domain_checked':False}

def transport(cfg,out):
    rng=random.Random(cfg['seed']);count=65536;rows=[]
    with tempfile.TemporaryDirectory(prefix='transport-',dir=out.parent) as td:
        path=Path(td)/'intervals.jsonl.gz'
        with phase('encode_compress_fsync_chunk'):
            for _ in range(count):
                x=rng.getrandbits(512);x=-x if rng.getrandbits(1) else x;rows.append((x,x+4))
            raw=b''.join((json.dumps([hex(a),hex(b)],separators=(',',':'))+'\n').encode() for a,b in rows)
            compressed=gzip.compress(raw,mtime=0)
            with path.open('xb') as f:f.write(compressed);f.flush();os.fsync(f.fileno())
        reads=[]
        for label in ('first_uncontrolled_cache_read','repeat_warm_read'):
            with phase(label):
                data=path.read_bytes();digest=hashlib.sha256(data).hexdigest();decoded=gzip.decompress(data)
                parsed=[tuple(int(s,16) for s in json.loads(line)) for line in decoded.splitlines()]
                if parsed!=rows:raise ValueError('exact chunk roundtrip')
                reads.append({'kind':label,'compressed_sha256':digest,'records':len(parsed)})
                del parsed,decoded,data
        with phase('corrupt_transport_control'):
            bad=bytearray(compressed);bad[-8]^=1
            try:gzip.decompress(bad)
            except (gzip.BadGzipFile,EOFError):rejected=True
            else:raise ValueError('corrupt CRC accepted')
        result={'scope':'synthetic high-entropy endpoints with narrow paired widths, not target compression/cold storage','records':count,'grid':512,'raw_bytes':len(raw),'compressed_bytes':len(compressed),'reads':reads,'corrupt_CRC_rejected':rejected,'scratch_removed_after_scope':True}
    return result

def child(cfg,out):
    ctx.prec=cfg['audit_bits'];ctx.threads=1;n=256
    before=snap();matrix=arb_mat(n,n);v=arb(1)/3
    for i in range(n):
        for j in range(n):matrix[i,j]=v
    live=snap();print('CHILD_READY '+json.dumps({'pid':os.getpid(),'before':before,'live':live}),flush=True)
    if sys.stdin.readline().strip()!='GO':raise ValueError('child overlap gate')
    value=sum((matrix[0,j] for j in range(n)),arb(0))
    if not value.contains(fmpq(n,3)):raise ValueError('native child row result')
    return {'scope':'native copied scalar allocation, not scientific matrix','pid':os.getpid(),'shape':[n,n],'precision':ctx.prec,'native_threads':ctx.threads,'live':live,'row_contains_exact_value':True}

def aggregate(cfg,out,inputs):
    count=min(2,int(os.environ.get('BOUNDED_CPU_BUDGET','1')));children=[];ready=[];reports=[]
    with tempfile.TemporaryDirectory(prefix='children-',dir=out.parent) as td:
        try:
            with phase('simultaneous_owned_native_children'):
                for i in range(count):
                    target=Path(td)/('child-'+str(i)+'.json')
                    p=subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'--mode','child','--inputs',str(inputs.resolve()),'--output',str(target)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
                    children.append((p,target))
                for p,target in children:
                    line=p.stdout.readline()
                    if not line.startswith('CHILD_READY '):raise ValueError('child failed before live overlap '+line)
                    ready.append(json.loads(line[len('CHILD_READY '):]))
                parent_live=snap();emit('children_live',children=count,parent=parent_live)
                for p,target in children:p.stdin.write('GO\n');p.stdin.flush();p.stdin.close();p.stdin=None
                for p,target in children:
                    stdout,stderr=p.communicate(timeout=60)
                    if p.returncode!=0:raise RuntimeError('native child exit '+str(p.returncode)+' '+stderr)
                    reports.append(json.loads(target.read_bytes()))
        finally:
            for p,target in children:
                if p.poll() is None:p.kill()
                p.wait()
    return {'scope':'one top-level owned stage with inherited numerical descendants, not production multiworker scheduler','children':count,'two_child_conclusion_exercised':count==2,'ready':ready,'parent_live':parent_live,'child_reports':reports,'owned_child_processes_reaped':all(p.returncode==0 for p,target in children)}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mode',choices=['prepare','images','frequency','transport','aggregate','child'],required=True);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    cfg=json.loads(args.inputs.read_bytes())
    for b in cfg['bindings'].values():
        if sha(ROOT/b['path'])!=b['sha256']:raise ValueError('changed dependency '+b['path'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    before=snap();w,c=time.monotonic(),time.process_time()
    funcs={'prepare':prepare,'images':image_values,'frequency':frequency}
    if args.mode in funcs:details=funcs[args.mode](cfg)
    elif args.mode=='transport':details=transport(cfg,args.output)
    elif args.mode=='aggregate':details=aggregate(cfg,args.output,args.inputs)
    else:details=child(cfg,args.output)
    result={'format':'bounded-native-observations-v1','mode':args.mode,'status':'PASS_RESTRICTED_OBSERVATION_ONLY','inputs_sha256':sha(args.inputs),'program_sha256':sha(__file__),'wall_seconds':time.monotonic()-w,'cpu_seconds':time.process_time()-c,'before':before,'after':snap(),'native_threads':ctx.threads,'phases':PHASES,'details':details,'full_target_matrices_computed':False,'target_positivity_proved':False,'production_admission':False}
    with args.output.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    emit('complete',mode=args.mode,wall_seconds=result['wall_seconds'])
    return 0
if __name__=='__main__':raise SystemExit(main())
