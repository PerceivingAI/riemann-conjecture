"""Compare real retained inventory streaming on small disposable metadata trees."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time
import tracemalloc
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--code-root',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--counts',type=int,nargs='+',default=[8,64,4097])
    args = parser.parse_args()
    root, output = args.code_root.resolve(), args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(root))
    from scripts.whole_source import retention as r
    results = []
    for count in args.counts:
        assert 1 <= count <= 8193
        directory = output/str(count)
        members = directory/'members'
        members.mkdir(parents=True)
        expected = hashlib.sha256()
        for index in range(count):
            raw = f'metadata-control:{index}\n'.encode()
            name = f'{index:06d}.dat'
            (members/name).write_bytes(raw)
            expected.update(name.encode()+b'\0'+raw)
        hashes = 0
        original_bytes_hashed = 0
        first_row_hashes = None
        verified_in_pass = 0
        decoded_in_pass = 0
        max_unconsumed_shard_rows = 0
        shard_decode_sizes = []
        verification_passes = 0
        active = False
        original_hash, original_json = r._hash_file, r._json
        original_verify, original_encode = r._verify_inventory_document, r.canonical_bytes
        def hashed(path):
            nonlocal hashes, original_bytes_hashed, verified_in_pass
            result = original_hash(path)
            if Path(path).parent == members:
                hashes += 1
                original_bytes_hashed += result['size']
                if active: verified_in_pass += 1
            return result
        def encoded(value):
            nonlocal first_row_hashes
            if first_row_hashes is None and type(value) is dict and set(value)=={'path','size','sha256'}:
                first_row_hashes = hashes
            return original_encode(value)
        def decoded(raw):
            nonlocal decoded_in_pass, max_unconsumed_shard_rows
            value = original_json(raw)
            if active and type(value) is dict and set(value)=={'files'}:
                size = len(value['files'])
                shard_decode_sizes.append(size)
                decoded_in_pass += size
                max_unconsumed_shard_rows = max(max_unconsumed_shard_rows,decoded_in_pass-verified_in_pass)
            return value
        def verified(*values,**kwargs):
            nonlocal active, verification_passes, verified_in_pass, decoded_in_pass
            verification_passes += 1
            verified_in_pass = decoded_in_pass = 0
            active = True
            try:
                return original_verify(*values,**kwargs)
            finally:
                active = False
        tracemalloc.start()
        started = time.perf_counter()
        with patch.object(r,'_hash_file',hashed),patch.object(r,'_json',decoded),\
             patch.object(r,'canonical_bytes',encoded),patch.object(r,'_verify_inventory_document',verified):
            result = r._seal(directory)
        elapsed = time.perf_counter()-started
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        assert result['status']=='PASS_RETAINED_INVENTORY' and result['members']==count
        assert hashes == 3*count and verification_passes==2
        before = {p.relative_to(directory).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in directory.rglob('*') if p.is_file()}
        assert r._seal(directory)==result
        assert before == {p.relative_to(directory).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in directory.rglob('*') if p.is_file()}
        results.append({'members':count,'member_payload_digest':expected.hexdigest(),
            'original_member_hash_calls':hashes,'original_logical_bytes_hashed':original_bytes_hashed,
            'original_member_hash_passes':3,'candidate_and_postpublication_checks':verification_passes,
            'member_hashes_before_first_snapshot_row_encoding':first_row_hashes,
            'max_decoded_shard_rows_ahead_of_member_verification':max_unconsumed_shard_rows,
            'decoded_shard_row_counts':shard_decode_sizes,'python_traced_current_bytes':current,
            'python_traced_peak_bytes':peak,'wall_seconds':elapsed,'already_sealed_tree_unchanged':True})
    report = {'status':'PASS_CONTROL_ONLY_INVENTORY_STREAMING','code_root':str(root),'results':results,
        'retention_program_sha256':hashlib.sha256((root/'scripts/whole_source/retention.py').read_bytes()).hexdigest(),
        'python':sys.version,'memory_scope':'Python-traced complete seal; excludes interpreter/native/RSS and fixture creation.',
        'io_scope':'Logical original-member bytes and metadata-consumer progress, not physical device traffic.',
        'scope':'DISPOSABLE_METADATA_ONLY_NO_SCIENTIFIC_REVIEW_OR_ACCEPTANCE','production_admission':False}
    (output/'result.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'cases':[{
        key:row[key] for key in ('members','member_hashes_before_first_snapshot_row_encoding',
            'max_decoded_shard_rows_ahead_of_member_verification','python_traced_peak_bytes')}
        for row in results]},sort_keys=True))


if __name__=='__main__':
    main()
