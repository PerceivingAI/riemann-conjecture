"""Target-size moment-vector/storage census; never allocates target dense matrices.

Research execution evidence, not analytical target acceptance or positivity.
The fixed T=1 declaration is read and SHA-bound. Lower-level moment construction
is reused unchanged; the .81 consumer's main()/guards are never called or patched.
"""
from __future__ import annotations
import argparse
import ctypes
import gc
import hashlib
import importlib.util
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path
from flint import arb, ctx, fmpq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / 'computations/2026-10-28T034134Z-t081-resource-execution'
CONSUMER = BASE / 'verify-whole-source-v2.py'


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + '\n')


def dyadic_dump(value):
    pieces = []
    for part in (value.mid(), value.rad()):
        rational = part.fmpq()
        numerator, denominator = int(rational.p), int(rational.q)
        assert denominator > 0 and denominator & (denominator - 1) == 0
        exponent = -(denominator.bit_length() - 1)
        # Canonicalise powers of two, including the native radius representation.
        if numerator:
            zeros = (abs(numerator) & -abs(numerator)).bit_length() - 1
            numerator >>= zeros
            exponent += zeros
        else:
            exponent = 0
        pieces.extend((format(numerator, 'x'), format(exponent, 'x')))
    return ' '.join(pieces).encode('ascii')


class NativeCensus:
    """Opaque owned C vectors: no Python object layout or internal pointer access."""
    def __init__(self, library):
        self.library = library
        self.dll = ctypes.CDLL(str(library))
        word, pointer = ctypes.c_ssize_t, ctypes.c_void_p
        signatures = {
            '_arb_vec_init': ([word], pointer),
            '_arb_vec_clear': ([pointer, word], None),
            '_arb_vec_allocated_bytes': ([pointer, word], word),
            'arb_allocated_bytes': ([pointer], word),
            'arb_load_str': ([pointer, ctypes.c_char_p], ctypes.c_int),
            'arb_bits': ([pointer], word),
            'arb_set': ([pointer, pointer], None),
        }
        for name, (arguments, result) in signatures.items():
            function = getattr(self.dll, name)
            function.argtypes, function.restype = arguments, result
        self.original = self.dll._arb_vec_init(1)
        self.copy = self.dll._arb_vec_init(1)
        self.struct_bytes = self.dll._arb_vec_allocated_bytes(self.copy, 1)
        assert self.struct_bytes > 0

    def close(self):
        self.dll._arb_vec_clear(self.original, 1)
        self.dll._arb_vec_clear(self.copy, 1)

    def fresh_copy_bytes(self, value):
        raw = dyadic_dump(value)
        assert self.dll.arb_load_str(self.original, raw) == 0
        assert self.dll.arb_bits(self.original) == value.bits()
        # Clearing is essential: capacity retained by a previously larger scalar
        # must not be confused with allocation of a fresh dense matrix entry.
        self.dll._arb_vec_clear(self.copy, 1)
        self.copy = self.dll._arb_vec_init(1)
        self.dll.arb_set(self.copy, self.original)
        assert self.dll.arb_bits(self.copy) == value.bits()
        return int(self.dll.arb_allocated_bytes(self.copy))

    def validate_vector(self, moments, count):
        vector = self.dll._arb_vec_init(count)
        expected = self.struct_bytes * count
        try:
            for index in range(count):
                value = moments[index % len(moments)]
                expected += self.fresh_copy_bytes(value)
                self.dll.arb_set(vector + index * self.struct_bytes, self.original)
            measured = int(self.dll._arb_vec_allocated_bytes(vector, count))
            assert measured == expected, (measured, expected)
            return {'entries': count, 'native_allocated_bytes': measured,
                    'scalar_sum_bytes': expected, 'exact_agreement': True}
        finally:
            self.dll._arb_vec_clear(vector, count)


