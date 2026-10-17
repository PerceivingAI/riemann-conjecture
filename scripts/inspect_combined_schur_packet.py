"""Research-only exact rational inspection of a frozen combined-Schur input packet.

No theorem admission. Float eigenvectors are ONLY trial-direction selectors;
all mathematical negative conclusions come from separate Fraction arithmetic.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json
from fractions import Fraction
from pathlib import Path

import numpy as np

def _pair(p: list[int],bits:int)->tuple[Fraction,Fraction]:
    d=1<<bits
    return Fraction(p[0],d), Fraction(p[1],d)

def matrices(packet:dict):
    n=packet["dimension"]
    bits=packet["dyadic_bits"]
    eta=Fraction(*packet["eta"])
    mlo,mhi=_pair(packet["mu_dyadic"],bits)
    dlo,dhi=_pair(packet["delta_dyadic"],bits)
    assert eta>0 and mlo>0 and dlo>=0
    centers=[]
    uppers=[]
    lowers=[]
    for key in ("low_A_triangular","truncated_gram_triangular"):
        pairs=packet[key]
        assert len(pairs)==n and all(len(row)==n-i for i,row in enumerate(pairs))
        center=[[Fraction()]*n for _ in range(n)]
        radius=[[Fraction()]*n for _ in range(n)]
        for i,row in enumerate(pairs):
            for k,p in enumerate(row):
                j=i+k
                lo,hi=_pair(p,bits)
                assert hi>=lo
                c=(lo+hi)/2
                r=(hi-lo)/2
                center[i][j]=center[j][i]=c
                radius[i][j]=radius[j][i]=r
        lower=[row[:] for row in center]
        upper=[row[:] for row in center]
        for i in range(n):
            x=sum(radius[i],Fraction())
            lower[i][i]-=x
            upper[i][i]+=x
        centers.append(center)
        lowers.append(lower)
        uppers.append(upper)
    A_lo=lowers[0]
    G_hi=uppers[1]
    norms=[Fraction(2,2*i+1) for i in range(n)]
    residual=(1+1/eta)*dhi*dhi
    G_full_up=[
        [(1+eta)*G_hi[i][j]+(residual*norms[i] if i==j else 0)
         for j in range(n)]
        for i in range(n)
    ]
    S_lo=[[A_lo[i][j]-G_full_up[i][j]/mlo for j in range(n)] for i in range(n)]
    return S_lo,centers,mlo,mhi,dhi,norms

def _float_mat(a:list[list[Fraction]]):
    return np.asarray([[float(x) for x in row] for row in a],dtype=float)

def exact_directional_upper(packet:dict, vec:np.ndarray, mu_hi:Fraction,
                             delta_hi:Fraction, norms:list[Fraction],
                             theta:Fraction=Fraction(1,1<<24)):
    n=packet["dimension"]
    bits=packet["dyadic_bits"]
    z=[Fraction(round(float(x)*(1<<20)),1<<20) for x in vec]
    if not any(z):
        raise ValueError("zero trial vector")
    a=Fraction()
    g=Fraction()
    for i in range(n):
        if not z[i]:
            continue
        for j in range(i,n):
            if not z[j]:
                continue
            w=z[i]*z[j]*(1 if i==j else 2)
            al,ah=_pair(packet["low_A_triangular"][i][j-i],bits)
            gl,gh=_pair(packet["truncated_gram_triangular"][i][j-i],bits)
            a += w*(ah if w>=0 else al)
            g += w*(gl if w>=0 else gh)
    norm=sum((norms[i]*z[i]**2 for i in range(n)),Fraction())
    a_full_upper=a+2*delta_hi*norm
    gram_lower=(1-theta)*g-(1/theta-1)*delta_hi**2*norm
    if gram_lower<0:gram_lower=Fraction()
    s_upper=a_full_upper-gram_lower/mu_hi
    return z, norm,a_full_upper,gram_lower,s_upper

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--packet",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    raw=args.packet.read_bytes()
    packet=json.loads(gzip.decompress(raw))
    assert packet["format"]=="pretheorem-combined-schur-rational-inputs-v1"
    assert packet["support"]==[11,20]
    assert packet["active_terms"]==[2,3]
    assert packet["residual_order"]==32
    assert packet["eta"]==[1,2**24]
    s,c,ml,mh,dh,norms=matrices(packet)
    n=packet["dimension"]
    e,ev=np.linalg.eigh(_float_mat(s))
    approximate=_float_mat(c[0])-_float_mat(c[1])/float((ml+mh)/2)
    ef,uf=np.linalg.eigh(approximate)
    print("PACKET",args.packet,"SHA256",hashlib.sha256(raw).hexdigest(),flush=True)
    print("FLOAT_DIAGNOSTIC_S_LOWER_EIG_MIN",e[0],flush=True)
    print("FLOAT_DIAGNOSTIC_S_APPROX_EIG_MIN",ef[0],flush=True)
    z,norm,a,g,upper=exact_directional_upper(packet,uf[:,0],mh,dh,norms)
    print("EXACT_DIRECTION_UPPER_SIGN", "NEGATIVE" if upper<0 else ("POSITIVE" if upper>0 else "ZERO"),flush=True)
    print("EXACT_DIRECTION_UPPER_APPROX",float(upper),flush=True)
    print("EXACT_FULL_GRAM_DIRECTION_LOWER_APPROX",float(g),flush=True)
    out={
        "packet_sha256":hashlib.sha256(raw).hexdigest(),
        "dimension":n,
        "status":"EXACT_NEGATIVE_UPPER_RAYLEIGH" if upper<0 else "NO_NEGATIVE_UPPER_WITNESS_FROM_TRIAL",
        "unverified_float_diagnostics":{
            "min_eigen_of_s_lower":float(e[0]),
            "min_eigen_of_midpoint_s":float(ef[0])
        },
        "direction_nonzero_rationals":[str(x) for x in z],
        "direction_norm_squared":str(norm),
        "a_full_rayleigh_upper":str(a),
        "full_gram_rayleigh_lower":str(g),
        "schur_rayleigh_upper":str(upper),
        "sign_test_is_exact_fraction":True,
        "independent_checker_required_before_claim":True,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print("OUT",args.output,flush=True)
    # This is not a proof positive: positivity requires a separate exact
    # rational congruence witness on the entire S_lower.
    if e[0]>0:
        print("POSITIVE_LOWER_NUMERICAL_CANDIDATE_NEEDS_EXACT_WITNESS",flush=True)

if __name__=="__main__":
    main()
