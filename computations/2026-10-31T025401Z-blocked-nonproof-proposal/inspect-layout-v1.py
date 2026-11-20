"""Inspect complete declared .81 proposal accounts without numerical imports."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.whole_source.contract import bind_problem, canonical_bytes
from scripts.whole_source.proposal import _proposal_accounts
from scripts.whole_source.execution import MIB


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    problem = bind_problem('retained-t081')
    dimension = problem.N//2
    layouts = []
    for panel_size in (16,32):
        accounts = _proposal_accounts(dimension,panel_size)
        native_scratch_mib = (accounts['native_staging_bytes']+MIB-1)//MIB+16
        floating_scratch_mib = (accounts['floating_staging_bytes']+MIB-1)//MIB+16
        admissible = (accounts['native_result_bytes'] <= MIB and
            accounts['native_working_bytes'] <= 128*MIB and accounts['floating_working_bytes'] <= 128*MIB and
            accounts['per_parity_panel_disk_bytes']+64*MIB <= 8192*MIB)
        if panel_size==32 and not admissible:
            raise ValueError('standard full proposal layout exceeds its declared component/transport accounts')
        if accounts['native_staging_bytes'] <= 128*MIB:
            raise ValueError('full-stage inspection missed the superseded fixed-scratch shortage')
        layouts.append({'dimension_per_parity':dimension,'panel_size':panel_size,'accounts':accounts,
                        'derived_native_scratch_mib':native_scratch_mib,
                        'derived_floating_scratch_mib':floating_scratch_mib,
                        'component_transport_layout_within_declarations':admissible,
                        'full_rational_coordinates':2*dimension*dimension})
    if any(name in sys.modules for name in ('flint','numpy','scipy')):
        raise RuntimeError('metadata inspection imported a numerical backend')
    program = (ROOT/'scripts/whole_source/proposal.py').read_bytes()
    result = {'status':'PASS_DECLARED_PROPOSAL_LAYOUT_ACCOUNTS','layouts':layouts,
              'accounting_program_sha256':hashlib.sha256(program).hexdigest(),
              'inspection_program_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'scope':'DERIVED_COMPONENT_TRANSPORT_DISK_ACCOUNTS_ONLY',
              'resource_admission_executed':False,'full_supported_proposal':False,
              'native_verification_executed':False,'measured_full_stage_peak':False,
              'matrix_positivity':False,'production_admission':False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('xb') as stream:
        stream.write(canonical_bytes(result))
    print(json.dumps(result,sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
