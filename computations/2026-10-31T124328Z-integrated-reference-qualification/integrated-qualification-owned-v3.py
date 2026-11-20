"""Fresh supervised reduced-role and manufactured finite recovery controls.

No integrated mathematical approval, full-source run or independent review.
"""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import runpy
import sys
import traceback
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
METHODS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
ORIGIN = 'a06cb9a74da776b71aa0113a81ccff30dc8a81f0'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, document):
    from scripts.whole_source.contract import canonical_bytes
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(canonical_bytes(document))


def files(root):
    return {p.relative_to(root).as_posix(): {'sha256': digest(p), 'size': p.stat().st_size}
            for p in root.rglob('*') if p.is_file()}


def child(action, work):
    from scripts.whole_source import pipeline, resources, proposal, exact, recovery, execution
    from scripts.whole_source.contract import bind_problem
    from scripts.whole_source.supervision import require_current, event
    from scripts.weil_whole_source_split import main as cli
    work = Path(work)
    require_current()
    origin = {'origin_git_commit': ORIGIN, 'origin_git_dirty': True}
    allocator = resources.auto_plan
    def bounded(template, *, parallel, memory_mib=None, helper_root=ROOT):
        # Two CPUs is an explicit finite-control policy, not a production default.
        return allocator(template, parallel=parallel, cpus=2, helper_root=helper_root)
    calls, injections = [], []
    original_stage = execution.WorkloadExecution.run_stage
    original_commit = recovery.RecoveryJournal.commit
    def stage(owner, name, tasks):
        tasks = list(tasks)
        calls.append({'stage': name, 'attempt_id': owner.attempt_id,
                      'operations': [t['operation'] for t in tasks], 'tasks': len(tasks)})
        if action == 'audit-injected-failure' and not injections:
            tasks[0] = {**tasks[0], 'parity': 2}
            injections.append('REAL_OWNED_REJECTION_OF_INVALID_PARITY')
        return original_stage(owner, name, tasks)
    def commit(owner, key, group, value):
        result = original_commit(owner, key, group, value)
        target = 'factor-diagonal_0' if action == 'proposal-stop' else 'global'
        if action in ('proposal-stop', 'exact-stop') and key == target and not injections:
            injections.append('AFTER_AUTHENTIC_COMMITTED_WAVE')
            raise KeyboardInterrupt('CONTROL stop after committed '+key)
        return result
    source_inputs = work/'source-inputs'
    manufactured = work/'manufactured/original-source/source-manifest.json'
    with patch.object(resources, 'auto_plan', bounded), \
         patch.object(execution.WorkloadExecution, 'run_stage', stage), \
         patch.object(recovery.RecoveryJournal, 'commit', commit):
        try:
            event(action)
            if action == 'prepare-source':
                pipeline.prepare_source_inputs(bind_problem('retained-t081'), source_inputs,
                    control=True, tile_modes=2, **origin)
                result = {'status': 'BOUND_REDUCED_CONTROL_INPUTS'}
            elif action == 'source':
                result = cli(['source', '--problem', str(source_inputs/'problem.json'),
                    '--execution', str(source_inputs/'execution.json'), '--output-dir', str(work/'source')])
                assert result == 0
            elif action in ('audit-injected-failure', 'audit-retry'):
                result = cli(['audit', '--problem', str(source_inputs/'problem.json'),
                    '--execution', str(source_inputs/'execution.json'),
                    '--source', str(work/'source/producer/source-manifest.json'),
                    '--output-dir', str(work/action)])
                assert result == 0
            elif action == 'prepare-manufactured':
                factory = runpy.run_path(str(METHODS/'verify-variant-snapshots-v1.py'))['manufactured_inputs']
                problem, source, _, _ = factory(work/'manufactured', origin)
                proposal.prepare_proposal_inputs(problem, source.path, work/'proposal-inputs', panel_size=2, **origin)
                result = {'status': 'BOUND_MANUFACTURED_FINITE_INPUTS'}
            elif action.startswith('proposal-'):
                destination = work/('proposal-fresh' if action == 'proposal-fresh' else 'proposal-retry')
                argv = ['propose', '--problem', str(work/'proposal-inputs/problem.json'),
                    '--execution', str(work/'proposal-inputs/execution.json'), '--source', str(manufactured),
                    '--output-dir', str(destination)]
                if action == 'proposal-resume':
                    argv.append('--resume')
                result = cli(argv)
                assert result == 0
            elif action == 'prepare-exact':
                exact.prepare_exact_inputs(bind_problem('retained-t081'), manufactured,
                    work/'proposal-retry/proposal.json', work/'exact-inputs', **origin)
                result = {'status': 'BOUND_ACTUAL_FINITE_OPERANDS'}
            elif action.startswith('exact-'):
                destination = work/('exact-fresh' if action == 'exact-fresh' else 'exact-retry')
                argv = ['exact', '--problem', str(work/'exact-inputs/problem.json'),
                    '--execution', str(work/'exact-inputs/execution.json'), '--source', str(manufactured),
                    '--proposal', str(work/'proposal-retry/proposal.json'), '--output-dir', str(destination)]
                if action in ('exact-resume', 'exact-verify'):
                    argv.append('--resume')
                result = cli(argv)
                assert result == 0
            else:
                raise ValueError('unknown control action')
        except BaseException as exc:
            save(work.parent/(action+'-outcome.json'), {'action': action, 'outcome': 'ERROR',
                'error_type': type(exc).__name__, 'error': str(exc), 'traceback': traceback.format_exc(),
                'calls': calls, 'injections': injections, 'scientific_acceptance': False})
            raise
        else:
            save(work.parent/(action+'-outcome.json'), {'action': action, 'outcome': 'COMPLETED',
                'result': result, 'calls': calls, 'injections': injections, 'scientific_acceptance': False})
            event(action, state='complete')


