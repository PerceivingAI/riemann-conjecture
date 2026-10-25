"""Retained Fourier-case comparison and scalar controls; no new source matrix."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from flint import arb, ctx
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.prime_power_terms import enumerate_active_prime_power_terms

BASE='computations/2026-10-25T155033Z-fourier-minorant-sign'
POST='computations/2026-10-25T220817Z-post-m4-fourier-sign'
MODEL='computations/2026-10-25T211305Z-post-m4-scalar-cost-assessment/data/assessment-v1.json'


def decode(raw):
    return json.loads(raw,parse_float=Q)


def interval(value):
    lo,hi=arb_to_rational_enclosure(value)
    return {'lower':str(lo),'upper':str(hi),'display':value.str(16)}


def evaluate(input_root,pins_path):
    pins=json.loads(pins_path.read_text(encoding='utf-8'))
    members={item['path']:item for item in pins['members']}
    manifests={}
    for item in pins['members']:
        manifest_path=item['bundle_manifest']
        if manifest_path not in manifests:
            raw=(input_root/manifest_path).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=item['bundle_manifest_sha256']:
                raise ValueError('inherited bundle seal changed')
            manifests[manifest_path]=json.loads(raw)
        relative=Path(item['path']).relative_to(Path(manifest_path).parent).as_posix()
        member=next(row for row in manifests[manifest_path]['members'] if row['path']==relative)
        if member['sha256']!=item['sha256'] or member['bytes']!=item['bytes']:
            raise ValueError('input not bound by inherited seal')
        raw=(input_root/item['path']).read_bytes()
        if len(raw)!=item['bytes'] or hashlib.sha256(raw).hexdigest()!=item['sha256']:
            raise ValueError('inherited input bytes changed')
    def load(relative):
        if relative not in members:raise ValueError('unbound input requested')
        raw=(input_root/relative).read_bytes()
        return decode(gzip.decompress(raw) if relative.endswith('.gz') else raw)
    def case(directory,version,source_stage,proof_stage,audit_stage):
        source_path=f'{directory}/data/source-{version}.json.gz'
        proof_path=f'{directory}/data/proof-{version}.json.gz'
        source=load(source_path);proof=load(proof_path)
        audit=load(f'{directory}/data/independent-audit-{version}.json')
        if audit['status']!='PASS' or proof['status']!='COMPLETE_POSITIVE_SUFFICIENT_LOWER':
            raise ValueError('retained case does not carry complete acceptance')
        if (proof['source_packet_sha256']!=members[source_path]['sha256']
            or audit['source_packet_sha256']!=members[source_path]['sha256']
            or audit['input_sha256']!=members[proof_path]['sha256']):
            raise ValueError('accepted source/proof linkage changed')
        names={'P','P_squared','GP','pole','band','A'}
        if set(source['matrices'])!=names or set(audit['matrix_entries_checked'])!=names:
            raise ValueError('complete source inventory changed')
        slots={name:sum(len(row) for row in source['matrices'][name]) for name in names}
        if audit['matrix_entries_checked']!=slots or sum(slots.values())!=292968:
            raise ValueError('accepted complete input count changed')
        t=Q(*source['support'])
        with ctx.workprec(512):
            terms=enumerate_active_prime_power_terms(t.numerator,t.denominator,prec=512)
            r=sum((term.coefficient*(2-term.tau) for term in terms),arb(0))
            left,right=source['matrices']['P'][0][0]
            lo,hi=arb_to_rational_enclosure(r)
            scale=1<<source['bits']
            if not Q(-right,2*scale)<=lo<=hi<=Q(-left,2*scale):
                raise ValueError('constant-trial source normalization disagrees')
            rayleigh=interval(r)
        blocks={name:str(Q(block['mass_normalized_gap_exact'])) for name,block in audit['blocks'].items()}
        if set(blocks)!={'even','odd'} or any(Q(v)<=0 for v in blocks.values()):
            raise ValueError('both retained finite lowers must be positive')
        if blocks!={name:block['mass_normalized_gap_exact'] for name,block in proof['blocks'].items()}:
            raise ValueError('audited exact lower identity changed')
        return {'support':str(t),'a':source['a'],'omega':source['omega'],'dimension':source['dimension'],
                'source_Arb_precision':source['source_precision'],'audit_Arb_precision':audit['independent_source_precision'],
                'source_polynomial_order':source['arithmetic_order'],'audit_polynomial_order':audit['independent_arithmetic_order'],
                'source_frequency_order':source['frequency_order'],'audit_frequency_order':audit['independent_frequency_order'],
                'matrix_fractional_bits':source['bits'],'source_slots':sum(slots.values()),
                'active_terms':[term.m for term in terms], 'constant_trial_reference_lower_requirement':rayleigh,
                'complete_complement':source['complement'],
                'quadrature_operator_upper':source['quadrature_operator_error_upper'],
                'reported_finite_mass_lowers':blocks,'numerical_width_reports':source.get('numerical_order_loss_bounds'),
                'source_packet_compressed_bytes':members[source_path]['bytes'],
                'proof_packet_compressed_bytes':members[proof_path]['bytes'],
                'recorded_operation_seconds':{'source':str(source_stage),'proof':str(proof_stage),'audit':str(audit_stage)}}
    baseline_times=load(f'{BASE}/data/corrected-execution-receipts-v2.json')
    baseline_audit_time=load(f'{BASE}/data/independent-execution-receipt-v2.json')
    before=case(BASE,'v2',baseline_times['source_v2']['tool_wall_seconds'],
                baseline_times['proof_v2']['tool_wall_seconds'],baseline_audit_time['tool_wall_seconds'])
    after=case(POST,'v1',load(f'{POST}/data/source-v1.run.json')['elapsed_seconds'],
               load(f'{POST}/data/proof-v1.run.json')['elapsed_seconds'],
               load(f'{POST}/data/independent-audit-v1.run.json')['elapsed_seconds'])
    if before['support']!='1353/2048' or after['support']!='3/4':
        raise ValueError('case identity changed')
    held=('a','omega','dimension','source_Arb_precision','audit_Arb_precision',
          'source_polynomial_order','audit_polynomial_order','audit_frequency_order','matrix_fractional_bits','source_slots')
    if any(before[key]!=after[key] for key in held):raise ValueError('declared held controls differ')
    model=load(MODEL)['work']
    timing_ratios={stage:str(Q(after['recorded_operation_seconds'][stage])/Q(before['recorded_operation_seconds'][stage]))
                   for stage in ('source','proof','audit')}
    lower_ratios={name:str(Q(after['reported_finite_mass_lowers'][name])/Q(before['reported_finite_mass_lowers'][name]))
                  for name in ('even','odd')}
    harmonic=sum((Q(1,n) for n in range(1,11)),Q())
    euler=Q(1)
    for prime in (2,3,5,7):euler*=Q(prime,prime-1)
    omitted=Q(1)
    for prime in (2,5,7):omitted*=Q(prime,prime-1)
    if not euler>=harmonic>omitted:raise ValueError('finite Euler coverage countercontrol failed')
    threshold_ratio=Q(15,(2*1+1)*(2*1+3))
    next_ratio=Q(15,(2*2+1)*(2*2+3))
    if threshold_ratio!=1 or not next_ratio<1:raise ValueError('strict geometric prerequisite control failed')
    return {'format':'retained-fourier-structural-assessment-v1','scope':'retained metadata/exact accounting and scalar controls only; no matrix regeneration',
            'baseline':before,'post_transition':after,'held_controls':list(held),
            'recorded_timing_ratios_post_to_baseline':timing_ratios,
            'timing_ratio_scope':'different supports, arithmetic, inflation bookkeeping and timer instrumentation; descriptive only, not speedup or scaling law',
            'reported_finite_lower_ratios_post_to_baseline':lower_ratios,
            'finite_lower_ratio_scope':'different sufficient matrices and rational congruence/trace certificates, not a spectral-gap ratio',
            'classical_contraction_proxy_ratios':{'source':model['producer_proxy_ratio'],'audit':model['audit_proxy_ratio']},
            'numerical_width_comparison':'new case reports separated widths; baseline has no equivalent report, so improvement cannot be inferred',
            'controls':{'constant_trials_contained_in_both_original_source_intervals':True,
                        'finite_Euler_product':str(euler),'harmonic_sum_through10':str(harmonic),
                        'omitting_prime3_product':str(omitted),'strict_geometric_ratio_at_boundary':str(threshold_ratio),
                        'next_dimension_geometric_ratio':str(next_ratio)},
            'new_support_matrix_computed':False,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'input_pins_sha256':hashlib.sha256(pins_path.read_bytes()).hexdigest()}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=evaluate(args.input_root,Path(__file__).with_name('input-pins.json'))
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:
        handle.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'source_slots_each':292968,'new_support_matrix_computed':False,
                      'constant_trial_controls':'PASS','finite_series_controls':'PASS',
                      'observed_timing_ratios_are_speedup_claims':False}))
