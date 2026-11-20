"""CONTROL_ONLY exact polynomial and native lifecycle workloads."""
from pathlib import Path
from fractions import Fraction
import os,subprocess,sys,time
from flint import ctx
ctx.prec=53
ctx.threads=1

def evaluate(task, staging):
    mode=task.get("mode","polynomial")
    if mode=="memory_error": raise MemoryError("owned deliberate MemoryError")
    if mode=="native_exit": os._exit(91)
    if mode=="native_denied":
        from flint import arb_mat
        value=arb_mat(40000,40000)
        raise RuntimeError("oversized native allocation unexpectedly succeeded")
    if mode=="flood":
        print("x"*200000,flush=True)
        time.sleep(60)
    if mode=="descendant":
        child=subprocess.Popen([sys.executable,"-B","-c","import time;time.sleep(60)"])
        Path(task["ready"]).write_text(str(child.pid))
    native=True
    if mode in ("native","native_wait"):
        from flint import arb_mat
        a=arb_mat([[1,2],[3,4]])
        b=a*a
        native=all(b[i,j]==v for i,j,v in ((0,0,7),(0,1,10),(1,0,15),(1,1,22)))
        retained=bytearray(8*1024*1024)
    if mode in ("wait","native_wait"):
        Path(task["ready"]).write_text(str(os.getpid()))
        while not Path(task["release"]).exists():time.sleep(.02)
    if mode=="stage":
        from scripts.whole_source.artifacts import Axis,ContributionTask,IntervalRecord
        from scripts.whole_source.contract import ModeRange,QuantityKey
        c=task["contribution"]
        domain=ContributionTask(QuantityKey("F_H",0),ModeRange(task["row"],task["row"]+4),
            ModeRange(0,4),(Axis("node",c,c+1),))
        records=[IntervalRecord(r,j,(c,),Fraction((-1)**c*(r+1)*(j+2)*(c+1)),
            Fraction((-1)**c*(r+1)*(j+2)*(c+1))) for r in domain.rows for j in domain.columns]
        staged=staging.stage_chunk(domain,records)
        return {"path":str(staged.path),"task":domain.to_dict(),
            "ref":{"path":staged.ref.path,"sha256":staged.ref.sha256,"size":staged.ref.size},
            "generation":staged.generation,"attempt_id":staged.attempt_id}
    x=task.get("x",2)
    value=1-2*x+3*x*x
    return {"polynomial":hex(value),"native_product_verified":native,
        "precision":ctx.prec,"threads":ctx.threads}
