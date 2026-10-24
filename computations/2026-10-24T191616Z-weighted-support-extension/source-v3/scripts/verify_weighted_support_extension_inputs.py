"""Independent fresh all-entry analytic audit for the selected support extension.

Reconstructs by global moments/Taylor transforms, not the generator's grouped
source assembly or local head projection. No cached analytical arrays are used.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import gzip
import hashlib
from pathlib import Path
import sys
import time

from flint import arb, arb_mat, ctx, fmpq, fmpq_poly
from scripts import verify_combined_schur_analytic_entries as native
from scripts import verify_weighted_low_space_inputs as validation
from scripts import weil_weighted_support_extension as experiment

ROOT = Path(__file__).resolve().parents[1]
AUDITOR = 'scripts/verify_weighted_support_extension_inputs.py'


def geometry(t: Q) -> tuple[list, list]:
    T = native.qarb(t)
    terms = [(m, arb(m).log()/T, arb(m).log()/arb(m).sqrt()) for m in (2, 3)]
    validation.require(arb(3).log() < 2*T < arb(4).log() and 2*T < arb.pi(),
                       'strict arithmetic/analytic window is uncertified')
    tau2, tau3 = terms[0][1], terms[1][1]
    validation.require(1 < tau2 < tau3 < 2, 'translation chain topology changed')
    points = [arb(-1), 1-tau3, 1-tau2, -1+tau2, -1+tau3, arb(1)]
    validation.require(all(a < b for a, b in zip(points[:-1], points[1:])),
                       'signed source cell ordering is uncertified')
    return terms, list(zip(points[:-1], points[1:]))


def check_images(basis: list[fmpq_poly], residual: list[fmpq_poly], order: int) -> int:
    validation.require(len(basis) == len(residual), 'residual image count mismatch')
    for j, (poly, image) in enumerate(zip(basis, residual, strict=True)):
        validation.require(poly.degree() == j and image.degree() <= j+order,
                           'source column degree bound changed')
        validation.require(all(not c for k, c in enumerate(poly.coeffs()) if (k-j) % 2)
                           and all(not c for k, c in enumerate(image.coeffs()) if (k-j) % 2),
                           'source column reflection parity changed')
    return max(p.degree() for p in residual)


def reconstruct_low(t: Q, n: int, order: int, precision: int) -> dict:
    with ctx.workprec(precision):
        T = native.qarb(t)
        terms, cells = geometry(t)
        basis = native.poly_basis(n)
        C = native.coeffs(basis, n)
        coefficients = native.exact_residual_coefficients(order)
        residual = native.residual_polys(basis, order, fmpq(t.numerator, t.denominator), coefficients)
        degree = check_images(basis, residual, order)
        mr = degree+1
        R = native.coeffs(residual, mr)
        V = C*native.hankel(native.global_v_moments(2*n-2), n, n)*C.transpose()
        V2 = C*native.hankel(native.global_v_moments(2*n-2, True), n, n)*C.transpose()
        VR = C*native.hankel(native.global_v_moments(n+mr-2), n, mr)*R.transpose()
        moments = native.integrate_power(arb(-1), arb(1), 2*mr-2)
        Rlow = C*native.hankel(moments, n, mr)*R.transpose()
        R2 = R*native.hankel(moments, mr, mr)*R.transpose()
        P, P2, VP, PR = (arb_mat(n, n) for _ in range(4))
        active_cells = 0
        for a, b in cells:
            S, L, active = native.shifted_cell_images(basis, terms, a, b)
            if not active:
                continue
            active_cells += 1
            radius = (b-a)/2
            A = native.local_legendre((a+b)/2, radius, n)
            W = arb_mat(n, n)
            for k in range(n):
                W[k, k] = 2*radius/(2*k+1)
            P += A*W*L.transpose()
            P2 += L*W*L.transpose()
            PR += S*native.hankel(native.integrate_power(a, b, n+mr-2), n, mr)*R.transpose()
            VP += C*native.hankel(native.cell_v_moments(a, b, 2*n-2), n, n)*S.transpose()
        validation.require(active_cells == 4, 'lost a signed active source cell')
        delta, rho = native.bound_tail(T, coefficients, order)
        cT = (2*arb.pi()*T).log()+arb.const_euler()
        complement = native.qarb(native.harmonic(n))-cT-rho-sum((c for _, _, c in terms), arb(0))
        Dinv = arb_mat(n, n)
        for j in range(n):
            Dinv[j, j] = arb(2*j+1)/2
        Wlow = V+P+Rlow
        G = V2+P2+R2+VP+VP.transpose()+VR+VR.transpose()+PR+PR.transpose()-Wlow*Dinv*Wlow
        for j in range(n):
            Wlow[j, j] += arb(2)/(2*j+1)*(native.qarb(native.harmonic(j))-cT)
        return {'A_K': Wlow, 'G_K': G, 'delta': delta, 'complement': complement,
                'cross_norm': arb.pi()/2+sum((c for _, _, c in terms), arb(0))+rho,
                'basis': basis, 'residual': residual, 'residual_max_degree': degree,
                'residual_signature': validation.residual_signature(residual)}


def reconstruct_heads(t: Q, n: int, order: int, boundary: int, precision: int,
                      residual: list[fmpq_poly]) -> dict:
    with ctx.workprec(precision):
        basis = native.poly_basis(boundary)
        low = basis[:n]
        degree = check_images(low, residual, order)
        C_high = native.coeffs(basis[n:], boundary)
        C_low = native.coeffs(low, n)
        V = C_high*native.hankel(native.global_v_moments(boundary+n-2), boundary, n)*C_low.transpose()
        P = arb_mat(boundary-n, n)
        terms, cells = geometry(t)
        active_cells = 0
        for a, b in cells:
            S, _, active = native.shifted_cell_images(low, terms, a, b)
            if active:
                active_cells += 1
                P += C_high*native.hankel(native.integrate_power(a, b, boundary+n-2), boundary, n)*S.transpose()
        validation.require(active_cells == 4, 'lost a signed active head cell')
        RK = arb_mat(boundary-n, n)
        end = min(boundary, degree+1)
        if end > n:
            C_residual_head = native.coeffs(basis[n:end], end)
            R = native.coeffs(residual, degree+1)
            moments = native.integrate_power(arb(-1), arb(1), end+degree-1)
            rectangle = C_residual_head*native.hankel(moments, end, degree+1)*R.transpose()
            for k in range(end-n):
                for j in range(n):
                    value = rectangle[k, j]
                    if n+k > residual[j].degree():
                        validation.require(value.contains(0), 'individual residual degree zero excluded')
                        value = arb(0)
                    RK[k, j] = value
        return {'V': V, 'P': P, 'RK': RK}


def audit(packet_path: Path) -> dict:
    start = time.perf_counter()
    raw = packet_path.read_bytes()
    packet = validation.decode_json(gzip.decompress(raw))
    experiment.validate_packet(packet)
    sources = experiment.fingerprint()
    own_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    validation.require(Path(native.__file__).resolve() == (ROOT/'scripts/verify_combined_schur_analytic_entries.py').resolve(),
                       'independent primitive helper origin changed')
    t = Q(*packet['support'])
    n, order, boundary = (packet[name] for name in ('dimension', 'residual_order', 'boundary'))
    low_precision, head_precision = 2*packet['source_precision'], 2*packet['head_precision']
    print(f'REBUILDING_ALL_LOW T={t} N={n} K={order} PRECISION={low_precision}', file=sys.stderr, flush=True)
    rebuilt = reconstruct_low(t, n, order, low_precision)
    validation.require(rebuilt['residual_signature'] == packet['residual_signature'],
                       'independent exact residual image mismatch')
    mu_lower, _ = native.endpoints(rebuilt['complement'])
    validation.require(0 < Q(packet['mu_reference_exact']) <= mu_lower,
                       'original mu does not survive the new support')
    matrices = {}
    count = 0
    for name in ('A_K', 'G_K'):
        rows = []
        for i in range(n):
            row = []
            for j in range(i, n):
                row.append(validation.reference_pair(rebuilt[name][i, j],
                    packet['matrices'][name][i][j-i], experiment.BITS,
                    f'{name}[{i},{j}]', parity_zero=bool((i-j) % 2)))
                count += 1
            rows.append(row)
        matrices[name] = rows
    scalars = {name: validation.reference_pair(rebuilt[name], packet[name], experiment.BITS, name)
               for name in ('delta', 'complement')}
    count += 2
    _, cross_upper = native.endpoints(rebuilt['cross_norm'])
    validation.require(cross_upper <= Q(packet['cross_norm_upper']),
                       'uniform cross norm exceeds its serialized upper')
    count += 1
    print(f'REBUILDING_ALL_HEADS m={boundary} PRECISION={head_precision}', file=sys.stderr, flush=True)
    fresh = reconstruct_heads(t, n, order, boundary, head_precision, rebuilt['residual'])
    heads = {}
    for name in ('V', 'P', 'RK'):
        rows = []
        for k in range(n, boundary):
            row = []
            for j in range(n):
                row.append(validation.reference_pair(fresh[name][k-n, j],
                    packet['heads'][name][k-n][j], experiment.BITS,
                    f'{name}[{k},{j}]', parity_zero=bool((k-j) % 2)))
                count += 1
            rows.append(row)
        heads[name] = rows
    expected = n*(n+1)+3*(boundary-n)*n+3
    validation.require(count == expected, 'incomplete fresh analytical reconstruction')
    validation.require(experiment.fingerprint() == sources
                       and hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == own_sha,
                       'source or auditor changed during reconstruction')
    return {'format': experiment.AUDIT_FORMAT, 'status': 'ALL_FRESH_SOURCE_INPUTS_ACCEPTED',
            'packet_sha256': hashlib.sha256(raw).hexdigest(), 'bits': 512,
            **{name: packet[name] for name in ('support', 'dimension', 'residual_order', 'boundary',
                'source_sha256', 'residual_signature', 'mu_reference_exact')},
            'complement_lower_exact': str(mu_lower), 'matrices': matrices, 'heads': heads,
            'cross_norm_upper': packet['cross_norm_upper'],
            'cross_norm_reference_upper_exact': str(cross_upper),
            **scalars, 'accepted_entries': count,
            'low_input_provenance': 'FRESH_NATIVE_NO_REUSE',
            'reference_precision': low_precision, 'head_reference_precision': head_precision,
            'residual_max_degree': rebuilt['residual_max_degree'],
            'auditor_sha256': own_sha, 'elapsed_seconds': time.perf_counter()-start,
            'scope': 'Analytical reconstruction under Arb/source premises; no production admission'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('refusing to overwrite previous evidence')
    value = audit(args.packet)
    experiment.save(args.output, value)
    print(f"ALL_FRESH_SOURCE_INPUTS_ACCEPTED entries={value['accepted_entries']}")


if __name__ == '__main__':
    main()
