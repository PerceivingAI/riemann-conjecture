"""Verify sealed raw evidence; this does not execute or establish mathematics."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat

EXCLUDED = {'manifest-v1.json','raw-verification-v1.json'}


def require(condition,message):
    if not condition:
        raise ValueError(message)


def safe(root,name):
    require(type(name) is str and name and '\\' not in name and ':' not in name,
            'noncanonical evidence path')
    rel = PurePosixPath(name)
    require(not rel.is_absolute() and str(rel) == name and
            all(part not in ('.','..') for part in rel.parts),'escaping evidence path')
    path = root
    for part in rel.parts:
        path = path/part
        require(not path.is_symlink() and not path.is_junction(),'linked evidence path')
    require(stat.S_ISREG(path.stat().st_mode),'nonregular evidence member')
    return path


def digest(path):
    value = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        while data := stream.read(1 << 20):
            value.update(data)
            size += len(data)
    return size,value.hexdigest()


def check_rows(root,rows):
    require(type(rows) is list,'invalid raw evidence inventory')
    names = []
    total = 0
    for row in rows:
        require(type(row) is dict and set(row) == {'path','size','sha256'},'invalid raw evidence row')
        require(type(row['size']) is int and row['size'] >= 0 and
                type(row['sha256']) is str and len(row['sha256']) == 64 and
                all(c in '0123456789abcdef' for c in row['sha256']),'invalid raw evidence identity')
        size,sha = digest(safe(root,row['path']))
        require((size,sha) == (row['size'],row['sha256']),'changed raw evidence: '+row['path'])
        names.append(row['path'])
        total += size
    require(names == sorted(set(names)),'unordered or repeated raw evidence member')
    return names,total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    bundle = args.bundle.resolve(strict=True)
    require(not args.output.exists(),'fresh raw-verification output required')
    require(args.output.resolve() == bundle/'raw-verification-v1.json',
            'raw-verification output must be the explicitly excluded verdict')
    manifest_path = safe(bundle,'manifest-v1.json')
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    require(set(manifest) == {'format','scope','excluded','members','external_bindings'},
            'unexpected raw manifest fields')
    require(manifest['format'] == 'nonproof-proposal-raw-manifest-v1' and
            manifest['scope'] == 'RAW_BINDINGS_ONLY' and
            manifest['excluded'] == sorted(EXCLUDED),'unexpected raw manifest contract')
    names,total = check_rows(bundle,manifest['members'])
    actual = sorted(path.relative_to(bundle).as_posix() for path in bundle.rglob('*')
                    if path.is_file() and path.relative_to(bundle).as_posix() not in EXCLUDED)
    require(names == actual,'incomplete raw bundle inventory')
    external,external_bytes = check_rows(Path(__file__).resolve().parents[2],manifest['external_bindings'])
    result = {'format':'nonproof-proposal-raw-verification-v1',
              'status':'PASS_RETAINED_NONPROOF_PROPOSAL_RAW_BINDINGS',
              'scope':'RAW_BINDINGS_ONLY','manifest_sha256':hashlib.sha256(manifest_raw).hexdigest(),
              'retained_members':len(names),'retained_bytes':total,
              'external_bindings':len(external),'external_bytes':external_bytes,
              'fresh_native_reconstruction':False,'mathematical_acceptance_repeated':False,
              'full_source_run':False,'matrix_positivity':False,'production_admission':False}
    with args.output.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(result,stream,indent=2,sort_keys=True)
        stream.write('\n')
    print(json.dumps(result,sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