def multiplicities(n, parity):
    length = 3 * n - 1
    result = []
    for index in range(length):
        low = max(0, -(-(index - parity - n + 1) // 2))
        high = min(n - 1, (index - parity) // 2)
        result.append(max(0, high - low + 1))
    # Independent row-interval prefix count, not a duplicate closed formula.
    difference = [0] * (length + 1)
    for row in range(n):
        start = 2 * row + parity
        difference[start] += 1
        difference[start + n] -= 1
    current = 0
    independently = []
    for change in difference[:-1]:
        current += change
        independently.append(current)
    assert result == independently and sum(result) == n * n
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    contract = json.loads(args.inputs.read_bytes())
    for binding in contract['bindings'].values():
        assert sha(ROOT / binding['path']) == binding['sha256'], binding['path']
    declaration = json.loads((ROOT / contract['bindings']['declaration']['path']).read_bytes())
    assert (declaration['support'], declaration['N'], declaration['M'], declaration['K']) == ('1', 5564, 11128, 132)
    sys.path.insert(0, str(BASE))
    consumer = load_module(CONSUMER, 't1_storage_moment_helper')
    from resource_limits_v1 import windows_resource_snapshot
    library = ROOT / contract['native_library']['path']
    assert sha(library) == contract['native_library']['sha256']
    census = NativeCensus(library)
    cases = []
    n = declaration['N']
    start_wall, start_cpu = time.monotonic(), time.process_time()
    try:
        # Every active term; first signed window, both parity index maps.
        # The opposite reflected window has the same midpoint bit/heap census;
        # that symmetry is checked explicitly below, not assumed for P or VP.
        for precision in contract['precisions']:
            ctx.prec = precision
            for term in declaration['active_terms']:
                m = term['m']
                case_wall, case_cpu = time.monotonic(), time.process_time()
                before = windows_resource_snapshot()['process']
                tau = arb(m).log()
                moments = consumer.power_window_moments(arb(-1), 1 - tau, 3 * n - 2)
                assert len(moments) == 3 * n - 1
                bits = [int(value.bits()) for value in moments]
                heap = [census.fresh_copy_bytes(value) for value in moments]
                reverse = consumer.power_window_moments(-1 + tau, arb(1), 3 * n - 2)
                assert all(reverse[i].mid() == moments[i].mid() * (-1 if i % 2 else 1)
                           and reverse[i].rad() == moments[i].rad()
                           for i in range(len(moments)))
                del reverse
                parities = []
                for parity in (0, 1):
                    counts = multiplicities(n, parity)
                    # Lower bound for explicit uncompressed midpoint limbs.
                    limb_floor = sum(count * ((bit + 63) // 64) * 8
                                     for count, bit in zip(counts, bits)
                                     if bit > 128)
                    copied_heap = sum(count * size for count, size in zip(counts, heap))
                    parities.append({'parity': parity, 'matrix_rows': n,
                        'matrix_columns': n, 'entries': n * n,
                        'midpoint_limb_payload_lower_bytes': limb_floor,
                        'native_fresh_copy_heap_bytes': copied_heap,
                        'native_struct_array_bytes': n * n * census.struct_bytes,
                        'dense_native_copy_account_bytes': copied_heap + n * n * census.struct_bytes})
                validation = census.validate_vector(moments, contract['validation_vector_entries'])
                after = windows_resource_snapshot()['process']
                row = {'support': '1', 'prime_power': m, 'precision': precision,
                    'window': ['-1', '1-log(m)'], 'reflected_window_exact_ball_equality': True,
                    'moment_count': len(moments), 'moment_bits_histogram': dict(Counter(bits)),
                    'native_heap_bytes_histogram': dict(Counter(heap)),
                    'native_struct_bytes': census.struct_bytes,
                    'parity_accounts': parities, 'native_vector_crosscheck': validation,
                    'process_before': before, 'process_after': after,
                    'wall_seconds': time.monotonic() - case_wall,
                    'cpu_seconds': time.process_time() - case_cpu}
                cases.append(row)
                print('MOMENT_CENSUS ' + json.dumps({k:row[k] for k in ('prime_power','precision','wall_seconds')}) , flush=True)
                del moments, bits, heap
                gc.collect()
    finally:
        census.close()
    output = {'format': 't1-target-moment-storage-census-v1',
        'status': 'MEASURED_VECTOR_AND_NATIVE_COPY_ACCOUNT_NOT_TARGET_EXECUTION',
        'inputs_sha256': sha(args.inputs), 'program_sha256': sha(Path(__file__)),
        'consumer_sha256': sha(CONSUMER), 'native_library_sha256': sha(library),
        'native_threads': ctx.threads, 'N': n, 'M': declaration['M'], 'K': declaration['K'],
        'support': '1', 'active_terms': declaration['active_terms'], 'cases': cases,
        'wall_seconds': time.monotonic() - start_wall, 'cpu_seconds': time.process_time() - start_cpu,
        'target_dense_matrix_allocated': False, 'target_numerical_goals_checked': False,
        'target_positivity_proved': False, 'production_admission': False}
    put(args.output, output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
