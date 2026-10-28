"""Neutral execution events. No mathematical helpers or producer state are shared."""
from __future__ import annotations
import functools
import json
import time

PREFIX = 'T081_EVENT '
_records = {}
_stack = []
_started = time.monotonic()


def emit(event, **fields):
    print(PREFIX + json.dumps({'event':event,'elapsed_seconds':time.monotonic()-_started,
                              **fields},sort_keys=True),flush=True)


def wrap(module, names):
    for name in names:
        if not hasattr(module,name):
            continue
        original=getattr(module,name)
        def decorate(function, phase):
            @functools.wraps(function)
            def timed(*args,**kwargs):
                wall,cpu=time.monotonic(),time.process_time()
                frame={'child_wall':0.0,'child_cpu':0.0}
                _stack.append(frame)
                emit('phase_started',phase=phase,depth=len(_stack))
                try:
                    return function(*args,**kwargs)
                finally:
                    elapsed,used=time.monotonic()-wall,time.process_time()-cpu
                    _stack.pop()
                    if _stack:
                        _stack[-1]['child_wall']+=elapsed;_stack[-1]['child_cpu']+=used
                    total=_records.setdefault(phase,{'calls':0,'inclusive_wall_seconds':0.0,
                        'exclusive_wall_seconds':0.0,'cpu_seconds':0.0})
                    total['calls']+=1;total['inclusive_wall_seconds']+=elapsed
                    total['exclusive_wall_seconds']+=max(0,elapsed-frame['child_wall'])
                    total['cpu_seconds']+=used
                    emit('phase_finished',phase=phase,depth=len(_stack)+1,
                         wall_seconds=elapsed,cpu_seconds=used)
            return timed
        setattr(module,name,decorate(original,name))


def report():
    return {'phases':_records,'timing_note':'inclusive includes nested calls; exclusive subtracts wrapped children; CPU is current process only'}
