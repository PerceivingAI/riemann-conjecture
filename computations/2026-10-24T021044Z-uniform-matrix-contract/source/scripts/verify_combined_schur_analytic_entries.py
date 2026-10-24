"""Independent research-only all-entry analytic interval auditor for T=11/20,N=192.

No imports of the SYS-3/SYS-4 generator's mathematical helpers. Constructs
the low form and full *truncated* combined tail Gram separately from exact
Legendre/Bernoulli polynomials, independent moment/cell formulas, and Arb
outward enclosures. A PASS requires EACH fresh interval to be CONTAINED in
the archived 352-bit rational input interval, not merely overlapping it.

This is a scientific audit, not Rust/Lean theorem admission.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import time
from fractions import Fraction as Q
from pathlib import Path

from flint import arb, acb, ctx, fmpq, fmpq_mat, fmpq_poly, arb_mat


def qarb(x: fmpq | Q | int) -> arb:
    if isinstance(x, Q):
        return arb(x.numerator)/x.denominator
    if isinstance(x, fmpq):
        return arb(int(x.p))/int(x.q)
    return arb(x)


def endpoints(x: arb) -> tuple[Q,Q]:
    m=x.mid().fmpq()
    r=x.rad().fmpq()
    a=m-r
    b=m+r
    return Q(int(a.p),int(a.q)),Q(int(b.p),int(b.q))


def poly_basis(n: int) -> list[fmpq_poly]:
    z=fmpq_poly([0,1])
    polys=[fmpq_poly([1]),z]
    for k in range(1,n-1):
        polys.append(((2*k+1)*z*polys[-1]-k*polys[-2])*fmpq(1,k+1))
    return polys[:n]


def coeffs(polys: list[fmpq_poly], size: int) -> arb_mat:
    mat=arb_mat(len(polys),size)
    for i,p in enumerate(polys):
        for j,c in enumerate(p.coeffs()):
            mat[i,j]=qarb(c)
    return mat


def hankel(moments: list[arb], rows:int, cols:int) -> arb_mat:
    return arb_mat([[moments[i+j] for j in range(cols)] for i in range(rows)])


def integrate_power(a: arb,b:arb,max_degree:int)->list[arb]:
    if not (a<b and a>=-1 and b<=1):
        raise ValueError("noncertified cell")
    aa,bb=arb(1),arb(1)
    moments=[]
    for k in range(max_degree+1):
        aa*=a
        bb*=b
        moments.append((bb-aa)/(k+1))
    return moments


def harmonic(n:int,power:int=1)->fmpq:
    return sum((fmpq(1,k**power) for k in range(1,n+1)),fmpq(0))


def global_v_moments(maxdegree:int, squared:bool=False)->list[arb]:
    h=[fmpq(0)]
    h2=[fmpq(0)]
    for k in range(1,maxdegree+3):
        h.append(h[-1]+fmpq(1,k))
        h2.append(h2[-1]+fmpq(1,k*k))
    log2=arb.const_log2()
    pi=arb.pi()
    out=[]
    for k in range(maxdegree+1):
        if k%2:
            out.append(arb(0))
            continue
        r=k//2
        a=2*h[2*r+2]-h[r+1]
        m=qarb(a)-2*log2
        if squared:
            beta=4*h2[2*r+2]-h2[r+1]
            out.append((m*m+qarb(beta)-pi*pi/3)/(2*(k+1)))
        else:
            out.append(m/(k+1))
    return out


def endpoint_primitive(n:int,x:arb,plus:bool)->arb:
    # Independent integration-by-parts expression for x^n log(1 +/- x).
    if plus and x == -1:
        return qarb(harmonic(n+1))*((-1)**n)/(n+1)
    if not plus and x == 1:
        return -qarb(harmonic(n+1))/(n+1)
    arg=1+x if plus else 1-x
    if not arg.lower()>0:
        raise ValueError("indeterminate log branch")
    if plus:
        polynomial=sum((qarb(fmpq((-1)**k,n-k+1))*x**(n-k+1) for k in range(n+1)),arb(0))
        return ((x**(n+1)-(-1)**(n+1))*arg.log()-polynomial)/(n+1)
    polynomial=sum((x**k/k for k in range(1,n+2)),arb(0))
    return ((x**(n+1)-1)*arg.log()-polynomial)/(n+1)


def cell_v_moments(a:arb,b:arb,degree:int)->list[arb]:
    if not (a<b and a>=-1 and b<=1):
        raise ValueError("noncertified logarithmic cell")
    out=[]
    for k in range(degree+1):
        minus=endpoint_primitive(k,b,False)-endpoint_primitive(k,a,False)
        plus=endpoint_primitive(k,b,True)-endpoint_primitive(k,a,True)
        out.append(-(minus+plus)/2)
    return out


def exact_residual_coefficients(order:int)->list[fmpq]:
    # Direct Bernoulli polynomial formula, not the original cached helper.
    coefficients=[]
    for n in range(order+1):
        bern=sum(
            (fmpq(math.comb(n+1,k))*fmpq.bernoulli(k)*fmpq(3,4)**(n+1-k)
             for k in range(n+2)),fmpq(0))
        one=bern*fmpq(2**n,math.factorial(n+1))
        zero=fmpq(-2,2**n*math.factorial(n)) if n%2==0 else fmpq(0)
        coefficients.append(one+zero)
    return coefficients


def monomial_kernel_power(d:int,k:int)->fmpq_poly:
    # Independently integrate both polynomial halves of |x-y|^d y^k.
    # No call to scripts.cert.multi_prime_legendre_schur._abs_power_action.
    out=fmpq_poly()
    x=fmpq_poly([0,1])
    for r in range(d+1):
        den=k+r+1
        coeff=math.comb(d,r)
        left=(fmpq(((-1)**r)*coeff,den)
              * (x**(d+k+1)-((-1)**(k+r+1))*x**(d-r)))
        right=(fmpq(((-1)**(d-r))*coeff,den)
               * (x**(d-r)-x**(d+k+1)))
        out+=left+right
    return out


def residual_polys(basis:list[fmpq_poly],order:int,t:fmpq,
                   coeff:list[fmpq])->list[fmpq_poly]:
    occupied={k for p in basis for k,c in enumerate(p.coeffs()) if c}
    mon={}
    for k in sorted(occupied):
        total=fmpq_poly()
        for d,c in enumerate(coeff):
            if c:
                total += monomial_kernel_power(d,k)*(-c*t**(d+1))
        mon[k]=total
    return [
        sum((mon[k]*c for k,c in enumerate(p.coeffs()) if c),fmpq_poly())
        for p in basis
    ]


def translate(poly:fmpq_poly,shift:arb,size:int)->list[arb]:
    # Direct Taylor/binomial transform with independently collected
    # monomial coefficients rather than source Horner-shift helper.
    out=[arb(0) for _ in range(size)]
    powers=[arb(1)]
    for n in range(poly.degree()):
        powers.append(powers[-1]*shift)
    for k,c in enumerate(poly.coeffs()):
        if not c: continue
        scale=qarb(c)
        for j in range(k+1):
            out[j]+=scale*math.comb(k,j)*powers[k-j]
    return out


def local_legendre(center:arb,radius:arb,n:int)->arb_mat:
    # Direct recurrence in local t-Legendre coordinates.
    seq=[[arb(1)],[center,radius]]
    for k in range(1,n-1):
        v=seq[-1]
        x=[arb(0) for _ in range(k+2)]
        for j,a in enumerate(v):
            x[j]+=center*a
            x[j+1]+=radius*a*(j+1)/(2*j+1)
            if j:
                x[j-1]+=radius*a*j/(2*j+1)
        older=seq[-2]
        seq.append([
            ((2*k+1)*x[j]-(k*older[j] if j<len(older) else 0))/(k+1)
            for j in range(k+2)])
    return arb_mat([
        list(row)+[arb(0)]*(n-len(row)) for row in seq[:n]
    ])


def shifted_cell_images(basis:list[fmpq_poly],terms:list[tuple[int,arb,arb]],
                        a:arb,b:arb)->tuple[arb_mat,arb_mat,bool]:
    n=len(basis)
    center=(a+b)/2
    radius=(b-a)/2
    global_image=arb_mat(n,n)
    local_image=arb_mat(n,n)
    active=False
    for m,tau,c in terms:
        for shift,left,right in ((tau,arb(-1),1-tau),(-tau,-1+tau,arb(1))):
            # Breakpoints include every exact translated support boundary;
            # certified strict midpoint activity is constant on this cell.
            if center>left and center<right:
                active=True
                image_coeffs=local_legendre(center+shift,radius,n)
                for i in range(n):
                    for j in range(n):
                        local_image[i,j]-=c*image_coeffs[i,j]
                for i,p in enumerate(basis):
                    co=translate(p,shift,n)
                    for j in range(n):
                        global_image[i,j]-=c*co[j]
            elif center<left or center>right:
                continue
            else:
                raise ValueError(f"cell crosses uncertified active boundary {m}")
    return global_image,local_image,active


def bound_tail(t:arb,coeff:list[fmpq],order:int)->tuple[arb,arb]:
    # Independently code Bernoulli Fourier series and exponential tail.
    pi=arb.pi()
    u=2*t
    if not (u>0 and u<pi):
        raise ValueError("residual analyticity radius failed")
    ratio=u/pi
    geo=(2/pi)*ratio**(order+1)/(1-ratio)
    e=u/2
    exp_tail=2*e**(order+1)/math.factorial(order+1)/(1-e/(order+2))
    tail=geo+exp_tail
    delta=2*t*tail
    rho=2*t*(sum((qarb(abs(c))*u**k for k,c in enumerate(coeff)),arb(0))+tail)
    return delta,rho


def current_packet(path:Path)->dict:
    raw=path.read_bytes()
    obj=json.loads(gzip.decompress(raw))
    if obj["support"]!=[11,20] or obj["active_terms"]!=[2,3]:
        raise ValueError("frozen packet support/terms changed")
    if obj["dimension"] not in (8,192) or obj["residual_order"]!=32:
        raise ValueError("unfrozen dimension/order")
    return obj


def is_inside(value:arb,pair:list[int],bits:int)->bool:
    lo,hi=endpoints(value)
    return Q(pair[0],1<<bits)<=lo and hi<=Q(pair[1],1<<bits)


def compare_record(value:arb,pair:list[int],bits:int)->tuple[bool,float]:
    lo,hi=endpoints(value)
    old_lo,old_hi=Q(pair[0],1<<bits),Q(pair[1],1<<bits)
    return old_lo<=lo and hi<=old_hi, float(hi-lo)


def run(n:int,precision:int,packet:dict|None,verbose:bool)->dict:
    start=time.perf_counter()
    t=fmpq(11,20)
    with ctx.workprec(precision):
        T=qarb(t)
        terms=[]
        for m in (2,3):
            logm=arb(m).log()
            if not logm<2*T:raise ValueError("missing active prime")
            tau=logm/T
            c=logm/arb(m).sqrt()
            terms.append((m,tau,c))
        if not (arb(4).log()>2*T):
            raise ValueError("incorrect next prime-power threshold")
        bp=[arb(-1),arb(1)]
        for _,tau,_ in terms:bp.extend([-1+tau,1-tau])
        bp=sorted(bp,key=lambda x:float(x.mid()))
        if any(not bp[k]<bp[k+1] for k in range(len(bp)-1)):
            raise ValueError("unresolved breakpoint topology")

        basis=poly_basis(n)
        C=coeffs(basis,n)
        allcoeff=exact_residual_coefficients(32)
        residual=residual_polys(basis,32,t,allcoeff)
        mr=max(p.degree() for p in residual)+1
        R=coeffs(residual,mr)
        print("REBUILT_EXACT_POLYNOMIALS",n,"MAX_RESIDUAL_DEGREE",mr-1,
              "SECONDS",round(time.perf_counter()-start,3),flush=True)

        V=C*hankel(global_v_moments(2*n-2),n,n)*C.transpose()
        V2=C*hankel(global_v_moments(2*n-2,True),n,n)*C.transpose()
        VR=C*hankel(global_v_moments(n+mr-2),n,mr)*R.transpose()
        base=integrate_power(arb(-1),arb(1),2*mr-2)
        Rlow=C*hankel(base,n,mr)*R.transpose()
        R2=R*hankel(base,mr,mr)*R.transpose()
        print("BUILT_WHOLE_INTERVAL_MATRICES","SECONDS",round(time.perf_counter()-start,3),flush=True)

        P=arb_mat(n,n)
        P2=arb_mat(n,n)
        VP=arb_mat(n,n)
        PR=arb_mat(n,n)
        for ci,(a,b) in enumerate(zip(bp[:-1],bp[1:])):
            S,L,active=shifted_cell_images(basis,terms,a,b)
            if not active:continue
            radius=(b-a)/2
            A=local_legendre((a+b)/2,radius,n)
            W=arb_mat(n,n)
            for k in range(n):W[k,k]=2*radius/(2*k+1)
            P+=A*W*L.transpose()
            P2+=L*W*L.transpose()
            PR+=S*hankel(integrate_power(a,b,n+mr-2),n,mr)*R.transpose()
            VP+=C*hankel(cell_v_moments(a,b,2*n-2),n,n)*S.transpose()
            if verbose:print("CERTIFIED_CELL",ci,"SECONDS",round(time.perf_counter()-start,3),flush=True)
        print("BUILT_ALL_SHIFT_MATRICES","SECONDS",round(time.perf_counter()-start,3),flush=True)

        # Independent complement, full residual estimates.
        delta,rho=bound_tail(T,allcoeff,32)
        cT=(2*arb.pi()*T).log()+arb.const_euler()
        mu=qarb(harmonic(n))-cT-rho-sum((c for _,_,c in terms),arb(0))
        if n==192 and not mu>0:
            raise ValueError("complement not certified")
        inv=arb_mat(n,n)
        for i in range(n):inv[i,i]=arb(2*i+1)/2
        K=V+P+Rlow
        G=V2+P2+R2+VP+VP.transpose()+VR+VR.transpose()+PR+PR.transpose()-K*inv*K
        low=K
        for i in range(n):
            low[i,i]+=arb(2)/(2*i+1)*(qarb(harmonic(i))-cT-delta)
        print("REBUILT_FULL_MIXED_GRAM","SECONDS",round(time.perf_counter()-start,3),flush=True)

        if n==8:
            from scripts.cert.mixed_gram_research import assemble_truncated_mixed_gram
            from scripts.cert.constants import arb_to_rational_enclosure
            source=assemble_truncated_mixed_gram(n=8,prec=precision,residual_order=32,
                                                  support_num=11,support_den=20)
            for i in range(n):
                for j in range(n):
                    fresh=endpoints(G[i,j])
                    saved=arb_to_rational_enclosure(source["Gk"][i][j])
                    if max(fresh[0],saved[0])>min(fresh[1],saved[1]):
                        raise AssertionError(f"small combined Gram disagreement {i},{j}: {fresh}, {saved}")
            print("SMALL_INDEPENDENT_FULL_GRAM_64_OVERLAPS_PASS",flush=True)
        response={
            "dimension":n,"reference_precision":precision,
            "source_independent_analytic_reconstruction":True,
            "passes_all_stored_intervals":None,
            "low_entries_checked":0,"gram_entries_checked":0,
            "mu_contained":None,"delta_contained":None,
            "first_failures":[],"elapsed_seconds":None,
        }
        if packet:
            bits=packet["dyadic_bits"]
            if n!=packet["dimension"]:
                raise ValueError("dimension mismatch")
            response["mu_contained"]=is_inside(mu,packet["mu_dyadic"],bits)
            response["delta_contained"]=is_inside(delta,packet["delta_dyadic"],bits)
            for i in range(n):
                for j in range(i,n):
                    # Parity zeros are mathematical exact zeros, not tiny
                    # noise from the independent matrix multiply.
                    if (i-j)%2:
                        valid_a=packet["low_A_triangular"][i][j-i][0]<=0<=packet["low_A_triangular"][i][j-i][1]
                        valid_g=packet["truncated_gram_triangular"][i][j-i][0]<=0<=packet["truncated_gram_triangular"][i][j-i][1]
                    else:
                        valid_a=is_inside(low[i,j],packet["low_A_triangular"][i][j-i],bits)
                        valid_g=is_inside(G[i,j],packet["truncated_gram_triangular"][i][j-i],bits)
                    response["low_entries_checked"]+=1
                    response["gram_entries_checked"]+=1
                    if not valid_a or not valid_g:
                        if len(response["first_failures"])<16:
                            response["first_failures"].append({
                                "i":i,"j":j,"low_inside":valid_a,"gram_inside":valid_g,
                                "low_reference":str(low[i,j]),"gram_reference":str(G[i,j]),
                            })
            response["passes_all_stored_intervals"]=(
                not response["first_failures"]
                and response["mu_contained"] and response["delta_contained"])
        response["elapsed_seconds"]=round(time.perf_counter()-start,3)
        print("REFERENCE_AUDIT",json.dumps({k:v for k,v in response.items() if k!="first_failures"}),
              "FAILURES",len(response["first_failures"]),flush=True)
        return response


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--dimension",type=int,choices=[8,192],default=192)
    parser.add_argument("--precision",type=int,default=2048)
    parser.add_argument("--packet",type=Path)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--verbose",action="store_true")
    args=parser.parse_args()
    p=current_packet(args.packet) if args.packet else None
    result=run(args.dimension,args.precision,p,args.verbose)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        tmp=args.output.with_suffix(args.output.suffix+".partial")
        tmp.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
        os.replace(tmp,args.output)
    if p is not None and not result["passes_all_stored_intervals"]:
        raise SystemExit(2)


if __name__=="__main__":
    main()
