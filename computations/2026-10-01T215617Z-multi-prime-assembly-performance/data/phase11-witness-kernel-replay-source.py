from pathlib import Path
from fractions import Fraction as Q
import sys,json,zipfile,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from scripts.audit_multi_prime_candidate import _margin
OUT=Path(__file__).parent

def main():
    results=[]
    cost=json.loads((OUT/"phase11-witness-kernel-cost.json").read_text(encoding="utf-8"))
    for row in cost["results"]:
        assert row["role"]=="proper_principal_block_witness_kernel_cost_only" and row["full_target_candidate"] is False
        if row["status"]!="completed":
            results.append({"parent_dimension":row["parent_target_dimension"],"status":"no successful kernel witness; actual failure retained"});continue
        with zipfile.ZipFile(OUT/row["replay_archive"]) as archive: proof=json.loads(archive.read("kernel-inputs-and-witness.json"))
        assert proof["theorem_status"] is False
        block=[[(Q(lo),Q(hi)) for lo,hi in r] for r in proof["block"]]
        witness=[[Q(value) for value in r] for r in proof["witness"]]
        n=row["block_dimension"]
        assert len(block)==len(witness)==n and all(len(r)==n for r in block+witness)
        for i in range(n):
            for j in range(n):
                assert block[i][j]==block[j][i] and block[i][j][0]<=block[i][j][1]
                value=witness[i][j];assert value.denominator<=1<<56 and not value.denominator&(value.denominator-1)
                assert (j<=i or value==0) and (i!=j or value==1)
        begin=time.perf_counter();margin=_margin(block,witness);elapsed=time.perf_counter()-begin
        assert margin==Q(proof["reported_margin"])==Q(row["strict_gershgorin_margin"]) and margin>0
        results.append({"parent_dimension":row["parent_target_dimension"],"block_dimension":n,"status":"PASS","exact_margin":str(margin),"native_exact_margin_audit_seconds":elapsed,"full_target_candidate":False})
    (OUT/"phase11-witness-kernel-exact-audit.json").write_text(json.dumps({"role":"independent rational replay of operation-only proper principal block proxies","results":results,"theorem_status":False},indent=2)+"\n",encoding="utf-8")
    print("Kernel witness exact audits:",[(r['parent_dimension'],r['status']) for r in results])
if __name__=="__main__":main()
