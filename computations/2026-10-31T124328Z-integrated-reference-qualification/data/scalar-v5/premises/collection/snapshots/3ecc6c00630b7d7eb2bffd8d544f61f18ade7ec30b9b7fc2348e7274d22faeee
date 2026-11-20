"""Execute one numerical stage only after the supervisor installs its budget."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--program',type=Path,required=True)
    parser.add_argument('--program-sha256',required=True)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--config-sha256',required=True)
    parser.add_argument('--profile',type=Path,required=True)
    parser.add_argument('--kind',choices=('source','audit','exact','fixture'),required=True)
    parser.add_argument('arguments',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    # The parent attaches the owned job before releasing this GO gate.
    print('T081_READY '+json.dumps({'pid':os.getpid(),'config_sha256':args.config_sha256}),flush=True)
    if sys.stdin.readline().strip()!='GO':
        raise RuntimeError('supervisor did not authorize the budgeted stage')
    raw=args.config.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=args.config_sha256:
        raise ValueError('execution configuration changed')
    config=json.loads(raw)
    if hashlib.sha256(args.program.read_bytes()).hexdigest()!=args.program_sha256:
        raise ValueError('numerical program changed')
    sys.path.insert(0,str(args.program.parent))
    from resource_limits_v1 import apply_posix_memory_limit
    containment={'mechanism':'owned Windows job installed before GO'}
    if os.name=='posix':
        containment=apply_posix_memory_limit(config['memory_budget_bytes'])
        if hasattr(os,'sched_setaffinity'):
            available=sorted(os.sched_getaffinity(0))
            os.sched_setaffinity(0,set(available[:config['cpu_budget']]))
    from flint import ctx
    import execution_events_v1 as events
    spec=importlib.util.spec_from_file_location('t081_owned_stage',args.program)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    ctx.threads=config['native_threads']
    stages={'source':('residual_matrices','combined_square','kernel_step','source'),
            'audit':('frozen_inputs','replay_declaration','residual_kernel','validate_model_allowance',
                'validate_weights','residual_outputs','residual_blocks','arithmetic_blocks',
                'complete_arithmetic_squared','frequency_kernels','reconstruct','check_matrix'),
            'exact':(), 'fixture':()}
    events.wrap(module,stages[args.kind])
    rest=args.arguments[1:] if args.arguments and args.arguments[0]=='--' else args.arguments
    sys.argv=[str(args.program),*rest]
    wall,cpu=time.monotonic(),time.process_time()
    code,error=0,None
    events.emit('program_started',kind=args.kind,threads=ctx.threads)
    try:
        code=int(module.main() or 0)
    except BaseException as exception:
        code=130 if isinstance(exception,KeyboardInterrupt) else 75 if isinstance(exception,MemoryError) else 1
        error=f'{type(exception).__name__}: {exception}'
        print(error,file=sys.stderr,flush=True)
    payload={'format':'t081-budgeted-stage-profile-v1','kind':args.kind,'exit_code':code,
        'error':error,'program_sha256':args.program_sha256,
        'wall_seconds':time.monotonic()-wall,'cpu_seconds':time.process_time()-cpu,
        'native_threads':ctx.threads,'precision':ctx.prec,'containment':containment,
        **events.report()}
    if os.name=='nt':
        from resource_limits_v1 import windows_resource_snapshot
        payload['process_memory']=windows_resource_snapshot()['process']
    args.profile.parent.mkdir(parents=True,exist_ok=True)
    with args.profile.open('x',encoding='utf-8',newline='\n') as handle:
        handle.write(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    events.emit('program_finished',kind=args.kind,exit_code=code,wall_seconds=payload['wall_seconds'])
    return code


if __name__=='__main__':raise SystemExit(main())
