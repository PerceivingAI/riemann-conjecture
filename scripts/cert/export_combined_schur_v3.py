"""Strict v3 combined-Schur schema and research export; theorem admission never happens here."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[2]
SCHEMA=ROOT/"docs/contracts/rh-weil-certificate-v3.json"
FORMAT="rh-weil-certificate-v3"
PROFILE="combined_multi_prime_legendre_schur"
IDENTITY="research-combined-schur-T11-20-N192"
SOURCE_PACKET_SHA="655d481d638f8b6fba0f95d01a4bab45079d905fbc6cb4f3e822571729d4d7c1"
SOURCE_WITNESS_SHA="d9130344b09978fe84026dff0cbe3bf54cbda4c0603828af9f36cc84a32fc48f"


def _unique_pairs(pairs:list[tuple[str,Any]])->dict[str,Any]:
    result={}
    for key,value in pairs:
        if key in result:raise ValueError(f"duplicate JSON key: {key}")
        result[key]=value
    return result


def canonical_json(value:Any)->bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")


def sha(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()


def parse_json_bytes(data:bytes)->dict[str,Any]:
    root=json.loads(data,object_pairs_hook=_unique_pairs,
                    parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))
    if not isinstance(root,dict):raise ValueError("expected JSON object")
    return root


def read_json(path:Path)->dict[str,Any]:
    data=path.read_bytes()
    if path.name.endswith(".gz"):
        data=gzip.decompress(data)
    return parse_json_bytes(data)


def check_integer(text:Any)->int:
    if type(text) is not str or re.fullmatch(r"(?:0|-[1-9][0-9]*|[1-9][0-9]*)",text) is None:
        raise ValueError("noncanonical v3 integer")
    return int(text)


def validate(c:dict[str,Any])->None:
    validator=Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf8")),format_checker=FormatChecker())
    errors=list(validator.iter_errors(c))
    if errors:
        errors.sort(key=lambda err:str(list(err.absolute_path)))
        raise ValueError(f"v3 schema: {list(errors[0].absolute_path)} {errors[0].message}")
    if type(c["generator_metadata"]["git_dirty"]) is not bool:
        raise ValueError("invalid dirty marker")
    prov=c["provenance"]["status"]
    if prov=="clean_candidate_pending_admission" and c["generator_metadata"]["script"]!="scripts/cert/export_combined_schur_v3_clean.py":
        raise ValueError("clean provenance requires the clean-source producer")
    if prov=="research_uncommitted_not_proof_bearing" and c["generator_metadata"]["script"]!="scripts/cert/export_combined_schur_v3.py":
        raise ValueError("historical research provenance requires the research exporter")
    if prov=="clean_candidate_pending_admission" and c["generator_metadata"]["git_dirty"]:
        raise ValueError("dirty source cannot claim clean proof provenance")
    if prov=="research_uncommitted_not_proof_bearing" and not c["generator_metadata"]["git_dirty"]:
        raise ValueError("clean source cannot reuse historical research-only proof claim")
    n=c["dimension"]
    for key in ("low_A_triangular","truncated_gram_triangular"):
        rows=c[key]
        for i,row in enumerate(rows):
            if len(row)!=n-i:raise ValueError(f"{key}: invalid row length {i}")
            for offset,pair in enumerate(row):
                a,b=map(check_integer,pair)
                if a>b:raise ValueError(f"{key}: reversed interval {i},{i+offset}")
                if offset%2 and (a!=0 or b!=0):
                    raise ValueError(f"{key}: opposite parity must be exactly zero")
    for key in ("mu_dyadic","delta_dyadic"):
        a,b=map(check_integer,c[key])
        if a>b:raise ValueError(f"reversed {key}")
        if key=="mu_dyadic" and a<=0:raise ValueError("nonpositive complement")
        if key=="delta_dyadic" and a<0:raise ValueError("negative residual bound")
    for i,row in enumerate(c["witness_numerators"]):
        if len(row)!=n:raise ValueError("witness size")
        for j,v in enumerate(row):
            value=check_integer(v)
            if j>i and value!=0:raise ValueError("witness not lower triangular")
            if (i-j)%2 and value!=0:raise ValueError("witness parity mismatch")
            if i==j and value==0:raise ValueError("singular witness")


def to_analytic_packet(c:dict[str,Any])->dict[str,Any]:
    """Only the exact v3 input fields; no original generator flags/sign metadata."""
    validate(c)
    return {
      "format":"pretheorem-combined-schur-rational-inputs-v1",
      "support":[11,20],"dimension":192,"precision_bits":1024,
      "residual_order":32,"active_terms":[2,3],
      "basis":"ordinary_unnormalized_legendre","dyadic_bits":352,
      "eta":[1,2**24],
      "low_A_triangular":[[list(map(check_integer,p)) for p in row] for row in c["low_A_triangular"]],
      "truncated_gram_triangular":[[list(map(check_integer,p)) for p in row] for row in c["truncated_gram_triangular"]],
      "mu_dyadic":list(map(check_integer,c["mu_dyadic"])),
      "delta_dyadic":list(map(check_integer,c["delta_dyadic"])),
    }


def create_research(packet:Path,witness:Path,audit:Path,output:Path,*,clean_source:bool=False)->dict[str,Any]:
    source_bytes=packet.read_bytes()
    proof_bytes=witness.read_bytes()
    if not clean_source and (sha(source_bytes)!=SOURCE_PACKET_SHA or sha(proof_bytes)!=SOURCE_WITNESS_SHA):
        raise ValueError("historical research exporter accepts only the original fixed 2026-10-17 evidence")
    p=read_json(packet)
    w=read_json(witness)
    a=read_json(audit)
    if not a["passes_all_stored_intervals"] or a["low_entries_checked"]!=18528 or a["gram_entries_checked"]!=18528:
        raise ValueError("independent analytic audit did not cover all input entries")
    if not a["mu_contained"] or not a["delta_contained"] or a["first_failures"]:
        raise ValueError("independent analytic scalar/input audit did not pass")
    if not clean_source and sha(audit.read_bytes())!="f410045743461cd09c97cda0fa1119ecea2111d738982381ff89542c5058bb2f":
        raise ValueError("historical analytical audit output bytes are not the verified retained result")
    if w["packet_sha256"]!=sha(source_bytes):
        raise ValueError("witness references another source packet")
    if (p["dimension"],p["support"],p["eta"],p["active_terms"],p["dyadic_bits"]) != (192,[11,20],[1,2**24],[2,3],352):
        raise ValueError("wrong archived mathematical scope")
    base_status=subprocess.run(["git","status","--porcelain"],cwd=ROOT,capture_output=True,text=True,check=True).stdout
    if clean_source:
        if base_status:
            raise ValueError("clean proof-bearing candidate requires fully clean Git tree")
        for path,digest in p["source_sha256"].items():
            if sha((ROOT/path).read_bytes())!=digest:
                raise ValueError(f"clean source fingerprint mismatch: {path}")
    elif not base_status:
        raise ValueError("historical research exporter cannot label a clean tree: use a fresh proof-bearing producer")
    commit=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
    from flint import __version__ as flint_version
    result={
      "format":FORMAT,"claim":IDENTITY,"claim_profile":PROFILE,
      "support_T":{"num":"11","den":"20","frac":"11/20"},
      "basis":{"type":"legendre","domain":"[-1, 1]","normalization":"P_n(1)=1","norm_sq":"2/(2n+1)","dimension":192},
      "parity_sector":"both","dimension":192,"residual_order":32,"active_terms":[2,3],
      "eta":{"num":"1","den":"16777216"},"dyadic_bits":352,
      "low_A_triangular":[[[str(q) for q in pair] for pair in row] for row in p["low_A_triangular"]],
      "truncated_gram_triangular":[[[str(q) for q in pair] for pair in row] for row in p["truncated_gram_triangular"]],
      "mu_dyadic":[str(x) for x in p["mu_dyadic"]],
      "delta_dyadic":[str(x) for x in p["delta_dyadic"]],
      "witness_bits":48,
      "witness_numerators":[[str(v) for v in row] for row in w["witness_numerators"]],
      "provenance":{"status":"clean_candidate_pending_admission" if clean_source else "research_uncommitted_not_proof_bearing",
                    "original_packet_sha256":sha(source_bytes),
                    "original_witness_sha256":sha(proof_bytes),
                    "independent_input_audit_sha256":sha(audit.read_bytes()),
                    "independent_auditor_sha256":sha((ROOT/"scripts/verify_combined_schur_analytic_entries.py").read_bytes())},
      "generator_metadata":{"script":"scripts/cert/export_combined_schur_v3_clean.py" if clean_source else "scripts/cert/export_combined_schur_v3.py",
                           "git_commit":commit,"git_dirty":not clean_source,
                           "timestamp_utc":datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z"),
                           "precision_bits":1024,"independent_precision_bits":2048,
                           "versions":{"python":sys.version.split()[0],"flint":flint_version}},
    }
    validate(result)
    output.parent.mkdir(parents=True,exist_ok=True)
    tmp=output.with_suffix(output.suffix+".partial")
    tmp.write_bytes(canonical_json(result)+b"\n")
    os.replace(tmp,output)
    return result


def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--packet",type=Path,required=True)
    parser.add_argument("--witness",type=Path,required=True)
    parser.add_argument("--analytic-audit",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    r=create_research(args.packet,args.witness,args.analytic_audit,args.output)
    print("V3_RESEARCH_ARTIFACT_ONLY_NOT_PROOF_BEARING",args.output,"SHA256",sha(args.output.read_bytes()),
          "N",r["dimension"],"STATUS",r["provenance"]["status"],flush=True)


if __name__=="__main__":
    main()
