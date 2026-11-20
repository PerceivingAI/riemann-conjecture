"""Bound source-task producers and complete artifact-derived stage selection."""
from dataclasses import asdict
import json
from pathlib import Path

from scripts.whole_source.contract import ArtifactRef, ContractError, QuantityKey, canonical_bytes
from scripts.whole_source.artifacts import _raw, _safe, _task
from scripts.whole_source.execution import MIB, _bytes, _json
from scripts.whole_source.receipts import discover_receipts, verify_stage
from scripts.whole_source.reuse import panel_inputs


def _require(value, message):
    if not value:
        raise ContractError(message)


def _ref(root, path):
    from scripts.whole_source.slice import _ref as reference
    return reference(root, path)


def check_history(root):
    """Cleanup is independent of whether an attempt contributes mathematics."""
    refs = []
    for path in discover_receipts(root):
        value = json.loads(_bytes(path))
        # last_metrics can precede cleanup on a failed stage; it is not final state.
        _require(value.get('worker_cleanup_verified') is True,
                 'uncontained source execution history')
        refs.append(asdict(_ref(root, path.relative_to(root).as_posix())))
    return refs


def _description(artifact, kind, domain):
    return {'artifact': asdict(artifact), 'kind': kind, 'domain': domain}


def _expression(spec, request, payload):
    """Derive the closed input/output interface of each actual source operation."""
    from scripts.whole_source.pipeline import (
        _column_task, _kernel_panels, _quantities, _tiles, COMPLETE, FAMILIES, math_problem,
    )
    from scripts.whole_source.artifacts import ContributionTask
    p, control, operation = request['parity'], request['control'], request['operation']
    _require(type(p) is int and p in (0, 1) and type(control) is bool and
             spec.quantities == _quantities(spec.problem, control), 'dependency source context differs')
    model = math_problem(spec.problem, control)
    data = payload['result']
    _require(set(data) == {'chunks', 'publications', 'kernel_group', 'scope', 'statistics'} and
             data['scope'] == 'SOURCE_EXPRESSIONS_ONLY', 'dependency result scope differs')
    inputs, expected = [], []
    base = {'task_id', 'operation', 'parity', 'control'}
    fields = {'kernel-group': {'anchor_start', 'anchor_stop'}, 'kernel-reduce': {'domain', 'groups'},
              'columns': {'inputs'}, 'heads': {'inputs','kernel'}, 'final': {'domain', 'columns'}}
    _require(operation in fields and set(request) == base | fields[operation],
             'unknown source dependency operation')
    def dependency(ref, kind, domain):
        inputs.append(_description(ArtifactRef(**ref), kind, domain))
    def output(kind, domain):
        expected.append((kind, domain))
    if operation == 'kernel-group':
        start, stop = request['anchor_start'], request['anchor_stop']
        _require(type(start) is type(stop) is int and
                 0 <= start < stop <= len(model.frequency_edges), 'dependency anchor range differs')
        for domain in _kernel_panels(spec, p):
            output('kernel_page', {'task': domain.to_dict(), 'anchor_start': start, 'anchor_stop': stop})
    elif operation == 'kernel-reduce':
        domain = _task(request['domain'])
        _require(domain in list(_kernel_panels(spec, p)), 'dependency kernel domain differs')
        next_anchor = 0
        for group in request['groups']:
            _require(set(group) == {'anchor_start', 'anchor_stop', 'artifact'} and
                     group['anchor_start'] == next_anchor and
                     type(group['anchor_stop']) is int and next_anchor < group['anchor_stop'],
                     'dependency anchor cover differs')
            dependency(group['artifact'], 'kernel_page', {'task': domain.to_dict(),
                       'anchor_start': group['anchor_start'], 'anchor_stop': group['anchor_stop']})
            next_anchor = group['anchor_stop']
        _require(next_anchor == len(model.frequency_edges), 'incomplete dependency anchor cover')
        for tile in _tiles(spec, QuantityKey('kernel_complete', p)):
            if tile.rows == domain.rows:
                output('chunk', tile.to_dict())
    elif operation in ('columns','heads'):
        values = request['inputs']
        if operation == 'heads':
            _require(type(values) is list and all(type(row) is dict and set(row)=={'n','F'} for row in values),
                     'dependency head panel differs')
            values = [row['n'] for row in values]
        _require(type(values) is list,'dependency input panel differs')
        try:
            inputs_n = panel_inputs(model,values)
        except (TypeError,ValueError) as exc:
            raise ContractError('dependency column panel differs') from exc
        _require(all(n%2==p for n in inputs_n),'dependency column parity differs')
        if operation == 'columns':
            for n in inputs_n:
                output('chunk',_column_task(spec,'F_column',n).to_dict())
        else:
            for row in request['inputs']:
                dependency(row['F'],'chunk',_column_task(spec,'F_column',row['n']).to_dict())
            kernels = list(_tiles(spec,QuantityKey('kernel_complete',p)))
            _require(len(request['kernel']) == len(kernels),'incomplete dependency kernel cover')
            for ref,domain in zip(request['kernel'],kernels,strict=True):
                dependency(ref,'chunk',domain.to_dict())
            for n in inputs_n:
                for name in ('head_column','head_image'):
                    output('chunk',_column_task(spec,name,n).to_dict())
    else:
        domain = _task(request['domain'])
        _require(domain in list(_tiles(spec, QuantityKey('A_model', p))), 'dependency final domain differs')
        modes = sorted(set(domain.rows) | set(domain.columns))
        _require([row['n'] for row in request['columns']] == modes, 'incomplete dependency column cover')
        for row in request['columns']:
            _require(set(row) == {'n', 'F', 'C', 'Y'}, 'foreign dependency column fields')
            for label, name in (('F', 'F_column'), ('C', 'head_column'), ('Y', 'head_image')):
                dependency(row[label], 'chunk', _column_task(spec, name, row['n']).to_dict())
        for name in FAMILIES.values():
            output('publication', ContributionTask(QuantityKey(name, p), domain.rows, domain.columns, COMPLETE).to_dict())
    emitted = []
    if operation == 'kernel-group':
        group = data['kernel_group']
        _require(not data['chunks'] and not data['publications'] and
                 (group['anchor_start'], group['anchor_stop']) ==
                 (request['anchor_start'], request['anchor_stop']), 'foreign dependency kernel result')
        for panel in group['panels']:
            emitted.append(('kernel_page', {'task': panel['domain'],
                'anchor_start': group['anchor_start'], 'anchor_stop': group['anchor_stop']},
                ArtifactRef(**panel['artifact'])))
    else:
        _require(data['kernel_group'] is None, 'unexpected partial kernel dependency')
        for kind, field in (('chunk', 'chunks'), ('publication', 'publications')):
            for wire in data[field]:
                _require(wire['attempt_id'] == payload['attempt_id'] and
                         wire['generation'] == payload['generation'], 'foreign dependency staged ownership')
                emitted.append((kind, wire['task'], ArtifactRef(**wire['ref'])))
    _require([(kind, domain) for kind, domain, _ in emitted] == expected,
             'dependency output domain/cover differs')
    outputs = []
    for kind, domain, ref in emitted:
        _require(ref.path.startswith('attempts/'+payload['attempt_id']+'/staging/'),
                 'foreign dependency staged output')
        family = 'chunks' if kind == 'chunk' else 'seals'
        outputs.append(_description(ArtifactRef(family+'/'+ref.sha256, ref.sha256, ref.size), kind, domain))
    return inputs, outputs


