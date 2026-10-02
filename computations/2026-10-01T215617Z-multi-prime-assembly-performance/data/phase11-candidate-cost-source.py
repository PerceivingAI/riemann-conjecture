from pathlib import Path
import sys,json,zipfile,hashlib,argparse
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from scripts import weil_multi_prime_continuation_driver as driver
from scripts import weil_multi_prime_support_candidate_check as candidate
from scripts.profile_multi_prime_workflow import _candidate_sample
from unittest.mock import patch

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--precision",type=int,required=True)
    parser.add_argument("--matrix-bits",type=int,default=64)
    parser.add_argument("--witness-bits",type=int,default=32)
    args=parser.parse_args()
    out=Path(__file__).parent
    payload={"role":"real uncached sequential target candidate cost sample, not confirmation or qualification","precision_bits":args.precision,"matrix_bits":args.matrix_bits,"witness_bits":args.witness_bits,"samples":[],"status":"running","theorem_status":False}
    result_path=out/f"phase11-candidates-{args.precision}-{args.matrix_bits}-{args.witness_bits}.json"
    original=candidate.run_candidate
    for n in (192,196):
        exact=None
        def capture(*positional,**keywords):
            nonlocal exact
            try:
                result=original(*positional,**keywords)
                exact=result["audit_inputs"]
                return result
            except candidate.CandidateStageError as error:
                exact=error.audit_inputs
                raise
        with patch.object(candidate,"run_candidate",capture):
            row=_candidate_sample(n,Fraction(11,20),args.precision,32,args.matrix_bits,args.witness_bits)
        if exact is not None:
            archive_path=out/f"phase11-candidate-inputs-N{n}-p{args.precision}-m{args.matrix_bits}-w{args.witness_bits}.zip"
            with zipfile.ZipFile(archive_path,"w",compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("candidate-inputs.json",json.dumps(exact))
            row["exact_inputs_archive"]=archive_path.name
            row["exact_inputs_sha256"]=hashlib.sha256(archive_path.read_bytes()).hexdigest()
        payload["samples"].append(row)
        result_path.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
        print(f"DONE N={n} p={args.precision} candidate={row['candidate_outcome']} wall={row['wall_seconds']:.3f}",flush=True)
    payload["status"]="completed"
    result_path.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
