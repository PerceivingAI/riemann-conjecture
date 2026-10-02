from pathlib import Path
from datetime import datetime,timezone
import subprocess,json,time
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).with_name("phase11-acceptance.json")
COMMANDS=[['uv', 'run', '--locked', '--extra', 'test', 'python', '-m', 'pytest', '-q', 'tests/test_prime_power_terms.py', 'tests/test_prime_power_local_legendre.py', 'tests/test_multi_prime_legendre_schur.py', 'tests/test_multi_prime_potential_grouping.py', 'tests/test_multi_prime_assembly_performance.py', 'tests/test_multi_prime_candidate_audit.py', 'tests/test_multi_prime_p4_stages.py', 'tests/test_multi_prime_precision_diagnostics.py', 'tests/test_multi_prime_continuation_driver.py', 'tests/test_continuation_bundle.py', 'tests/test_one_prime_v1_freeze.py', 'tests/test_admission_consistency.py', 'tests/test_v2_adversarial_consistency.py', 'tests/test_pre_theorem_boundary.py', 'tests/test_certificate_v2_contract.py'], ['uv', 'run', '--locked', '--extra', 'test', 'python', '-m', 'pytest', '-q'], ['cargo', 'test', '--locked', '--workspace'], ['cargo', 'fmt', '--all', '--', '--check'], ['cargo', 'clippy', '--locked', '--workspace', '--all-targets', '--', '-D', 'warnings'], ['uv', 'run', '--locked', 'python', '-m', 'scripts.cert.verify_retained_proofs']]
def main():
    payload={"role":"Phase 11 full tooling acceptance, not qualification","status":"running","started_utc":datetime.now(timezone.utc).isoformat(),"results":[]}
    for command in COMMANDS:
        print("START "+" ".join(command),flush=True)
        started=time.perf_counter()
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=1800)
        payload["results"].append({"argv":command,"exit_code":result.returncode,"wall_seconds":time.perf_counter()-started,"stdout":result.stdout,"stderr":result.stderr})
        OUT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
        print(result.stdout+result.stderr,flush=True)
        if result.returncode:
            payload["status"]="failed";OUT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
            raise SystemExit(result.returncode)
    payload["status"]="PASS";payload["finished_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print("PHASE 11 FULL ACCEPTANCE PASS",flush=True)
if __name__=="__main__":main()
