"""Complete fixed Fourier-minorant matrix source and exact research proof."""
from __future__ import annotations

import os
for _key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_key,'1')

import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
from math import factorial
from pathlib import Path

from flint import acb, arb, arb_mat, ctx, fmpq_mat
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms, _translation_partition
from scripts import verify_weighted_low_space as exact

ROOT=Path(__file__).resolve().parents[1]
N=312
PRECISION=512
BITS=128
T=Q(1353,2048)
A=Q(7,2)
OMEGA=256
C94_PATH='computations/2026-10-25T142424Z-reference-route-selection/data/scalar-controls-v1.json'


def qa(q):
    q=Q(q)
    return arb(q.numerator)/q.denominator


def outward(value):
    lo,hi=arb_to_rational_enclosure(value)
    scale=1<<BITS
    return [(lo*scale).__floor__(),(hi*scale).__ceil__()]


def save(path,obj):
    raw=(json.dumps(obj,indent=2,allow_nan=False)+'\n').encode()
    if path.suffix=='.gz': raw=gzip.compress(raw,mtime=0)
    with path.open('xb') as handle: handle.write(raw)


def load(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def legendre(x,count=N):
    values=[arb(1)]
    if count>1: values.append(x)
    for k in range(1,count-1):
        values.append(((2*k+1)*x*values[-1]-k*values[-2])/(k+1))
    return values


def cross(left,right,weights,parity):
    indices=range(parity,N,2)
    first=arb_mat([[row[i] for row in left] for i in indices])
    second=arb_mat([[weight*row[i] for i in indices] for row,weight in zip(right,weights)])
    return first*second


def arithmetic():
    terms=enumerate_active_prime_power_terms(T.numerator,T.denominator,prec=PRECISION)
    if [term.m for term in terms]!=[2,3]: raise ValueError('wrong complete active set')
    breaks=_translation_partition(terms)
    rule=[arb.legendre_p_root(N,k,weight=True) for k in range(N)]
    p=[arb_mat(N//2,N//2) for _ in (0,1)]
    square=[arb_mat(N//2,N//2) for _ in (0,1)]
    for lo,hi in zip(breaks,breaks[1:]):
        mid,half=(lo+hi)/2,(hi-lo)/2
        active=[]
        for term in terms:
            for sign in (-1,1):
                shifted=mid+sign*term.tau
                if -1<shifted<1: active.append((term,sign))
                elif not (shifted < -1 or shifted > 1): raise ValueError('uncertain shift cell')
        if not active: continue
        basis,images,weights=[],[],[]
        for node,weight in rule:
            x=mid+half*node
            row=[arb(0) for _ in range(N)]
            for term,sign in active:
                moved=x+sign*term.tau
                if not -1<moved<1: raise ValueError('shift node crosses support boundary')
                values=legendre(moved)
                for k in range(N): row[k]-=term.coefficient*values[k]/2
            basis.append(legendre(x)); images.append(row); weights.append(half*weight)
        for parity in (0,1):
            p[parity]+=cross(basis,images,weights,parity)
            square[parity]+=cross(images,images,weights,parity)
    gp=[]
    for parity in (0,1):
        p[parity]=(p[parity]+p[parity].transpose())/2
        scaled=arb_mat([[p[parity][i,j]*qa(Q(2*(2*i+parity)+1,2)) for j in range(N//2)] for i in range(N//2)])
        gp.append(square[parity]-p[parity]*scaled)
    return p,square,gp


def odd_factorial(n):
    return factorial(2*n+1)//(2**n*factorial(n))


def bessel_vector(w,count=N):
    if not w>0: raise ValueError('positive nonzero real Fourier node required')
    values=[arb(0) for _ in range(count+2)]
    for n in (count,count+1):
        hyper=acb(-w*w/4).hypgeom_0f1(qa(Q(2*n+3,2)))
        if arb(0) not in hyper.imag: raise ValueError('nonreal entire hypergeometric value')
        values[n]=w**n/odd_factorial(n)*hyper.real
    for n in range(count,0,-1):
        values[n-1]=(2*n+1)*values[n]/w-values[n+1]
    return [2*(-1 if (n//2)%2 else 1)*values[n] for n in range(count)]


def panels():
    edges=[Q(0),Q(1,4),Q(1,2),Q(1),Q(2),Q(4)]
    edges.extend(Q(k) for k in range(8,257,4))
    return list(zip(edges,edges[1:]))


def operator_error(order):
    result=arb(0)
    for lo,hi in panels():
        h=qa((hi-lo)/2)
        bound=2*qa(T)/arb.pi()*(4*qa(T)*h).exp()*4096
        result+=8*h*bound/(1<<(2*order))
    return result


def band():
    result=[arb_mat(N//2,N//2) for _ in (0,1)]
    rule=[arb.legendre_p_root(48,k,weight=True) for k in range(48)]
    for lo,hi in panels():
        mid,half=qa((lo+hi)/2),qa((hi-lo)/2)
        vectors,weights=[],[]
        for node,weight in rule:
            t=mid+half*node
            multiplier=acb(arb(1)/4,t/2).digamma().real-arb.pi().log()-qa(A)
            vectors.append(bessel_vector(qa(T)*t))
            weights.append(qa(T)/arb.pi()*half*weight*multiplier)
        for parity in (0,1): result[parity]+=cross(vectors,vectors,weights,parity)
    error=Q(outward(operator_error(48))[1],1<<BITS)
    for parity in (0,1):
        for i in range(N//2):
            di=qa(Q(2,2*(2*i+parity)+1))
            for j in range(i,N//2):
                dj=qa(Q(2,2*(2*j+parity)+1))
                radius=qa(error)*(di*dj).sqrt()
                result[parity][i,j]+=arb(0,radius.abs_upper())
                result[parity][j,i]=result[parity][i,j]
    return result,error


def pole():
    alpha=qa(T)/2
    values=[]
    for n in range(N):
        value=acb(alpha*alpha/4).hypgeom_0f1(qa(Q(2*n+3,2)))
        if arb(0) not in value.imag: raise ValueError('nonreal polar entire value')
        values.append(2*alpha**n/odd_factorial(n)*value.real)
    return [arb_mat([[2*qa(T)*(-1 if parity else 1)*values[i]*values[j]
                      for j in range(parity,N,2)] for i in range(parity,N,2)]) for parity in (0,1)]


def triangle(blocks):
    return [[outward(blocks[i%2][i//2,j//2]) if (j-i)%2==0 else [0,0]
             for j in range(i,N)] for i in range(N)]


def source():
    with ctx.workprec(PRECISION):
        p,square,gp=arithmetic()
        polar=pole()
        frequency,error=band()
        low=[]
        for parity in (0,1):
            block=p[parity]+polar[parity]+frequency[parity]
            for i,degree in enumerate(range(parity,N,2)):
                block[i,i]+=qa(A*Q(2,2*degree+1))
            low.append(block)
        matrices={name:triangle(value) for name,value in
                  (('P',p),('P_squared',square),('GP',gp),('pole',polar),('band',frequency),('A',low))}
    scalar_raw=(ROOT/C94_PATH).read_bytes()
    return {'format':'research-fourier-minorant-matrix-v1','support':[1353,2048],'a':'7/2','omega':256,
            'dimension':N,'basis':'ordinary_unnormalized_legendre','bits':BITS,'source_precision':PRECISION,
            'frequency_order':48,'arithmetic_order':312,'quadrature_operator_error_upper':str(error),
            'matrices':matrices,'complement':{'d_exact':str(Q(19,8)-Q(1,10**82)),
                'mixed_allowance_exact':str(Q(3,10**40)),'scalar_source':C94_PATH,
                'scalar_sha256':hashlib.sha256(scalar_raw).hexdigest()},
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope':'complete fixed research minorant inputs; no positivity or admission until accepted proof'}


def prove(path):
    obj=load(path)
    lower,_,_=exact._order_bounds(obj['matrices']['A'],BITS)
    _,gp_upper,_=exact._order_bounds(obj['matrices']['GP'],BITS)
    d=Q(19,8)-Q(1,10**82)
    from flint import fmpq
    for i in range(N): gp_upper[i,i]+=fmpq(3,10**40)*fmpq(2,2*i+1)
    sufficient=lower-gp_upper/fmpq(d.numerator,d.denominator)
    blocks={}
    for parity,name in enumerate(('even','odd')):
        indices=list(range(parity,N,2))
        block=fmpq_mat([[sufficient[i,j] for j in indices] for i in indices])
        proof=exact._positive_proof(block)
        if proof is None: raise ValueError('complete sufficient lower not certified: '+name)
        witness=[[Q(v,proof['denominator']) for v in row] for row in proof['numerators']]
        trace=sum((witness[i][j]**2*Q(2,2*indices[j]+1) for i in range(len(indices)) for j in range(len(indices))),Q())
        blocks[name]={'transform':[[str(witness[j][i]) for j in range(len(indices))] for i in range(len(indices))],
                      'claimed_margin':proof['exact_margin'],
                      'mass_normalized_gap_exact':str(Q(proof['exact_margin'])/trace)}
    obj['blocks']=blocks
    obj['source_packet_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    obj['status']='COMPLETE_POSITIVE_SUFFICIENT_LOWER'
    return obj


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    generation=commands.add_parser('source');generation.add_argument('--output',type=Path,required=True)
    proof=commands.add_parser('prove');proof.add_argument('--source',type=Path,required=True);proof.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=source() if args.command=='source' else prove(args.source)
    save(args.output,result)
    print(json.dumps({'scope':result['scope'],'status':result.get('status','SOURCE_ONLY'),
                      'quadrature_operator_error_upper':result['quadrature_operator_error_upper'],
                      'gaps':{k:v['mass_normalized_gap_exact'] for k,v in result.get('blocks',{}).items()}}))