class SourceDependencies:
    """One verified catalog per collection; native payloads stay bounded on disk."""
    def __init__(self, root, spec, plan):
        self.root, self.spec, self.plan = Path(root).resolve(), spec, plan
        self.stages = {}

    def _stage(self, ref):
        key = canonical_bytes(ref)
        if key not in self.stages:
            path = self.root/ref['path']
            _raw(self.root, ArtifactRef(**ref), 8*MIB)
            evidence = verify_stage(path)
            stage, plan = evidence['stage'], evidence['plan']
            _require(stage['plan'] == self.plan.to_dict() and plan.collection_sha256 == self.spec.collection_id and
                     stage['collection'] == self.spec.to_dict() and plan.task_function == 'evaluate_source' and
                     plan.role == self.spec.role and plan.threads == self.spec.native_threads,
                     'source stage belongs to another operational collection')
            tasks = {}
            with Path(stage['task_file']).open('rb') as stream:
                for line in stream:
                    task = _json(line)
                    tasks[task['task_id']] = task
            results = {}
            with (Path(stage['result_dir'])/'completed.jsonl').open('rb') as stream:
                for line in stream:
                    row = _json(line)
                    result_ref = {k: row[k] for k in ('path', 'sha256', 'size')}
                    identity = Path(row['path']).stem
                    _require(row['path'] == identity+'.json' and identity in tasks,
                             'dependency result filename differs')
                    results[identity] = result_ref
            self.stages[key] = evidence, tasks, results
        return self.stages[key]

    def bind(self, lock, name, result):
        """Persist producer claims before the sole owner commits their bytes."""
        attempt = self.root/'attempts'/result['attempt_id']
        receipt = asdict(_ref(self.root, (attempt/name/'receipt.json').relative_to(self.root).as_posix()))
        evidence, tasks, results = self._stage(receipt)
        identity = result['task_id']
        _require(identity in tasks and identity in results, 'missing dependency task result')
        result_ref = results[identity]
        payload = _json(_raw(Path(evidence['stage']['result_dir']), ArtifactRef(**result_ref), self.plan.result_bytes))
        _require(payload == result, 'dependency result differs from completed payload')
        inputs, outputs = _expression(self.spec, tasks[identity], payload)
        folder = _safe(self.root, 'dependencies', missing=True)
        folder.mkdir(exist_ok=True)
        for output in outputs:
            record = {'format': 'whole-source-artifact-dependency-v1', 'collection_id': self.spec.collection_id,
                      'output': output, 'receipt': receipt, 'task_id': identity,
                      'result': result_ref, 'inputs': inputs}
            raw = canonical_bytes(record)
            _require(len(raw) <= self.spec.bounds.max_header_bytes, 'dependency metadata cap')
            relative = 'dependencies/'+output['artifact']['sha256']+'.json'
            if not (self.root/relative).exists():
                lock._exclusive(relative, raw)
            else:
                # A successful identical-task retry retains the first producer.
                previous = _json(_bytes(self.root/relative))
                _require(previous['output'] == output, 'conflicting dependency output')
                self._node(previous)

    def _node(self, record):
        _require(set(record) == {'format', 'collection_id', 'output', 'receipt', 'task_id', 'result', 'inputs'} and
                 record['format'] == 'whole-source-artifact-dependency-v1' and
                 record['collection_id'] == self.spec.collection_id, 'foreign dependency binding')
        evidence, tasks, results = self._stage(record['receipt'])
        identity = record['task_id']
        _require(identity in tasks and results.get(identity) == record['result'],
                 'dependency producer is not a completed task')
        payload = _json(_raw(Path(evidence['stage']['result_dir']), ArtifactRef(**record['result']), self.plan.result_bytes))
        inputs, outputs = _expression(self.spec, tasks[identity], payload)
        _require(record['inputs'] == inputs and record['output'] in outputs,
                 'dependency binding differs from executed task')
        return inputs

    def select(self, tiles):
        selected, receipts, active, visited = {}, {}, set(), set()
        def visit(description):
            ref = ArtifactRef(**description['artifact'])
            identity = canonical_bytes(description)
            _require(identity not in active, 'cyclic source dependencies')
            if identity in visited:
                return
            active.add(identity)
            _raw(self.root, ref, self.spec.bounds.max_raw_bytes)
            path = 'dependencies/'+ref.sha256+'.json'
            binding_ref = _ref(self.root, path)
            record = _json(_raw(self.root, binding_ref, self.spec.bounds.max_header_bytes))
            _require(record['output'] == description, 'dependency artifact/domain differs')
            for dependency in self._node(record):
                visit(dependency)
            selected[path] = asdict(binding_ref)
            receipts[record['receipt']['path']] = record['receipt']
            active.remove(identity)
            visited.add(identity)
        for tile in tiles:
            visit({'artifact': tile['artifact'], 'kind': 'publication', 'domain': tile['task']})
        all_receipts = check_history(self.root)
        history = [ref for ref in all_receipts if ref['path'] not in receipts]
        return {'receipts': [receipts[k] for k in sorted(receipts)],
                'dependencies': [selected[k] for k in sorted(selected)], 'history': history}
