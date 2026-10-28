"""Measure process startup, module import and per-work-unit transfer costs.

Quantifies what a parallel work unit would pay to start, reconstruct its own
small immutable inputs, and return a published dyadic matrix, using the actual
retained publications of the frozen T81/100 candidate. Measurements only.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import pickle
import subprocess
import sys
import time
from pathlib import Path

from flint import arb, arb_mat, ctx, fmpq

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "computations/2026-10-27T140745Z-t081-complete-gram-attempt"


def median(values: list[float]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def repeated(function, repetitions: int) -> dict[str, float]:
    values = []
    for _ in range(repetitions):
        started = time.perf_counter()
        function()
        values.append(time.perf_counter() - started)
    return {"median_seconds": round(median(values), 6),
            "min_seconds": round(min(values), 6), "max_seconds": round(max(values), 6),
            "repetitions": repetitions}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS"):
        os.environ.setdefault(key, "1")
    report: dict = {
        "format": "t081-work-unit-cost-probe-v1",
        "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": sys.version,
        "cpu_count": os.cpu_count(),
        "process_startup": {},
        "module_import": {},
        "publication_transfer": {},
        "in_memory_transfer": {},
        "input_regeneration": {},
        "production_admission": False,
    }
    report["process_startup"]["bare"] = repeated(
        lambda: subprocess.run([sys.executable, "-I", "-B", "-c", "pass"],
                               capture_output=True, check=True), 5)
    report["process_startup"]["import_flint"] = repeated(
        lambda: subprocess.run([sys.executable, "-I", "-B", "-c", "import flint"],
                               capture_output=True, check=True), 5)

    producer = CANDIDATE / "build-whole-source-v1.py"
    raw_producer = producer.read_bytes()

    def import_producer() -> None:
        spec = importlib.util.spec_from_file_location("t081_producer_probe", producer)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

    report["module_import"]["frozen_producer"] = repeated(import_producer, 3)
    report["module_import"]["producer_sha256"] = hashlib.sha256(raw_producer).hexdigest()

    packet = CANDIDATE / "data/whole-matrices-v1/A_model-0.json.gz"
    raw = packet.read_bytes()
    compressed = gzip.decompress(raw)
    report["publication_transfer"]["packet"] = packet.name
    report["publication_transfer"]["file_bytes"] = len(raw)
    report["publication_transfer"]["uncompressed_bytes"] = len(compressed)
    report["publication_transfer"]["gzip_decompress"] = repeated(
        lambda: gzip.decompress(raw), 5)
    report["publication_transfer"]["json_loads"] = repeated(
        lambda: json.loads(compressed), 5)
    payload = json.loads(compressed)
    report["publication_transfer"]["entries"] = len(payload["upper_triangle"])
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    report["publication_transfer"]["encode_and_compress"] = repeated(
        lambda: gzip.compress(encoded, mtime=0), 3)

    def published_triangle(bits: int, size: int) -> list[list[int]]:
        scale = 1 << bits
        return [[((i * 31 + j * 7) % 61 - 30) * scale, ((i * 31 + j * 7) % 61 - 30) * scale + 1]
                for i in range(size) for j in range(i, size)]

    try:
        ctx.prec = 6144
        probe_matrix = arb_mat(2, 2)
        pickle.dumps(probe_matrix, protocol=5)
        report["in_memory_transfer"]["arb_mat_picklable"] = True
    except TypeError as error:
        report["in_memory_transfer"]["arb_mat_picklable"] = False
        report["in_memory_transfer"]["arb_mat_pickle_error"] = str(error)
    triangle_413 = published_triangle(256, 413)
    report["in_memory_transfer"]["published_dyadic_413"] = {
        "entries": len(triangle_413),
        "pickle_bytes": len(pickle.dumps(triangle_413, protocol=5)),
        "dumps": repeated(lambda: pickle.dumps(triangle_413, protocol=5), 3),
        "gzip_bytes": len(gzip.compress(json.dumps(triangle_413).encode(), mtime=0)),
        "encode_and_compress": repeated(
            lambda: gzip.compress(json.dumps(triangle_413).encode(), mtime=0), 3),
    }
    triangle_826 = published_triangle(256, 826)
    report["in_memory_transfer"]["published_dyadic_826"] = {
        "entries": len(triangle_826),
        "pickle_bytes": len(pickle.dumps(triangle_826, protocol=5)),
    }
    ctx.prec = 4608

    def rebuild_413() -> None:
        matrix = arb_mat(413, 413)
        for index, (low, high) in enumerate(triangle_413):
            row, column = divmod(index, 413)
            value = arb(fmpq(low, 1 << 256), fmpq(high - low, 1 << 256))
            matrix[row, column] = matrix[column, row] = value

    report["in_memory_transfer"]["rebuild_arb_mat_413_from_dyadic"] = repeated(rebuild_413, 2)
    ctx.prec = 4608
    started = time.perf_counter()
    nodes = [arb.legendre_p_root(826, j, weight=True) for j in range(826)]
    report["input_regeneration"]["legendre_roots_826_at_4608"] = {
        "seconds": round(time.perf_counter() - started, 6), "count": len(nodes)}
    ctx.prec = 6144
    started = time.perf_counter()
    nodes = [arb.legendre_p_root(826, j, weight=True) for j in range(826)]
    report["input_regeneration"]["legendre_roots_826_at_6144"] = {
        "seconds": round(time.perf_counter() - started, 6), "count": len(nodes)}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: report[key] for key in (
        "process_startup", "publication_transfer")}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
