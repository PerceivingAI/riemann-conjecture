"""Research-only rounded numerical congruence, certified by EXACT rational evaluation.

A floating Cholesky inverse proposes the matrix only. Its success is *solely*
the exact rational Gershgorin strict margin after an invertible congruence.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json,os,time
from fractions import Fraction
from pathlib import Path
import numpy as np
from flint import fmpq,fmpq_mat
from scripts.inspect_combined_schur_packet import matrices

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--packet",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--witness-bits",type=int,default=48)
    args=ap.parse_args()
    start=time.perf_counter()
    src=args.packet.read_bytes()
    p=json.loads(gzip.decompress(src))
    s,_,_,_,_,_=matrices(p)
    n=len(s)
    a=np.array([[float(x) for x in row] for row in s],dtype=float)
    L=np.linalg.cholesky(a)
    inverse=np.linalg.inv(L)
    den=1<<args.witness_bits
    W_num=[[int(round(float(inverse[i,j])*den)) if j<=i else 0 for j in range(n)] for i in range(n)]
    if any(W_num[i][i]==0 for i in range(n)):
        raise RuntimeError("singular rounded congruence witness")
    rounded=np.array(W_num,dtype=float)/den
    c=rounded@a@rounded.T
    tentative=min(float(c[i,i]-sum(abs(c[i,j]) for j in range(n) if j!=i)) for i in range(n))
    print("FLOAT_ONLY_TRIAL_MARGIN",tentative,flush=True)
    if tentative<=0:
        raise RuntimeError("trial witness not numerically viable")
    mat=fmpq_mat(n,n)
    witness=fmpq_mat(n,n)
    for i in range(n):
        for j in range(n):
            v=s[i][j]
            mat[i,j]=fmpq(v.numerator,v.denominator)
            witness[i,j]=fmpq(W_num[i][j],den)
    print("EXACT_INPUT_MATRICES_READY",n,"SECS",round(time.perf_counter()-start,3),flush=True)
    congruence=witness*mat*witness.transpose()
    print("EXACT_CONGRUENCE_READY","SECS",round(time.perf_counter()-start,3),flush=True)
    margin=min(
        congruence[i,i]-sum((abs(congruence[i,j]) for j in range(n) if j!=i),fmpq(0))
        for i in range(n)
    )
    if margin<=0:
        raise RuntimeError("exact rational congruence not strictly positive")
    print("EXACT_GERSHGORIN_POSITIVE","MARGIN_APPROX",float(margin),
          "SECS",round(time.perf_counter()-start,3),flush=True)
    report={
        "format":"pretheorem-combined-schur-exact-congruence-v1",
        "status":"GENERATOR_SIDE_EXACT_WITNESS_PENDING_INDEPENDENT_AUDIT",
        "packet_sha256":hashlib.sha256(src).hexdigest(),
        "dimension":n,
        "witness_denominator":den,
        "witness_numerators":W_num,
        "gershgorin_margin_exact":str(Fraction(int(margin.p),int(margin.q))),
        "mathematical_scope":"exact positivity of conservative S_lower; no certificate admission"
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    blob=gzip.compress(json.dumps(report,sort_keys=True,separators=(",",":")).encode(),mtime=0)
    tmp=args.output.with_suffix(args.output.suffix+".partial")
    tmp.write_bytes(blob);os.replace(tmp,args.output)
    print("WITNESS_OUTPUT",args.output,"SHA256",hashlib.sha256(blob).hexdigest(),flush=True)

if __name__=="__main__":
    main()
