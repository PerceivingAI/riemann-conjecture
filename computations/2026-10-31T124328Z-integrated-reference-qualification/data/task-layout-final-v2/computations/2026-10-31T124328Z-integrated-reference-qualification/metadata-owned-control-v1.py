"""Owned exact-polynomial artifact staging, explicitly not source mathematics."""
from dataclasses import asdict
from fractions import Fraction
from scripts.whole_source.artifacts import IntervalRecord, _task, _coordinates


def evaluate(task, staging):
    from scripts.whole_source import execution
    from scripts.whole_source.contract import ContractError
    if execution._WORKER is None or execution._WORKER[-1] is not staging:
        raise ContractError('structural control requires its actual owned staging context')
    domain = _task(task['domain'])
    quantity = staging.spec.quantity(domain.quantity)
    records = []
    for row, column in _coordinates(domain, quantity.symmetric_upper):
        value = Fraction((row+1)*(column+3),8)
        records.append(IntervalRecord(row,column,(0,),value-Fraction(1,32),value+Fraction(3,64)))
    staged = staging.stage_chunk(domain,records)
    return {'scope':'CONTROL_ONLY_STRUCTURAL_NOT_WEIL_SOURCE','domain':domain.to_dict(),
        'artifact':asdict(staged.ref),'generation':staged.generation,'attempt_id':staged.attempt_id}
