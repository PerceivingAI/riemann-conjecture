"""Inspect task and evidence geometry; do not allocate a full numerical workload."""
from pathlib import Path
from fractions import Fraction
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    from scripts.whole_source import proposal, exact
    from scripts.whole_source.exact_tasks import layout
    from scripts.whole_source.contract import bind_problem, canonical_bytes
    problem = bind_problem('retained-t081')
    rows = []
    for width in (16, 32):
        accounts, blocks = [], []
        for parity in (0, 1):
            context = {'dimension': 413, 'panel_size': width, 'parity': parity, 'u': 80,
                       'endpoint_bits': 288, 'z_bits': 112}
            parameters = exact.paid_parameters(256, Fraction(3,2), problem.eta)
            account = exact.integer_bounds(context, parameters, problem.model_error)
            accounts.append(account)
            blocks.append({'context': context})
        geometry = layout({'blocks': blocks})
        p_accounts = proposal._proposal_accounts(413, width)
        rows.append({'panel_size': width, 'exact_accounts': accounts, 'exact_layout': geometry,
                     'proposal_accounts': p_accounts,
                     'explicit_operand_bit_assumptions': {'source_bits': 256, 'endpoint_bits': 288,
                                                         'transform_bits': 80, 'z_bits': 112, 'theta': '3/2'}})
    assert not any(name in sys.modules for name in ('flint','numpy','scipy'))
    result = {'status': 'PASS_METADATA_ONLY_TASK_LAYOUT_ACCOUNTS', 'rows': rows,
              'numerical_packages_imported': False, 'owned_workers_started': False,
              'full_stage_peaks_measured': False, 'full_qualification': False, 'production_admission': False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as stream:
        stream.write(canonical_bytes(result))
    print(json.dumps({'status': result['status'], 'rows': len(rows)}))


if __name__ == '__main__':
    main()
