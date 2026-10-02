from pathlib import Path
from fractions import Fraction as Q
import sys,json,zipfile,hashlib,time,functools
from contextlib import ExitStack
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from scripts import weil_multi_prime_continuation_driver
from scripts.cert import exact_prime_schur_common as exact
from scripts.cert.matrices import RationalInterval as RI
from scripts.profile_multi_prime_assembly import _peak_memory_bytes
OUT=Path(__file__).parent

def main():
    results=[]
    for n in (192,196):
        source=OUT/f"phase11-candidate-inputs-N{n}-p512-m104-w56.zip"
        with zipfile.ZipFile(source) as archive: proof=json.loads(archive.read("candidate-inputs.json"))
        assert proof["status"]=="WITNESS_FAILED" and proof["dimension"]==n and proof["matrix_bits"]==104
        mu=Q(proof["mu_lower"]);assert mu>0
        matrices={}
        for name in ("A","GV","GP","GR"):
            values=[[None]*n for _ in range(n)]
            for item in proof["matrices"][name]["entries"]:
                values[item["row"]][item["col"]]=RI(Q(int(item["lo_num"]),int(item["lo_den"])),Q(int(item["hi_num"]),int(item["hi_den"])))
            matrices[name]=values
        indices=list(range(0,n,2))[:-1]
        block=[[matrices["A"][i][j]-(matrices["GV"][i][j]+matrices["GP"][i][j]+matrices["GR"][i][j])*(Q(3)/mu) for j in indices] for i in indices]
        stages={};row={"role":"proper_principal_block_witness_kernel_cost_only","parent_target_dimension":n,"parent_precision_bits":512,"parent_matrix_bits":104,"witness_bits":56,"block_dimension":len(block),"basis_degrees":indices,"source_archive":source.name,"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"full_target_candidate":False,"qualification_run":False,"theorem_status":False,"stage_timings_inclusive":stages}
        def install(stack,name):
            original=getattr(exact,name)
            @functools.wraps(original)
            def timed(*args,**kwargs):
                wall,cpu=time.perf_counter(),time.process_time()
                try:return original(*args,**kwargs)
                finally:
                    entry=stages.setdefault(name,{"calls":0,"wall_seconds":0.0,"cpu_seconds":0.0})
                    entry["calls"]+=1;entry["wall_seconds"]+=time.perf_counter()-wall;entry["cpu_seconds"]+=time.process_time()-cpu
            stack.enter_context(patch.object(exact,name,timed))
        wall,cpu=time.perf_counter(),time.process_time()
        try:
            with ExitStack() as stack:
                for name in ("_exact_ldl_midpoint","_inverse_lower_triangular","_round_fraction_nearest_dyadic","_exact_congruence","_gershgorin_margin"):install(stack,name)
                witness,margin=exact.make_witness(block,56)
            row.update(status="completed",strict_gershgorin_margin=str(margin),all_operations_completed=True)
        except RuntimeError as error:
            row.update(status="failed",error=str(error),all_operations_completed=False)
            witness=None
        row.update(wall_seconds=time.perf_counter()-wall,cpu_seconds=time.process_time()-cpu,peak_memory_bytes=_peak_memory_bytes())
        if witness is not None:
            filename=f"phase11-witness-kernel-N{n}-prefix{len(block)}.zip"
            with zipfile.ZipFile(OUT/filename,"w",compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("kernel-inputs-and-witness.json",json.dumps({"role":row["role"],"block":[[[str(value.lo),str(value.hi)] for value in r] for r in block],"witness":[[str(value) for value in r] for r in witness],"reported_margin":str(margin),"theorem_status":False}))
            row["replay_archive"]=filename
        results.append(row)
        (OUT/"phase11-witness-kernel-cost.json").write_text(json.dumps({"role":"local operation proxies, not successful full target candidates or runtime upper bounds","results":results},indent=2)+"\n",encoding="utf-8")
        print(f"Kernel parentN={n} prefix={len(block)} outcome={row['status']} wall={row['wall_seconds']:.3f}",flush=True)
if __name__=="__main__":main()
