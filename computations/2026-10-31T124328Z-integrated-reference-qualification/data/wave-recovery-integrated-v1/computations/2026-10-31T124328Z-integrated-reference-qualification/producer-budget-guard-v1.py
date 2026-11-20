"""CONTROL_ONLY: exercise full source tile admission without evaluating source values."""
from flint import ctx


def evaluate(task, staging):
    from scripts.whole_source.execution import _WORKER
    from scripts.whole_source.pipeline import _tiles
    from scripts.whole_source.contract import QuantityKey
    from scripts.whole_source.producer import tile_account
    if (task.get('operation') != 'producer-budget-guard' or _WORKER is None or
            _WORKER[-1] is not staging or ctx.prec != staging.spec.problem.arithmetic.source_bits):
        raise RuntimeError('bound owned guard control required')
    maximum = {'private_bytes': 0, 'native_bytes': 0}
    counts = []
    for parity in (0, 1):
        count = 0
        for domain in _tiles(staging.spec, QuantityKey('A_model', parity)):
            account = tile_account(staging.spec.problem, domain.rows, domain.columns)
            for name in maximum:
                maximum[name] = max(maximum[name], account[name])
            count += 1
        counts.append(count)
    return {'status': 'PASS_CONTROL_ONLY_PRODUCER_TILE_ADMISSION', 'tiles_per_parity': counts,
            'maximum_required_bytes': maximum, 'precision_bits': ctx.prec,
            'private_allowance_mib': _WORKER[0].worker_private_mib,
            'native_allowance_mib': _WORKER[0].native_workspace_mib,
            'source_values_evaluated': False, 'scientific_acceptance': False}
