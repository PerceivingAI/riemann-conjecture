"""Non-proof reconnaissance for one fixed bounded Fourier minorant."""
from __future__ import annotations

import os
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_key, "1")

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss, legvander
from scipy.special import digamma, spherical_in, spherical_jn

ROOT = Path(__file__).resolve().parents[1]
RETAINED = "computations/2026-10-25T010204Z-complete-retained-reprojection/data/complete-reference-v1.json"
T = Q(1353, 2048)
N = 312
A = Q(7, 2)
OMEGA = 256


def scout(order: int) -> dict:
    t = float(T)
    normalization = np.sqrt((2*np.arange(N)+1)/2)
    x, w = leggauss(N)
    arithmetic = np.zeros((N, N))
    for m in (2, 3):
        shift = np.log(m)/t
        half = (2-shift)/2
        left = -1+half*(x+1)
        vl = legvander(left, N-1)*normalization
        vr = legvander(left+shift, N-1)*normalization
        correlation = vl.T @ ((half*w)[:,None]*vr)
        arithmetic -= np.log(m)/np.sqrt(m)*(correlation+correlation.T)
    gx, gw = leggauss(order)
    frequencies, weights = [], []
    boundaries = (0, Q(1,2), 1, 2, 4, 8, 16, 32, 64, 128, OMEGA)
    for lo, hi in zip(boundaries, boundaries[1:]):
        half, middle = float(hi-lo)/2, float(hi+lo)/2
        frequencies.extend(middle+half*gx)
        weights.extend(half*gw)
    frequencies, weights = np.array(frequencies), np.array(weights)
    multiplier = digamma(Q(1,4).numerator/Q(1,4).denominator+0.5j*frequencies).real-np.log(np.pi)-float(A)
    bessel = spherical_jn(np.arange(N)[:,None], t*frequencies[None,:])
    polar = np.sqrt(2*(2*np.arange(N)+1))*spherical_in(np.arange(N),t/2)
    retained_raw = (ROOT/RETAINED).read_bytes()
    retained = json.loads(retained_raw)
    blocks = []
    for parity in (0, 1):
        indices = np.arange(parity,N,2)
        waves = np.sqrt(2*t*(2*indices+1))[:,None]*((-1.)**(indices//2))[:,None]*bessel[indices]
        matrix = float(A)*np.eye(len(indices))+arithmetic[np.ix_(indices,indices)]
        matrix += 2*t*((-1)**parity)*np.outer(polar[indices],polar[indices])
        matrix += (waves*(weights*multiplier/np.pi)[None,:])@waves.T
        eigenvalues, eigenvectors = np.linalg.eigh((matrix+matrix.T)/2)
        vector = np.zeros(N)
        vector[indices] = eigenvectors[:,0]*normalization[indices]
        rational = [str(Q(round(float(v)*(1<<40)),1<<40)) for v in vector]
        old = np.array([float(Q(v)) for v in retained['blocks'][parity]['trial']])
        embedded = np.zeros(N)
        embedded[:len(old)] = old/normalization[:len(old)]
        old_parity = embedded[indices]
        blocks.append({'parity':parity,'minimum_eigenvalue_display':float(eigenvalues[0]),
                       'retained_trial_rayleigh_display':float(old_parity@matrix@old_parity/(old_parity@old_parity)),
                       'proposal_legendre_coefficients':rational,
                       'proposal_rayleigh_display':float(eigenvalues[0]),'proposal_rounding_bits':40})
    return {'format':'nonproof-fourier-minorant-scout-v1','scope':'floating proposals only, never a proof',
            'support':[1353,2048],'a':'7/2','omega':OMEGA,'dimension':N,'frequency_order_per_segment':order,
            'retained_trial_source':RETAINED,'retained_trial_source_sha256':hashlib.sha256(retained_raw).hexdigest(),
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'blocks':blocks}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--order',type=int,default=64)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    if args.order<16: parser.error('order must be at least16')
    result=scout(args.order)
    with args.output.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(result,stream,indent=2,allow_nan=False)
        stream.write('\n')
    print(json.dumps({'scope':result['scope'],'blocks':[{k:b[k] for k in ('parity','minimum_eigenvalue_display','retained_trial_rayleigh_display')} for b in result['blocks']]}))