def proposal_science(directory):
    from scripts.whole_source.proposal import PanelStore
    core = json.loads((directory/'proposal.json').read_bytes())
    values = []
    for block in core['blocks']:
        refs = {f"Z/{r['row']}/{r['column']}": r['artifact'] for r in block['integer_panels']}
        store = PanelStore(directory, block['context'], refs)
        values.append({'parity': block['parity'], 'theta': block['theta'], 'coordinates':
                       {name: store.read(name, 'integer') for name in sorted(refs)}})
    return values


def main():
    from scripts.whole_source import supervision as s, receipts, admission
    from scripts.whole_source.lifecycle_observations import lifecycle_resources
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--resume-control', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.relative_to(ROOT)
    output.mkdir(parents=True, exist_ok=False)
    prior = args.resume_control.resolve(strict=True)
    prior.relative_to(ROOT)
    work = prior/'operation'
    from scripts.whole_source import pipeline
    _, config, bound = pipeline._bind(work/'source-inputs/problem.json', work/'source-inputs/execution.json', ROOT)
    reader = pipeline.SourceReader(work/'source/producer/source-manifest.json', bound['producer'][0], control=True)
    assert config['control'] is True and sum(len(values) for _, values in reader.tiles()) == 36
    pipeline.verify_source_execution(reader)
    settings = {'format': s.POLICY, 'wall_seconds': 180, 'active_seconds': 2400,
        'grace_seconds': 3, 'memory_mib': None, 'sample_milliseconds': 1000,
        'stale_milliseconds': 10000, 'observation_bytes': 16*s.MIB}
    save(output/'policy.json', settings)
    rows, protected = [], {'original-source': (work/'source', files(work/'source'))}
    actions = ('audit-injected-failure', 'audit-retry',
        'prepare-manufactured', 'proposal-fresh', 'proposal-stop', 'proposal-resume',
        'prepare-exact', 'exact-fresh', 'exact-stop', 'exact-resume', 'exact-verify')
    self_path = Path(__file__).resolve()
    self_hash = digest(self_path)
    try:
        for action in actions:
            if action == 'audit-retry':
                protected['failed-audit'] = (work/'audit-injected-failure', files(work/'audit-injected-failure'))
            if action == 'proposal-resume':
                protected['proposal-producer'] = (work/'proposal-retry/native-0/attempts',
                    files(work/'proposal-retry/native-0/attempts'))
            if action == 'exact-resume':
                protected['exact-producer'] = (work/'exact-retry/collection/attempts',
                    files(work/'exact-retry/collection/attempts'))
            if action == 'exact-verify':
                protected['complete-exact'] = (work/'exact-retry/report.json', digest(work/'exact-retry/report.json'))
            wrapper = output/(action+'-child.py')
            source = ('from pathlib import Path\nimport hashlib,runpy\n'
                f'p=Path({str(self_path)!r})\n'
                f'assert hashlib.sha256(p.read_bytes()).hexdigest()=={self_hash!r}\n'
                f'runpy.run_path(str(p))["child"]({action!r},{str(work)!r})\n')
            wrapper.write_text(source, encoding='utf-8')
            receipt = s.supervise([], observation_root=prior/'operation.lifecycle', operation_root=work,
                                   policy_document=settings, script=wrapper)
            outcome_path = prior/(action+'-outcome.json')
            outcome = json.loads(outcome_path.read_bytes()) if outcome_path.exists() else None
            intentional = action in ('audit-injected-failure', 'proposal-stop', 'exact-stop')
            row = {'action': action, 'receipt': receipt, 'outcome': outcome,
                   'expected_interruption': intentional}
            rows.append(row)
            save(output/(action+'-check.json'), row)
            assert receipt['cleanup_verified'] is True and receipt['final_job']['active_process_count'] == 0
            assert receipt['status'] == ('INTERRUPTED' if intentional else 'COMPLETED'), row
            assert outcome is not None
            assert outcome['outcome'] == ('ERROR' if intentional else 'COMPLETED'), row
            if intentional:
                assert outcome['injections'], row
            if action == 'audit-retry':
                audit = json.loads((work/'audit-retry/analytical-receipt.json').read_bytes())
                assert audit['entries_checked'] == 36 and audit['full_mathematical_source'] is False
            if action == 'proposal-resume':
                assert proposal_science(work/'proposal-fresh') == proposal_science(work/'proposal-retry')
                assert all(c['stage'] != 'factor-diagonal_0' for c in outcome['calls'][:1])
            if action == 'exact-resume':
                left = json.loads((work/'exact-fresh/report.json').read_bytes())
                right = json.loads((work/'exact-retry/report.json').read_bytes())
                fields = ('parity', 'dimension', 'goal', 'width', 'margin', 'tau', 'direction_index',
                          'direction_upper', 'direction_mass', 'row_margins', 'transformed_digest',
                          'transformed_upper_entries', 'modular', 'source_tiles_consumed')
                assert [{k:b[k] for k in fields} for b in left['blocks']] == [{k:b[k] for k in fields} for b in right['blocks']]
                assert left['assessment'] == right['assessment']
                assert right['proof_scope'] == 'CONTROL_ONLY'
                assert [c['stage'] for c in outcome['calls']] == ['first', 'second', 'reduce', 'assess']
            if action == 'exact-verify':
                assert outcome['calls'] == []
            print(json.dumps({'action': action, 'status': receipt['status'],
                              'owned_stages': len(outcome['calls'])}), flush=True)
        for name, (path, before) in protected.items():
            if isinstance(before, str):
                assert digest(path) == before, name
            else:
                assert all((path/key).is_file() and digest(path/key) == ref['sha256']
                           for key, ref in before.items()), name
        all_stages, failed = [], []
        for path in receipts.discover_receipts(work):
            raw = json.loads(path.read_bytes())
            assert raw['worker_cleanup_verified'] is True
            if raw['exit_code'] == 0 and raw['error'] is None:
                all_stages.append(receipts.verify_stage(path)['record'])
            else:
                failed.append(asdict_from_path(path))
        assert len(failed) == 1
        observed = files(work)
        logical = sum(ref['size'] for ref in observed.values())
        forecast = admission.topology(__import__('scripts.whole_source.contract', fromlist=['bind_problem']).bind_problem('retained-t081'))
        # This broad full-profile ceiling is NOT validation of a reduced demand forecast.
        report = {'format': 'whole-source-integrated-software-qualification-v3',
            'created_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'status': 'PASS_REDUCED_ROLES_AND_FINITE_RECOVERY_ONLY', 'actions': rows,
            'successful_stages': all_stages, 'failed_stages': failed,
            'history_byte_identity': True, 'original_source_control': str(prior), 'reduced_entries_checked': 36,
            'actual_logical_retained_bytes': logical, 'actual_retained_files': len(observed),
            'full_profile_logical_ceiling_bytes': forecast['logical_allowance_bytes'],
            'small_forecast_validation': 'PENDING_ROLE_SPECIFIC_ACCOUNT_CHECK',
            'lifecycle': lifecycle_resources(prior/'operation.lifecycle'),
            'full_qualification': False, 'scientific_acceptance': False, 'production_admission': False}
        save(output/'qualification.json', report)
        print(json.dumps({'status': report['status'], 'successful_stages': len(all_stages),
                          'failed_stages': len(failed)}))
    except BaseException as exc:
        save(output/'qualification-failure.json', {'error_type': type(exc).__name__, 'error': str(exc),
            'traceback': traceback.format_exc(), 'actions': rows, 'scientific_acceptance': False})
        raise


def asdict_from_path(path):
    return {'path': str(path), 'sha256': digest(path), 'size': path.stat().st_size}


if __name__ == '__main__':
    main()
