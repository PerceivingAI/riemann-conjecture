"""Replay the immutable captured assessment in a fresh tree; never recapture or overwrite."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    source=json.loads((HERE/'data/whole-source-v4.json').read_text())
    bundle=HERE.relative_to(ROOT).as_posix()
    manifest_path=HERE/'captured-source-v2.json'
    manifest=json.loads(manifest_path.read_text())
    files={item['destination']:item['stored'] for item in manifest['files']}
    if len(files)!=len(manifest['files']):raise ValueError('duplicate captured destination')
    result={'format':'complete-fixed-assessment-isolated-replay-v3','captured_manifest_sha256':sha(manifest_path.read_bytes()),'captured_files':len(files),'driver_sha256':sha(Path(__file__).read_bytes()),'steps':[],'checks':{},'original_tree_execution':False}
    with tempfile.TemporaryDirectory(prefix='rh_complete_gram_') as td:
        isolate=Path(td)
        for item in manifest['files']:
            raw=(HERE/item['stored']).read_bytes()
            if sha(raw)!=item['sha256']:raise ValueError('captured input changed')
            dest=isolate/item['destination'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        relative=Path(bundle)
        def run(name,argv):
            start=time.perf_counter();proc=subprocess.run([sys.executable,'-B',str(relative/argv[0]),*argv[1:]],cwd=isolate,text=True,capture_output=True)
            result['steps'].append({'name':name,'argv':argv,'exit_code':proc.returncode,'elapsed_seconds':time.perf_counter()-start,'stdout':proc.stdout,'stderr':proc.stderr})
            if proc.returncode:raise ValueError('isolated step failed '+name+' '+proc.stderr[-2000:])
        def data(x):return (relative/'data'/x).as_posix()
        run('directional_source',['assess-physical-v2.py',data('proposal-v2.json'),'--output',data('physical-source-v2.json')])
        run('directional_audit',['verify-physical-v1.py',data('physical-source-v2.json'),'--output',data('independent-audit-v1.json')])
        run('complete_source',['build-whole-source-v4.py','--output',data('whole-source-v4.json')])
        run('complete_audit',['verify-whole-v1.py','--source',data('whole-source-v4.json'),'--output',data('whole-independent-audit-v1.json')])
        run('complete_exact_proof',['verify-whole-proof-v1.py','--source',data('whole-source-v4.json'),'--proposal',data('whole-proposal-v2.json'),'--output',data('whole-exact-proof-v1.json')])
        for name in ('physical-source-v2.json','independent-audit-v1.json','whole-source-v4.json','whole-exact-proof-v1.json'):
            current=(HERE/'data'/name).read_bytes();replay=(isolate/relative/'data'/name).read_bytes()
            if current!=replay:raise ValueError('scientific byte replay mismatch '+name)
            result['checks'][name]={'byte_identical':True,'sha256':sha(current)}
        current=json.loads((HERE/'data/whole-independent-audit-v1.json').read_text());replay=json.loads((isolate/relative/'data/whole-independent-audit-v1.json').read_text())
        current.pop('source');replay.pop('source')
        if current!=replay:raise ValueError('whole audit semantic replay mismatch')
        result['checks']['whole-independent-audit-v1.json']={'identical_except_absolute_source_path':True,'absolute_source_path_intentionally_not_compared':True}
        for name,descriptor in source['matrices'].items():
            raw=(HERE/descriptor['path']).read_bytes();replayed=(isolate/relative/descriptor['path']).read_bytes()
            if raw!=replayed:raise ValueError('complete matrix replay mismatch '+name)
            result['checks'][name]={'byte_identical':True,'sha256':sha(raw)}
    result['isolated_tree_removed']=not isolate.exists();result['status']='PASS_CAPTURED_ISOLATED_REPLAY'
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps({'status':result['status'],'captured_files':len(files),'checks':len(result['checks'])}),flush=True)
if __name__=='__main__':main()
