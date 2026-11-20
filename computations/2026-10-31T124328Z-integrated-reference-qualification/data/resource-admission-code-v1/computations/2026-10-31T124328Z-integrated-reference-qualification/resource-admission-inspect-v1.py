"""Inspect declared caller/storage accounts and compressed publication byte identity.

This launches no numerical worker and grants no phase/full-reference clearance.
The host sample is not an idle baseline or a reservation.
"""
import argparse
import ast
from datetime import datetime, timezone
import gzip
import hashlib
import io
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.relative_to(ROOT)
    if output.exists():
        raise FileExistsError('inspection output must be fresh')
    from scripts.whole_source import admission, artifacts, execution, retention
    from scripts.whole_source.contract import bind_problem, canonical_bytes
    problem = bind_problem('retained-t081')
    old_path = ROOT/'computations/2026-10-31T124328Z-integrated-reference-qualification/data/phase-coordinator-code-v1/scripts/whole_source/artifacts.py'
    old_raw = old_path.read_bytes()
    tree = ast.parse(old_raw)
    definition = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == '_CompressedWriter')
    namespace = {'_require': artifacts._require, '_write_all': artifacts._write_all}
    exec(compile(ast.Module(body=[definition], type_ignores=[]), str(old_path), 'exec'), namespace)

    class Sink(io.BytesIO):
        def __init__(self):
            super().__init__()
            self.writes = 0
        def write(self, raw):
            self.writes += 1
            return super().write(raw)

    rows = [f'{index}:0x123456789abcdef\n'.encode() for index in range(4096)]
    writers = []
    for implementation in (namespace['_CompressedWriter'], artifacts._CompressedWriter):
        sink = Sink()
        writer = implementation(sink, execution.MIB)
        with gzip.GzipFile(fileobj=writer, mode='wb', filename='', mtime=0) as compressed:
            for row in rows:
                compressed.write(row)
        writer.flush()
        writers.append((sink.getvalue(), sink.writes))
    if writers[0][0] != writers[1][0]:
        raise ValueError('buffering changed the retained packet encoding')
    detection = execution.exact_telemetry(execution.neutral_helpers()[0].detect_resources())
    baseline = admission.current_commit(ROOT)
    caller = admission.phase_caller_account('source', problem)
    try:
        admission.admit_caller({'required_bytes': baseline+caller['required_bytes']}, detection,
                               existing_bytes=baseline)
        caller_fit = True
    except ValueError:
        caller_fit = False
    names = sorted(set((*retention.CODE, *execution._RUNTIME, Path(__file__).relative_to(ROOT).as_posix())))
    result = {'format': 'whole-source-admission-inspection-v1',
        'created_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'python': sys.version, 'scope': 'CODE_AND_METADATA_INSPECTION_ONLY',
        'code': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names},
        'legacy_writer_source': {'path': old_path.relative_to(ROOT).as_posix(),
                                 'sha256': hashlib.sha256(old_raw).hexdigest()},
        'compressed_writer': {'records': len(rows), 'legacy_sink_writes': writers[0][1],
            'current_sink_writes': writers[1][1], 'byte_identical': True,
            'packet_sha256': hashlib.sha256(writers[0][0]).hexdigest(),
            'scope': 'write-call mechanism, not measured filesystem I/O or full-workload speed'},
        'lifetime': admission.topology(problem), 'empty_operation_caller': caller,
        'sampled_current_commit_bytes': baseline, 'detected': detection,
        'empty_operation_caller_fits_snapshot': caller_fit,
        'fresh_exact_operand_demand': None, 'full_case_feasibility_established': False,
        'numerical_libraries_loaded': [name for name in ('flint', 'numpy', 'scipy') if name in sys.modules],
        'numerical_work': False, 'execution_authorized': False, 'scientific_acceptance': False}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        stream.write(canonical_bytes(result))
    print({'scope': result['scope'], 'compressed_writer': result['compressed_writer'],
           'numerical_libraries_loaded': result['numerical_libraries_loaded']})


if __name__ == '__main__':
    main()
