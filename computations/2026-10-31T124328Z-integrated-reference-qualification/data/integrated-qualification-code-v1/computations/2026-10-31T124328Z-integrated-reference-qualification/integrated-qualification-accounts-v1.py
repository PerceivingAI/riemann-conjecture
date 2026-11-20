"""Inspect current full-shape metadata accounts without starting numerical work.

Only --output is written. PASS validates metadata formulas, not workload fit,
scientific acceptance, execution permission, or an independent review.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
MIB = 1024 * 1024
NUMERICAL = frozenset(('flint', 'numpy', 'scipy', 'sympy', 'mpmath', 'gmpy2'))


class AccountError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AccountError(message)


class MetadataImports:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in NUMERICAL:
            raise AccountError('numerical import forbidden: ' + fullname)
        return None


def identity(path):
    digest, size = hashlib.sha256(), 0
    with path.open('rb') as stream:
        while raw := stream.read(MIB):
            digest.update(raw)
            size += len(raw)
    return {'sha256': digest.hexdigest(), 'size': size}


def source_geometry(problem, spec, width, workers):
    """Count actual domain factories, including ragged diagonal upper triangles."""
    from scripts.whole_source import pipeline
    from scripts.whole_source.contract import QuantityKey
    n, h = problem.N // 2, (problem.M - problem.N) // 2
    q, k = (n + width - 1) // width, (h + width - 1) // width
    counts, chunks, final_entries = [], Counter(), 0
    for p in (0, 1):
        finals = list(pipeline._tiles(spec, QuantityKey('A_model', p)))
        kernels = list(pipeline._tiles(spec, QuantityKey('kernel_complete', p)))
        pages = list(pipeline._kernel_panels(spec, p))
        require(len(finals) == q * (q + 1) // 2, 'source final task formula changed')
        require(len(kernels) == k * (k + 1) // 2, 'source kernel tile formula changed')
        require(len(pages) == k, 'source kernel page formula changed')
        entries = sum(len(t.rows) * len(t.columns) -
                      (len(t.rows) * (len(t.rows) - 1) // 2 if t.rows == t.columns else 0)
                      for t in finals)
        require(entries == n * (n + 1) // 2, 'ragged source upper cover changed')
        final_entries += 3 * entries
        groups = min(workers, len(problem.frequency_edges))
        stages = {'kernel-groups': groups, 'kernel-reduce': len(pages),
                  'columns': (n + 1) // 2, 'heads': (n + 1) // 2,
                  'final': len(finals)}
        counts.append({'parity': p, 'stage_tasks': stages,
                       'tasks': sum(stages.values()), 'kernel_tiles': len(kernels),
                       'kernel_partial_pages': groups * len(pages),
                       'final_publication_tiles': 3 * len(finals),
                       'final_publication_entries': 3 * entries})
        chunks.update(F_column=n, head_column=n, head_image=n,
                      kernel_complete=len(kernels))
    require(final_entries == 512946, 'retained final-entry identity changed')
    for quantity in spec.quantities:
        if quantity.key.name in pipeline.FAMILIES.values():
            continue
        require(len(quantity.rows) > 0 and len(quantity.columns) > 0, 'empty source quantity')
    return {'workers': workers, 'parities': counts, 'stages': 10,
            'tasks': sum(row['tasks'] for row in counts),
            'cache_chunk_count_by_family': dict(chunks),
            'final_publication_entries': final_entries,
            'final_publication_tiles': sum(row['final_publication_tiles'] for row in counts),
            'numerical_operation_count': None,
            'numerical_operation_count_basis': 'Task counts are not arithmetic or wall-time bounds.'}


def proposal_geometry(problem, width):
    from scripts.whole_source import proposal
    from scripts.whole_source.contract import problem_id
    n = problem.N // 2
    q = (n + width - 1) // width
    layout = proposal._proposal_layout(n, width)
    parities = []
    for p in (0, 1):
        # These are domain-only identities, not a fabricated source/proposal artifact.
        context = {'proposal_id': '0' * 64, 'problem_id': problem_id(problem),
                   'source_sha256': '0' * 64, 'dimension': n, 'panel_size': width,
                   'precision_bits': proposal.BITS, 'grid_bits': proposal.BITS,
                   'transform_bits': proposal.TRANSFORM_BITS, 'parity': p}
        base = {'context': context, 'source': None, 'source_snapshot': None}
        tasks, stages, panels = Counter(), 0, Counter()
        for operation in ('factor-diagonal', 'factor-below', 'whiten-forward',
                          'whiten-transpose', 'float-optimize', 'backsolve-quantize'):
            columns = range(0, n, width) if operation.startswith('factor-') else (None,)
            for column in columns:
                wave = proposal._make_tasks(base, operation, {}, column)
                if wave:
                    stages += 1
                tasks[operation] += len(wave)
                for task in wave:
                    panels[operation] += len(proposal._task_panels(task))
        expected = {'factor-diagonal': q, 'factor-below': q * (q - 1) // 2,
                    'whiten-forward': 3 * q, 'whiten-transpose': 3 * q,
                    'float-optimize': 1, 'backsolve-quantize': q}
        require(dict(tasks) == expected, 'proposal task factory formula changed')
        require(stages == layout['stages_per_parity'] == 2 * q + 3,
                'proposal barrier formula changed')
        require(sum(panels.values()) == q * (q + 1) // 2 + 9 * q * q,
                'proposal panel publication formula changed')
        parities.append({'parity': p, 'stages': stages, 'tasks_by_operation': dict(tasks),
                         'tasks': sum(tasks.values()), 'panels_by_operation': dict(panels)})
    return {'layout': layout, 'accounts_per_parity': proposal._proposal_accounts(n, width),
            'parities': parities, 'stages': sum(row['stages'] for row in parities),
            'tasks': sum(row['tasks'] for row in parities),
            'factory_validation': 'Actual task and output-name factories; no matrix values.'}


def exact_geometry(problem, width):
    from scripts.whole_source import exact_tasks
    n, q = problem.N // 2, (problem.N // 2 + width - 1) // width
    descriptor = {'blocks': [{'context': {'dimension': n, 'panel_size': width, 'parity': p}}
                             for p in (0, 1)]}
    layout = exact_tasks.layout(descriptor)
    counts, outputs = {}, {}
    dependencies = {'global': (), 'first': ('global',), 'second': ('global', 'first'),
                    'reduce': ('global', 'first', 'second')}
    for operation in dependencies:
        count = 0
        for p in (0, 1):
            coordinates = ([{}] if operation in ('global', 'reduce') else
                           [{'row': i} for i in range(0, n, width)] if operation == 'first' else
                           [{'row': i, 'column': j} for i in range(0, n, width)
                            for j in range(i, n, width)])
            for values in coordinates:
                task = exact_tasks._request(operation, None,
                    {name: None for name in dependencies[operation]}, parity=p, **values)
                exact_tasks._validate_task(task, operation)
                count += 1
        counts[operation] = count
        outputs[operation] = len(exact_tasks._expected(descriptor, operation))
    require(counts == {'global': 2, 'first': 2 * q, 'second': q * (q + 1), 'reduce': 2},
            'exact wave count formula changed')
    require(layout['max_wave_tasks'] == max(counts.values()), 'exact maximum wave changed')
    counts['assess'] = 1
    outputs['assess'] = 1
    return {'layout': layout, 'stages': 5, 'tasks_by_operation': counts,
            'tasks': sum(counts.values()), 'sealed_outputs_by_operation': outputs,
            'actual_operand_account': None,
            'pending_required_bounds': {
                'source_endpoint_bits_per_parity': None, 'transform_integer_bits_per_parity': None,
                'fresh_theta_per_parity': None, 'paid_parameters_per_parity': None,
                'private_bytes_per_worker': None, 'staged_bytes': None,
                'normalized_transform_bytes': None, 'preparation_caller_scratch_bytes': None,
                'dependency_repository_bytes': None, 'integer_codec_fit': None},
            'pending_basis': 'Requires actual complete source and fresh proposal integers. '
                             'Codec caps, publication precision and transform grid precision '
                             'are not observed endpoint, Z or theta bounds.',
            'required_factory': 'exact.inspect_exact_preparation followed by '
                                'exact.prepare_exact_operands admission and recheck',
            'factory_validation': 'Actual layout, request validator and output-name factories only.'}


def select_live(requirements, baseline, detected, caller_growth, *, parallel):
    from scripts.whole_source import resources
    if detected is None:
        return {'status': 'BLOCKED', 'reason': 'live resource detection unavailable'}
    sample = {**detected, 'phase_caller_future_bytes': caller_growth}
    try:
        selected, owned = resources._select(requirements, baseline, sample, parallel, None, None)
    except (ValueError, OSError) as error:
        return {'status': 'REFUSED', 'error_type': type(error).__name__, 'reason': str(error)}
    return {'status': 'PASS_SNAPSHOT_ONLY', 'selected': selected, 'owned_required_bytes': owned,
            'requirements': requirements, 'baseline': baseline,
            'future_caller_bytes': caller_growth, 'reservation': False,
            'execution_plan_created': False}


def source_accounts(problem, width, detected, caller_growth):
    from scripts.whole_source import pipeline, execution
    from scripts.whole_source.artifacts import CodecBounds, CollectionSpec, _catalog_limit
    from scripts.whole_source.contract import ArtifactRef
    common = (*execution._RUNTIME, 'scripts/whole_source/slice.py',
              'scripts/whole_source/gram.py', 'scripts/whole_source/pipeline.py',
              'scripts/weil_whole_source_split.py')
    bounds = CodecBounds(8*MIB, 8*MIB, 8*MIB, 16384, 8192, 256*1024,
                         64*1024, 8192*MIB, 128*MIB, 64*MIB)
    result = {}
    for role in ('producer', 'analytic'):
        names = sorted(set((*common, 'scripts/whole_source/'+role+'.py')))
        refs = tuple(ArtifactRef(name, **identity(ROOT / name)) for name in names)
        spec = CollectionSpec.create(problem, role=role, quantities=pipeline._quantities(problem, False),
            partition=pipeline._partition(problem, False, width), backend='python-flint',
            backend_version=importlib.metadata.version('python-flint'), native_threads=1,
            code_refs=refs, bounds=bounds, code_root=ROOT)
        required = (pipeline._producer_requirements(spec, False) if role == 'producer'
                    else pipeline._analytic_requirements(spec, False))
        private = max(128, (required['private_bytes'] + _catalog_limit(spec) + MIB - 1) // MIB)
        native = max(128, (required['native_bytes'] + MIB - 1) // MIB)
        requirements = {'root_mib': 128, 'worker_base_mib': 80, 'worker_private_mib': private,
                        'conversion_mib': 64, 'supervisor_increment_mib': 256,
                        'task_bytes': 128*1024, 'result_bytes': MIB}
        baseline = {'reserve_mib': 128, 'native_per_thread_mib': native,
                    'codec_per_worker_mib': 256, 'queue_mib': 8}
        live = select_live(requirements, baseline, detected, caller_growth, parallel=True)
        # Transport validation reads factories and serializes descriptors only.
        transport = SimpleNamespace(max_tasks=4096, task_bytes=128*1024, result_bytes=MIB, workers=61)
        pipeline._admit_transport(ROOT / 'metadata-only-domain', spec, transport, False)
        geometry = source_geometry(problem, spec, width, 61)
        if live['status'] == 'PASS_SNAPSHOT_ONLY':
            workers = live['selected']['workers']
            geometry_live = source_geometry(problem, spec, width, workers)
            h = (problem.M - problem.N) // 2
            group_bytes = h * (h + 1) // 2 * (2 * ((spec.grid_bits + 35) // 4) + 64)
            temporary = max(128, (workers * (group_bytes + 2 * spec.bounds.max_raw_bytes) + MIB - 1) // MIB)
        else:
            geometry_live, temporary = None, None
        result[role] = {'required_factory_bytes': required, 'catalog_decoded_bound_bytes': _catalog_limit(spec),
                        'worker_private_mib': private, 'native_per_thread_mib': native,
                        'codec_bounds': asdict(spec.bounds), 'live_selection': live,
                        'live_geometry': geometry_live, 'live_temporary_mib': temporary,
                        'worker_ceiling_geometry': geometry,
                        'geometry_basis': 'Windows maximum61 workers, not a selected plan.',
                        'factory_validation': 'CollectionSpec.create, source requirement factories, '
                                              'tile/page factories and _admit_transport. '
                                              'No prepare_source_inputs output is created.'}
    return result


def accounts(problem, width, detected, existing):
    from scripts.whole_source import admission, coordinator, controls
    lifetime = admission.topology(problem, tile_modes=width)
    capture = sum(ref.size for ref in problem.evidence) + 64 * MIB
    caller = admission.phase_caller_account('source', problem)
    maximum = admission.caller_account('source', file_count=admission.MAX_FILES,
        path_bytes=admission.MAX_FILES * admission.MAX_PATH_BYTES, capture_bytes=capture)
    live_caller = {'status': 'BLOCKED', 'reason': 'qualified live process commitment unavailable'}
    if detected is not None and existing is not None:
        try:
            live_caller = {'status': 'PASS_SNAPSHOT_ONLY', **admission.admit_caller(
                {**caller, 'required_bytes': existing + caller['required_bytes']},
                detected, existing_bytes=existing)}
        except (ValueError, OSError) as error:
            live_caller = {'status': 'REFUSED', 'error_type': type(error).__name__, 'reason': str(error)}
    source = source_accounts(problem, width, detected, caller['required_bytes'])
    for role in source.values():
        require(role['worker_ceiling_geometry']['tasks'] == lifetime['source_tasks'],
                'admission.topology source task formula differs from current factories')
        require(role['worker_ceiling_geometry']['stages'] == lifetime['source_stages'],
                'admission.topology source barrier count changed')
    proposed, exact = proposal_geometry(problem, width), exact_geometry(problem, width)
    premises = 8
    source_control_stages = 1 + len(controls.SOURCE_CASES)
    control_stages = source_control_stages + len(controls.EXACT_CASES) * exact['stages']
    first_science = premises + 20 + proposed['stages'] + exact['stages']
    replay = premises + 20 + exact['stages']
    source_tasks = lifetime['source_tasks']
    first_tasks = premises + 2*source_tasks + proposed['tasks'] + exact['tasks']
    control_tasks = source_control_stages + len(controls.EXACT_CASES)*exact['tasks']
    replay_tasks = premises + 2*source_tasks + exact['tasks']
    return {'tile_modes': width, 'integrated_entrypoint_uses_this_width': width == 32,
        'width_scope': 'Integrated dispatch fixes32;16 is direct-factory prospective geometry.',
        'logical_lifetime_allowance': lifetime,
        'source_and_independent_audit': source, 'proposal': proposed, 'exact': exact,
        'work_topology': {'coordinator_phases': list(coordinator.PHASES),
            'science_phases': list(coordinator.SCIENCE_PHASES),
            'attempts_per_phase': lifetime['attempts_per_phase'],
            'failed_attempt_bytes_retained': True, 'premise_stages': premises,
            'first_science_stages': first_science, 'control_stages': control_stages,
            'control_source_tasks': source_control_stages,
            'control_exact_runs': len(controls.EXACT_CASES),
            'replay_science_stages': replay, 'replay_proposal_stages': 0,
            'replay_basis': 'Captured replay installs the selected proposal; no controls in child.',
            'fresh_complete_run_owned_stages_before_external_assessment': first_science + control_stages + replay,
            'first_science_task_ceiling': first_tasks, 'control_task_count': control_tasks,
            'replay_science_task_ceiling': replay_tasks,
            'fresh_complete_task_ceiling_before_external_assessment': first_tasks + control_tasks + replay_tasks,
            'task_ceiling_basis': 'Each source/audit kernel group count uses the Windows61-worker '
                                 'ceiling. Live selected source counts are reported separately.',
            'external_review_owned_stages': 0, 'external_assessment_owned_stages_if_admitted': 1,
            'stage_counts_exclude_retries_and_recovered_waves': True,
            'retry_stage_upper_bound': None,
            'retry_stage_bound_basis': 'Two coordinator attempts do not bound all interrupted '
                                      'resumes and retained runtime history to twice fresh work.'},
        'caller_accounts': {'empty_run_by_phase': {phase: admission.phase_caller_account(phase, problem)
                             for phase in (*coordinator.PHASES, 'review', 'assessment', 'retention', 'validation')},
            'maximum_filename_view': maximum,
            'maximum_filename_view_basis': 'MAX_FILES paths at MAX_PATH_BYTES; no physical allocation claim.',
            'live_empty_source_caller': live_caller,
            'replay_waiting_parent_future_bytes': 4*MIB,
            'max_concurrent_caller_contexts': 2,
            'overlap': 'Ordinary coordinator plus owned root/pool. Replay keeps a4MiB waiting '
                       'parent and a separately admitted child coordinator. Guardian/observer '
                       'is outside the numerical job, inside the lifecycle outer job.'},
        'metadata_accounts': {'coordinator_total_bytes': coordinator.METADATA_BYTES,
            'coordinator_file_bytes': coordinator.FILE_BYTES, 'coordinator_head_bytes': coordinator.HEAD_BYTES,
            'coordinator_max_nodes': coordinator.MAX_NODES,
            'phase_policy_metadata_increment_bytes': 32*MIB,
            'max_storage_policies_exclusive': 1024,
            'policy_lifetime_allowance_bytes': 1024*9*MIB,
            'external_inventory_generations_charged': 4,
            'external_inventory_allowance_bytes': lifetime['external_growth_bytes']['inventory'],
            'source_task_and_result_envelope_per_task_bytes': 128*1024 + MIB + 4096,
            'source_owner_capture_count_per_attempt': 2,
            'capture_bytes': capture,
            'exact_task_spool_cap_bytes': 128*1024,
            'exact_result_spool_cap_bytes': 4*MIB,
            'exact_dependency_envelope_bytes': exact['layout']['max_wave_tasks']*(128*1024+4*MIB+1024),
            'exact_repository_formula': '2*sum(actual staged_bytes)+5*dependency_envelope+80MiB <=8192MiB',
            'actual_exact_repository_formula_bytes': None},
        'storage_basis': {'logical': 'All retained pathnames charged, including failed/retried '
                                    'attempts, snapshots, staging/publication overlap and inventory generations.',
            'physical': 'Free-space comparison uses logical remaining growth as conservative '
                        'headroom. No hardlink/compression discount, reservation, filesystem '
                        'allocation measurement or physical I/O enforcement.',
            'exact8192_mib': 'Local allowed ceiling only, not an actual operand forecast.',
            'operation_minimum_free_bytes': 64*MIB,
            'independent_observer_additional_free_headroom_max_bytes': 16*MIB,
            'integrated_initial_minimum_free_bytes': 32*1024*MIB},
        'full_workload_fit': False}


def control_accounts(directory, problem):
    """Read actual small-run plans; never reinterpret an allowed cap as demand."""
    from fractions import Fraction
    from scripts.whole_source import admission, exact, pipeline, proposal
    from scripts.whole_source.execution import _bytes, _json
    from scripts.whole_source.storage import _census, _inspect, _volume
    directory = Path(directory).absolute()
    directory.relative_to(ROOT)
    _inspect(directory)
    require(directory.is_dir(), 'control directory does not exist')
    def census(path):
        return _census(path, _volume(path), admission.MAX_FILES, admission.MAX_PATH_BYTES)
    records, blockers, inputs = [], [], {}
    def document(path):
        raw = _bytes(path, 8*MIB)
        inputs[path.relative_to(ROOT).as_posix()] = identity(path)
        return _json(raw)
    def inspect_collection(path, plan, bounds, forecast=None):
        if not path.exists():
            blockers.append('missing control collection: ' + path.relative_to(directory).as_posix())
            return
        totals = census(path)
        limits = {'repository_plan_bytes': plan['repository_mib']*MIB,
                  'temporary_plan_bytes': plan['temporary_mib']*MIB,
                  'repository_codec_bytes': bounds['max_total_bytes'],
                  'temporary_codec_bytes': bounds['max_temporary_bytes']}
        staging = [leaf for leaf in path.glob('attempts/*/staging') if leaf.is_dir()]
        staging_rows = [census(leaf) for leaf in staging]
        staged_bytes = sum(row['logical_bytes'] for row in staging_rows)
        fits = {name: (staged_bytes if name.startswith('temporary') else totals['logical_bytes']) <= value
                for name, value in limits.items()}
        require(all(fits.values()), 'control collection exceeds a declared disk limit: ' + str(path))
        demand_comparison = None
        if forecast is not None and 'repository_demand_envelope_bytes' in forecast:
            demand_comparison = totals['logical_bytes'] <= forecast['repository_demand_envelope_bytes']
            require(demand_comparison, 'retained exact collection exceeds actual operand demand envelope')
        staging_comparison = None
        if forecast is not None and 'temporary_demand_envelope_bytes' in forecast:
            staging_comparison = staged_bytes <= forecast['temporary_demand_envelope_bytes']
            require(staging_comparison, 'current staging exceeds its role demand forecast')
        stages = []
        for stage_path in sorted(path.glob('attempts/*/*-stage.json')):
            stage = document(stage_path)
            count = stage['task_count']
            stage_plan = stage['plan']
            task_path, result_dir = Path(stage['task_file']), Path(stage['result_dir'])
            require(task_path.is_relative_to(path) and result_dir.is_relative_to(path),
                    'control stage paths escape collection')
            task_bytes = task_path.stat().st_size
            result_bytes = 0
            completed = result_dir/'completed.jsonl'
            if completed.exists():
                with completed.open('rb') as stream:
                    for line in stream:
                        require(len(line) <= 65536, 'oversized result inventory row')
                        member = _json(line)
                        target = result_dir/member['path']
                        require(target.is_relative_to(result_dir) and '..' not in Path(member['path']).parts,
                                'result inventory path escape')
                        actual = target.stat().st_size
                        require(actual == member['size'] and actual <= stage_plan['result_bytes'],
                                'result payload exceeds actual stage transport')
                        result_bytes += actual
            forecast_transport = count*(stage_plan['task_bytes']+stage_plan['result_bytes']+4096)
            require(task_bytes <= count*stage_plan['task_bytes'] and
                    task_bytes+result_bytes <= forecast_transport,
                    'observed task/result spool exceeds its stage forecast')
            stages.append({'stage': stage_path.relative_to(directory).as_posix(), 'task_count': count,
                'retained_task_bytes': task_bytes, 'retained_result_payload_bytes': result_bytes,
                'task_result_metadata_forecast_bytes': forecast_transport,
                'within_task_result_forecast': True,
                'forecast_scope': 'Task/result payloads plus4096 bytes per completion; '
                                  'excludes native products, logs, receipts and snapshots.'})
        records.append({'collection': path.relative_to(directory).as_posix(),
            'current_logical_census': totals, 'declared_disk_limits': limits,
            'within_declared_disk_limits': fits, 'demand_forecast': forecast,
            'current_retained_within_repository_demand_envelope': demand_comparison,
            'current_staging_within_temporary_demand_envelope': staging_comparison,
            'plan_disk_limit_scope': 'Repository/temporary plan fields select free-space headroom; '
                'CodecBounds separately limits all collection bytes and aggregate staging bytes.',
            'current_staging_logical_bytes': sum(row['logical_bytes'] for row in staging_rows),
            'current_staging_files': sum(row['file_count'] for row in staging_rows),
            'stage_transport_accounts': stages,
            'historical_temporary_peak_bytes': None,
            'historical_temporary_peak_basis': 'Post-run census cannot recover removed staging '
                'or overlapping immutable copies. A live storage peak observer is required.',
            'physical_allocated_bytes': None, 'hardlink_discount': False})
    for prefix, producer_outputs, analytic_outputs in (
            (Path('.'), ('source',), ('audit-failed', 'audit-retry')),
            (Path('manufactured'), ('original-source',), ())):
        folder = directory/prefix
        config_path = folder/'source-inputs/execution.json'
        problem_path = folder/'source-inputs/problem.json'
        if not config_path.exists():
            blockers.append('missing source input plan: ' + config_path.relative_to(directory).as_posix())
            continue
        document(config_path)
        document(problem_path)
        _, config, bound = pipeline._bind(problem_path, config_path, ROOT)
        require(config['control'] is True, 'control directory contains a full source run')
        for role, outputs in (('producer', producer_outputs), ('analytic', analytic_outputs)):
            spec, plan = bound[role]
            model = pipeline.math_problem(problem, config['control'])
            head = (model.M-model.N)//2
            group_bytes = head*(head+1)//2*(2*((spec.grid_bits+35)//4)+64)
            overlap = plan.workers*(group_bytes+2*spec.bounds.max_raw_bytes)
            temporary_mib = max(128, (overlap+MIB-1)//MIB)
            require(plan.temporary_mib == temporary_mib and
                    spec.bounds.max_temporary_bytes == temporary_mib*MIB,
                    'small source temporary account differs from its actual factory')
            for name in outputs:
                target = folder/name if prefix == Path('manufactured') else folder/name/role
                inspect_collection(target, plan.to_dict(), asdict(spec.bounds),
                    {'factory': 'pipeline.prepare_source_inputs group/page overlap formula',
                     'temporary_demand_envelope_bytes': overlap,
                     'rounded_temporary_allowance_bytes': temporary_mib*MIB,
                     'repository_demand_envelope_bytes_pending': None,
                     'scope': 'Current source staging compared to derived group/page overlap, '
                              'not to the rounded128MiB minimum or full-profile ceiling.'})
        blockers.append('Source retained demand forecast is absent from its actual factory. '
                        'repository_mib and CodecBounds are allowed ceilings, not a prediction: ' +
                        config_path.relative_to(directory).as_posix())
    config_path = directory/'proposal-inputs/execution.json'
    if config_path.exists():
        config = document(config_path)
        context = config['context']
        forecast = proposal._proposal_accounts(context['dimension'], context['panel_size'])
        parity_checks = []
        for name in ('proposal-fresh', 'proposal-retry'):
            for p in (0, 1):
                parity_roots = [directory/name/(segment+'-'+str(p))
                                for segment in ('native', 'floating', 'solve')]
                present = [path for path in parity_roots if path.exists()]
                if len(present) == 3:
                    observed = sum(census(path)['logical_bytes'] for path in present)
                    snapshots = sum(census(path/'snapshots')['logical_bytes']
                                    for path in present if (path/'snapshots').exists())
                    graph_demand = forecast['per_parity_panel_disk_bytes']+forecast['retained_graph_bytes']
                    require(observed-snapshots <= graph_demand,
                            'retained small proposal graph exceeds its actual parity demand account')
                    parity_checks.append({'run': name, 'parity': p,
                        'observed_graph_logical_bytes_excluding_snapshots': observed-snapshots,
                        'snapshot_logical_bytes_separately_counted': snapshots,
                        'factory_graph_demand_bytes': graph_demand, 'within_forecast': True,
                        'temporary_historical_peak_bytes': None})
                for segment, phase in (('native', 'native'), ('floating', 'floating'), ('solve', 'native')):
                    data = config['phases'][phase]
                    inspect_collection(directory/name/(segment+'-'+str(p)),
                        data['execution'], data['collection']['bounds'],
                        {'factory': 'proposal._proposal_accounts', 'per_parity': forecast,
                         'scope': 'Shared parity graph demand envelope, not an independent '
                                  'whole-directory cap for each segment.'})
        for record in records:
            if record['collection'].startswith(('proposal-fresh/', 'proposal-retry/')):
                record['shared_parity_graph_forecast_checks'] = parity_checks
    else:
        blockers.append('missing manufactured proposal input plan')
    config_path = directory/'exact-inputs/execution.json'
    preparation_path = directory/'exact-inputs/preparation-account.json'
    if config_path.exists() and preparation_path.exists():
        config, preparation = document(config_path), document(preparation_path)
        recomputed = []
        for p, context in enumerate(preparation['contexts']):
            parameters = exact.paid_parameters(problem.arithmetic.publication_bits,
                Fraction(preparation['theta'][p]), problem.eta)
            current = exact.integer_bounds(context, parameters, problem.model_error)
            recorded = preparation['accounts'][p]
            require(all(recorded[key] == value for key, value in current.items()),
                    'actual small exact preparation forecast differs from its factory')
            recomputed.append(current)
        dependency = config['layout']['max_wave_tasks']*(
            config['execution']['task_bytes']+config['execution']['result_bytes']+1024)
        demand = 2*sum(row['staged_bytes'] for row in recomputed)+5*dependency+80*MIB
        require(demand <= config['execution']['repository_mib']*MIB,
                'actual small exact demand exceeds repository allowance')
        for name in ('exact-fresh', 'exact-retry'):
            inspect_collection(directory/name/'collection', config['execution'],
                config['collection']['bounds'],
                {'factory': 'exact.integer_bounds and prepare_exact_operands repository formula',
                 'actual_operand_accounts': recomputed, 'repository_demand_envelope_bytes': demand,
                 'temporary_demand_envelope_bytes': sum(row['staged_bytes'] for row in recomputed),
                 'scope': 'Inspected operand formula, not a historical temporary-peak measurement.'})
    else:
        blockers.append('missing manufactured exact input/preparation accounts')
    blockers.append('No historical temporary byte peak can be inferred from retained files.')
    return {'status': 'BLOCKED_RETAINED_DEMAND_AND_TEMPORARY_PEAK_VALIDATION',
        'scope': 'Actual small-run declared quotas and retained task/result forecast checks only.',
        'directory': directory.relative_to(ROOT).as_posix(), 'input_identities': inputs,
        'current_operation_census': census(directory), 'collections': records,
        'blockers': blockers, 'full_profile_ceiling_used_as_prediction': False,
        'numerical_work': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--control-dir', type=Path,
                        help='Read actual small-run retained plans and storage without executing work.')
    args = parser.parse_args()
    output = args.output.absolute()
    output.relative_to(ROOT)
    from_root = output.resolve()
    from_root.relative_to(ROOT)
    require(not output.exists() and not output.is_symlink(), 'output must be fresh')
    # Reject reparse/symlink ancestors before resolve can hide them.
    for ancestor in (output.parent, *output.parents):
        if ancestor.exists():
            info = ancestor.lstat()
            require(not ancestor.is_symlink() and not getattr(info, 'st_file_attributes', 0) & 0x400,
                    'output ancestor is a reparse point or symlink')
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT))
    guard = MetadataImports()
    sys.meta_path.insert(0, guard)
    result = {'format': 'whole-source-integrated-qualification-accounts-v1',
        'created_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'scope': 'METADATA_ONLY_PROSPECTIVE_ACCOUNTS', 'python': sys.version,
        'status': 'BLOCKED', 'metadata_validation': 'NOT_COMPLETED',
        'numerical_work': False, 'workers_started': False, 'execution_authorized': False,
        'scientific_acceptance': False, 'independent_review': False,
        'full_case_feasibility_established': False, 'full_workload_fit': False,
        'control_growth_validation': {'status': 'NOT_PERFORMED',
            'reason': 'This command does not execute controls or measure temporary peaks. '
                      'Small-control retained/temporary forecast validation belongs to the supervised driver.'}}
    try:
        require(not any(name.split('.')[0] in NUMERICAL for name in sys.modules),
                'numerical package already loaded')
        from scripts.whole_source import admission, execution, retention, supervision
        from scripts.whole_source.contract import bind_problem, problem_id
        problem = bind_problem('retained-t081')
        require(problem.N // 2 == 413 and problem.M == 1652, 'retained shape changed')
        names = sorted(set((*retention.CODE, *execution._RUNTIME,
            'scripts/whole_source/task_groups.py', 'scripts/whole_source/exact_tasks.py',
            'scripts/whole_source/recovery.py', Path(__file__).relative_to(ROOT).as_posix())))
        result['code'] = {name: identity(ROOT/name) for name in names}
        result['inputs'] = {ref.path: asdict(ref) for ref in problem.evidence}
        result['problem_id'] = problem_id(problem)
        result['geometry'] = {'N': problem.N, 'M': problem.M, 'K': problem.K,
            'parity_dimensions': [413, 413], 'families': 3, 'final_entries': 512946,
            'frequency_anchors': len(problem.frequency_edges),
            'source_bits': problem.arithmetic.source_bits,
            'audit_bits': problem.arithmetic.audit_bits,
            'publication_bits': problem.arithmetic.publication_bits,
            'checkpoint_bits': problem.arithmetic.checkpoint_bits}
        detected, existing = None, None
        try:
            detected = execution.exact_telemetry(execution.neutral_helpers(ROOT)[0].detect_resources())
            detected = supervision.constrain_detection(detected)
            existing = admission.current_commit(ROOT)
            result['host_sample'] = {'status': 'PASS_SNAPSHOT_ONLY', 'detected': detected,
                                    'current_process_committed_bytes': existing}
        except (ValueError, OSError, AttributeError) as error:
            result['host_sample'] = {'status': 'BLOCKED', 'error_type': type(error).__name__,
                                    'reason': str(error), 'detected': detected,
                                    'current_process_committed_bytes': existing}
        result['rows'] = [accounts(problem, width, detected, existing) for width in (16, 32)]
        if args.control_dir is not None:
            result['control_growth_validation'] = control_accounts(args.control_dir, problem)
        free = shutil.disk_usage(ROOT).free
        result['storage_snapshot'] = {'free_bytes': free, 'reservation': False,
            'scope': 'Current ROOT volume only; no external roots or existing run were supplied.',
            'by_tile': [{'tile_modes': row['tile_modes'],
                'logical_lifetime_allowance_bytes': row['logical_lifetime_allowance']['logical_allowance_bytes'],
                'status': 'PASS_HEADROOM_SNAPSHOT_ONLY' if free >=
                    row['logical_lifetime_allowance']['logical_allowance_bytes'] + 80*MIB else 'REFUSED_HEADROOM',
                'full_workload_fit': False} for row in result['rows']]}
        result['lifecycle'] = {'policy': supervision.POLICY, 'observer_root': '<run>.lifecycle',
            'finite_owner_policy_required': True, 'policy_supplied': False,
            'guardian_started': False, 'actual_outer_job_memory_cap_bytes': None,
            'observation_allowance_max_bytes': 16*MIB,
            'reason': 'No lifecycle permission is granted by this inspection.'}
        require(all(identity(ROOT/name) == value for name, value in result['code'].items()),
                'code changed during metadata inspection')
        result['metadata_validation'] = 'PASS'
        result['status'] = 'BLOCKED_ACTUAL_OPERANDS_PENDING'
        result['required_next_evidence'] = ['actual source/proposal exact-preparation bounds',
            'finite supervised lifecycle policy and live per-phase admission',
            'measured small retained and temporary growth against forecast']
    except (ValueError, OSError, ImportError, KeyError, TypeError) as error:
        result['status'] = 'REFUSED_METADATA_ACCOUNTS'
        result['metadata_validation'] = 'REFUSED'
        result['error'] = {'type': type(error).__name__, 'reason': str(error)}
    finally:
        result['numerical_packages_loaded'] = sorted(name for name in sys.modules
                                                    if name.split('.')[0] in NUMERICAL)
        sys.meta_path.remove(guard)
    if result['numerical_packages_loaded']:
        result['metadata_validation'] = 'REFUSED'
        result['status'] = 'REFUSED_NUMERICAL_IMPORT'
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        stream.write((json.dumps(result, sort_keys=True, separators=(',', ':'),
                                 ensure_ascii=True, allow_nan=False) + '\n').encode('ascii'))
    print(json.dumps({'status': result['status'], 'metadata_validation': result['metadata_validation'],
                      'output': output.relative_to(ROOT).as_posix(), 'numerical_work': False}))
    return 0 if result['metadata_validation'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
