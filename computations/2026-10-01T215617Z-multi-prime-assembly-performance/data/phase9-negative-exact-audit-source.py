from fractions import Fraction as Q
from pathlib import Path
import json,zipfile,hashlib
out=Path("computations/2026-10-01T215617Z-multi-prime-assembly-performance/data")
def scalar(value):
    lo,hi=Q(value["lower"]),Q(value["upper"])
    assert lo<=hi
    return lo,hi

def rayleigh(block,q):
    center=Q(0);radius=Q(0)
    for i in range(len(q)):
        for j in range(i,len(q)):
            lo,hi=block[i][j]
            assert lo<=hi and block[i][j]==block[j][i]
            weight=q[i]*q[j]*(1 if i==j else 2)
            center+=weight*(lo+hi)/2
            radius+=abs(weight)*(hi-lo)/2
    return center-radius,center+radius

def matrix(value,n):
    assert value["dimension"]==n and len(value["entries"])==n*n
    rows=[[None]*n for _ in range(n)]
    for e in value["entries"]:
        i,j=e["row"],e["col"]
        assert type(i)==type(j)==int and 0<=i<n and 0<=j<n and rows[i][j] is None
        lo,hi=Q(int(e["lo_num"]),int(e["lo_den"])),Q(int(e["hi_num"]),int(e["hi_den"]))
        assert lo<=hi
        for endpoint in (lo,hi):
            d=endpoint.denominator
            assert d<=1<<104 and not d&(d-1)
        rows[i][j]=(lo,hi)
    assert all(rows[i][j]==rows[j][i] for i in range(n) for j in range(n))
    assert all(rows[i][j]==(0,0) for i in range(n) for j in range(n) if i%2!=j%2)
    return rows

results=[]
for n in (192,196):
    for prec in (384,512):
        path=out/f"phase9-targets-N{n}-p{prec}-cell-legendre.zip"
        with zipfile.ZipFile(path) as archive: raw=json.loads(archive.read("rayleigh-inputs.json"))
        assert raw["dimension"]==n and raw["precision_bits"]==prec and raw["support"]=="11/20"
        assert raw["theorem_status"] is False and raw["parity"]=="even"
        q=[Q(x) for x in raw["vector"]]
        assert len(q)==n//2 and q[-1]==1
        assert all(v.denominator<=1<<56 and not v.denominator&(v.denominator-1) for v in q)
        block=[[(Q(lo),Q(hi)) for lo,hi in row] for row in raw["schur_interval_block"]]
        assert len(block)==n//2 and all(len(row)==n//2 for row in block)
        lo,hi=rayleigh(block,q)
        norm=sum((v*v*Q(2,4*i+1) for i,v in enumerate(q)),Q(0))
        assert (lo,hi)==(Q(raw["rayleigh_lower"]),Q(raw["rayleigh_upper"]))
        assert norm==Q(raw["basis_norm_squared"]) and hi/norm==Q(raw["normalized_rayleigh_upper"]) and hi<0
        row={"dimension":n,"precision_bits":prec,"Arb_interval_rayleigh_upper":str(hi),"normalized_upper":str(hi/norm),"status":"STRICT_NEGATIVE_UPPER"}
        if prec==384:
            archive_path=out/f"phase9-targets-candidate-N{n}-p384-cell-legendre.zip"
            with zipfile.ZipFile(archive_path) as archive: proof=json.loads(archive.read("candidate-inputs.json"))
            assert proof["status"]=="WITNESS_FAILED" and proof["theorem_status"] is False
            assert proof["support"]=="11/20" and proof["dimension"]==n and proof["residual_order"]==32
            assert proof["matrix_bits"]==104 and proof["witness_bits"]==56 and proof["factor"]=="3"
            assert proof["basis"]=="unnormalized_legendre_degree_order"
            assert [t["m"] for t in proof["active_terms"]]==[2,3]
            losses=[]
            for t in proof["active_terms"]:
                assert scalar(t["compressed_shift_norm_bound"])==(1,1)
                c=scalar(t["coefficient"]);loss=scalar(t["rounded_complement_contribution"])
                assert 0<c[0]<=c[1] and loss[0]<=c[0]<=c[1]<=loss[1]
                losses.append(loss[1])
            mu=sum((Q(1,k) for k in range(1,n+1)),Q(0))-scalar(proof["c_T"])[1]-scalar(proof["rho_R"])[1]-sum(losses,Q(0))
            assert mu==Q(proof["mu_lower"]) and mu>0
            matrices={name:matrix(proof["matrices"][name],n) for name in ("A","GV","GP","GR")}
            factor=Q(3)/mu
            indices=list(range(0,n,2))
            rounded=[[(matrices["A"][i][j][0]-factor*sum((matrices[k][i][j][1] for k in ("GV","GP","GR")),Q(0)),
                       matrices["A"][i][j][1]-factor*sum((matrices[k][i][j][0] for k in ("GV","GP","GR")),Q(0)))
                      for j in indices] for i in indices]
            _,rounded_upper=rayleigh(rounded,q)
            assert rounded_upper<0
            row.update(exact_rounded_schur_rayleigh_upper=str(rounded_upper),normalized_rounded_upper=str(rounded_upper/norm),exact_complement_lower=str(mu))
        results.append(row)
(out/"phase9-negative-exact-audit.json").write_text(json.dumps({"role":"independent_generator_side_negative_direction_audit","status":"PASS","results":results,"theorem_status":False,"trust_boundary":"serialized rational arithmetic only; upstream Arb enclosures assumed"},indent=2)+"\n",encoding="utf-8")
print("Independent exact audit: 4/4 Arb interval directions strictly negative; 2/2 complete rounded candidate Schur matrices strictly negative")
