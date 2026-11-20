"""Read exact retained source/head evidence without rerunning native mathematics."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def require(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)+'\n').encode('ascii')


def bound(root, ref):
    path = root/ref['path']
    require(path.resolve().is_relative_to(root.resolve()), 'artifact escapes retained root')
    raw = path.read_bytes()
    require(len(raw) == ref['size'] and hashlib.sha256(raw).hexdigest() == ref['sha256'],
            'changed retained bytes: '+ref['path'])
    return raw


def scientific(path):
    raw = path.read_bytes()
    value = json.loads(raw)
    require(value['format'] == 'whole-source-scientific-manifest-v1' and
            value['control'] is True and value['scope'] == 'CONTROL_ONLY_REDUCED_MODEL' and
            value['full_mathematical_source'] is False and value['matrix_positivity'] is False and
            value['production_admission'] is False, 'unexpected retained control scope')
    role, bits = value['role'], value['publication_bits']
    require((role,bits) in (('producer',256),('analytic',512)), 'incorrect publication role/grid')
    collection_id = hashlib.sha256(canonical(value['collection'])).hexdigest()
    entries = {}
    digest = hashlib.sha256()
    n = value['geometry']['N']
    for tile in value['tiles']:
        digest.update(canonical(tile))
        packet = json.loads(bound(path.parent, tile['artifact']))
        header = packet['header']
        require(header['collection_id'] == collection_id and header['task'] == tile['task'] and
                header['grid_bits'] == bits and header['role'] == role, 'changed consumed tile context')
        for m,k,lo,hi in packet['records']:
            key = (tile['family'],tile['parity'],m,k)
            require(key not in entries and type(m) is int and type(k) is int and m <= k and
                    m % 2 == k % 2 == tile['parity'] and 0 <= m <= k < n, 'duplicate/foreign final coordinate')
            lower,upper = int(lo,16),int(hi,16)
            require(lower <= upper, 'inverted final interval')
            entries[key] = (lower,upper)
    expected = {(family,p,m,k) for family in ('A_model','weighted_head','weighted_complete_tail')
                for p in (0,1) for m in range(p,n,2) for k in range(m,n,2)}
    require(set(entries) == expected, 'incomplete six-family domain')
    return raw,value,entries,digest.hexdigest()


def check_control(run, audit_name):
    source_path = run/'source/producer/source-manifest.json'
    independent_path = run/audit_name/'analytic/source-manifest.json'
    raw,source,produced,digest = scientific(source_path)
    _,independent,actual,_ = scientific(independent_path)
    require(source['geometry'] == independent['geometry'] and set(produced) == set(actual),
            'different source/analytical domains')
    for key,(lo,hi) in produced.items():
        alo,ahi = actual[key]
        require(lo << 256 <= alo <= ahi <= hi << 256, 'retained inclusive containment failed')
    receipt = json.loads((run/audit_name/'analytical-receipt.json').read_bytes())
    require(receipt['status'] == 'VERIFIED_ALL_DECLARED_SOURCE_ENTRIES' and
            receipt['entries_checked'] == len(produced) == 36 and
            receipt['source_manifest']['sha256'] == hashlib.sha256(raw).hexdigest() and
            receipt['source_manifest']['size'] == len(raw) and
            receipt['consumed_source_tiles_sha256'] == digest and
            receipt['full_mathematical_source'] is False and
            receipt['matrix_positivity'] is False and receipt['physical_row_width_accepted'] is False,
            'changed analytical receipt bindings/scope')
    state = json.loads((run/'source/source-state.json').read_bytes())
    require(bound(run/'source',state['manifest']) == raw, 'incorrect machine-readable source locator')
    return len(produced)


def cache_records(root, collection_id, ref, expected_task):
    lines = gzip.decompress(bound(root,ref)).splitlines()
    header = json.loads(lines[0])
    require(header['collection_id'] == collection_id and header['grid_bits'] == 512 and
            header['task'] == expected_task, 'changed full head cache context')
    for line in lines[1:]:
        m,n,axis,lo,hi = json.loads(line)
        require(axis == [0], 'incomplete cached head expression')
        yield m,n,int(lo,16),int(hi,16)


def check_owned(root, attempt, receipts):
    peaks = []
    for entry in receipts:
        folder = root/'attempts'/attempt/entry['stage']
        recorded = json.loads((folder/'receipt.json').read_bytes())
        require(recorded['exit_code'] == 0 and recorded['worker_cleanup_verified'] is True and
                entry['worker_cleanup_verified'] is True and
                recorded['peak_budgeted_memory_bytes'] == entry['peak_budgeted_memory_bytes'],
                'incomplete owned stage or changed observation')
        for channel, ref in recorded['logs'].items():
            require(hashlib.sha256((folder/(channel+'.txt')).read_bytes()).hexdigest() == ref['sha256'],
                    'changed retained native stream')
        peaks.append(recorded['peak_budgeted_memory_bytes'])
    return len(receipts), max(peaks, default=0)


def check_control_owned(run):
    count, peak = 0, 0
    for directory in (run/'source/producer', run/'audit/analytic', run/'audit-resume/analytic'):
        for path in directory.glob('run-*.json'):
            value = json.loads(path.read_bytes())
            require(value['status'] == 'COMPLETE_SOURCE_EXPRESSIONS', 'unfinished source expression run')
            n, p = check_owned(directory, path.stem[4:], value['owned_receipts'])
            count, peak = count+n, max(peak,p)
    return count, peak


def check_head(run):
    roles = {role:json.loads((run/(role+'-result.json')).read_bytes()) for role in ('producer','analytic')}
    collections = {role:hashlib.sha256(canonical(value['collection'])).hexdigest() for role,value in roles.items()}
    kernel = {role:{} for role in roles}
    goal = json.loads((run/'inputs/problem.json').read_bytes())['parameters']['numerical_goal']
    goal_num, goal_den = int(goal['numerator'],16), int(goal['denominator'],16)
    for role,value in roles.items():
        for encoded,ref in value['cache'].items():
            task = json.loads(bytes.fromhex(encoded))
            if task['quantity']['name'] != 'kernel_complete':
                continue
            p = task['quantity']['parity']
            for m,n,lo,hi in cache_records(run/role,collections[role],ref,task):
                key = p,m,n
                require(key not in kernel[role], 'repeated full kernel coordinate')
                kernel[role][key] = lo,hi
    expected = {(p,m,n) for p in (0,1) for m in range(826+p,1652,2) for n in range(m,1652,2)}
    require(set(kernel['producer']) == set(kernel['analytic']) == expected, 'incomplete two-parity full K domain')
    for key,(lo,hi) in kernel['producer'].items():
        # Reproduce the producer's outward256 publication comparison exactly.
        lower = (lo >> 256)-1
        upper = -((-hi) >> 256)+1
        alo,ahi = kernel['analytic'][key]
        require(lower << 256 <= alo <= ahi <= upper << 256, 'independent complete K containment failed')
        _,m,n = key
        require((upper-lower)*(2*max(m,n)+1)*goal_den < (4 << 256)*goal_num,
                'selected kernel physical entry width goal failed')
    pairs = [(0,0),(0,824),(824,824),(1,1),(1,825),(825,825)]
    source,actual = roles['producer']['selected'],roles['analytic']['selected']
    require([(r['m'],r['n']) for r in source] == [(r['m'],r['n']) for r in actual] == pairs,
            'incomplete full-head selected output cover')
    for x,y in zip(source,actual,strict=True):
        require(x['bits'] == 256 and y['bits'] == 512,'changed selected head grids')
        lo,hi,alo,ahi = int(x['lower'],16),int(x['upper'],16),int(y['lower'],16),int(y['upper'],16)
        require(lo << 256 <= alo <= ahi <= hi << 256, 'retained full-head containment failed')
        require((hi-lo)*(2*max(x['m'],x['n'])+1)*goal_den < (4 << 256)*goal_num,
                'selected head physical entry width goal failed')
    stages, peak = 0, 0
    for role,value in roles.items():
        count, observed = check_owned(run/role,value['attempt_id'],value['owned_receipts'])
        stages, peak = stages+count,max(peak,observed)
    original = Path(__file__).resolve().parents[2]/'computations/2026-10-27T140745Z-t081-complete-gram-attempt/data'
    raw = (original/'source-v1.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == 'f69fee0feb9c08833ad6a3091718c9a6a301e5b5ddbea96ee5f0f6c0553c8b6e',
            'changed original supplementary source')
    old = json.loads(raw)
    require(type(old['bits']) is int and old['bits'] == 256,'changed retained supplementary endpoint grid')
    comparisons = 0
    for parity in (0,1):
        packet = json.loads(gzip.decompress(bound(original,old['matrices']['weighted_head-'+str(parity)])))
        for entry in source:
            if entry['m'] % 2 != parity:
                continue
            i,j,d = entry['m']//2,entry['n']//2,413
            offset = i*d-i*(i-1)//2+j-i
            lo,hi = packet['upper_triangle'][offset]
            require(max(lo,int(entry['lower'],16)) <= min(hi,int(entry['upper'],16)),
                    'new and retained head enclosures disagree')
            comparisons += 1
    require(comparisons == 6, 'incomplete retained head comparison')
    return len(expected),len(pairs),stages,peak


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control-run',type=Path,required=True)
    parser.add_argument('--head-run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    require(not args.output.exists(),'fresh retained-check output required')
    checked = check_control(args.control_run,'audit')
    resumed = check_control(args.control_run,'audit-resume')
    kernels,heads,head_stages,head_peak = check_head(args.head_run)
    control_stages,control_peak = check_control_owned(args.control_run)
    require(head_stages == 14 and control_stages == 24, 'incomplete qualified owned-stage inventory')
    result = {'format':'retained-frequency-head-verification-v1','status':'PASS_RETAINED_FREQUENCY_HEAD_EVIDENCE',
              'control_entries_checked':checked,'resumed_control_entries_checked':resumed,
              'actual_kernel_entries_checked':kernels,'actual_head_entries_checked':heads,
              'supplementary_retained_head_comparisons':6,'selected_physical_entry_width_goal':True,
              'owned_stages_cleanup_verified':head_stages+control_stages,
              'maximum_observed_owned_peak_bytes':max(head_peak,control_peak),
              'fresh_native_reconstruction':False,'full_source_run':False,'matrix_positivity':False,
              'physical_row_width_accepted':False,'production_admission':False,
              'scope':'RETAINED_EXACT_BYTES_AND_CONTAINMENT_ONLY'}
    with args.output.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(result,stream,indent=2,sort_keys=True)
        stream.write('\n')
    print(json.dumps(result,sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
