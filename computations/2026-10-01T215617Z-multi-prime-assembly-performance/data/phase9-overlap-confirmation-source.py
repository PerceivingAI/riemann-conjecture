from pathlib import Path
from fractions import Fraction
import json,tempfile,multiprocessing
from scripts.weil_multi_prime_continuation_driver import _confirm_candidate_precision_stability
from scripts.continuation_bundle import write_continuation_bundle,_result_payload_digest
out=Path("computations/2026-10-01T215617Z-multi-prime-assembly-performance/data")
base=json.loads((out/"phase9-overlap-base.json").read_text())
view={"dimension":40,"selected_matrix_bits":64,"selected_witness_bits":32,"attempts":[base]}
confirmation=_confirm_candidate_precision_stability(Fraction(2,5),40,view,32,precision_step=128,extra_steps=2,cache_dir=None)
assert confirmation["qualified"] and confirmation["selected_confirmation_precision_bits"]==384
(out/"phase9-overlap-confirmation.json").write_text(json.dumps(confirmation,indent=2)+"\n",encoding="utf-8")
high=next(item for item in confirmation["attempts"] if item["precision_bits"]==384)
(out/"phase9-overlap-confirmation-audit-inputs.json").write_text(json.dumps(high["audit_inputs"],indent=2)+"\n",encoding="utf-8")
view["candidate_precision_stability"]=confirmation
result={"role":"pre_theorem_multi_prime_continuation_driver","state":"CANDIDATE_READY","workflow_state":"CANDIDATE_READY","support":"2/5","active_terms":[2],"residual_order":32,"selected_candidate_dimension":40,"candidates":[view],"theorem_status":False,"independently_verified":False,"whitelisted":False,"automatic_promotion":False}
cleanup={"verified":not multiprocessing.active_children(),"executors_shutdown":0,"worker_processes_reaped":0,"cleanup_escalations":0,"workers_joined_after_shutdown":0,"workers_terminated":0,"workers_killed":0,"active_children_after_cleanup":len(multiprocessing.active_children()),"stages":[]}
with tempfile.TemporaryDirectory(prefix="phase9-packaging-smoke-") as temporary:
    manifest=write_continuation_bundle(result,Path(temporary),worker_cleanup=cleanup,result_payload_sha256=_result_payload_digest(result),provenance={"role":"component_packaging_smoke_not_qualification"})
    exact=[item for item in manifest["artifacts"] if item["kind"]=="pre_theorem_exact_candidate_audit"]
    assert len(exact)==2
    report={"role":"component_packaging_smoke_not_qualification","status":"PASS","audit_artifacts":exact,"source":"real_overlap_candidates","theorem_status":False,"canonical_driver_run":False}
    (out/"phase9-packaging-smoke.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print("Actual fixed 64/32 overlap confirmation 256 -> 384: CANDIDATE_STABLE")
print("Production bundle publication smoke: two exact audit artifacts sealed; not qualification")
