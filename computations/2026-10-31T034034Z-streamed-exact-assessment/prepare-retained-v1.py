"""Test-only byte-pinned transcription, not fresh analytical source generation."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from fractions import Fraction
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.whole_source.artifacts import (
    CodecBounds, CollectionLock, CollectionSpec, _coordinates, _publication_header,
)
from scripts.whole_source.contract import QuantityKey, bind_problem, canonical_bytes, problem_id
from scripts.whole_source.execution import MIB, _RUNTIME
from scripts.whole_source.pipeline import FAMILIES, _partition, _quantities, _tiles
from scripts.whole_source.slice import _ref

REFERENCE = ROOT / 'computations/2026-10-27T140745Z-t081-complete-gram-attempt/data'
SOURCE_SHA = 'f69fee0feb9c08833ad6a3091718c9a6a301e5b5ddbea96ee5f0f6c0553c8b6e'
PROPOSAL_SHA = '3444b4cd498e16b46d9c10b539285cd5038489976a88b3111bd47364d247c85e'
SCOPE = 'REFERENCE_ARITHMETIC_ONLY'
N = 413
CAP = 32 * MIB


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def load(raw):
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda text: (_ for _ in ()).throw(ValueError(text)))


def pinned(path, digest, size=None):
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == digest, 'reference hash mismatch: ' + str(path))
    require(size is None or len(raw) == size, 'reference size mismatch: ' + str(path))
    return raw


def unpack(raw):
    with gzip.GzipFile(fileobj=io.BytesIO(raw), mode='rb') as stream:
        decoded = stream.read(CAP + 1)
    require(len(decoded) <= CAP, 'reference decoded packet exceeds 32 MiB')
    return load(decoded)


def write_json(path, document):
    with path.open('xb') as stream:
        stream.write(canonical_bytes(document))


def reference_ref(name, raw):
    return {'path': (REFERENCE / name).relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(raw).hexdigest(), 'size': len(raw)}


def source_fixture(problem, source, directory):
    paths = set(_RUNTIME) | {
        'scripts/whole_source/slice.py', 'scripts/whole_source/gram.py',
        'scripts/whole_source/pipeline.py', 'scripts/whole_source/proposal.py',
        'scripts/whole_source/proposal_float.py', 'scripts/whole_source/exact.py',
        'scripts/whole_source/exact_global.py', Path(__file__).relative_to(ROOT).as_posix(),
    }
    refs = tuple(_ref(ROOT, path) for path in sorted(paths))
    bounds = CodecBounds(8*MIB, 8*MIB, 8*MIB, 16384, 8192, 256*1024,
                         64*1024, 8*1024*MIB, 128*MIB, 64*MIB)
    spec = CollectionSpec.create(problem, role='producer',
        quantities=tuple(q for q in _quantities(problem, False) if q.key.name in FAMILIES.values()),
        partition=_partition(problem, False, 32), backend='integer-rational',
        backend_version='stdlib-v1', native_threads=1, code_refs=refs, bounds=bounds, code_root=ROOT)
    count = 0
    tiles = []
    with CollectionLock.acquire(directory, spec) as lock:
        for family, name in FAMILIES.items():
            for parity in (0, 1):
                ref = source['matrices'][f'{family}-{parity}']
                relative = Path(ref['path'])
                require(not relative.is_absolute() and '..' not in relative.parts,
                        'invalid reference packet path')
                packet = unpack(pinned(REFERENCE / relative, ref['sha256'], ref['size']))
                require(set(packet) == {'bits', 'dimension', 'kind', 'parity', 'upper_triangle'} and
                        packet['bits'] == 256 and packet['dimension'] == N and
                        packet['kind'] == family and type(packet['parity']) is int and
                        packet['parity'] == parity, 'changed reference packet metadata')
                upper = packet['upper_triangle']
                require(type(upper) is list and len(upper) == N*(N+1)//2,
                        'incomplete reference upper triangle')
                for pair in upper:
                    require(type(pair) is list and len(pair) == 2 and
                            all(type(x) is int for x in pair) and pair[0] <= pair[1],
                            'invalid original integer endpoints')
                covered = 0
                for task in _tiles(spec, QuantityKey(name, parity)):
                    records = []
                    for m, n in _coordinates(task, True):
                        i, j = (m-parity)//2, (n-parity)//2
                        lo, hi = upper[i*N-i*(i-1)//2+j-i]
                        records.append([m, n, hex(lo), hex(hi)])
                    raw = canonical_bytes({'header': _publication_header(spec, task, 256),
                                           'records': records})
                    require(len(raw) <= bounds.max_raw_bytes, 'transcribed tile exceeds cap')
                    artifact = lock._immutable('seals', raw)
                    tiles.append({'family': family, 'parity': parity, 'task': task.to_dict(),
                                  'artifact': asdict(artifact)})
                    covered += len(records)
                require(covered == len(upper), 'reference packet cover mismatch')
                count += covered
                del upper, packet
        require(count == 512946, 'incomplete retained endpoint-pair transcription')
        manifest = {'format': 'whole-source-scientific-manifest-v1',
            'problem_id': problem_id(problem), 'collection': spec.to_dict(), 'control': False,
            'geometry': {'N': 826, 'M': 1652, 'K': 86}, 'role': 'producer',
            'publication_bits': 256, 'scope': 'FULL_DECLARED_SOURCE', 'tiles': tiles,
            'full_mathematical_source': True, 'analytical_acceptance': False,
            'matrix_positivity': False, 'production_admission': False,
            'residual_model_payment': 'Lambda D once in later exact full-space proof'}
        write_json(directory / 'source-manifest.json', manifest)
    return directory / 'source-manifest.json', count


def proposal_blocks(proposal):
    require(proposal['format'] == 't081-whole-congruence-proposal-v1' and
            proposal['rational_transform_bits'] == 80 and proposal['source_sha256'] == SOURCE_SHA and
            set(proposal['blocks']) == {'even', 'odd'}, 'changed reference proposal context')
    blocks = []
    entries = 0
    for parity, label in enumerate(('even', 'odd')):
        block = proposal['blocks'][label]
        require(type(block['parity']) is int and block['parity'] == parity,
                'changed reference proposal parity')
        theta = Fraction(block['theta'])
        require(str(theta) == block['theta'] and theta > 0, 'noncanonical reference theta')
        transform = block['proposal_transform']
        require(type(transform) is list and len(transform) == N and
                all(type(row) is list and len(row) == N for row in transform),
                'incomplete reference transform')
        integers = []
        for row in transform:
            values = []
            for text in row:
                require(type(text) is str, 'rational transform string required')
                value = Fraction(text)
                require(str(value) == text, 'noncanonical reference transform entry')
                scaled = value * (1 << 80)
                require(scaled.denominator == 1, 'reference transform is not on the 80-bit grid')
                values.append(scaled.numerator)
                entries += 1
            integers.append(values)
        def read_values(i, j, matrix=integers):
            require(type(i) is int and type(j) is int and 0 <= i < N and 0 <= j < N and
                    i % 32 == j % 32 == 0, 'noncanonical transform panel request')
            return [matrix[r][c] for r in range(i, min(i+32, N))
                    for c in range(j, min(j+32, N))]
        blocks.append({'parity': parity, 'dimension': N, 'u': 80, 'theta': theta,
                       'panel_size': 32, 'read_values': read_values})
    require(entries == 341138, 'incomplete retained Z transcription')
    return blocks, entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--run', action='store_true', help='Run the owned exact lane after transcription')
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.relative_to(ROOT)
    output.mkdir(parents=True, exist_ok=False)
    source_raw = pinned(REFERENCE / 'source-v1.json', SOURCE_SHA)
    proposal_raw = pinned(REFERENCE / 'proposal-v1.json.gz', PROPOSAL_SHA)
    source = load(source_raw)
    require(source['format'] == 't081-complete-signed-weighted-Gram-source-v1' and
            source['N'] == 826 and source['physical_extent'] == 1652 and source['order'] == 86 and
            source['bits'] == 256 and source['support'] == '81/100' and
            set(source['matrices']) == {f'{f}-{p}' for f in FAMILIES for p in (0, 1)},
            'changed reference source context')
    proposal = unpack(proposal_raw)
    require(proposal['inputs_sha256'] == source['inputs_sha256'], 'reference scalar closure mismatch')
    problem = bind_problem('retained-t081')
    require(Fraction(source['eta_lower']) == problem.eta and
            Fraction(source['model_error_upper']) == problem.model_error,
            'reference scalar bounds differ from frozen problem')
    manifest, pairs = source_fixture(problem, source, output / 'source')
    blocks, entries = proposal_blocks(proposal)
    origin = {'format': 'retained-exact-reference-origin-v1', 'proof_scope': SCOPE,
              'source': reference_ref('source-v1.json', source_raw),
              'proposal': reference_ref('proposal-v1.json.gz', proposal_raw),
              'endpoint_pairs': pairs, 'Z_entries': entries,
              'fresh_source_construction': False, 'fresh_proposal_construction': False,
              'analytical_source_acceptance': False, 'production_admission': False}
    origin_path = output / 'reference-origin.json'
    write_json(origin_path, origin)
    origin_raw = origin_path.read_bytes()
    origin_ref = {'kind': 'REFERENCE_TRANSCRIPTION', 'directory': str(output),
                  'artifact': {'path': origin_path.name,
                               'sha256': hashlib.sha256(origin_raw).hexdigest(), 'size': len(origin_raw)}}
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    from scripts.whole_source.exact import prepare_exact_operands, run_exact_operands
    prepared = prepare_exact_operands(problem, manifest, output / 'inputs', blocks, origin_ref,
        origin_git_commit=commit, origin_git_dirty=True, code_root=ROOT, proof_scope=SCOPE)
    result = {'format': 'retained-exact-preparation-v1', 'proof_scope': SCOPE, 'origin': origin_ref,
              'endpoint_pairs': pairs, 'Z_entries': entries,
              'inputs': {key: str(path.relative_to(output)) for key, path in prepared.items()},
              'prepare_invocation': [sys.executable, *sys.argv],
              'exact_execution_requested': args.run, 'production_admission': False}
    if args.run:
        started = time.perf_counter()
        report = run_exact_operands(prepared['problem'], prepared['execution'], output / 'exact', code_root=ROOT)
        result['exact_elapsed_seconds_hex'] = (time.perf_counter() - started).hex()
        result['exact_status'] = report['status']
    write_json(output / 'prepare-result.json', result)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
