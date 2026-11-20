"""Read-only recovery evidence census; no unlinking, relinking or history repair."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


def category(relative):
    parts = relative.parts
    name = relative.name
    if 'staging' in parts:
        return 'staging-retained-not-authorized-for-deletion'
    if 'recovery' in parts or 'recovery-terminal' in parts or 'recovery-' in name:
        return 'journal-adoption-terminal'
    if 'runtime' in parts:
        return 'captured-runtime-and-inputs'
    if 'attempts' in parts:
        return 'owned-task-result-profile-stream-cleanup-history'
    if any('pending' in p or 'generation' in p for p in parts):
        return 'pending-retention-history'
    if 'review' in name or 'assessment' in name:
        return 'external-review-assessment'
    if 'seals' in parts or 'panels' in parts:
        return 'immutable-mathematical-and-group-payloads'
    if 'inputs' in str(relative) or 'source' in str(relative) or 'operand' in name:
        return 'source-original-normalized-inputs'
    return 'operation-other-retained'


def census(root):
    root = Path(root).resolve(strict=True)
    rows, classes, physical, unsupported = [], {}, {}, []
    for folder, directories, names in os.walk(root, followlinks=False):
        for directory in list(directories):
            path = Path(folder)/directory
            if path.is_symlink() or getattr(path.lstat(), 'st_file_attributes', 0) & 0x400:
                unsupported.append({'path': path.relative_to(root).as_posix(), 'reason': 'reparse-directory-not-traversed'})
                directories.remove(directory)
        for name in names:
            path = Path(folder)/name
            info = path.lstat()
            relative = path.relative_to(root)
            if path.is_symlink() or getattr(info, 'st_file_attributes', 0) & 0x400:
                unsupported.append({'path': relative.as_posix(), 'reason': 'reparse-file-not-read'})
                continue
            identity = [info.st_dev, info.st_ino] if info.st_ino else None
            allocated = getattr(info, 'st_blocks', None)
            allocated = allocated*512 if allocated is not None else None
            kind = category(relative)
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(1024*1024), b''):
                    digest.update(block)
            rows.append({'path': relative.as_posix(), 'class': kind, 'logical_bytes': info.st_size,
                         'sha256': digest.hexdigest(), 'physical_identity': identity,
                         'hardlink_count': info.st_nlink, 'allocated_bytes': allocated})
            summary = classes.setdefault(kind, {'files': 0, 'logical_bytes': 0})
            summary['files'] += 1
            summary['logical_bytes'] += info.st_size
            if identity is not None:
                physical.setdefault(tuple(identity), (info.st_size, allocated))
    known = all(row['physical_identity'] is not None for row in rows)
    return {'format': 'wave-recovery-storage-census-v1', 'root': str(root), 'read_only': True,
            'files': sorted(rows, key=lambda row: row['path']), 'classes': classes,
            'logical_bytes': sum(row['logical_bytes'] for row in rows),
            'unique_physical_identities': len(physical) if known else None,
            'unique_identity_logical_bytes': sum(row[0] for row in physical.values()) if known else None,
            'unique_allocated_bytes': sum(row[1] for row in physical.values())
                if known and all(row[1] is not None for row in physical.values()) else None,
            'unsupported': unsupported,
            'limits': ['File identity is not a claim about shared extents, compression or physical I/O.',
                       'Unknown allocation metrics remain null; hardlinks do not reduce logical quota.',
                       'All histories, failed attempts and staging are retained.'],
            'consumer_lifetimes': {
                'source-original-normalized-inputs': 'Every new callback, resume raw validation and retained reproduction.',
                'immutable-mathematical-and-group-payloads': 'Committed consumers, adoption and retained raw verification.',
                'captured-runtime-and-inputs': 'Original producer verification and historical reproduction.',
                'owned-task-result-profile-stream-cleanup-history': 'Producer authority and cleanup, including failed stages.',
                'journal-adoption-terminal': 'Head/predecessor/origin validation and immutable publication recovery.',
                'external-review-assessment': 'Independent review and retained assessment verification.',
                'pending-retention-history': 'Report-first/seal-last reconstruction and pending generation checks.',
                'staging-retained-not-authorized-for-deletion': 'Uncommitted/failed evidence remains history; no automatic release.'}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.root.resolve(strict=True), args.output.resolve()
    if output.is_relative_to(root):
        parser.error('--output must be outside the censused tree')
    result = census(root)
    with output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({key: result[key] for key in ('logical_bytes', 'unique_physical_identities',
                                                'unique_identity_logical_bytes', 'unique_allocated_bytes')}))


if __name__ == '__main__':
    main()
