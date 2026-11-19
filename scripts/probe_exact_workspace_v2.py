"""Synthetic native arithmetic and reduced numerical workspace measurements, not proofs."""
from __future__ import annotations

import argparse
import contextlib
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import re
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_DIR = ROOT / "computations/2026-10-28T034134Z-t081-resource-execution"
sys.path.insert(0, str(RESOURCE_DIR))
from resource_limits_v1 import windows_resource_snapshot
import flint
from flint import arb, arb_mat, ctx, fmpq, fmpq_mat, fmpz_mat, nmod_mat


DECLARATION = {
    "dimension": 2782, "basis_dimension": 5564, "extent": 11128,
    "exact_panel": 16, "integer_bits": 512, "witness_bits": 107,
    "proposal_dimension": 65, "proposal_tile": 8, "seed": 8120132,
}
THREAD_VARIABLES = ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                    "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS")
BACKENDS = {"openblas", "scipy-openblas", "mkl", "blas", "lapack", "accelerate", "blis",
            "flexiblas", "atlas", "netlib"}


def numpy_backend(np):
    dependencies = np.show_config(mode="dicts").get("Build Dependencies", {})
    result = {}
    for role in ("blas", "lapack"):
        dependency = dependencies.get(role, {})
        backend = dependency.get("name")
        version = dependency.get("version")
        result[role] = {
            "found": dependency.get("found") is True,
            "backend": backend if isinstance(backend, str) and backend in BACKENDS else "unclassified",
            "version": version if isinstance(version, str) and
            re.fullmatch(r"[0-9]{1,6}(?:\.[0-9]{1,6}){0,6}", version) else None,
        }
    return result


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def snapshot():
    if os.name == "nt":
        return windows_resource_snapshot()
    return {"unavailable": "Windows process snapshots require Windows"}


def event(name, **fields):
    print("T081_EVENT " + json.dumps({"event": name, **fields}, sort_keys=True), flush=True)


class Measurement:
    def __init__(self):
        self.phases = []

    @contextlib.contextmanager
    def phase(self, name):
        record = {"name": name, "before": snapshot()}
        wall, cpu = time.perf_counter(), time.process_time()
        event("phase_started", phase=name)
        try:
            yield record
        finally:
            record.update(wall_seconds=time.perf_counter() - wall,
                          cpu_seconds=time.process_time() - cpu, after=snapshot())
            self.phases.append(record)
            event("phase_finished", phase=name,
                  wall_seconds=record["wall_seconds"], cpu_seconds=record["cpu_seconds"])


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


def bit_range(matrix):
    lo, hi = None, 0
    for i in range(matrix.nrows()):
        for j in range(matrix.ncols()):
            bits = abs(int(matrix[i, j])).bit_length()
            lo = bits if lo is None else min(lo, bits)
            hi = max(hi, bits)
    return {"minimum": lo, "maximum": hi}


def submatrix(matrix, r0, r1, c0, c1):
    result = arb_mat(r1 - r0, c1 - c0)
    for i in range(r0, r1):
        for j in range(c0, c1):
            result[i - r0, j - c0] = matrix[i, j]
    return result


