"""Admit and independently REPLAY the *one* closed v3 retained theorem artifact.

The manifest cannot broaden the theorem whitelist. Acceptance always checks
immutable approved bytes, clean committed mathematical source, complete
independent Arb-2048 analytical enclosures, and separate exact Rust theorem
replay. Source hashes are provenance controls, NEVER mathematical proofs.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

from scripts.cert.export_combined_schur_v3 import (
    canonical_json, parse_json_bytes, to_analytic_packet, validate, sha,
)
from scripts.verify_combined_schur_analytic_entries import run

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"computations/retained-proofs-v3.json"
APPROVED_CERT_REL="computations/2026-10-18T010000Z-v3-clean-proof-candidate/data/certificate-v3-clean.json"
APPROVED_SHA="f9948f22010d258d1c01c988fd0f18a3110c3c13453473c8c48953560a7fffcb"
SOURCE_COMMIT="f0350f89ec5189648cfc271c4ddd3a97355a2343"
AUDITOR_SHA="15961f4b337e1d26cc63aa41bcb3976fa975636d0b5e006b0f51bd3d625576e4"
CLAIM="C-0067"
EXPECTED={
 "claim":CLAIM,
 "computation_id":"X-20261018-002",
 "certificate_path":APPROVED_CERT_REL,
 "certificate_sha256":APPROVED_SHA,
 "source_commit":SOURCE_COMMIT,
 "independent_analytic_source_sha256":AUDITOR_SHA,
 "support_T":"11/20",
 "dimension":192,
 "claim_profile":"combined_multi_prime_legendre_schur",
 "verified_scope":"localized_weil_smooth_test_positivity_T_11_20",
}
SOURCES=(
 "scripts/run_combined_schur_experiment.py",
 "scripts/cert/mixed_gram_research.py",
 "scripts/prove_combined_schur_fast.py",
 "scripts/cert/export_combined_schur_v3_clean.py",
 "scripts/verify_combined_schur_analytic_entries.py",
)


def checked_manifest(path:Path=MANIFEST)->dict[str,Any]:
    data=parse_json_bytes(path.read_bytes())
    if set(data)!={"format","proofs"} or data["format"]!="rh-retained-proofs-v3":
        raise ValueError("not the closed independent v3 retained manifest")
    if not isinstance(data["proofs"],list) or len(data["proofs"])!=1:
        raise ValueError("the v3 retained proof list must contain exactly one entry")
    proof=data["proofs"][0]
    if type(proof) is not dict or proof!=EXPECTED:
        raise ValueError("v3 manifest does not match exact independently authorized C-0067 identity")
    rel=PurePosixPath(proof["certificate_path"])
    if rel.is_absolute() or '..' in rel.parts or str(rel)!=proof["certificate_path"]:
        raise ValueError("noncanonical v3 proof relative path")
    return proof


def committed_source_sha(path:str)->str:
    proc=subprocess.run(["git","show",f"{SOURCE_COMMIT}:{path}"],cwd=ROOT,
                        capture_output=True,check=True,timeout=20)
    return sha(proc.stdout)


def verify_committed_sources()->dict[str,str]:
    # The immutable certificate's original generator code and the exact
    # independently audited source expressions are pinned to the CLEAN source
    # commit. A later modified script cannot silently count as that audit.
    subprocess.run(["git","cat-file","-e",f"{SOURCE_COMMIT}^{{commit}}"],
                   cwd=ROOT,capture_output=True,check=True,timeout=20)
    found={}
    for item in SOURCES:
        actual=sha((ROOT/item).read_bytes())
        committed=committed_source_sha(item)
        if actual!=committed:
            raise ValueError(f"v3 mathematical source differs from clean committed proof version: {item}")
        found[item]=actual
    if found["scripts/verify_combined_schur_analytic_entries.py"]!=AUDITOR_SHA:
        raise ValueError("independent Arb analytical evaluator not at admitted version")
    return found


def replay(output:Path,manifest:Path=MANIFEST,*,binary:Path=Path("target/debug/rh_cert.exe"))->dict[str,Any]:
    proof=checked_manifest(manifest)
    manifest_sha_at_start=sha(manifest.read_bytes())
    sources=verify_committed_sources()
    cert_path=ROOT/proof["certificate_path"]
    if cert_path.is_symlink() or not cert_path.is_file():
        raise ValueError("v3 retained artifact must be a regular repository file")
    raw=cert_path.read_bytes()
    if sha(raw)!=APPROVED_SHA:
        raise ValueError("retained v3 certificate hash mismatch")
    cert=parse_json_bytes(raw)
    validate(cert)
    if (cert["provenance"]["status"]!="clean_candidate_pending_admission"
        or cert["generator_metadata"]["git_dirty"] is not False
        or cert["generator_metadata"]["git_commit"]!=SOURCE_COMMIT
        or cert["provenance"]["independent_auditor_sha256"]!=AUDITOR_SHA
        or cert["claim"]!="research-combined-schur-T11-20-N192"):
        raise ValueError("v3 clean-source identity mismatch")

    # Source is recomputed, not read from a PASS receipt.
    packet=to_analytic_packet(cert)
    input_sha=sha(canonical_json(packet))
    analytical=run(192,2048,packet,False)
    if (analytical["low_entries_checked"]!=18528
        or analytical["gram_entries_checked"]!=18528
        or not analytical["passes_all_stored_intervals"]
        or not analytical["mu_contained"]
        or not analytical["delta_contained"]
        or analytical["first_failures"]):
        raise ValueError("v3 analytical enclosure acceptance FAILURE")

    tool=binary if binary.is_absolute() else ROOT/binary
    if not tool.is_file():
        raise ValueError("independent zero-float Rust rh_cert executable missing")
    before=sha(tool.read_bytes())
    with tempfile.TemporaryDirectory(prefix="v3-retained-exact-") as td:
        snap=Path(td)/"certificate-v3.json"
        snap.write_bytes(raw)
        proc=subprocess.run([str(tool),"verify","--cert",str(snap),"--json"],
                            cwd=ROOT,capture_output=True,text=True,timeout=150)
        if sha(snap.read_bytes())!=APPROVED_SHA or sha(tool.read_bytes())!=before:
            raise ValueError("verifier input or binary modified during admitted exact replay")
    # Guard the full analytic/Rust replay against simultaneous source, proof,
    # or manifest changes; the recorded result must bind to the same inputs.
    if (sha(cert_path.read_bytes())!=APPROVED_SHA
        or sha(manifest.read_bytes())!=manifest_sha_at_start
        or verify_committed_sources()!=sources):
        raise ValueError("retained v3 manifest, certificate or mathematical sources changed during replay")
    if proc.returncode!=0:
        raise ValueError(f"Rust admitted exact theorem verification failed: exit={proc.returncode}, {proc.stderr[-1100:]}")
    accepted=json.loads(proc.stdout)
    if any(accepted.get(key)!=value for key,value in {
        "passed":True,"claim":CLAIM,"format":"rh-weil-certificate-v3",
        "claim_profile":proof["claim_profile"],"verified_scope":proof["verified_scope"],
        "dimension":192,"support_T":"11/20","parity_sector":"both",
    }.items()):
        raise ValueError("Rust theorem PASS identity does not match retained v3 manifest")
    sr=accepted.get("schur_report")
    if not isinstance(sr,dict) or sr.get("is_positive_definite") is not True:
        raise ValueError("independent Rust strict Schur positivity was not shown")
    for block in ("even","odd"):
        if sr[block]["is_positive_definite"] is not True:
            raise ValueError("an exact parity congruence failed")
    result={
        "format":"rh-retained-v3-admission-replay-v1",
        "admitted_claim":CLAIM,
        "source_commit":SOURCE_COMMIT,
        "certificate_sha256":APPROVED_SHA,
        "manifest_sha256":manifest_sha_at_start,
        "canonical_input_sha256":input_sha,
        "analytical_source_sha256":AUDITOR_SHA,
        "committed_mathematical_sources":sources,
        "rust_binary_sha256":before,
        "analytical_verification":{
            "precision_bits":2048,
            "low_entries_checked":analytical["low_entries_checked"],
            "gram_entries_checked":analytical["gram_entries_checked"],
            "all_intervals_contained":True,
            "mu_contained":True,
            "delta_contained":True,
        },
        "rust_outcome":accepted,
        "overall":"PASS_ONE_ADMITTED_FIXED_SUPPORT",
        "scope":"Suzuki localized Weil smooth test class at T=11/20 only",
        "rh_status":"UNRESOLVED",
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    temp=output.with_name(output.name+".partial")
    temp.write_bytes(canonical_json(result)+b"\n")
    os.replace(temp,output)
    print("V3_RETAINED_ADMISSION_PASS",CLAIM,"SOURCE",SOURCE_COMMIT,
          "ENTRIES",37056,"CERT_SHA",APPROVED_SHA,flush=True)
    return result


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",type=Path,default=MANIFEST)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--rust-binary",type=Path,default=Path("target/debug/rh_cert.exe"))
    args=ap.parse_args()
    replay(args.output,args.manifest,binary=args.rust_binary)


if __name__=="__main__":
    main()
