"""Retention output boundaries on disposable metadata, never scientific acceptance."""
from pathlib import Path

import pytest

from scripts.whole_source import pipeline, retention
from scripts.whole_source.contract import ContractError, canonical_bytes


@pytest.fixture(autouse=True)
def synthetic_guardian(monkeypatch):
    """Path-only tests bypass OS authority, never science or approval gates."""
    from scripts.whole_source import supervision
    monkeypatch.setattr(supervision, 'require_current',
                        lambda: {'scope': 'SYNTHETIC_PATH_CONTROL_NONAPPROVAL'})


@pytest.fixture(params=['accept', 'prepare_review'])
def operation(request):
    return getattr(retention, request.param)


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() if p.is_file() else None
            for p in root.rglob('*')}


def prerequisites(monkeypatch, run):
    """Explicit synthetic upstream metadata leaves path/publication logic real."""
    from contextlib import nullcontext
    from scripts.whole_source import admission
    monkeypatch.setattr(admission, 'admitted_problem', lambda *args: None)
    monkeypatch.setattr(admission, 'admitted_phase', lambda *args, **kw: nullcontext({}))
    monkeypatch.setattr(retention, '_selected_supervision',
                        lambda *args: [{'scope': 'SYNTHETIC_PATH_CONTROL_NONAPPROVAL'}])
    ref = {'directory': str(run), 'artifact': {'path': 'placeholder.json'}}
    (run/'pipeline-result.json').write_bytes(canonical_bytes(
        {'problem': ref, 'source_execution': ref}))
    (run/'review-decision.json').write_bytes(b'{}')
    monkeypatch.setattr(pipeline, '_bind', lambda *args: (None, None, {}))
    monkeypatch.setattr(retention, '_validate_review', lambda *args: {})
    monkeypatch.setattr(retention, '_review_manifest', lambda *args: {'scope': 'METADATA_ONLY'})


@pytest.mark.parametrize('kind', ['same-run', 'other-sealed', 'enclosing-sealed',
    'normalized', 'root-sealed', 'sealed-destination', 'malformed', 'directory-marker'])
def test_rejected_output_preserves_membership_before_lock_or_publication(tmp_path, monkeypatch, operation, kind):
    root = tmp_path
    run = root/'retained'/'run' if kind == 'enclosing-sealed' else root/'run'
    run.mkdir(parents=True)
    prerequisites(monkeypatch, run)
    protected = root/'retained'
    protected.mkdir(exist_ok=True)
    output = protected/'new'/'assessment'
    valid_seal = True
    if kind == 'same-run':
        protected, output = run, run/'assessment'
    elif kind == 'enclosing-sealed':
        output = protected/'results'/'assessment'
    elif kind == 'normalized':
        output = protected/'unused'/'..'/'assessment'
    elif kind == 'root-sealed':
        protected, output = root, root/'assessment'
    elif kind == 'sealed-destination':
        output = protected
    elif kind in ('malformed', 'directory-marker'):
        valid_seal = False
        marker = protected/'retained-manifest.json'
        if kind == 'malformed':
            marker.write_bytes(b'not json')
        else:
            marker.mkdir()
    if valid_seal:
        retention._seal(protected)
    before = snapshot(root)
    with pytest.raises(ContractError, match='outside|sealed'):
        operation(run, output, code_root=root)
    assert snapshot(root) == before
    assert not (run/'.slice.lock').exists()
    if kind != 'sealed-destination':
        assert not output.resolve().exists()
    if valid_seal:
        assert retention.verify_inventory(protected)['status'] == 'PASS_RETAINED_INVENTORY'


def test_seal_inspection_denial_rejects_without_creating_paths(tmp_path, monkeypatch, operation):
    run = tmp_path/'run'
    run.mkdir()
    output = tmp_path/'results'/'assessment'
    marker = tmp_path/'results'/'retained-manifest.json'
    original = Path.lstat

    def denied(path, *args, **kwargs):
        if path == marker:
            raise PermissionError('fixture seal inspection denied')
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'lstat', denied)
    before = snapshot(tmp_path)
    with pytest.raises(ContractError, match='inspect.*seal'):
        operation(run, output, code_root=tmp_path)
    assert snapshot(tmp_path) == before


def test_seal_published_during_validation_rejects_before_output(tmp_path, monkeypatch, operation):
    run = tmp_path/'run'
    run.mkdir()
    prerequisites(monkeypatch, run)
    target = tmp_path/'results'
    target.mkdir()
    output = target/'assessment'

    def newly_sealed(*args):
        retention._seal(target)
        return {'scope': 'METADATA_ONLY'}

    name = '_validate_review' if operation is retention.accept else '_review_manifest'
    monkeypatch.setattr(retention, name, newly_sealed)
    with pytest.raises(ContractError, match='sealed'):
        operation(run, output, code_root=tmp_path)
    assert not output.exists()
    assert retention.verify_inventory(target)['status'] == 'PASS_RETAINED_INVENTORY'


def test_fresh_sibling_reaches_existing_validation_without_output(tmp_path, monkeypatch, operation):
    run = tmp_path/'run'
    run.mkdir()
    prerequisites(monkeypatch, run)
    output = tmp_path/'results'/'assessment'

    class ValidationReached(Exception):
        pass

    def reject_science(*args):
        raise ValidationReached('explicit stop before synthetic science could be accepted')

    name = '_validate_review' if operation is retention.accept else '_review_manifest'
    monkeypatch.setattr(retention, name, reject_science)
    with pytest.raises(ValidationReached):
        operation(run, output, code_root=tmp_path)
    assert not output.parent.exists()


def test_output_outside_code_root_rejects_before_lock(tmp_path, operation):
    root = tmp_path/'root'
    root.mkdir()
    run = root/'run'
    run.mkdir()
    before = snapshot(tmp_path)
    with pytest.raises(ValueError):
        operation(run, tmp_path/'external', code_root=root)
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize('kind',['same-run','ancestor','sealed-run','sealed-output','sealed-ancestor'])
def test_assessment_publication_recovery_rejects_forbidden_paths_before_lock(tmp_path,kind):
    run = tmp_path/'science'/'run'
    run.mkdir(parents=True)
    output = tmp_path/'assessment'
    output.mkdir()
    (output/'assessment-publication.json').write_bytes(b'{}')
    if kind=='same-run':
        output = run/'assessment'
    elif kind=='ancestor':
        output = run.parent
    elif kind=='sealed-run':
        retention._seal(run)
    elif kind=='sealed-output':
        retention._seal(output)
    else:
        retention._seal(run.parent)
    before = snapshot(tmp_path)
    with pytest.raises(ContractError,match='outside|sealed'):
        retention.recover_assessment_publication(run,output,code_root=tmp_path)
    assert snapshot(tmp_path)==before
    assert not (run/'.slice.lock').exists()