def exact_probe(measure, d, panel, seed, integer_bits, witness_bits):
    p = 65521
    with measure.phase("modular_prime_and_expected_determinant"):
        require(all(p % k for k in range(2, math.isqrt(p) + 1)), "modulus is not prime")
        require(d < p, "Vandermonde points must be distinct modulo p")
        expected = 1
        for i in range(d):
            for j in range(i + 1, d):
                expected = expected * (j - i) % p
    with measure.phase("native_modular_allocation_and_fill") as phase:
        matrix = nmod_mat(d, d, p)
        for i in range(d):
            value, x = 1, i + 1
            for j in range(d):
                matrix[i, j] = value
                value = value * x % p
            if (i + 1) % 256 == 0:
                event("fill_rows", phase="native_modular_allocation_and_fill", rows=i + 1, total=d)
        phase["allocated"] = snapshot()
    with measure.phase("native_modular_full_determinant"):
        determinant = int(matrix.det())
        require(determinant == expected and determinant != 0, "Vandermonde determinant mismatch")
    del matrix
    gc.collect()
    rng = random.Random(seed)
    with measure.phase("native_integer_panel_fill"):
        a, z = fmpz_mat(panel, d), fmpz_mat(d, panel)
        for i in range(panel):
            for k in range(d):
                value = rng.getrandbits(integer_bits) | (1 << (integer_bits - 1))
                a[i, k] = -value if rng.getrandbits(1) else value
        for k in range(d):
            for j in range(panel):
                value = rng.getrandbits(witness_bits) | (1 << (witness_bits - 1))
                z[k, j] = -value if rng.getrandbits(1) else value
        a_bits, z_bits = bit_range(a), bit_range(z)
    selected = sorted({(0, 0), (0, panel - 1), (panel - 1, 0), (panel - 1, panel - 1)})
    with measure.phase("native_integer_full_inner_product"):
        product = a * z
        checked = []
        for i, j in selected:
            independent = sum(int(a[i, k]) * int(z[k, j]) for k in range(d))
            require(int(product[i, j]) == independent, "integer product mismatch")
            missing_last = sum(int(a[i, k]) * int(z[k, j]) for k in range(d - 1))
            require(missing_last != independent, "omitted-final-inner control did not differ")
            checked.append({"row": i, "column": j, "exact_match": True,
                            "omitted_final_inner_differs": True})
        product_bits = bit_range(product)
    del product
    with measure.phase("native_mass_weighted_panel_fill"):
        lcm = 1
        for i in range(d):
            lcm = math.lcm(lcm, 4 * i + 3)
        weighted = fmpz_mat(d, panel)
        mass_min, mass_max = None, 0
        for i in range(d):
            dint = 2 * (lcm // (4 * i + 3))
            bits = dint.bit_length()
            mass_min = bits if mass_min is None else min(mass_min, bits)
            mass_max = max(mass_max, bits)
            for j in range(panel):
                weighted[i, j] = dint * z[i, j]
        weighted_bits = bit_range(weighted)
    with measure.phase("native_mass_weighted_full_inner_product"):
        product = a * weighted
        for i, j in selected:
            independent = sum(int(a[i, k]) * (2 * (lcm // (4 * k + 3))) * int(z[k, j])
                              for k in range(d))
            require(int(product[i, j]) == independent, "mass-weighted product mismatch")
        mass_product_bits = bit_range(product)
    return {"scope": "synthetic exact native arithmetic; no target witness",
            "dimension": d, "panel": panel, "full_inner_domain": d,
            "modulus": p, "prime_trial_division_verified": True,
            "vandermonde_determinant": determinant, "independent_expected_determinant": expected,
            "integer_operand_bits": a_bits, "witness_operand_bits": z_bits,
            "integer_result_bits": product_bits, "selected_entry_checks": checked,
            "mass_lcm_bits": lcm.bit_length(), "mass_integer_bits": {"minimum": mass_min, "maximum": mass_max},
            "mass_weighted_operand_bits": weighted_bits, "mass_result_bits": mass_product_bits,
            "mass_selected_entry_checks_passed": True}


def block_cholesky(a, tile, omit_cross=False):
    n = a.nrows()
    result = arb_mat(n, n)
    for start in range(0, n, tile):
        stop = min(start + tile, n)
        diagonal = submatrix(a, start, stop, start, stop)
        if start and not omit_cross:
            previous = submatrix(result, start, stop, 0, start)
            diagonal = diagonal - previous * previous.transpose()
        for i in range(stop - start):
            value = diagonal[i, i]
            for k in range(i):
                value -= result[start + i, start + k] ** 2
            require(value > 0, "block diagonal pivot not certified positive")
            result[start + i, start + i] = value.sqrt()
            for j in range(i + 1, stop - start):
                value = diagonal[j, i]
                for k in range(i):
                    value -= result[start + j, start + k] * result[start + i, start + k]
                result[start + j, start + i] = value / result[start + i, start + i]
        if stop < n:
            panel = submatrix(a, stop, n, start, stop)
            if start and not omit_cross:
                left = submatrix(result, stop, n, 0, start)
                right = submatrix(result, start, stop, 0, start)
                panel = panel - left * right.transpose()
            # Solve X * L_block^T = panel by forward substitution in each row.
            for i in range(n - stop):
                for j in range(stop - start):
                    value = panel[i, j]
                    for k in range(j):
                        value -= result[stop + i, start + k] * result[start + j, start + k]
                    result[stop + i, start + j] = value / result[start + j, start + j]
        if not omit_cross:
            event("cholesky_panel", completed=stop, total=n)
    return result


def reduced_probe(measure, n, tile):
    ctx.prec = 1024
    with measure.phase("reduced_exact_rational_construction"):
        known = fmpq_mat(n, n)
        for i in range(n):
            known[i, i] = fmpq(1, 1 << i)
            for j in range(i):
                known[i, j] = fmpq((i + 3 * j) % 7 + 1, 16 * (1 << i))
        exact_a = known * known.transpose()
        a = arb_mat(n, n)
        for i in range(n):
            for j in range(n):
                a[i, j] = arb(exact_a[i, j])
    with measure.phase("reduced_native_block_cholesky"):
        result = block_cholesky(a, tile)
        for i in range(n):
            for j in range(n):
                require(result[i, j].is_finite() and result[i, j].contains(known[i, j]),
                        "Cholesky interval does not contain known exact entry")
    with measure.phase("reduced_omitted_cross_update_control"):
        wrong = block_cholesky(a, tile, omit_cross=True)
        different = sum(not wrong[i, j].contains(known[i, j]) for i in range(n) for j in range(i + 1))
        require(different > 0, "omitted-cross-update control did not differ")
    del wrong
    with measure.phase("reduced_complete_forward_backward_solve"):
        b, y, x = arb_mat(n, 1), arb_mat(n, 1), arb_mat(n, 1)
        for i in range(n):
            b[i, 0] = i + 1
            value = b[i, 0]
            for j in range(i):
                value -= result[i, j] * y[j, 0]
            y[i, 0] = value / result[i, i]
        for i in range(n - 1, -1, -1):
            value = y[i, 0]
            for j in range(i + 1, n):
                value -= result[j, i] * x[j, 0]
            x[i, 0] = value / result[i, i]
        residual = a * x - b
        for i in range(n):
            require(residual[i, 0].is_finite() and residual[i, 0].contains(0),
                    "reduced solve residual excludes zero")
        exact_b = fmpq_mat(n, 1)
        for i in range(n):
            exact_b[i, 0] = i + 1
        exact_x = exact_a.solve(exact_b)
        for i in range(n):
            require(x[i, 0].contains(exact_x[i, 0]), "reduced solve excludes exact rational solution")
    return {"scope": "synthetic reduced row-scaled rational SPD matrix; not target conditioning",
            "dimension": n, "tile": tile, "precision_bits": ctx.prec,
            "diagonal_definition": "2^-i, zero-based i", "all_factor_entries_checked": n * n,
            "known_factor_contained": True, "wrong_cross_update_entries_excluding_known": different,
            "all_solve_residual_intervals_contain_zero": True, "exact_solution_contained": True}


def float_probe(measure, d, seed):
    import numpy as np
    backends = numpy_backend(np)
    environment = {}
    for key in THREAD_VARIABLES:
        setting = os.environ.get(key, "")
        if re.fullmatch(r"[1-9][0-9]{0,4}", setting):
            environment[key] = int(setting)
    with measure.phase("float_six_array_construction") as phase:
        arrays = [np.empty((d, d), dtype=np.float64) for _ in range(6)]
        rng = np.random.default_rng(seed)
        rng.standard_normal(out=arrays[0])
        for i in range(d):
            np.add(arrays[0][i, i + 1:], arrays[0][i + 1:, i], out=arrays[0][i, i + 1:])
            arrays[0][i, i + 1:] *= 0.5
            arrays[0][i + 1:, i] = arrays[0][i, i + 1:]
        for index in range(1, 6):
            np.copyto(arrays[index], arrays[0])
        phase["six_arrays_materialized"] = snapshot()
        phase["six_arrays_bytes"] = sum(array.nbytes for array in arrays)
    with measure.phase("float_full_eigenspectrum_and_vectors") as phase:
        values, vectors = np.linalg.eigh(arrays[0])
        phase["six_arrays_and_eigenvectors_live"] = snapshot()
        require(values.shape == (d,) and vectors.shape == (d, d), "incomplete eigensolver output")
        require(bool(np.isfinite(values).all() and np.isfinite(vectors).all()), "nonfinite eigensolver output")
    with measure.phase("float_selected_eigenpair_residuals"):
        norm = float(np.linalg.norm(arrays[0], ord="fro"))
        checks = []
        for index in sorted({0, d // 2, d - 1}):
            vector = vectors[:, index]
            residual = arrays[0] @ vector - values[index] * vector
            relative = float(np.linalg.norm(residual) / max(norm + abs(float(values[index])), np.finfo(float).tiny))
            tolerance = float(1000 * d * np.finfo(float).eps)
            require(relative <= tolerance, "floating eigenpair residual exceeds declared tolerance")
            checks.append({"index": index, "relative_residual": relative, "tolerance": tolerance})
        # Read every retained array so the report records the actual materialized working set.
        checksums = [float(np.sum(array)) for array in arrays]
    return {"scope": "synthetic float64 full eigensolver working-set reference; not a proof or speed forecast",
            "dimension": d, "six_arrays_bytes": 6 * d * d * 8,
            "full_spectrum_count": int(values.size), "full_eigenvector_shape": list(vectors.shape),
            "selected_residual_checks": checks, "six_array_sums": checksums,
            "numpy_version": np.__version__, "numpy_backends": backends,
            "blas_environment": environment, "eigensolver": "numpy.linalg.eigh",
            "peak_accounting": "Windows process snapshots include cumulative process peaks, not isolated phase peaks"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=("exact", "proposal", "control"))
    parser.add_argument("--inputs", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    # Exclusive creation prevents replacement of any earlier measurement.
    with args.output.open("x", encoding="utf-8") as output:
        measure = Measurement()
        report = {"format": "exact-workspace-probe-v2", "mode": args.mode,
                  "target_positivity_proved": False, "full_target_matrices_computed": False,
                  "production_admission": False, "phases": measure.phases,
                  "scope": "contained synthetic nonproof measurements",
                  "script": {"role": "exact-workspace-probe", "sha256": digest(__file__)},
                  "software": {"python": ".".join(map(str, sys.version_info[:3])), "platform": sys.platform,
                               "python_flint": flint.__version__,
                               "flint_threads": ctx.threads}, "initial_snapshot": snapshot()}
        code = 0
        try:
            with measure.phase("input_binding_validation"):
                input_path = args.inputs.resolve()
                report["inputs"] = {"sha256": digest(input_path)}
                inputs = json.loads(input_path.read_text(encoding="utf-8-sig"))
                for key, expected in DECLARATION.items():
                    if type(inputs.get(key)) is not int or inputs[key] != expected:
                        raise ValueError(f"input declaration mismatch: {key}")
                if not isinstance(inputs.get("bindings"), dict):
                    raise ValueError("bindings must be an object")
                bindings = []
                for key, entry in inputs["bindings"].items():
                    path = Path(entry["path"])
                    if not path.is_absolute():
                        path = ROOT / path
                    actual = digest(path)
                    if actual.lower() != entry["sha256"].lower():
                        raise ValueError(f"binding digest mismatch: {key}")
                    bindings.append(actual)
                report["validated_binding_sha256"] = sorted(bindings)
                report["declaration"] = {key: inputs[key] for key in DECLARATION}
            control = args.mode == "control"
            if control:
                report["control_dimensions"] = {"exact": 5, "panel": 3, "reduced": 9, "tile": 4, "float": 9}
                report["scope"] = "tiny synthetic control only; no heavy target-shaped allocations"
            if args.mode in ("exact", "control"):
                report["exact"] = exact_probe(measure, 5 if control else inputs["dimension"],
                    3 if control else inputs["exact_panel"], inputs["seed"],
                    inputs["integer_bits"], inputs["witness_bits"])
                gc.collect()
            if args.mode in ("proposal", "control"):
                report["reduced"] = reduced_probe(measure, 9 if control else inputs["proposal_dimension"],
                                                   4 if control else inputs["proposal_tile"])
                with measure.phase("release_native_data_before_float"):
                    gc.collect()
                report["float"] = float_probe(measure, 9 if control else inputs["dimension"], inputs["seed"])
            report["status"] = "passed"
        except Exception as error:
            report["status"] = "failed"
            error_type = type(error)
            report["error"] = {"type": error_type.__name__ if error_type.__module__ == "builtins"
                               else "ProbeError"}
            if isinstance(error, OSError) and type(error.errno) is int:
                report["error"]["errno"] = error.errno
            code = 1
        finally:
            report["final_snapshot"] = snapshot()
            report["software"]["final_precision_bits"] = ctx.prec
            json.dump(report, output, indent=2, sort_keys=True, allow_nan=False)
            output.write("\n")
        event("program_finished", mode=args.mode, status=report["status"])
        return code


if __name__ == "__main__":
    raise SystemExit(main())
