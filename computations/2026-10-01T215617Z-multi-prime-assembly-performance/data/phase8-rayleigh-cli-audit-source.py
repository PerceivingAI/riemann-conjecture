from fractions import Fraction
from pathlib import Path
import json,zipfile,hashlib
output=Path("computations/2026-10-01T215617Z-multi-prime-assembly-performance/data")
results=[]
for n in (192,196):
    path=output/f"phase8-rayleigh-cli-N{n}-p384-cell-legendre.zip"
    with zipfile.ZipFile(path) as archive: raw=json.loads(archive.read("rayleigh-inputs.json"))
    vector=[Fraction(value) for value in raw["vector"]]
    intervals=[[(Fraction(lo),Fraction(hi)) for lo,hi in row] for row in raw["schur_interval_block"]]
    dim=n//2
    assert len(vector)==dim and len(intervals)==dim
    assert vector[-1] == 1
    assert all(value.denominator <= 1<<56 for value in vector)
    assert all(len(row)==dim for row in intervals)
    center=Fraction(0); uncertainty=Fraction(0)
    for i in range(dim):
        for j in range(i,dim):
            lo,hi=intervals[i][j]
            assert lo <= hi and intervals[j][i] == (lo,hi)
            weight=vector[i]*vector[j]*(1 if i==j else 2)
            center += weight*(lo+hi)/2
            uncertainty += abs(weight)*(hi-lo)/2
    lower,upper=center-uncertainty,center+uncertainty
    assert lower==Fraction(raw["rayleigh_lower"]) and upper==Fraction(raw["rayleigh_upper"])
    assert upper < 0
    norm=sum((value*value*Fraction(2,4*i+1) for i,value in enumerate(vector)),Fraction(0))
    assert norm==Fraction(raw["basis_norm_squared"])
    assert upper/norm==Fraction(raw["normalized_rayleigh_upper"])
    results.append({"dimension":n,"status":"PASS","archive_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"recomputed_lower":str(lower),"recomputed_upper":str(upper),"exact_vector_nonzero":True})
(output/"phase8-rayleigh-cli-audit.json").write_text(json.dumps({"scope":"independent zero-float rational Rayleigh reconstruction only; upstream Arb enclosures not independently derived","theorem_status":False,"results":results},indent=2)+"\n",encoding="utf-8")
print("Independent zero-float Rayleigh audit: 2/2 PASS; both exact upper bounds strictly negative.")
