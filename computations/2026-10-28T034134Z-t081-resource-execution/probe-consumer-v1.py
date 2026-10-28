"""Timing-only reduced-dimension probe of the frozen independent consumer.

No candidate, enclosure acceptance, positivity or admission is produced. Full
6144-bit precision and support are preserved; dimensions are reduced solely to
choose an execution optimization before the complete unchanged-target run.
"""
from __future__ import annotations
import argparse
import cProfile
import hashlib
import importlib.util
import json
import time
from pathlib import Path
from flint import ctx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONSUMER = ROOT / 'computations/2026-10-27T140745Z-t081-complete-gram-attempt/verify-whole-source-v1.py'
POLICY = ROOT / 'computations/2026-10-28T024305Z-t081-execution-corrections/execution_resources_v1.py'
INSTRUMENT = ROOT / 'computations/2026-10-28T024305Z-t081-execution-corrections/instrument-t081-v2.py'


def module(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    consumer=module(CONSUMER,'independent_timing_probe')
    policy=module(POLICY,'probe_cpu_policy')
    counters=module(INSTRUMENT,'probe_process_counters')
    consumer.N=256;consumer.EXTENT=512;consumer.DIM=128
    ctx.prec=6144
    polynomials=[consumer.rodrigues(n) for n in range(consumer.EXTENT)]
    harmonic,_=consumer.harmonic_tables(consumer.EXTENT+2)
    results=[]
    for threads in dict.fromkeys((1,policy.detect_cpu_resources()['effective_cpu_budget'])):
        ctx.threads=threads
        profiler=cProfile.Profile()
        wall=time.perf_counter();cpu=time.process_time()
        profiler.enable()
        matrices=consumer.arithmetic_blocks(polynomials,0,harmonic)
        profiler.disable()
        elapsed=time.perf_counter()-wall;cpu=time.process_time()-cpu
        stats=[]
        for entry in profiler.getstats():
            if hasattr(entry.code,'co_filename') and entry.code.co_filename==str(CONSUMER):
                stats.append({'function':entry.code.co_name,'calls':entry.callcount,
                              'inclusive_seconds':entry.totaltime,'exclusive_seconds':entry.inlinetime})
        results.append({'threads':threads,'wall_seconds':elapsed,'cpu_seconds':cpu,
                        'cpu_over_wall':cpu/elapsed,'os_memory':counters._process_memory(),
                        'stages':sorted(stats,key=lambda x:-x['inclusive_seconds']),
                        'sample_endpoints':[[str(x.lower().fmpq()),str(x.upper().fmpq())]
                                            for mat in matrices for x in (mat[0,0],mat[127,127])]})
        print(json.dumps({'threads':threads,'wall_seconds':elapsed,'cpu_over_wall':cpu/elapsed}),flush=True)
    ctx.threads=1
    output={'format':'t081-independent-consumer-timing-probe-v1','status':'TIMING_ONLY_NOT_A_PROOF',
            'consumer_sha256':hashlib.sha256(CONSUMER.read_bytes()).hexdigest(),
            'precision':6144,'probe_N':256,'full_target_N':826,'results':results,
            'production_admission':False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8',newline='\n') as handle:
        handle.write(json.dumps(output,indent=2,sort_keys=True)+'\n')
    return 0
if __name__=='__main__':raise SystemExit(main())
