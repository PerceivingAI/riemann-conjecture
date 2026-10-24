"""Fixed T=3/5,N=192 weighted research inputs; no theorem admission."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

from flint import arb, arb_mat, ctx, fmpq, fmpq_poly
from scripts.cert.constants import c_T_enclosure
from scripts.cert.legendre_schur import harmonic, legendre_polynomials
from scripts.cert.mixed_gram_research import assemble_truncated_mixed_gram
from scripts.cert.multi_prime_legendre_schur import _residual_rho, _residual_truncation_operator
from scripts.cert.prime_power_terms import (
    _affine_legendre, _exact_inner, combined_piecewise_images,
    enumerate_active_prime_power_terms,
)
from scripts.verify_combined_schur_analytic_entries import endpoints

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = 'computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json'
ORIGINAL_SHA = '44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b'
SOURCES = (
    'scripts/weil_weighted_low_space.py', 'scripts/cert/constants.py',
    'scripts/cert/legendre_schur.py', 'scripts/cert/mixed_gram_research.py',
    'scripts/cert/multi_prime_legendre_schur.py', 'scripts/cert/prime_power_terms.py',
    'scripts/cert/residual_kernel.py', 'scripts/verify_combined_schur_analytic_entries.py',
)
N, K, BITS = 192, 32, 352


def publish(value: arb) -> list[int]:
    lo, hi = endpoints(value)
    den = 1 << BITS
    return [(lo*den).__floor__(), (hi*den).__ceil__()]


def original() -> dict:
    raw = (ROOT/ORIGINAL).read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError('original input byte identity changed')
    return json.loads(raw)


def signature(images: list[fmpq_poly]) -> str:
    text = '\n'.join('|'.join(map(str, p.coeffs())) for p in images)
    return hashlib.sha256(text.encode()).hexdigest()


def triangular(matrix: list[list[arb]]) -> list:
    result = []
    for i,row in enumerate(matrix):
        out = []
        for j in range(i,len(matrix)):
            if (i-j) % 2:
                if not row[j].contains(0) or not matrix[j][i].contains(0):
                    raise ValueError('source excludes mathematical parity zero')
                out.append([0,0])
            else:
                if not row[j].overlaps(matrix[j][i]):
                    raise ValueError('source symmetry inconsistency')
                out.append(publish((row[j]+matrix[j][i])/2))
        result.append(out)
    return result


def head_inputs(n: int, boundary: int, precision: int) -> tuple[dict,str]:
    """Rectangular raw pairings, never a sparse-subspace complement Gram."""
    with ctx.workprec(precision):
        polys = legendre_polynomials(boundary-1)
        exact = [fmpq_poly([fmpq(c.numerator,c.denominator) for c in p]) for p in polys]
        terms = enumerate_active_prime_power_terms(3,5,prec=precision)
        if [t.m for t in terms] != [2,3]:
            raise ValueError('incorrect active terms')
        points, pieces = combined_piecewise_images(polys[:n],terms,prec=precision)
        arithmetic = arb_mat(boundary-n,n)
        for ci,(a,b) in enumerate(zip(points[:-1],points[1:])):
            if not pieces[0][ci].legendre_coefficients:
                continue
            radius = (b-a)/2
            table = _affine_legendre(boundary-1,(a+b)/2,radius)
            high = arb_mat([list(table[k][:n]) for k in range(n,boundary)])
            low = arb_mat(n,n)
            for j in range(n):
                for r,v in enumerate(pieces[j][ci].legendre_coefficients):
                    low[j,r] = v*2*radius/(2*r+1)
            arithmetic += high*low.transpose()
        images,_,_,_ = _residual_truncation_operator(polys[:n],K,precision,3,5)
        if any(p.degree()>n+K-1 for p in images):
            raise ValueError('residual image degree exceeds source bound')
        result = {name:[] for name in ('V','P','R32')}
        for row,k in enumerate(range(n,boundary)):
            values = {name:[] for name in result}
            for j in range(n):
                if (k-j)%2:
                    if not arithmetic[row,j].contains(0):
                        raise ValueError('arithmetic parity zero excluded')
                    v,p,r = arb(0),arb(0),arb(0)
                else:
                    v = arb(fmpq(2,k*(k+1)-j*(j+1)))
                    p = arithmetic[row,j]
                    r = arb(_exact_inner(exact[k],images[j])) if k<n+K else arb(0)
                for name,value in zip(('V','P','R32'),(v,p,r)):
                    values[name].append(publish(value))
            for name in result:
                result[name].append(values[name])
        return result,signature(images)


def generate(boundary: int, base: Path | None = None) -> dict:
    if type(boundary) is not int or boundary%2 or not N+K<=boundary<=1024:
        raise ValueError('boundary outside fixed execution range')
    old = original()
    start = time.perf_counter()
    fingerprints = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}
    if base is None:
        print('BUILDING_FULL_SOURCE_GRAM',flush=True,file=sys.stderr)
        source = assemble_truncated_mixed_gram(N,1024,K,3,5)
        with ctx.workprec(1024):
            c = c_T_enclosure(1024,3,5)
            a = [[source['V'][i][j]+source['P'][i][j]+source['Rk'][i][j]
                  for j in range(N)] for i in range(N)]
            for j in range(N):
                d = arb(2)/(2*j+1)
                hj = harmonic(j)
                a[j][j] += d*(arb(hj.numerator)/hj.denominator-c)
            terms = source['active_terms']
            mu = arb(harmonic(N).numerator)/harmonic(N).denominator-c
            mu -= _residual_rho(arb(3)/5,K)+sum((t.coefficient for t in terms),arb(0))
            matrices = {'A_K':triangular(a),'G_K':triangular(source['Gk'])}
            delta,complement = publish(source['delta_R']),publish(mu)
    else:
        blob = base.read_bytes()
        previous = json.loads(gzip.decompress(blob) if base.suffix=='.gz' else blob)
        if (previous.get('format'),previous.get('dimension'),previous.get('support'),
            previous.get('mu_reference_exact'),previous.get('source_sha256')) != (
                'research-weighted-low-space-source-v1',N,[3,5],old['mu_lower_exact'],fingerprints):
            raise ValueError('base input identity mismatch')
        matrices,delta,complement = previous['matrices'],previous['delta'],previous['complement']
    hp = 256*((4*max(boundary,N+K)+512+255)//256)
    print('BUILDING_RECTANGULAR_HEAD',boundary,'PRECISION',hp,flush=True,file=sys.stderr)
    heads,digest = head_inputs(N,boundary,hp)
    packet = {'format':'research-weighted-low-space-source-v1','support':[3,5],
              'dimension':N,'residual_order':K,'active_terms':[2,3],
              'basis':'ordinary_unnormalized_legendre','bits':BITS,'boundary':boundary,
              'source_precision':1024,'head_precision':hp,'mu_reference_exact':old['mu_lower_exact'],
              'original_mu_input_sha256':ORIGINAL_SHA,'source_sha256':fingerprints,
              'matrices':matrices,'heads':heads,'delta':delta,'complement':complement,
              'residual_signature':digest,'elapsed_seconds':time.perf_counter()-start}
    if base is not None:
        packet['base_packet_sha256'] = hashlib.sha256(blob).hexdigest()
        if digest != previous['residual_signature']:
            raise ValueError('base residual signature mismatch')
    return packet


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--boundary',type=int,default=224)
    ap.add_argument('--base',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    if args.output.exists():
        ap.error('output already exists')
    try:
        result = generate(args.boundary,args.base)
        blob = json.dumps(result,sort_keys=True,separators=(',',':')).encode()+b'\n'
        if args.output.suffix=='.gz':
            blob = gzip.compress(blob,mtime=0)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('xb') as stream:
            stream.write(blob)
        print(json.dumps({'status':'RESEARCH_SOURCE_INPUTS_ONLY','boundary':args.boundary,
                          'elapsed_seconds':result['elapsed_seconds'],
                          'sha256':hashlib.sha256(blob).hexdigest()}))
        return 0
    except (ValueError,KeyError,TypeError,OSError) as exc:
        print(str(exc),file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
