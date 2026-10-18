"""Two-gate research validation for v3; NEVER grants theorem admission.

Gate A independently rebuilds every analytic interval from the *actual*
certificate input. Gate B invokes separately compiled zero-float Rust on that
same certificate. Hash metadata alone has no mathematical authority.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

from scripts.cert.export_combined_schur_v3 import parse_json_bytes,validate,to_analytic_packet,canonical_json,sha
from scripts.verify_combined_schur_analytic_entries import run

ROOT=Path(__file__).resolve().parents[1]


def check(candidate:Path,output:Path,rust_binary:Path,precision:int=2048)->dict:
    input_bytes=candidate.read_bytes()
    cert=parse_json_bytes(input_bytes)
    validate(cert)
    if cert["provenance"]["status"] not in (
        "research_uncommitted_not_proof_bearing", "clean_candidate_pending_admission"
    ):
        raise ValueError("unrecognized v3 provenance status")
    actual_auditor_hash=sha((ROOT/"scripts/verify_combined_schur_analytic_entries.py").read_bytes())
    if actual_auditor_hash!=cert["provenance"]["independent_auditor_sha256"]:
        raise ValueError("independent analytical implementation differs from candidate's pinned source")
    if precision!=2048:
        raise ValueError("fixed research reference precision must be 2048")
    packet=to_analytic_packet(cert)
    # The exact numerical source-input object being checked is the one from
    # the certificate, not a prior receipt / research packet on disk.
    input_sha=sha(canonical_json(packet))
    if cert["provenance"]["status"]=="clean_candidate_pending_admission":
        head=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,
                            capture_output=True,text=True,check=True).stdout.strip()
        status_command=["git","status","--porcelain","--untracked-files=all"]
        try:
            candidate_relative=candidate.resolve().relative_to(ROOT.resolve())
        except ValueError:
            candidate_relative=None
        if candidate_relative is not None:
            # The one newly generated proof artifact itself may be untracked;
            # never confuse that with a dirty mathematical *source* tree.
            status_command.extend(["--",".",":(exclude)"+candidate_relative.as_posix()])
        dirty=subprocess.run(status_command,cwd=ROOT,
                             capture_output=True,text=True,check=True).stdout
        if dirty.strip() or head!=cert["generator_metadata"]["git_commit"]:
            raise ValueError("clean-source certificate must be checked at its clean recorded commit")
    audit=run(192,precision,packet,False)
    if (audit["low_entries_checked"]!=18528 or audit["gram_entries_checked"]!=18528
         or not audit["passes_all_stored_intervals"] or audit["first_failures"]
         or not audit["mu_contained"] or not audit["delta_contained"]):
        raise ValueError("Gate A failure: full independent analytic input containment is not certified")
    executable=rust_binary
    if not executable.is_absolute():
        executable=ROOT/executable
    if not executable.is_file():
        raise ValueError("missing compiled independent Rust verifier")
    # Never let Gate B reopen a mutable input path that Gate A checked earlier.
    # The separately written private snapshot contains EXACTLY the original
    # candidate bytes; it is the only certificate path supplied to Rust.
    with tempfile.TemporaryDirectory(prefix="v3-two-gate-") as td:
        snapshot=Path(td)/"certificate-v3-input.json"
        snapshot.write_bytes(input_bytes)
        if sha(snapshot.read_bytes())!=sha(input_bytes):
            raise ValueError("candidate snapshot differs from Gate A input")
        executable_sha_before=sha(executable.read_bytes())
        proc=subprocess.run([str(executable),"verify-candidate-v3","--cert",str(snapshot),"--json"],
                            cwd=ROOT,capture_output=True,text=True,timeout=600)
        if sha(snapshot.read_bytes())!=sha(input_bytes) or sha(executable.read_bytes())!=executable_sha_before:
            raise ValueError("certificate or Rust executable changed during Gate B")
    if proc.returncode!=0:
        raise ValueError(f"Gate B Rust failure ({proc.returncode}): {proc.stderr[:1500]}")
    report=json.loads(proc.stdout)
    if (not report["exact_margin_positive"] or report["theorem_admitted"]
            or report["analytic_inputs_independently_verified_here"]
            or report["support_t"]!="11/20" or report["dimension"]!=192
            or report["claim"]!=cert["claim"] or report["format"]!=cert["format"]
            or report["admission_status"]!="UNADMITTED"
            or report["mathematical_status"]!="POSITIVE_RATIONAL_SCHUR_LOWER"
            or report["classification"]!="RESEARCH_EXACT_RATIONAL_ONLY_NOT_A_THEOREM"
            or Fraction(report["exact_margin"])<=0):
        raise ValueError("Gate B identity/positivity/trust mismatch")
    result={
      "format":"v3-research-two-gate-audit-v1",
      "candidate_sha256":sha(input_bytes),
      "actual_certificate_input_sha256":input_sha,
      "independent_source_file_sha256":sha((ROOT/"scripts/verify_combined_schur_analytic_entries.py").read_bytes()),
      "rust_executable_sha256":executable_sha_before,
      "analytic_result":audit,
      "rational_result":report,
      "gates":{"analytic_full_containment":"PASS","exact_rational_schur":"PASS","theorem_admission":"NOT_PERFORMED"},
      "research_only":True,
      "theorem_admitted":False,
      "status":"VALIDATED_PRETHEOREM_RESEARCH_ONLY",
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    temp=output.with_suffix(output.suffix+".partial")
    temp.write_bytes(canonical_json(result)+b"\n")
    os.replace(temp,output)
    print("V3_TWO_INDEPENDENT_GATES_PASS_PRETHEOREM_ONLY",
          "CANDIDATE_SHA",result["candidate_sha256"],
          "INPUT_SHA",input_sha,
          "EXACT_MARGIN_POSITIVE",report["exact_margin_positive"],flush=True)
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--rust-binary",type=Path,default=Path("target/debug/rh_cert.exe"))
    ap.add_argument("--precision",type=int,default=2048)
    args=ap.parse_args()
    check(args.candidate,args.output,args.rust_binary,args.precision)


if __name__=="__main__":
    main()
