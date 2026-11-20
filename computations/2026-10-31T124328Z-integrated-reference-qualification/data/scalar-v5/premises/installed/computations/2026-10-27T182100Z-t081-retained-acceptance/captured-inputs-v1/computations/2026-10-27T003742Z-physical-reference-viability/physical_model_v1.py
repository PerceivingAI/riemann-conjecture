"""Exact finite residual head and sparse Legendre action for this fixed study."""
import math
from flint import fmpq,fmpq_poly

def legendre_polynomials(degree):
    x=fmpq_poly([0,1]);out=[fmpq_poly([1])]
    if degree:out.append(x)
    for n in range(1,degree):out.append(((2*n+1)*x*out[-1]-n*out[-2])/(n+1))
    return out

def exact_residual_head(kernel):
    K=len(kernel)-1;basis=legendre_polynomials(2*K);out=[]
    for n in range(K+1):
        p=basis[n];mom=[sum((p[k]*fmpq(2,k+j+1) for k in range(len(p)) if (k+j)%2==0),fmpq(0)) for j in range(K+1)]
        half=[sum((p[k]/(k+j+1) for k in range(len(p))),fmpq(0)) for j in range(K+1)]
        total=fmpq_poly([0]);primitive=p
        for d,c in enumerate(kernel):
            if d%2==0:
                coeff=[fmpq(0)]*(d+1)
                for j in range(d+1):coeff[d-j]+=c*((-1)**j)*math.comb(d,j)*mom[j]
                total+=fmpq_poly(coeff)
            else:
                primitive=p
                for _ in range(d+1):primitive=primitive.integral()
                total+=primitive*(2*math.factorial(d)*c)
                coeff=[fmpq(0)]*(d+1)
                for j in range(d+1):coeff[d-j]+=c*math.comb(d,j)*(((-1)**n)-((-1)**j))*half[j]
                total+=fmpq_poly(coeff)
        row=[fmpq(0)]*(2*K+1)
        for m in range(len(total)-1,-1,-1):
            value=total[m]/basis[m][m];row[m]=value;total-=basis[m]*value
        if total:raise ValueError('residual power-to-Legendre conversion')
        out.append(row)
    return out

def primitive_walk(n,K):
    current={n:fmpq(1)}
    for step in range(1,K+1):
        nxt={}
        for j,value in current.items():
            if j<1:raise ValueError('positive Legendre primitive required')
            value/=2*j+1;nxt[j+1]=nxt.get(j+1,fmpq(0))+value;nxt[j-1]=nxt.get(j-1,fmpq(0))-value
        current=nxt
        if step%2==0:yield step,current
