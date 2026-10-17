"""Independent exact rational research verifier; no generator sign flag is trusted.

The packet's analytical Arb provenance remains generator-side evidence.
This verifies the exact rational matrix implications and witness *separately*.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json,os,time
from fractions import Fraction
from pathlib import Path

from flint import fmpq, fmpq_mat


def fq(v:Fraction)->fmpq:
    return fmpq(v.numerator,v.denominator)


def check(args):
    start=time.perf_counter()
    inputs=args.packet.read_bytes()
    proofbytes=args.proof.read_bytes()
    p=json.loads(gzip.decompress(inputs))
    w=json.loads(gzip.decompress(proofbytes))
    if p.get("format")!="pretheorem-combined-schur-rational-inputs-v1":
        raise ValueError("wrong generator input format")
    if w.get("format")!="pretheorem-combined-schur-exact-congruence-v1":
        raise ValueError("wrong exact witness format")
    if w["packet_sha256"]!=hashlib.sha256(inputs).hexdigest():
        raise ValueError("witness packet sha mismatch")
    n=p["dimension"]
    if n not in (192,196) or w["dimension"]!=n:
        raise ValueError("unfrozen dimension")
    if (p["support"],p["precision_bits"],p["residual_order"],
        p["active_terms"],p["basis"],p["eta"])!=(
        [11,20],1024,32,[2,3],"ordinary_unnormalized_legendre",[1,2**24]):
        raise ValueError("unfrozen mathematical parameter")
    bits=p["dyadic_bits"]
    if type(bits) is not int or bits != 352:
        raise ValueError("unfrozen dyadic interval precision")
    den=1<<bits
    for key in ("mu_dyadic","delta_dyadic"):
        pair=p[key]
        if (not isinstance(pair,list) or len(pair)!=2
                or any(type(v) is not int for v in pair) or pair[0]>pair[1]):
            raise ValueError(f"invalid exact rational interval: {key}")
    mu_lo=Fraction(p["mu_dyadic"][0],den)
    delta_hi=Fraction(p["delta_dyadic"][1],den)
    if mu_lo<=0 or p["delta_dyadic"][0]<0 or delta_hi<0:
        raise ValueError("invalid complement or residual")
    for key in ("low_A_triangular","truncated_gram_triangular"):
        rows=p[key]
        if len(rows)!=n or any(len(row)!=n-i for i,row in enumerate(rows)):
            raise ValueError("invalid matrix shape")
    eta=Fraction(1,2**24)
    a=fmpq_mat(n,n)
    g=fmpq_mat(n,n)
    low_radii=[Fraction() for _ in range(n)]
    gram_radii=[Fraction() for _ in range(n)]
    for i in range(n):
        for j in range(i,n):
            al,ah=p["low_A_triangular"][i][j-i]
            gl,gh=p["truncated_gram_triangular"][i][j-i]
            if al>ah or gl>gh:
                raise ValueError("invalid outward interval")
            ac=Fraction(al+ah,2*den);gc=Fraction(gl+gh,2*den)
            ar=Fraction(ah-al,2*den);gr=Fraction(gh-gl,2*den)
            a[i,j]=a[j,i]=fq(ac)
            g[i,j]=g[j,i]=fq(gc)
            low_radii[i]+=ar;gram_radii[i]+=gr
            if i!=j:
                low_radii[j]+=ar;gram_radii[j]+=gr
    for i in range(n):
        a[i,i]-=fq(low_radii[i])
        g[i,i]+=fq(gram_radii[i])
    residual=(1+1/eta)*delta_hi**2
    def fmpq_fraction(value):
        return Fraction(int(value.p),int(value.q))
    schur=fmpq_mat(n,n)
    for i in range(n):
        for j in range(n):
            big=(1+eta)*fmpq_fraction(g[i,j])+(residual*Fraction(2,2*i+1) if i==j else 0)
            x=fmpq_fraction(a[i,j])-big/mu_lo
            schur[i,j]=fq(x)
    print("RECONSTRUCTED_WITHOUT_GENERATOR_RATIONAL_HELPERS",n,"SECS",round(time.perf_counter()-start,3),flush=True)
    nums=w["witness_numerators"]
    scale=w["witness_denominator"]
    if scale!=2**48 or len(nums)!=n or any(len(row)!=n for row in nums):
        raise ValueError("invalid witness matrix")
    transform=fmpq_mat(n,n)
    for i in range(n):
        for j in range(n):
            val=nums[i][j]
            if not isinstance(val,int) or (j>i and val):
                raise ValueError("noncanonical lower triangular rational witness")
            transform[i,j]=fmpq(val,scale)
        if transform[i,i]==0:
            raise ValueError("singular transform")
    congruence=transform*schur*transform.transpose()
    print("EXACT_CONGRUENCE_RECOMPUTED","SECS",round(time.perf_counter()-start,3),flush=True)
    margins=[]
    for i in range(n):
        m=congruence[i,i]-sum((abs(congruence[i,j]) for j in range(n) if j!=i),fmpq(0))
        margins.append(m)
    margin=min(margins)
    if not margin>0:
        raise ValueError("exact congruence has nonpositive Gershgorin margin")
    if Fraction(int(margin.p),int(margin.q))!=Fraction(w["gershgorin_margin_exact"]):
        raise ValueError("claimed exact margin mismatch")
    result={
        "classification":"POSITIVE_CANDIDATE_PRETHEOREM",
        "scope":"Exact rational positive-definiteness of conservative Schur lower matrix; upstream analytic Arb enclosure independently not rederived",
        "dimension":n,
        "packet_sha256":hashlib.sha256(inputs).hexdigest(),
        "witness_sha256":hashlib.sha256(proofbytes).hexdigest(),
        "exact_margin":str(Fraction(int(margin.p),int(margin.q))),
        "exact_margin_positive":True,
        "witness_independently_recomputed":True,
        "elapsed_seconds":round(time.perf_counter()-start,3)
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    tmp=args.output.with_suffix(".partial")
    tmp.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    os.replace(tmp,args.output)
    print("INDEPENDENT_EXACT_POSITIVE_CONGRUENCE_PASS","MARGIN_APPROX",float(margin),
          "SECS",round(time.perf_counter()-start,3),flush=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--packet",required=True,type=Path)
    ap.add_argument("--proof",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    check(ap.parse_args())

if __name__=="__main__":
    main()
