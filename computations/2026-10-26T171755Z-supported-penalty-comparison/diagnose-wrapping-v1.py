"""Diagnose rectangular interval wrapping in an auxiliary direct Fourier control."""
import json,sys
from flint import arb,acb,ctx
ctx.prec=192
K=62582;nt=65536;t=arb.pi()*K/12;step=arb(3)/(2*nt)
ratio=acb(0,-t*step).exp();phase=acb(1);rows=[]
for n in range(1,nt+1):
    phase*=ratio
    if n in (1,128,1024,4096,16384,65536):
        direct=acb(0,-t*step*n).exp()
        rows.append({'iterations':n,'recurrence_real_radius':str(phase.real.rad()),'direct_real_radius':str(direct.real.rad()),'recurrence_contains_direct':phase.contains(direct),'direct_absolute_upper':str(abs(direct).upper())})
print(json.dumps({'precision_bits':192,'phase_step':'pi*62582/(12)*3/(2*65536)','rows':rows},indent=2))
