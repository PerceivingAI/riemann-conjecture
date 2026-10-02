from pathlib import Path
import json,subprocess,time
ROOT=Path(__file__).resolve().parents[3]
COMMANDS=[['uv', 'run', '--locked', 'python', 'computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase11-candidate-cost-source.py', '--precision', '512', '--matrix-bits', '64', '--witness-bits', '32'], ['uv', 'run', '--locked', 'python', 'computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase11-candidate-cost-source.py', '--precision', '640', '--matrix-bits', '64', '--witness-bits', '32'], ['uv', 'run', '--locked', 'python', 'computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase11-candidate-cost-source.py', '--precision', '768', '--matrix-bits', '64', '--witness-bits', '32'], ['uv', 'run', '--locked', 'python', 'computations/2026-10-01T215617Z-multi-prime-assembly-performance/data/phase11-candidate-cost-source.py', '--precision', '512', '--matrix-bits', '104', '--witness-bits', '56']]
def main():
    report={"role":"Phase 11 uncontended component benchmarks, not qualification","status":"running","commands":[]}
    for argv in COMMANDS:
        print("START "+" ".join(argv),flush=True)
        begin=time.perf_counter()
        process=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=1800)
        report["commands"].append({"argv":argv,"exit_code":process.returncode,"wall_seconds":time.perf_counter()-begin,"stdout":process.stdout,"stderr":process.stderr})
        Path(__file__).with_name("phase11-candidate-commands.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        print(process.stdout+process.stderr,flush=True)
        if process.returncode:raise SystemExit(process.returncode)
    report["status"]="completed"
    Path(__file__).with_name("phase11-candidate-commands.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
