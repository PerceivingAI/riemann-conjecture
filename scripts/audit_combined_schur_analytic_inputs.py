"""Targeted independent mathematical controls for the existing positive research packet.

This is an audit, NOT a new experiment at another support/dimension. High-precision
mpmath integrations are secondary NONPROOF checks; exact rational interval
comparison against historical projected-tail evidence is rigorous conditional
on both previous Arb source enclosures.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json, time
from fractions import Fraction
from pathlib import Path
from flint import arb, ctx
from scripts.cert.constants import arb_to_rational_enclosure
from scripts.cert.legendre_schur import legendre_polynomials
from scripts.cert.multi_prime_legendre_schur import assemble_multi_prime_schur
from scripts.cert.prime_power_terms import _exact_polynomials, enumerate_active_prime_power_terms
from scripts.cert.mixed_gram_research import _mixed_by_shifts, logarithmic_cell_moments
from scripts.weil_projected_mixed_schur_check import read_historical_direction
import mpmath as mp

RECORD = Path("computations/2026-10-17T150153Z-combined-schur-bounded-test/data/matrix-N192.json.gz")
PROJECTED = Path("computations/2026-10-17T124000Z-sys2-projected-obstruction/data/projected-M224.json")
def enclosure(pair,bits):
 d=1<<bits
 return Fraction(pair[0],d),Fraction(pair[1],d)
def overlap(pair,bits,ref):
 low,high=enclosure(pair,bits)
 lo,hi=arb_to_rational_enclosure(ref)
 return max(low,lo)<=min(high,hi)

def audit():
 start=time.perf_counter()
 payload=RECORD.read_bytes()
 p=json.loads(gzip.decompress(payload))
 assert hashlib.sha256(payload).hexdigest()=="655d481d638f8b6fba0f95d01a4bab45079d905fbc6cb4f3e822571729d4d7c1"
 assert (p["support"],p["dimension"],p["precision_bits"],p["active_terms"])==([11,20],192,1024,[2,3])
 bits=p["dyadic_bits"]
 assert bits==352

 # Separate old low assembler, fresh arithmetic build and interval arithmetic.
 ref=assemble_multi_prime_schur(n=12,prec=384,residual_order=32,
                               support_num=11,support_den=20,require_positive_mu=False)
 assert [x.m for x in ref["active_terms"]]==[2,3]
 lows=((0,0),(1,1),(0,2),(2,4),(5,7),(10,10))
 for i,j in lows:
  assert overlap(p["low_A_triangular"][i][j-i],bits,ref["A"][i][j]),(i,j)
 print("INDEPENDENT_LOW_A_OVERLAP",len(lows),"PASS",flush=True)
 plo,phi=enclosure(p["mu_dyadic"],bits)
 assert plo>0
 adjusted_mu=ref["mu"] + arb(sum((Fraction(1,k) for k in range(13,193)),Fraction()).numerator)/sum((Fraction(1,k) for k in range(13,193)),Fraction()).denominator
 assert plo<=arb_to_rational_enclosure(adjusted_mu)[1] and phi>=arb_to_rational_enclosure(adjusted_mu)[0]
 print("INDEPENDENT_COMPLEMENT_OVERLAP_PASS",flush=True)

 # Independent direct mpmath numerical integrals over the two geometric
 # translated cells. This does NOT constitute another rigorous enclosure.
 mp.mp.dps=95
 t=mp.mpf(11)/20
 terms=enumerate_active_prime_power_terms(11,20,768)
 polys=legendre_polynomials(96)
 exact=_exact_polynomials([polys[0],polys[96]])
 with ctx.workprec(768):
  vp=_mixed_by_shifts(exact,[],terms,potential=True)
  bounds=arb_to_rational_enclosure(vp[0][1])
  reference=mp.mpf(0)
  for m in (2,3):
   tau=mp.log(m)/t
   cm=mp.log(m)/mp.sqrt(m)
   def val(x,shift):
    return -mp.log(1-x*x)*mp.legendre(96,x+shift)/2
   reference-=cm*(mp.quad(lambda x: val(x,tau),[-1,1-tau])
                   +mp.quad(lambda x: val(x,-tau),[-1+tau,1]))
  mid=(bounds[0]+bounds[1])/2
  observed=mp.mpf(mid.numerator)/mid.denominator
  diff=abs(observed-reference)
  print("HIGH_DEGREE_VP_0_96_ABS_DISCREPANCY",mp.nstr(diff,18),flush=True)
  assert diff<mp.mpf("1e-55")
  # Also independently integrate singular endpoint and interior split for
  # polynomial x^96; this checks x^n*log(1-x^2) cell antiderivatives.
  shift=arb(1)-terms[0].tau
  moment=logarithmic_cell_moments(arb(-1),shift,96)[96]
  lower,upper=arb_to_rational_enclosure(moment)
  q=1-mp.log(2)/t
  num=mp.quad(lambda x:x**96*(-mp.log(1-x*x))/2,[-1,q])
  midpoint=(lower+upper)/2
  approxim=mp.mpf(midpoint.numerator)/midpoint.denominator
  err=abs(num-approxim)
  print("HIGH_DEGREE_LOG_CELL_96_ABS_DISCREPANCY",mp.nstr(err,18),flush=True)
  assert err<mp.mpf("1e-55")

 # Fully exact rational independent comparison of current full-tail Gram
 # upper bound with *older and different* finite Legendre tail projected
 # lower bound for the historical vector u. No new large assembly.
 historical=json.loads(PROJECTED.read_text(encoding="utf8"))
 old=next(x for x in historical["results"] if x["N"]==192)
 u,_=read_historical_direction(192)
 nz=[(i,x) for i,x in enumerate(u) if x]
 norm=sum((Fraction(2,2*i+1)*x*x for i,x in nz),Fraction())
 lower_record=arb(old["projected_full_norm_sq_lower"])
 projected_lower=arb_to_rational_enclosure(lower_record)[0]
 g_upper=Fraction()
 for at,(i,ci) in enumerate(nz):
  for j,cj in nz[at:]:
   lo,hi=enclosure(p["truncated_gram_triangular"][i][j-i],bits)
   weight=ci*cj*(1 if i==j else 2)
   g_upper += weight*(hi if weight>=0 else lo)
 eta=Fraction(*p["eta"])
 delta_hi=enclosure(p["delta_dyadic"],bits)[1]
 full_upper=(1+eta)*g_upper + (1+1/eta)*delta_hi**2*norm
 assert full_upper>=projected_lower
 print("INDEPENDENT_HISTORICAL_PROJECTED_LOWER_LE_FULL_UPPER_PASS",
       "old_lower_approx",float(projected_lower),
       "new_upper_approx",float(full_upper),flush=True)
 print("AUDIT_SECONDS",round(time.perf_counter()-start,3),flush=True)
 return {"low_A_selected_overlaps":len(lows),
         "mu_overlaps_existing":True,
         "high_degree_vp_discrepancy_decimal":str(diff),
         "high_degree_log_cell_discrepancy_decimal":str(err),
         "historical_projected_lower":str(projected_lower),
         "full_mixed_gram_upper_direction":str(full_upper),
         "elapsed_seconds":round(time.perf_counter()-start,3),
         "numerical_quad_is_not_proof":True}
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--output",type=Path,required=True)
 args=ap.parse_args()
 data=audit()
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf8")
if __name__=="__main__":main()
