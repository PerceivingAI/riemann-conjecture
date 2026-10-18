"""Fresh clean-source v3 proof-bearing *candidate* producer; NO theorem admission.

Requires an entirely clean committed repository BEFORE producing any proof
artifacts. Recomputes the original Arb matrix and exact rational witness, then
INDEPENDENTLY reconstructs ALL analytical intervals against the new packet.
Does not relabel the historical uncommitted SYS-4 research packet as clean.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from scripts.cert.export_combined_schur_v3 import ROOT, create_research, read_json
from scripts.verify_combined_schur_analytic_entries import run


def clean_git()->bool:
    status=subprocess.run(["git","status","--porcelain"],cwd=ROOT,capture_output=True,
                          text=True,check=True).stdout
    return not status.strip()


def execute(args:list[str],timeout:int)->None:
    p=subprocess.run([sys.executable,*args],cwd=ROOT,text=True,timeout=timeout,
                     capture_output=True)
    if p.returncode!=0:
        raise RuntimeError(f"fresh mathematical computation failed: {args[1]}: {p.stderr[-1500:]}")
    print(p.stdout[-800:],flush=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True,
                    help="New clean candidate output; not an admitted theorem")
    args=ap.parse_args()
    if not clean_git():
        raise SystemExit("FAIL CLOSED: fresh clean-source proof generation requires a clean committed Git tree")
    with tempfile.TemporaryDirectory(prefix="rh-v3-clean-") as d:
        path=Path(d)
        packet=path/"matrix-N192.json.gz"
        witness=path/"witness-N192.json.gz"
        audit=path/"independent-audit-N192.json"
        execute(["-m","scripts.run_combined_schur_experiment","--dimension","192",
                 "--precision","1024","--output",str(packet)],300)
        execute(["-m","scripts.prove_combined_schur_fast","--packet",str(packet),
                 "--output",str(witness),"--witness-bits","48"],240)
        p=read_json(packet)
        a=run(192,2048,p,False)
        if (not a["passes_all_stored_intervals"] or a["low_entries_checked"]!=18528
           or a["gram_entries_checked"]!=18528 or not a["mu_contained"]
           or not a["delta_contained"] or a["first_failures"]):
            raise RuntimeError("independent full analytical acceptance FAILED")
        audit.write_text(json.dumps(a,sort_keys=True,indent=2)+"\n",encoding="utf8")
        if not clean_git():
            raise RuntimeError("source tree became dirty during proof-bearing generation")
        output=args.output.resolve()
        result=create_research(packet,witness,audit,output,clean_source=True)
        assert result["provenance"]["status"]=="clean_candidate_pending_admission"
        print("V3_CLEAN_CANDIDATE_GENERATED_PENDING_ADMISSION",output,flush=True)
    # Gate A and Gate B replay on this exact newly written artifact is
    # still mandatory via scripts.verify_combined_schur_v3_bundle.


if __name__=="__main__":
    main()
