from pathlib import Path
import argparse,datetime,json,subprocess,time,sys
p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('argv',nargs=argparse.REMAINDER);a=p.parse_args();argv=a.argv[1:] if a.argv and a.argv[0]=='--' else a.argv
if a.receipt.exists():raise SystemExit('fresh receipt required')
start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic();r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');data={'started':start,'argv':argv,'exit_code':r.returncode,'elapsed_seconds':time.monotonic()-t,'stdout':r.stdout,'stderr':r.stderr};a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8');print(json.dumps(data,indent=2));raise SystemExit(r.returncode)
