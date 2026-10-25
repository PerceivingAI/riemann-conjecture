"""Fresh independent inputs for the fixed N=16 tail-complement research reference.

Reuses the unchanged native all-entry reconstruction, not cached source arrays.
Only the tail-to-tail complement uses C-0088. The cross norm retains the full
residual norm, and acceptance supplies no production admission or sign result.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import gzip
import hashlib
from pathlib import Path
import sys
import time

from flint import arb, ctx, fmpq
from scripts import verify_combined_schur_analytic_entries as native
from scripts import verify_residual_tail_bound as tail_validation
from scripts import verify_weighted_low_space_inputs as validation
from scripts import verify_weighted_support_extension_inputs as reconstruction
from scripts import weil_tail_complement_assessment as experiment

ROOT = Path(__file__).resolve().parents[1]
AUDITOR = 'scripts/verify_tail_complement_inputs.py'
AUDIT_SOURCE_PATHS = (
    AUDITOR,
    'scripts/verify_weighted_support_extension_inputs.py',
    'scripts/verify_weighted_low_space_inputs.py',
    'scripts/verify_combined_schur_analytic_entries.py',
    'scripts/verify_residual_tail_bound.py',
)


def _audit_snapshot() -> dict[str, str]:
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
            for name in AUDIT_SOURCE_PATHS}


def _require_helper_origins() -> None:
    modules = (
        (reconstruction, AUDIT_SOURCE_PATHS[1]),
        (validation, AUDIT_SOURCE_PATHS[2]),
        (native, AUDIT_SOURCE_PATHS[3]),
        (tail_validation, AUDIT_SOURCE_PATHS[4]),
        (experiment, 'scripts/weil_tail_complement_assessment.py'),
    )
    validation.require(Path(__file__).resolve() == (ROOT/AUDITOR).resolve(),
                       'independent auditor origin changed')
    for module, name in modules:
        validation.require(Path(module.__file__).resolve() == (ROOT/name).resolve(),
                           'independent audit dependency origin changed: '+name)


def audit(packet_path: Path) -> dict:
    """Rebuild every stored interval and bind exact scalar and byte identities."""
    started = time.perf_counter()
    _require_helper_origins()
    sources = experiment.fingerprint()
    audit_sources = _audit_snapshot()
    raw = packet_path.read_bytes()
    packet = validation.decode_json(gzip.decompress(raw))
    # The producer owns packet structure and source provenance, not the
    # independent coefficient, complement, or cross-norm calculations below.
    experiment.validate_packet(packet)
    validation.require(packet['source_sha256'] == sources,
                       'source byte identity changed before reconstruction')
    validation.require(validation.REFERENCE_BITS == 512,
                       'independent receipt precision changed')
    t = Q(*packet['support'])
    n, order, boundary = (packet[name] for name in
                          ('dimension', 'residual_order', 'boundary'))
    low_precision = 2*packet['source_precision']
    head_precision = 2*packet['head_precision']
    print(f'REBUILDING_ALL_LOW T={t} N={n} K={order} PRECISION={low_precision}',
          file=sys.stderr, flush=True)
    rebuilt = reconstruction.reconstruct_low(t, n, order, low_precision)
    validation.require(rebuilt['residual_signature'] == packet['residual_signature'],
                       'independent exact residual image mismatch')
    with ctx.workprec(low_precision):
        # Reconstruct the signed kernel coefficients from the native Bernoulli
        # formula. Do not call the producer's tail-coefficient helper.
        t_exact = fmpq(t.numerator, t.denominator)
        coefficients = native.exact_residual_coefficients(order)
        kernel_coefficients = [-coefficient*t_exact**(d+1)
                               for d, coefficient in enumerate(coefficients)]
        constant = tail_validation.smoothing_upper(kernel_coefficients, n)
        validation.require(packet['tail_constant_exact'] == str(constant),
                           'independent exact tail smoothing constant mismatch')
        T = native.qarb(t)
        rho_tail = rebuilt['delta']+native.qarb(constant)/fmpq(n*(n+1))
        _, rho_tail_upper = native.endpoints(rho_tail)
        validation.require(rho_tail_upper <= Q(packet['rho_tail_upper_exact']),
                           'tail compression exceeds its serialized upper')
        cT = (2*arb.pi()*T).log()+arb.const_euler()
        arithmetic = sum((arb(m).log()/arb(m).sqrt() for m in (2, 3)), arb(0))
        rebuilt['complement'] = native.qarb(native.harmonic(n))-cT-arithmetic-rho_tail
        # reconstructed cross_norm deliberately remains pi/2+p+rho_global.
        # A double-tail compression bound cannot replace a low-to-tail norm.
    complement_lower, _ = native.endpoints(rebuilt['complement'])
    validation.require(0 < Q(packet['mu_reference_exact']) <= complement_lower,
                       'chosen mu exceeds the fresh independent tail complement')
    matrices = {}
    count = 0
    for name in ('A_K', 'G_K'):
        rows = []
        for i in range(n):
            row = []
            for j in range(i, n):
                row.append(validation.reference_pair(
                    rebuilt[name][i, j], packet['matrices'][name][i][j-i],
                    experiment.BITS, f'{name}[{i},{j}]',
                    parity_zero=bool((i-j) % 2)))
                count += 1
            rows.append(row)
        matrices[name] = rows
    scalars = {name: validation.reference_pair(
        rebuilt[name], packet[name], experiment.BITS, name)
        for name in ('delta', 'complement')}
    count += 2
    _, cross_upper = native.endpoints(rebuilt['cross_norm'])
    validation.require(cross_upper <= Q(packet['cross_norm_upper']),
                       'full uniform cross norm exceeds its serialized upper')
    count += 1
    print(f'REBUILDING_ALL_HEADS m={boundary} PRECISION={head_precision}',
          file=sys.stderr, flush=True)
    fresh = reconstruction.reconstruct_heads(t, n, order, boundary, head_precision,
                                              rebuilt['residual'])
    heads = {}
    for name in ('V', 'P', 'RK'):
        rows = []
        for k in range(n, boundary):
            row = []
            for j in range(n):
                row.append(validation.reference_pair(
                    fresh[name][k-n, j], packet['heads'][name][k-n][j],
                    experiment.BITS, f'{name}[{k},{j}]',
                    parity_zero=bool((k-j) % 2)))
                count += 1
            rows.append(row)
        heads[name] = rows
    expected = n*(n+1)+3*(boundary-n)*n+3
    validation.require(count == expected, 'incomplete fresh analytical reconstruction')
    validation.require(experiment.fingerprint() == sources
                       and _audit_snapshot() == audit_sources,
                       'source, auditor, or reconstruction helper changed during audit')
    return {
        'format': experiment.AUDIT_FORMAT,
        'status': 'ALL_FRESH_SOURCE_INPUTS_ACCEPTED',
        'packet_sha256': hashlib.sha256(raw).hexdigest(),
        'bits': 512,
        **{name: packet[name] for name in
           ('support', 'dimension', 'residual_order', 'boundary', 'source_sha256',
            'residual_signature', 'mu_reference_exact')},
        'tail_constant_exact': str(constant),
        'rho_tail_reference_upper_exact': str(rho_tail_upper),
        'complement_lower_exact': str(complement_lower),
        'matrices': matrices,
        'heads': heads,
        'cross_norm_upper': packet['cross_norm_upper'],
        'cross_norm_reference_upper_exact': str(cross_upper),
        **scalars,
        'accepted_entries': count,
        'low_input_provenance': 'FRESH_NATIVE_NO_REUSE',
        'reference_precision': low_precision,
        'head_reference_precision': head_precision,
        'residual_max_degree': rebuilt['residual_max_degree'],
        'auditor_sha256': audit_sources[AUDITOR],
        'audit_source_sha256': audit_sources,
        'elapsed_seconds': time.perf_counter()-started,
        'scope': 'Analytical reconstruction under Arb/source premises; research only, no production admission',
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        validation.require(not args.output.exists() and not args.output.is_symlink(),
                           'refusing to overwrite previous evidence')
        value = audit(args.packet)
        # The producer's shared writer uses exclusive creation, including if
        # another process creates the output while reconstruction is running.
        experiment.save(args.output, value)
        print(f"ALL_FRESH_SOURCE_INPUTS_ACCEPTED entries={value['accepted_entries']}")
        return 0
    except Exception as exc:
        print(f'REJECTED: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
