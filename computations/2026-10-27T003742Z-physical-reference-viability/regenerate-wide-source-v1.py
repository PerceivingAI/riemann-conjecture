"""Regenerate unaccepted wide raw matrices without replacing any past record."""
import argparse,hashlib,json,subprocess,sys,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--export-dir',type=Path);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    if args.export_dir and args.export_dir.exists():raise FileExistsError(args.export_dir)
    manifest=json.loads((HERE/'captured-source-v2.json').read_text());oldraw=(HERE/'data/whole-source-v3.json').read_bytes();old=json.loads(oldraw)
    bundle=HERE.relative_to(HERE.parents[1]);result={'format':'wide-unaccepted-raw-regeneration-v1','accepted_positive_source':False,'original_records_overwritten':False,'matrices':{}}
    with tempfile.TemporaryDirectory(prefix='rh_wide_source_') as td:
        root=Path(td)
        for member in manifest['files']:
            raw=(HERE/member['stored']).read_bytes()
            if sha(raw)!=member['sha256']:raise ValueError('captured input hash')
            dest=root/member['destination'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        for name in ('build-whole-source-v3.py','whole-gram-inputs-v1.json'):
            (root/bundle/name).write_bytes((HERE/name).read_bytes())
        argv=[sys.executable,'-B',str(bundle/'build-whole-source-v3.py'),'--output',str(bundle/'data/whole-source-v3.json')];start=time.perf_counter();proc=subprocess.run(argv,cwd=root,capture_output=True,text=True)
        result.update({'argv':argv,'exit_code':proc.returncode,'elapsed_seconds':time.perf_counter()-start,'stdout':proc.stdout,'stderr':proc.stderr})
        if proc.returncode:raise ValueError('raw regeneration failed '+proc.stderr[-2000:])
        if (root/bundle/'data/whole-source-v3.json').read_bytes()!=oldraw:raise ValueError('unaccepted source metadata replay mismatch')
        if args.export_dir:args.export_dir.mkdir(parents=True,exist_ok=False)
        for name,member in old['matrices'].items():
            raw=(root/bundle/member['path']).read_bytes()
            if sha(raw)!=member['sha256'] or len(raw)!=member['size']:raise ValueError('raw matrix mismatch '+name)
            result['matrices'][name]={'sha256':sha(raw),'size':len(raw),'byte_identical_to_recorded_hash':True}
            if args.export_dir and member['size']>2000000:
                with (args.export_dir/Path(member['path']).name).open('xb') as handle:handle.write(raw)
    result['status']='PASS_WIDE_RAW_REGENERATION';result['isolated_tree_removed']=not root.exists()
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps({'status':result['status'],'matrix_hashes_checked':len(result['matrices'])}),flush=True)
if __name__=='__main__':main()
