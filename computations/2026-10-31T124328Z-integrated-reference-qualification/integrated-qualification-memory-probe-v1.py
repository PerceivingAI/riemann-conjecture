"""Inspect Windows limit rounding on an empty owned job; no process is launched."""
import argparse
import ctypes
import json
from pathlib import Path
import sys
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.whole_source.lifecycle_windows import WindowsLifecycle
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',required=True,type=Path)
args=parser.parse_args()
args.output.resolve().relative_to(ROOT)
rows=[]
def observe(self):
    limits=self._query(9,self._limits._ExtendedLimits())
    cpu=self._query(15,self._limits._CpuRate())
    flags=ctypes.c_ulong()
    if not self._kernel.GetHandleInformation(self._open_handle(),ctypes.byref(flags)):
        raise self._error('GetHandleInformation')
    rows.append({'requested_bytes':self.memory_bytes,'installed_process_bytes':int(limits.process_memory_limit),
        'installed_job_bytes':int(limits.job_memory_limit),'flags':int(limits.basic.flags),
        'cpu_flags':int(cpu.flags),'cpu_rate':int(cpu.rate),'handle_flags':flags.value})
    return rows[-1]
with patch.object(WindowsLifecycle,'_installed_limits',observe):
    for requested in (128*1024*1024,128*1024*1024+17):
        with WindowsLifecycle(requested):
            pass
args.output.parent.mkdir(parents=True,exist_ok=True)
with args.output.open('x',encoding='utf-8') as stream:
    json.dump({'scope':'EMPTY_JOB_DIAGNOSTIC_NOT_QUALIFICATION','rows':rows},stream,indent=2)
print(json.dumps(rows))
