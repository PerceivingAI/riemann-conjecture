"""Read retained signed quantities and exact endpoints; do not rerun native mathematics."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.whole_source.artifacts import CollectionSpec, decode_rational, encode_rational, _raw
from scripts.whole_source.contract import ArtifactRef, bind_problem, canonical_bytes, quantity_document
from scripts.whole_source.execution import _bytes, _json
from scripts.whole_source.gram import check_columns, check_entries, selected_keys, value_task, _read_complete


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "fresh verification output required")
    run = args.run_dir.resolve()
    state = _json(_bytes(run/"collection/slice-state.json"))
    receipt = ArtifactRef(**state["receipt"])
    report = _json(_raw(run/"collection", receipt, 8*1024**2))
    require(state["status"] == report["status"] == "VERIFIED_SELECTED_COMPLETE_SIGNED_QUANTITIES", "unaccepted signed run")
    problem = bind_problem("retained-t081")
    config = _json(_bytes(run/"inputs/execution.json"))
    bound, actual = {}, {}
    for role in ("producer", "analytic"):
        spec = CollectionSpec.from_dict(problem, config["roles"][role]["collection"])
        bound[role] = (spec, None)
        manifest = _json(_bytes(run/"collection"/role/"collection.json"))
        require(manifest["collection_id"] == spec.collection_id and
                canonical_bytes(manifest["collection"]) == canonical_bytes(spec.to_dict()), "changed role context")
        rows = []
        retained = report["roles"][role]
        require(len(retained["entries"]) == len(selected_keys(problem)), "incomplete selected role inventory")
        for key, row in zip(selected_keys(problem), retained["entries"]):
            require(row["quantity"] == quantity_document(key), "changed selected quantity mapping")
            ref = ArtifactRef(**row["chunk"])
            snapshot = _read_complete(spec, run/"collection"/role, value_task(spec, key), ref)
            require(len(snapshot.records) == 1, "incomplete selected expression")
            value = snapshot.records[0]
            require(row["lower"] == encode_rational(value.lower, 8192) and
                    row["upper"] == encode_rational(value.upper, 8192), "report differs from consumed chunk")
            rows.append(row)
        actual[role] = rows
        for receipt in retained["owned_receipts"]:
            folder = run/"collection"/role/"attempts"/retained["attempt_id"]/receipt["stage"]
            recorded = json.loads(_bytes(folder/"receipt.json"))
            require(recorded["worker_cleanup_verified"] is True and recorded["exit_code"] == 0,
                    "incomplete owned stage")
            for channel, ref in recorded["logs"].items():
                require(digest(folder/(channel+".txt")) == ref["sha256"], "changed raw stage stream")
    entries = check_entries(problem, actual["producer"], actual["analytic"])
    require(entries == report["entries"], "changed mathematical acceptance")
    columns = check_columns(problem, bound, run/"collection", report["roles"])
    require(columns == report["independent_columns"], "changed complete column acceptance")
    original_dir = ROOT/"computations/2026-10-27T140745Z-t081-complete-gram-attempt/data"
    source_raw = (original_dir/"source-v1.json").read_bytes()
    require(hashlib.sha256(source_raw).hexdigest() == "f69fee0feb9c08833ad6a3091718c9a6a301e5b5ddbea96ee5f0f6c0553c8b6e",
            "changed original reference source")
    original = json.loads(source_raw)
    comparisons = []
    for kind in ("A_model", "weighted_complete_tail"):
        for parity in (0, 1):
            ref = original["matrices"][kind+"-"+str(parity)]
            path = (original_dir/ref["path"]).resolve()
            require(path.is_relative_to(original_dir.resolve()), "reference packet escapes source directory")
            require(path.stat().st_size == ref["size"] and digest(path) == ref["sha256"], "changed reference packet")
            packet = json.loads(gzip.decompress(path.read_bytes()))
            for row in entries:
                q = row["quantity"]
                if q["name"] != kind or q["parity"] != parity:
                    continue
                m, n = q["entry"]
                i, j, d = m//2, n//2, problem.N//2
                offset = i*d-i*(i-1)//2+j-i
                lower, upper = (Fraction(v, 1 << original["bits"]) for v in packet["upper_triangle"][offset])
                lo, hi = (decode_rational(v, 8192) for v in row["publication"])
                require(max(lo, lower) <= min(hi, upper), "new and retained reference enclosures disagree")
                comparisons.append({"quantity": q, "enclosures_intersect": True})
    require(len(comparisons) == 12, "incomplete reference comparison")
    result = {"format": "retained-selected-signed-verification-v1", "status": "PASS_RETAINED_SELECTED_SIGNED_EVIDENCE",
              "selected_quantities": len(entries), "complete_column_entries": columns["entries"],
              "reference_comparisons": comparisons, "all_owned_cleanup_verified": True,
              "fresh_native_reconstruction": False, "matrix_positivity": False, "production_admission": False,
              "scope": "RETAINED_EXACT_ENDPOINT_AND_IDENTITY_CHECK_ONLY"}
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({k: result[k] for k in ("status", "selected_quantities", "complete_column_entries")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
