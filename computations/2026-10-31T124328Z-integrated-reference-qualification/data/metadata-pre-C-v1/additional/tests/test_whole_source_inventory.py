"""Interrupted inventory publication retains every earlier byte as evidence."""
import hashlib
import json
from pathlib import Path

import pytest

from scripts.whole_source import retention
from scripts.whole_source.contract import ContractError, canonical_bytes


def _tree(directory):
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob('*')) if path.is_file()
    }


def _row(name, raw):
    return {'path': name, 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def _source(directory, count=2):
    source = directory/'source'
    source.mkdir()
    for index in range(count):
        (source/f'{index:06d}.dat').write_bytes(f'evidence:{index:06d}\n'.encode('ascii'))
    (directory/'.slice.lock').write_bytes(b'writer lock\n')


def _interrupt(directory, monkeypatch, phase):
    original = retention._write
    calls = []

    def write(path, raw):
        path = Path(path)
        relative = path.relative_to(directory).as_posix()
        if ((phase == 'first-shard' and path.name == '000000.json') or
                (phase == 'between-shards' and path.name == '000001.json') or
                (phase == 'manifest' and relative == 'retained-manifest.json')):
            calls.append(relative)
            raise OSError('injected inventory publication failure')
        return original(path, raw)

    with monkeypatch.context() as patch:
        patch.setattr(retention, '_write', write)
        with pytest.raises(OSError, match='injected inventory publication failure'):
            retention._seal(directory)
    assert len(calls) == 1
    assert not (directory/'retained-manifest.json').exists()
    return Path(calls[0])


def _manifest(directory):
    return json.loads((directory/'retained-manifest.json').read_bytes())


def _members(directory, manifest):
    return [row for ref in manifest['shards']
            for row in json.loads((directory/ref['path']).read_bytes())['files']]


def _assert_full_inventory(directory, result):
    manifest = _manifest(directory)
    assert result['status'] == 'PASS_RETAINED_INVENTORY'
    assert manifest['format'] == 'whole-source-retained-inventory-v2'
    assert manifest['excluded'] == ['.slice.lock', 'retained-manifest.json']
    assert manifest['production_admission'] is False
    active = [manifest['snapshot'], manifest['intent'], *manifest['shards']]
    for ref in active:
        assert ref == _row(ref['path'], (directory/ref['path']).read_bytes())
    generation = Path(manifest['snapshot']['path']).parent
    assert generation.parent.as_posix() == 'inventory'
    assert manifest['generation'] == generation.name
    assert len(generation.name) == 32
    assert all(character in '0123456789abcdef' for character in generation.name)
    assert Path(manifest['intent']['path']) == generation/'intent.json'
    assert all(Path(ref['path']).parent == generation for ref in manifest['shards'])
    assert [Path(ref['path']).name for ref in manifest['shards']] == [
        f'{index:06d}.json' for index in range(len(manifest['shards']))]
    ignored = {'.slice.lock', 'retained-manifest.json', *(ref['path'] for ref in active)}
    expected = [_row(name, raw) for name, raw in sorted(_tree(directory).items())
                if name not in ignored]
    assert _members(directory, manifest) == expected
    assert result['members'] == len(expected)
    snapshot = (directory/manifest['snapshot']['path']).read_bytes()
    assert snapshot == b''.join(canonical_bytes(row) for row in expected)
    intent = json.loads((directory/manifest['intent']['path']).read_bytes())
    assert intent['format'] == 'whole-source-inventory-intent-v1'
    assert intent['snapshot'] == manifest['snapshot']
    assert retention.verify_inventory(directory) == result
    return manifest


@pytest.mark.parametrize('phase,count,old_shards', [
    ('first-shard', 2, 0),
    ('between-shards', 4097, 1),
    ('manifest', 2, 1),
])
def test_publication_failure_retries_in_a_fresh_generation_without_rewriting(
        tmp_path, monkeypatch, phase, count, old_shards):
    _source(tmp_path, count)
    original = _tree(tmp_path)
    _interrupt(tmp_path, monkeypatch, phase)
    interrupted = _tree(tmp_path)
    assert all(interrupted[name] == raw for name, raw in original.items())
    intents = list((tmp_path/'inventory').glob('*/intent.json'))
    assert len(intents) == 1
    old_generation = intents[0].parent
    assert len(list(old_generation.glob('[0-9]*.json'))) == old_shards
    result = retention._seal(tmp_path)
    manifest = _assert_full_inventory(tmp_path, result)
    assert (tmp_path/manifest['intent']['path']).parent != old_generation
    assert all((tmp_path/name).read_bytes() == raw for name, raw in interrupted.items())
    member_names = {row['path'] for row in _members(tmp_path, manifest)}
    assert set(interrupted) - {'.slice.lock'} <= member_names


@pytest.mark.parametrize('change', ['replace', 'delete'])
def test_retry_rejects_changed_snapshot_members_without_writing(tmp_path, monkeypatch, change):
    _source(tmp_path)
    _interrupt(tmp_path, monkeypatch, 'first-shard')
    member = tmp_path/'source'/'000000.dat'
    if change == 'replace':
        member.write_bytes(b'changed source bytes\n')
    else:
        member.unlink()
    before = _tree(tmp_path)
    with pytest.raises(ContractError):
        retention._seal(tmp_path)
    assert _tree(tmp_path) == before


@pytest.mark.parametrize('change', ['invalid-json', 'wrong-format', 'missing-snapshot', 'snapshot-hash'])
def test_retry_rejects_malformed_pending_intent_without_writing(tmp_path, monkeypatch, change):
    _source(tmp_path)
    _interrupt(tmp_path, monkeypatch, 'first-shard')
    path = next((tmp_path/'inventory').glob('*/intent.json'))
    intent = json.loads(path.read_bytes())
    if change == 'invalid-json':
        raw = b'{not json\n'
    else:
        if change == 'wrong-format':
            intent['format'] = 'unrecognized-inventory-intent'
        elif change == 'missing-snapshot':
            del intent['snapshot']
        else:
            intent['snapshot']['sha256'] = '0'*64
        raw = canonical_bytes(intent)
    path.write_bytes(raw)
    before = _tree(tmp_path)
    with pytest.raises(ContractError):
        retention._seal(tmp_path)
    assert _tree(tmp_path) == before


def test_retry_validates_every_pending_generation_before_writing(tmp_path, monkeypatch):
    _source(tmp_path)
    _interrupt(tmp_path, monkeypatch, 'first-shard')
    first = next((tmp_path/'inventory').glob('*/snapshot.jsonl'))
    _interrupt(tmp_path, monkeypatch, 'manifest')
    assert len(list((tmp_path/'inventory').glob('*/intent.json'))) == 2
    first.write_bytes(first.read_bytes() + b'changed\n')
    before = _tree(tmp_path)
    with pytest.raises(ContractError):
        retention._seal(tmp_path)
    assert _tree(tmp_path) == before


@pytest.mark.parametrize('changed', [
    'inventory/000000.json',
    'inventory/.000001.json.' + 'a'*32 + '.tmp',
    'inventory/' + 'b'*32 + '/snapshot.jsonl',
])
def test_unfinished_v1_shards_temporary_files_and_orphan_snapshots_are_hash_bound(tmp_path, changed):
    _source(tmp_path)
    evidence = {
        'inventory/000000.json': canonical_bytes({'files': [_row('old.dat', b'old')]}),
        'inventory/.000001.json.' + 'a'*32 + '.tmp': b'partial old shard\n',
        'inventory/' + 'b'*32 + '/snapshot.jsonl': b'orphan snapshot without intent\n',
    }
    for name, raw in evidence.items():
        path = tmp_path/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    before = _tree(tmp_path)
    manifest = _assert_full_inventory(tmp_path, retention._seal(tmp_path))
    assert all((tmp_path/name).read_bytes() == raw for name, raw in before.items())
    members = {row['path']: row for row in _members(tmp_path, manifest)}
    assert all(members[name] == _row(name, raw) for name, raw in evidence.items())
    path = tmp_path/changed
    path.write_bytes(path.read_bytes() + b'changed\n')
    with pytest.raises(ContractError):
        retention.verify_inventory(tmp_path)


def test_completed_v2_seal_only_verifies_and_preserves_every_byte(tmp_path):
    _source(tmp_path)
    expected = retention._seal(tmp_path)
    _assert_full_inventory(tmp_path, expected)
    before = _tree(tmp_path)
    assert retention._seal(tmp_path) == expected
    assert retention.verify_inventory(tmp_path) == expected
    assert _tree(tmp_path) == before


def test_completed_v1_keeps_its_verifier_result_and_every_byte(tmp_path):
    _source(tmp_path)
    rows = [_row(name, raw) for name, raw in sorted(_tree(tmp_path).items())
            if name != '.slice.lock']
    shard_name = 'inventory/000000.json'
    shard = canonical_bytes({'files': rows})
    (tmp_path/'inventory').mkdir()
    (tmp_path/shard_name).write_bytes(shard)
    manifest = {
        'format': 'whole-source-retained-inventory-v1',
        'excluded': ['.slice.lock', 'retained-manifest.json'],
        'shards': [_row(shard_name, shard)],
        'production_admission': False,
    }
    manifest_bytes = canonical_bytes(manifest)
    path = tmp_path/'retained-manifest.json'
    path.write_bytes(manifest_bytes)
    expected = {
        'status': 'PASS_RETAINED_INVENTORY',
        'members': len(rows),
        'manifest': {'directory': str(tmp_path.resolve()),
                     'artifact': _row('retained-manifest.json', manifest_bytes)},
    }
    before = _tree(tmp_path)
    assert retention.verify_inventory(tmp_path) == expected
    assert retention._seal(tmp_path) == expected
    assert _tree(tmp_path) == before


@pytest.mark.parametrize('change', [
    'addition', 'replacement', 'deletion', 'active-shard', 'active-snapshot',
    'active-intent', 'extra-generation-file',
])
def test_postseal_mutation_is_rejected_by_verification_and_reseal(tmp_path, change):
    _source(tmp_path)
    retention._seal(tmp_path)
    manifest = _manifest(tmp_path)
    if change == 'addition':
        (tmp_path/'source'/'added.dat').write_bytes(b'new evidence\n')
    elif change == 'replacement':
        (tmp_path/'source'/'000000.dat').write_bytes(b'changed evidence\n')
    elif change == 'deletion':
        (tmp_path/'source'/'000000.dat').unlink()
    elif change == 'extra-generation-file':
        generation = (tmp_path/manifest['snapshot']['path']).parent
        (generation/'extra.tmp').write_bytes(b'unbound evidence\n')
    else:
        ref = (manifest['shards'][0] if change == 'active-shard'
               else manifest['snapshot'] if change == 'active-snapshot'
               else manifest['intent'])
        path = tmp_path/ref['path']
        path.write_bytes(path.read_bytes() + b'changed\n')
    before = _tree(tmp_path)
    with pytest.raises(ContractError):
        retention.verify_inventory(tmp_path)
    with pytest.raises(ContractError):
        retention._seal(tmp_path)
    assert _tree(tmp_path) == before

def test_retry_rejects_a_conflicting_committed_pending_shard(tmp_path, monkeypatch):
    _source(tmp_path)
    _interrupt(tmp_path, monkeypatch, 'manifest')
    shard = next((tmp_path/'inventory').glob('*/000000.json'))
    shard.write_bytes(canonical_bytes({'files': []}))
    before = _tree(tmp_path)
    with pytest.raises(ContractError):
        retention._seal(tmp_path)
    assert _tree(tmp_path) == before


@pytest.mark.parametrize('filename', ['snapshot.jsonl', 'intent.json'])
def test_snapshot_or_intent_publication_failure_retains_orphans_and_retries(tmp_path, monkeypatch, filename):
    _source(tmp_path)
    original = retention._write

    def stop(path, raw):
        if Path(path).name == filename:
            raise OSError('controlled generation metadata failure')
        return original(path, raw)

    def stop_snapshot(directory, path, names):
        raise OSError('controlled generation metadata failure')

    with monkeypatch.context() as patch:
        if filename == 'snapshot.jsonl':
            patch.setattr(retention, '_write_inventory_snapshot', stop_snapshot)
        else:
            patch.setattr(retention, '_write', stop)
        with pytest.raises(OSError):
            retention._seal(tmp_path)
    before = _tree(tmp_path)
    result = retention._seal(tmp_path)
    _assert_full_inventory(tmp_path, result)
    assert all((tmp_path/name).read_bytes() == raw for name, raw in before.items())


def test_member_change_during_publication_prevents_final_manifest(tmp_path, monkeypatch):
    _source(tmp_path)
    original = retention._write

    def changed_member(path, raw):
        result = original(path, raw)
        if Path(path).name == '000000.json':
            (tmp_path/'source/000000.dat').write_bytes(b'changed during publication')
        return result

    with monkeypatch.context() as patch:
        patch.setattr(retention, '_write', changed_member)
        with pytest.raises(ContractError):
            retention._seal(tmp_path)
    assert not (tmp_path/'retained-manifest.json').exists()


def test_snapshot_encodes_each_member_before_hashing_the_next(tmp_path, monkeypatch):
    _source(tmp_path, 3)
    original_hash, original_encode = retention._hash_file, retention.canonical_bytes
    encoded = set()

    def encode(value):
        if type(value) is dict and set(value) == {'path', 'size', 'sha256'}:
            encoded.add(value['path'])
        return original_encode(value)

    def hashed(path):
        if Path(path) == tmp_path/'source/000001.dat':
            assert 'source/000000.dat' in encoded
        return original_hash(path)

    monkeypatch.setattr(retention, '_hash_file', hashed)
    monkeypatch.setattr(retention, 'canonical_bytes', encode)
    _assert_full_inventory(tmp_path, retention._seal(tmp_path))


@pytest.mark.parametrize('phase', ['short-write', 'fsync', 'replace'])
def test_streamed_snapshot_failure_retains_partial_evidence_and_retries(tmp_path, monkeypatch, phase):
    _source(tmp_path)
    original_open, original_fsync, original_replace = Path.open, retention.os.fsync, retention.os.replace

    class ShortWriter:
        def __init__(self, stream):
            self.stream = stream
        def __enter__(self):
            self.stream.__enter__()
            return self
        def __exit__(self, *args):
            return self.stream.__exit__(*args)
        def write(self, raw):
            return self.stream.write(raw[:-1])

    def opened(path, *args, **kwargs):
        stream = original_open(path, *args, **kwargs)
        if phase == 'short-write' and path.name.startswith('.snapshot.jsonl.'):
            return ShortWriter(stream)
        return stream

    def synced(fd):
        if phase == 'fsync':
            raise OSError('controlled snapshot fsync failure')
        return original_fsync(fd)

    def replaced(source, target):
        if phase == 'replace' and Path(target).name == 'snapshot.jsonl':
            raise OSError('controlled snapshot replace failure')
        return original_replace(source, target)

    with monkeypatch.context() as patch:
        patch.setattr(Path, 'open', opened)
        patch.setattr(retention.os, 'fsync', synced)
        patch.setattr(retention.os, 'replace', replaced)
        with pytest.raises((ContractError, OSError)):
            retention._seal(tmp_path)
    before = _tree(tmp_path)
    assert any('/.snapshot.jsonl.' in name for name in before)
    assert not list((tmp_path/'inventory').glob('*/intent.json'))
    _assert_full_inventory(tmp_path, retention._seal(tmp_path))
    assert all((tmp_path/name).read_bytes() == raw for name, raw in before.items())


def test_multishard_verification_hashes_consumers_before_decoding_the_next_shard(tmp_path, monkeypatch):
    _source(tmp_path, 4097)
    retention._seal(tmp_path)
    original_json, original_hash = retention._json, retention._hash_file
    checked, shards = 0, 0

    def hashed(path):
        nonlocal checked
        result = original_hash(path)
        if Path(path).parent == tmp_path/'source':
            checked += 1
        return result

    def decoded(raw):
        nonlocal shards
        value = original_json(raw)
        if 'files' in value:
            if shards:
                assert checked >= 4096
            assert len(value['files']) <= 4096
            shards += 1
        return value

    monkeypatch.setattr(retention, '_hash_file', hashed)
    monkeypatch.setattr(retention, '_json', decoded)
    assert retention.verify_inventory(tmp_path)['members'] == 4097
    assert checked == 4097 and shards == 2


def test_pending_noncontiguous_shard_subset_is_validated_and_retained(tmp_path, monkeypatch):
    _source(tmp_path, 4097)
    _interrupt(tmp_path, monkeypatch, 'manifest')
    generation = next((tmp_path/'inventory').glob('*/intent.json')).parent
    (generation/'000000.json').unlink()
    before = _tree(tmp_path)
    manifest = _assert_full_inventory(tmp_path, retention._seal(tmp_path))
    assert manifest['generation'] != generation.name
    assert all((tmp_path/name).read_bytes() == raw for name, raw in before.items())
