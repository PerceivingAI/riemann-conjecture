from pathlib import Path
from fractions import Fraction as Q
import json,zipfile,hashlib
OUT=Path(__file__).parent
def scalar(value):
    lo, hi = (Q(value['lower']), Q(value['upper']))
    assert lo <= hi
    return (lo, hi)

def rayleigh(block, q):
    center = Q(0)
    radius = Q(0)
    for i in range(len(q)):
        for j in range(i, len(q)):
            lo, hi = block[i][j]
            assert lo <= hi and block[i][j] == block[j][i]
            weight = q[i] * q[j] * (1 if i == j else 2)
            center += weight * (lo + hi) / 2
            radius += abs(weight) * (hi - lo) / 2
    return (center - radius, center + radius)

def matrix(value, n):
    assert value['dimension'] == n and len(value['entries']) == n * n
    rows = [[None] * n for _ in range(n)]
    for e in value['entries']:
        i, j = (e['row'], e['col'])
        assert type(i) == type(j) == int and 0 <= i < n and (0 <= j < n) and (rows[i][j] is None)
        lo, hi = (Q(int(e['lo_num']), int(e['lo_den'])), Q(int(e['hi_num']), int(e['hi_den'])))
        assert lo <= hi
        for endpoint in (lo, hi):
            d = endpoint.denominator
            assert d <= 1 << 104 and (not d & d - 1)
        rows[i][j] = (lo, hi)
    assert all((rows[i][j] == rows[j][i] for i in range(n) for j in range(n)))
    assert all((rows[i][j] == (0, 0) for i in range(n) for j in range(n) if i % 2 != j % 2))
    return rows

def main():
    results=[]
    for prec,bits,wbits in ((512,64,32),(640,64,32),(768,64,32),(512,104,56)):
        for n in (192,196):
            filename=f"phase11-candidate-inputs-N{n}-p{prec}-m{bits}-w{wbits}.zip"
            path=OUT/filename
            with zipfile.ZipFile(path) as archive: proof=json.loads(archive.read("candidate-inputs.json"))
            assert proof["format"]=="rh-multi-prime-candidate-audit-v1"
            assert proof["status"]=="WITNESS_FAILED" and proof["theorem_status"] is False
            assert proof["support"]=="11/20" and proof["dimension"]==n and proof["precision_bits"]==prec
            assert proof["matrix_bits"]==bits and proof["witness_bits"]==wbits and proof["residual_order"]==32
            assert proof["basis"]=="unnormalized_legendre_degree_order" and proof["factor"]=="3"
            assert [term["m"] for term in proof["active_terms"]]==[2,3]
            losses=[]
            for term in proof["active_terms"]:
                assert scalar(term["compressed_shift_norm_bound"])==(1,1)
                coefficient=scalar(term["coefficient"]);loss=scalar(term["rounded_complement_contribution"])
                assert 0<coefficient[0]<=coefficient[1] and loss[0]<=coefficient[0]<=coefficient[1]<=loss[1]
                losses.append(loss[1])
            mu=sum((Q(1,k) for k in range(1,n+1)),Q(0))-scalar(proof["c_T"])[1]-scalar(proof["rho_R"])[1]-sum(losses,Q(0))
            assert mu==Q(proof["mu_lower"]) and mu>0
            matrices={name:matrix(proof["matrices"][name],n) for name in ("A","GV","GP","GR")}
            assert all(endpoint.denominator<=1<<bits for m in matrices.values() for r in m for entry in r for endpoint in entry)
            with zipfile.ZipFile(OUT/f"phase9-targets-N{n}-p512-cell-legendre.zip") as archive:
                direction=json.loads(archive.read("rayleigh-inputs.json"))
            assert direction["dimension"]==n and direction["parity"]=="even" and direction["support"]=="11/20"
            q=[Q(value) for value in direction["vector"]]
            assert len(q)==n//2 and q[-1]==1
            factor=Q(3)/mu;indices=list(range(0,n,2))
            schur=[[(matrices["A"][i][j][0]-factor*sum((matrices[name][i][j][1] for name in ("GV","GP","GR")),Q(0)),matrices["A"][i][j][1]-factor*sum((matrices[name][i][j][0] for name in ("GV","GP","GR")),Q(0))) for j in indices] for i in indices]
            lower,upper=rayleigh(schur,q)
            assert upper<0
            norm=sum((value*value*Q(2,4*i+1) for i,value in enumerate(q)),Q(0))
            results.append({"dimension":n,"precision_bits":prec,"matrix_bits":bits,"witness_bits":wbits,"source_archive":filename,"source_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"complement_lower":str(mu),"rayleigh_upper":str(upper),"normalized_upper":str(upper/norm),"status":"STRICT_NEGATIVE_UPPER"})
    (OUT/"phase11-negative-exact-audit.json").write_text(json.dumps({"status":"PASS","role":"independent exact rounded sufficient-Schur rejection audit, not theorem admission","direction_source":"Retained Phase 9 56-bit dyadic direction reused only as a test vector; independent of candidate witness resolution","results":results,"theorem_status":False,"trust_boundary":"Serialized rational arithmetic; upstream Arb enclosures assumed"},indent=2)+"\n",encoding="utf-8")
    print("Independent exact outcome replay: 8/8 rounded target Schur matrices have strict negative upper directions")
if __name__=="__main__":main()
