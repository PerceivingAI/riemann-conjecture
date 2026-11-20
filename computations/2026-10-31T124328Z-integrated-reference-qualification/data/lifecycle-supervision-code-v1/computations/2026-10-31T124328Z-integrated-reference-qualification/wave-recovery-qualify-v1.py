"""Bounded owned recovery qualification. Manufactured finite operands, no analytic acceptance.

Run against a frozen code root. Every failure, attempt, stream and receipt is
retained. Failure injection changes a task request, never a successful receipt.
"""
from dataclasses import asdict
from fractions import Fraction
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import time
import traceback
from unittest.mock import patch

PROCEDURES = Path('computations/2026-10-31T124328Z-integrated-reference-qualification')
FIELDS = ('parity', 'dimension', 'goal', 'width', 'margin', 'tau', 'direction_index',
          'direction_upper', 'direction_mass', 'row_margins', 'transformed_digest',
          'transformed_upper_entries', 'modular', 'source_tiles_consumed')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in root.rglob('*') if p.is_file()}


def preserved(root, before):
    assert all((root/name).is_file() and digest(root/name) == sha for name, sha in before.items())


def science(report):
    return [{key: block[key] for key in FIELDS} for block in report['blocks']]


def fraction_reference(exact, graph, problem, reader, descriptor, directory, report, code_root):
    """Independent tiny dense Fraction contractions of every signed/ragged entry."""
    context_doc = json.loads((directory/'recovery/context.json').read_bytes())
    from scripts.whole_source import recovery
    from scripts.whole_source.artifacts import decode_rational
    records, _ = recovery._state(directory, context_doc)
    second = next(node['payload']['value']['outputs'] for _, node in records
                  if node['kind'] == 'wave' and node['key'] == 'second')
    def transpose(matrix):
        return list(map(list, zip(*matrix)))
    def multiply(left, right):
        return [[sum((a*b for a, b in zip(row, column)), Fraction())
                 for column in zip(*right)] for row in left]
    for p, block in enumerate(descriptor['blocks']):
        context = block['context']
        n, b = context['dimension'], context['panel_size']
        transform = exact.IntegerTiles(code_root, context, block['panels'])
        z = [[Fraction(int(transform.tile(r//b*b, c//b*b)[r%b, c%b]), 1 << context['u'])
              for c in range(n)] for r in range(n)]
        source = exact.SourceIntegers(reader, context)
        theta = Fraction(block['theta'])
        head, tail = (1+theta)/problem.eta, (1+1/theta)/problem.eta
        low, high = [], []
        for r in range(n):
            lr, hr = [], []
            for c in range(n):
                bounds = [source.bounds(family, r//b*b, c//b*b) for family in
                          ('A_model', 'weighted_head', 'weighted_complete_tail')]
                a, h, t = [(Fraction(int(lo[r%b, c%b]), 1 << reader.bits),
                            Fraction(int(hi[r%b, c%b]), 1 << reader.bits)) for lo, hi in bounds]
                lr.append(a[0]-head*h[1]-tail*t[1])
                hr.append(a[1]-head*h[0]-tail*t[0])
            low.append(lr)
            high.append(hr)
        centers = [[(lo+hi)/2 for lo, hi in zip(lr, hr)] for lr, hr in zip(low, high)]
        radii = [[(hi-lo)/2 for lo, hi in zip(lr, hr)] for lr, hr in zip(low, high)]
        absolute = [[abs(value) for value in row] for row in z]
        center = multiply(multiply(transpose(z), centers), z)
        radius = multiply(multiply(transpose(absolute), radii), absolute)
        mass = [[Fraction(2, 2*(2*r+p)+1) if r == c else Fraction()
                 for c in range(n)] for r in range(n)]
        transformed_mass = multiply(multiply(transpose(z), mass), z)
        actual = report['blocks'][p]
        bd, ed = int(actual['center_denominator'], 16), int(actual['radius_denominator'], 16)
        account = exact.integer_bounds(context, exact.paid_parameters(reader.bits, theta, problem.eta), problem.model_error)
        for i in range(0, n, b):
            for j in range(i, n, b):
                ref = second[f'block/{p}/{i}/{j}']
                _, ac, ar = graph._block_values((directory/ref['path']).read_bytes(), context, i, j, account)
                columns = min(b, n-j)
                for r in range(min(b, n-i)):
                    for c in range(columns):
                        k = r*columns+c
                        assert Fraction(ac[k], bd) == center[i+r][j+c]-problem.model_error*transformed_mass[i+r][j+c]
                        assert Fraction(ar[k], ed) == radius[i+r][j+c]
        margins = [center[r][r]-problem.model_error*transformed_mass[r][r]
                   -sum(abs(center[r][c]-problem.model_error*transformed_mass[r][c])
                        for c in range(n) if c != r)-sum(radius[r]) for r in range(n)]
        assert [decode_rational(value, 65536) for value in actual['row_margins']] == margins


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--code-root', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--origin-commit', required=True)
    parser.add_argument('--baseline-root', type=Path,
                        default=Path(__file__).resolve().parent/'data')
    args = parser.parse_args()
    root, output = args.code_root.resolve(strict=True), args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    work = output/'work'
    work.mkdir()
    sys.path.insert(0, str(root))
    from scripts.whole_source import proposal, exact, resources, recovery, execution, controls
    from scripts.whole_source.contract import ArtifactRef, ContractError, canonical_bytes
    from scripts.whole_source.receipts import discover_receipts, verify_stage
    from scripts.whole_source.execution import exact_telemetry, _write, WorkloadExecution
    factory = runpy.run_path(str(root/PROCEDURES/'verify-variant-snapshots-v1.py'))['manufactured_inputs']
    origin = {'origin_git_commit': args.origin_commit, 'origin_git_dirty': True}
    auto_plan = resources.auto_plan
    events, calls = [], []
    save_count = 0
    started = time.perf_counter()

    def save():
        nonlocal save_count
        save_count += 1
        _write(output/f'qualification-progress-{save_count:04d}.json', canonical_bytes(exact_telemetry({
            'format': 'wave-recovery-owned-qualification-v1', 'events': events,
            'calls': calls, 'elapsed_s': time.perf_counter()-started,
            'scope': 'MANUFACTURED_FINITE_CONTROL_ONLY', 'production_admission': False})))

    def allocate(cpus):
        def bounded(template, *, parallel, memory_mib=None, helper_root=root):
            return auto_plan(template, parallel=parallel, cpus=cpus, memory_mib=2048, helper_root=helper_root)
        return bounded

    run_stage = WorkloadExecution.run_stage
    commit = recovery.RecoveryJournal.commit

    def invoke(label, function, *, fail_stage=None, stop_commit=None,
               orphan=None, head_cut=None, pre_group=False, post_assess=False,
               expect_failure=False, zero=False):
        local = []
        injected = []
        def stage(owner, name, tasks):
            tasks = list(tasks)
            local.append({'stage': name, 'operations': [task['operation'] for task in tasks],
                          'tasks': len(tasks), 'attempt_id': owner.attempt_id})
            if name == fail_stage and not injected:
                # Real owned worker rejection of a changed logical task ID. The
                # program, task spool, result/failure and containment stay real.
                tasks[0] = {**tasks[0], 'task_id': '0'*64}
                injected.append('owned-task-failure')
            result = run_stage(owner, name, tasks)
            if post_assess and name == 'assess':
                injected.append('successful-assess-before-owner-publication')
                raise KeyboardInterrupt('CONTROL successful assess before parent publication')
            return result
        def checkpoint(journal, key, group, value):
            if key == orphan:
                if head_cut == key:
                    replace = journal._replace
                    def interrupted_head(relative, raw):
                        if relative == 'recovery/head.json':
                            injected.append('immutable-record-before-head')
                            raise KeyboardInterrupt('CONTROL immutable journal record before atomic head')
                        return replace(relative, raw)
                    with patch.object(journal, '_replace', interrupted_head):
                        return commit(journal, key, group, value)
                injected.append('group-before-head')
                raise KeyboardInterrupt('CONTROL group exists but no committed checkpoint')
            result = commit(journal, key, group, value)
            if key == stop_commit and not injected:
                injected.append('after-committed-wave')
                raise KeyboardInterrupt('CONTROL after complete committed wave')
            return result
        from scripts.whole_source import exact_tasks
        seal = exact_tasks.seal_group
        def before_group(lock, owner, name, context, outputs):
            if pre_group and name == 'first':
                injected.append('before-owner-group')
                raise KeyboardInterrupt('CONTROL complete owned stage before group publication')
            return seal(lock, owner, name, context, outputs)
        before = time.perf_counter()
        try:
            with patch.object(WorkloadExecution, 'run_stage', stage), \
                 patch.object(recovery.RecoveryJournal, 'commit', checkpoint), \
                 patch.object(exact_tasks, 'seal_group', before_group):
                result = function()
        except BaseException as exc:
            events.append({'label': label, 'outcome': 'retained-error', 'error_type': type(exc).__name__,
                           'error': str(exc), 'injection': injected, 'elapsed_s': time.perf_counter()-before})
            (output/(label+'-error.txt')).write_text(traceback.format_exc(), encoding='utf-8')
            if not expect_failure:
                raise
            result = None
        else:
            assert not expect_failure, label+' unexpectedly succeeded'
            events.append({'label': label, 'outcome': 'completed', 'elapsed_s': time.perf_counter()-before})
        finally:
            calls.append({'label': label, 'stages': local})
            save()
        if zero:
            assert not local, label+' unexpectedly executed numerical stages'
        return result, local

    try:
        with patch.object(resources, 'auto_plan', allocate(2)):
            problem, source, identity, identity_core = factory(work/'manufactured', origin)
            pinputs = proposal.prepare_proposal_inputs(problem, source.path, work/'proposal-inputs', panel_size=2, **origin)
        source_before = snapshot(source.path.parent)
        def propose(destination, resume=False):
            return proposal.run_proposal(pinputs['problem'], source.path, pinputs['execution'], destination,
                                         code_root=root, resume=resume)
        fresh = work/'proposal-fresh'
        retry = work/'proposal-retry'
        pbase, baseline_pcalls = invoke('proposal-fresh', lambda: propose(fresh))
        _, failed = invoke('proposal-owned-failure', lambda: propose(retry),
                           fail_stage='factor-below_0', expect_failure=True)
        # Stage spelling is the journal key, fixed by the executed layout.
        assert len(failed) == 2 and failed[0]['operations'] == ['factor-diagonal']
        original_p_history = snapshot(retry/'native-0/attempts')
        _, second = invoke('proposal-second-interruption', lambda: propose(retry, True),
                           stop_commit='factor-below_0', expect_failure=True)
        assert len(second) == 1 and second[0]['operations'] == ['factor-below']
        pfinal, remaining = invoke('proposal-third-owner', lambda: propose(retry, True))
        assert sum(row['tasks'] for row in second+remaining) == sum(row['tasks'] for row in baseline_pcalls)-1
        preserved(retry/'native-0/attempts', original_p_history)
        def pscience(document, directory):
            values = []
            for block in document['blocks']:
                refs = {f"Z/{row['row']}/{row['column']}": row['artifact'] for row in block['integer_panels']}
                store = proposal.PanelStore(directory, block['context'], refs)
                values.append({'parity': block['parity'], 'theta': block['theta'],
                    'panels': [{'row': row['row'], 'column': row['column'],
                        'values': store.read(f"Z/{row['row']}/{row['column']}", 'integer')}
                        for row in block['integer_panels']]})
            return values
        assert pscience(pbase, fresh) == pscience(pfinal, retry)
        proposal_before = (retry/'proposal.json').read_bytes()
        invoke('proposal-completed-resume', lambda: propose(retry, True), zero=True)
        assert (retry/'proposal.json').read_bytes() == proposal_before

        with patch.object(resources, 'auto_plan', allocate(2)):
            einputs = exact.prepare_exact_inputs(problem, source.path, retry/'proposal.json', work/'exact-inputs', **origin)
        normalized_before = snapshot(work/'exact-inputs')
        def assess(destination, resume=False, inputs=einputs):
            return exact.run_exact(inputs['problem'], source.path, retry/'proposal.json', inputs['execution'],
                                   destination, code_root=root, resume=resume)
        ebase, baseline_calls = invoke('exact-fresh', lambda: assess(work/'exact-fresh'))
        assert ebase['status'] == 'PASS_EXACT_PAID_LOWER_SOURCE_CONDITIONAL'
        assert ebase['proof_scope'] == 'CONTROL_ONLY'
        resumed = work/'exact-retry'
        invoke('exact-owned-failure', lambda: assess(resumed), fail_stage='first', expect_failure=True)
        history = snapshot(resumed/'collection/attempts')
        _, first_only = invoke('exact-second-interruption', lambda: assess(resumed, True),
                               stop_commit='first', expect_failure=True)
        final, missing = invoke('exact-third-owner', lambda: assess(resumed, True))
        assert [row['stage'] for row in first_only] == ['first']
        assert [row['stage'] for row in missing] == ['second', 'reduce', 'assess']
        assert sum(row['tasks'] for row in first_only+missing) == sum(row['tasks'] for row in baseline_calls)-2
        assert science(final) == science(ebase)
        preserved(resumed/'collection/attempts', history)
        raw_report = (resumed/'report.json').read_bytes()
        invoke('exact-completed-resume', lambda: assess(resumed, True), zero=True)
        assert (resumed/'report.json').read_bytes() == raw_report
        # Public CLI verification-only edge, not a patched Python entry point.
        receipts_before = set(discover_receipts(resumed))
        command = [sys.executable, '-B', '-m', 'scripts.weil_whole_source_split', 'exact',
                   '--problem', str(einputs['problem']), '--source', str(source.path),
                   '--proposal', str(retry/'proposal.json'), '--execution', str(einputs['execution']),
                   '--output-dir', str(resumed), '--resume']
        cli = subprocess.run(command, cwd=root, capture_output=True)
        (output/'cli-resume-stdout.txt').write_bytes(cli.stdout)
        (output/'cli-resume-stderr.txt').write_bytes(cli.stderr)
        assert cli.returncode == 0, cli.stderr.decode(errors='replace')
        assert set(discover_receipts(resumed)) == receipts_before
        assert (resumed/'report.json').read_bytes() == raw_report
        events.append({'label': 'public-cli-resume', 'argv': command, 'returncode': cli.returncode,
                       'new_receipts': 0})

        final_destination = work/'exact-final-publication'
        invoke('successful-assess-owner-interruption', lambda: assess(final_destination),
               post_assess=True, expect_failure=True)
        successful_assess = [path for path in discover_receipts(final_destination)
                             if json.loads(path.read_bytes())['stage'] == 'assess']
        assert len(successful_assess) == 1
        verify_stage(successful_assess[0])
        assert not (final_destination/'report.json').exists()
        final_history = snapshot(final_destination/'collection/attempts')
        recovered, _ = invoke('final-intent-recovery', lambda: assess(final_destination, True), zero=True)
        assert science(recovered) == science(ebase)
        preserved(final_destination/'collection/attempts', final_history)

        orphan_destination = work/'exact-orphan-group'
        invoke('group-before-journal-head', lambda: assess(orphan_destination), orphan='first', expect_failure=True)
        assert len(recovery.selected_receipts(orphan_destination/'collection')) == 1
        orphan_history = snapshot(orphan_destination/'collection/attempts')
        _, orphan_calls = invoke('orphan-recomputed-not-adopted', lambda: assess(orphan_destination, True))
        assert [row['stage'] for row in orphan_calls] == ['first', 'second', 'reduce', 'assess']
        preserved(orphan_destination/'collection/attempts', orphan_history)
        for edge in ('before-group', 'before-atomic-head'):
            destination = work/('exact-'+edge)
            invoke(edge, lambda: assess(destination), orphan='first' if edge == 'before-atomic-head' else None,
                   head_cut='first' if edge == 'before-atomic-head' else None,
                   pre_group=edge == 'before-group', expect_failure=True)
            assert len(recovery.selected_receipts(destination/'collection')) == 1
            original = snapshot(destination/'collection/attempts')
            result, executed = invoke(edge+'-resume', lambda: assess(destination, True))
            assert [row['stage'] for row in executed] == ['first', 'second', 'reduce', 'assess']
            assert science(result) == science(ebase)
            preserved(destination/'collection/attempts', original)

        corrupt = work/'exact-corrupt-committed'
        invoke('corrupt-control-preparation', lambda: assess(corrupt), stop_commit='first', expect_failure=True)
        # Resolve the selected immutable first-wave operand, not arbitrary staging.
        context_doc = json.loads((corrupt/'collection/recovery/context.json').read_bytes())
        records, _ = recovery._state(corrupt/'collection', context_doc)
        node = next(node for _, node in records if node['kind'] == 'wave' and node['key'] == 'first')
        operand = next(ref for name, ref in node['payload']['value']['outputs'].items() if '/J/' in name)
        badpath = corrupt/'collection'/operand['path']
        badpath.write_bytes(b'CONTROL deliberate committed operand corruption')
        corrupt_hash = digest(badpath)
        invoke('corrupt-operand-rejected', lambda: assess(corrupt, True), expect_failure=True, zero=True)
        assert digest(badpath) == corrupt_hash
        relocated = work/'exact-relocated'
        shutil.copytree(resumed, relocated)
        invoke('relocated-output-rejected', lambda: assess(relocated, True), expect_failure=True, zero=True)
        changed = dict(json.loads(Path(einputs['execution']).read_bytes()))
        changed['recovery_policy'] = 'CONTROL changed configuration'
        changed_path = work/'changed-execution.json'
        changed_path.write_bytes(canonical_bytes(changed))
        invoke('changed-config-rejected', lambda: assess(resumed, True,
            {**einputs, 'execution': changed_path}), expect_failure=True, zero=True)

        # Separate expendable controls retain the corrupted bytes. Never repair
        # the original successful source/proposal or a committed dependency.
        for target in ('original-source', 'original-proposal', 'normalized-transform'):
            control_dir = work/('raw-revalidation-'+target)
            with patch.object(resources, 'auto_plan', allocate(2)):
                cp, cs, ci, _ = factory(control_dir/'manufactured', origin)
                cin = exact.prepare_exact_inputs(cp, cs.path, ci, control_dir/'inputs', **origin)
            destination = control_dir/'exact'
            def control_run(resume=False):
                return exact.run_exact(cin['problem'], cs.path, ci, cin['execution'], destination,
                                       code_root=root, resume=resume)
            invoke(target+'-checkpoint', control_run, stop_commit='global', expect_failure=True)
            if target == 'original-source':
                raw_path = cs.path.parent/cs.document['tiles'][0]['artifact']['path']
            elif target == 'original-proposal':
                raw_path = ci
            else:
                _, _, cd, _, _ = exact._bind_exact(cin['problem'], cin['execution'], root)
                raw_path = root/next(iter(cd['blocks'][0]['panels'].values()))['path']
            # Whitespace changes raw identity without supplying altered maths.
            raw_path.write_bytes(raw_path.read_bytes()+b'\n')
            raw_hash = digest(raw_path)
            invoke(target+'-rejected', lambda: control_run(True), expect_failure=True,
                   zero=target != 'original-source')
            assert digest(raw_path) == raw_hash

        # Independent one-worker owned replay under a separately bound plan.
        with patch.object(resources, 'auto_plan', allocate(1)):
            serial_inputs = exact.prepare_exact_inputs(problem, source.path, retry/'proposal.json',
                                                       work/'exact-serial-inputs', **origin)
        serial, _ = invoke('exact-one-worker-replay', lambda: assess(work/'exact-serial', inputs=serial_inputs))
        assert science(serial) == science(ebase)

        # Signed, ragged n=3/b=2 finite transform. This is explicitly an artificial
        # nonproof proposal, not a positive analytic source or review fixture.
        signed_dir = work/'signed-proposal'
        signed_dir.mkdir()
        signed_core = json.loads(canonical_bytes(identity_core))
        for block in signed_core['blocks']:
            store = proposal.PanelStore(signed_dir, block['context'])
            n, b = block['dimension'], block['context']['panel_size']
            assert (n, b) == (3, 2)
            panels = []
            for i in range(0, n, b):
                for j in range(0, n, b):
                    name = f'Z/{i}/{j}'
                    store.put(name, 'integer', [hex((1 << block['u']) if r == c else (r+c)%3-1)
                        for r in range(i, min(i+b, n)) for c in range(j, min(j+b, n))])
                    panels.append({'row': i, 'column': j, 'artifact': store.refs[name]})
            block['integer_panels'] = panels
        signed_core['diagnostics'] = asdict(_write(signed_dir/'diagnostics.json', canonical_bytes({
            'scope': 'CONTROL_ONLY', 'kind': 'MANUFACTURED_SIGNED_RAGGED_NONPROOF'})))
        signed_path = signed_dir/'proposal.json'
        _write(signed_path, canonical_bytes(signed_core))
        with patch.object(resources, 'auto_plan', allocate(2)):
            signed_inputs = exact.prepare_exact_inputs(problem, source.path, signed_path, work/'signed-inputs', **origin)
        signed_report, _ = invoke('signed-ragged-owned', lambda: exact.run_exact(
            signed_inputs['problem'], source.path, signed_path, signed_inputs['execution'], work/'signed-exact', code_root=root))
        _, _, descriptor, _, _ = exact._bind_exact(signed_inputs['problem'], signed_inputs['execution'], root)
        reader = exact._validate_operands(problem, descriptor, root)
        for p, block in enumerate(descriptor['blocks']):
            context = block['context']
            transform = exact.IntegerTiles(root, context, block['panels'])
            refdir = work/('signed-reference-'+str(p))
            refdir.mkdir()
            (refdir/'.volume.lock').touch()
            products = exact.IntegerTiles(refdir, context)
            source_ints = exact.SourceIntegers(reader, context)
            masses = exact.mass_trace(3, p, context['u'], 2, transform.tile)
            reference = exact.integer_congruence(source_ints, transform, products,
                exact.paid_parameters(256, Fraction(block['theta']), problem.eta), masses, problem.model_error)
            reference = json.loads(canonical_bytes(reference))
            assert all(signed_report['blocks'][p][key] == value for key, value in reference.items())
        from scripts.whole_source import exact_tasks
        fraction_reference(exact, exact_tasks, problem, reader, descriptor,
                           work/'signed-exact/collection', signed_report, root)

        # Compare actual complete science to both retained owned runs.
        baseline_comparisons = []
        current_p = pscience(pfinal, retry)
        for name in ('task-layout-owned-parallel-v1', 'task-layout-owned-serial-v1'):
            path = args.baseline_root/name/'verification.json'
            old = json.loads(path.read_bytes())
            assert old['proposal_science'] == current_p
            assert old['exact_science'] == science(ebase)
            assert old['assessment'] == ebase['assessment']
            baseline_comparisons.append({'path': str(path.resolve()), 'sha256': digest(path),
                                         'complete_mathematics_equal': True})
        negatives = []
        with patch.object(resources, 'auto_plan', allocate(2)):
            for name, expected in controls.EXACT_CASES:
                row = controls._exact_case(problem, source, identity, identity_core, work/name, name, root, origin)
                assert row['passed'] is True
                negatives.append(row)
        preserved(source.path.parent, source_before)
        preserved(work/'exact-inputs', normalized_before)
        assert (retry/'proposal.json').read_bytes() == proposal_before

        stages, negative_history, multiworker = [], [], False
        for collection in sorted({path.parent for path in work.rglob('recovery/context.json')}):
            recovery.check_history(collection.parent)
        for path in discover_receipts(work):
            receipt = json.loads(path.read_bytes())
            assert receipt['worker_cleanup_verified'] is True
            if receipt['exit_code'] != 0:
                negative_history.append({'receipt': str(path), 'sha256': digest(path),
                                         'exit_code': receipt['exit_code'], 'cleanup_verified': True})
                continue
            verified = verify_stage(path)
            stage, plan = verified['stage'], verified['plan']
            assert plan.memory_mib == 2048 and plan.cpus in (1, 2)
            complete = json.loads((Path(stage['result_dir'])/'complete.json').read_bytes())
            actual_workers = len(complete['worker_pids'])
            multiworker |= (path.is_relative_to(resumed) and receipt['stage'] == 'second' and actual_workers > 1)
            stages.append({'receipt': verified['record'], 'attempt_id': stage['attempt_id'],
                           'stage': receipt['stage'], 'tasks': stage['task_count'],
                           'actual_task_workers': actual_workers, 'cpus': plan.cpus,
                           'peak_owned_bytes': receipt['peak_budgeted_memory_bytes']})
        assert multiworker, 'no actual multiworker missing-work wave observed'
        assert len(negative_history) >= 2
        selected = recovery.selected_receipts(resumed/'collection')
        assert len(selected) == 5
        assert len({Path(row['directory']).parent.name for row in selected}) == 3
        assert len(discover_receipts(resumed)) > len(selected)
        result = {'format': 'wave-recovery-owned-qualification-v1', 'status': 'PASS_CONTROL_ONLY_WAVE_RECOVERY',
                  'scope': 'MANUFACTURED_FINITE_CONTROL_ONLY', 'events': events, 'calls': calls,
                  'baseline_comparisons': baseline_comparisons, 'selected_retry_receipts': selected,
                  'stages': stages, 'negative_history': negative_history, 'negative_mathematical_controls': negatives,
                  'elapsed_s': time.perf_counter()-started, 'source_raw_preserved': True,
                  'proposal_raw_preserved': True, 'normalized_operand_raw_preserved': True,
                  'actual_multiworker_wave': multiworker, 'full_qualification': False,
                  'production_admission': False, 'independent_review': False,
                  'limitations': ['Graceful owner interruption only; no power-loss or abrupt-stop containment claim.',
                                 'Manufactured source is not analytic acceptance or a Weil/RH proof.',
                                 'Reviewed-assessment publication is separately qualified by its owner.',
                                 'No historical data are migrated, repaired or deleted.']}
        _write(output/'verification.json', canonical_bytes(exact_telemetry(result)))
        census = runpy.run_path(str(root/PROCEDURES/'wave-recovery-storage-v1.py'))['census']
        _write(output/'storage-census.json', canonical_bytes(census(work)))
        print(json.dumps({'status': result['status'], 'successful_stages': len(stages),
                          'retained_failed_stages': len(negative_history)}))
    except BaseException:
        save()
        (output/'qualifier-failure.txt').write_text(traceback.format_exc(), encoding='utf-8')
        raise


if __name__ == '__main__':
    main()
