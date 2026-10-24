# Reviewed source-tail envelope and a fixed-data jump obstruction

- **Finding ID:** `F-20261023-003`
- **Created:** `2026-10-23T17:03:43Z`
- **Last updated:** `2026-10-23T17:10:27Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED` — separately reviewed paper-level implications and exact retained-data predicates under the inherited source premises; not a positivity theorem, new source acceptance or Lean proof.
- **Claims:** reviewed C-0075; new C-0076.
- **Source baseline:** `acc63ac6d41138280236850c3fbc586e20998cc4` plus the preserved earlier [qualification](2026-10-23T131836Z-source-tail-concentration-qualification.md).

## Statement

Fix the original odd rational trial at T=3/5, N=192, residual order K=32, and retained prefix ending before 211. Keep the same mu, omitted-mass lower R_- and positive headroom h=a_up-P_- from C-0074. For C-0075's envelope, write

\[
E_L=\left(\frac{\sqrt2 A_z}{\eta_L L}
 +D(q)\sqrt{\frac{\pi}{2(L-2)}}+\delta\|u\|\right)^2,
\quad K_L=w_{L-1}\max(0,R_--E_L),\quad B_L=h-K_L.
\]

Here B_L is a **reported upper** on the exact diagonal-reference direction s0, not the actual direction. For every integer L>=224, the retained data and unavoidable arithmetic jumps imply

\[
B_L\ge\varepsilon:=h-w_{259}R_->0.
\tag{1}
\]

Thus this envelope/concentration family, with these fixed retained inputs, cannot certify a negative reference direction. The obstruction holds even when D(q) is known exactly, and therefore for every valid substituted upper on D(q). Computing a tighter upper for that variation cannot remove this obstruction within the same envelope. This does not exclude sharper inequalities, changed inputs, positivity of the actual reference, negativity of that reference, or either Weil sign.

## Independent mathematical review of C-0075

A separate read-only review reconstructed equations (1)-(11) of the earlier qualification and found them correct under their stated local source premises. The essential checks were:

1. Subtracting the two Legendre Sturm-Liouville equations gives the log-product identity with numerator -2. Reflection and V=-log(1-x^2)/2 yield (1+(-1)^(n+j))/(n(n+1)-j(j+1)). Ordinary-to-orthonormal scaling and the telescoping series give exactly sqrt(2)A_z/(eta_L L).
2. Laplace's integral representation, followed by a Gaussian integral, gives |P_n(x)|<=sqrt(pi/(2n))/sqrt(1-x^2). No sharp Bernstein estimate is assumed.
3. Distributional integration by parts includes the derivative inside cells and every interior jump. The antiderivative vanishes at both endpoints. The resulting normalized coefficient square is bounded by pi D(q)^2/((2k+1)(k-1)); summing the full infinite tail gives pi D(q)^2/(2(L-2)).
4. The explicit variation upper (10) has the correct geometry and odd-endpoint factors. It is an upper, not a lower, on actual D(q). Its first-window disjoint-support and exact-oddness assumptions matter.
5. For odd kernel powers at most 31 and trial degree 191, split integration has degree at most 223. Even powers at most 32 produce degree at most 32. Consequently Q_L R_32 u=0 for L>=224, but the full omitted residual still contributes the collective delta||u|| allowance.
6. Parseval, projection contractivity, the triangle inequality and decreasing positive w_k give C-0075's full-tail bound and the correct w_(L-1) concentration factor. The nonzero-witness construction correctly requires R_->0 and the original degree setting.

No additional global boundedness, H^1, operator-composition or equal-domain assumption is needed. The original source/domain and 2T<pi premises remain imported. This review establishes mathematical validity, not the sharpness of the bound or independent analytical reconstruction of original A/G.

The earlier finding remains byte-for-byte as its contemporaneous PROVISIONAL record. This successor records the later review; the maintained claim ledger now distinguishes the reviewed argument from its earlier state.

## Why actual arithmetic jumps force a large envelope

Let q=mathcal P_T u be the combined signed arithmetic image. For each m=2,3 its contribution is

\[
q_m(x)=-c_m\bigl[\mathbf1_{x<1-\tau_m}u(x+\tau_m)
 +\mathbf1_{x>\tau_m-1}u(x-\tau_m)\bigr].
\]

The accepted rational enclosures certify 1<tau_2<tau_3<2. The four breakpoints are distinct and interior. At each breakpoint the other prime contribution is locally continuous, so combining the signed terms cannot cancel the jump there. Exact oddness gives u(-1)=-u(1). Both jumps of q_m have signed value c_m u(1) and magnitude c_m U_e, where U_e=|u(1)|=|sum z_j|.

Dropping the nonnegative derivative contribution in C-0075's definition of D(q) gives the genuine **lower** bound

\[
D(q)\ge 2U_e\sum_{m=2,3}
 \frac{c_m}{\sqrt{\tau_m(2-\tau_m)}}>2U_e,
\tag{2}
\]

because 0<tau_m(2-tau_m)<1, c_m>0 and the retained coefficient-sum lower is greater than one. This is not obtained by reversing the earlier coarse upper on D(q).

For 224<=L<=259, all terms inside E_L are nonnegative and pi>3, so

\[
E_L\ge\frac{\pi D(q)^2}{2(L-2)}
 >\frac{12U_e^2}{2(L-2)}
 \ge\frac{12U_e^2}{514}>R_-.
\tag{3}
\]

The final inequality is an exact rational retained-data predicate. It forces K_L=0 in this entire range, even if the potential term and residual allowance were removed optimistically from E_L. A large lower bound on this **upper envelope** is not a large lower bound on actual tail energy.

For all L>=260, decreasing harmonic weights give

\[
K_L\le w_{L-1}R_-\le w_{259}R_-<h.
\tag{4}
\]

Equations (3)-(4) cover every permitted integer L, without a scan or selecting/evaluating a new source prefix. They prove (1). The proof index 260 is a fixed analytical split, not a new source cutoff experiment.

## Exact retained-data assessment

All comparisons were exact rational predicates on SHA-pinned existing packets. The following decimals are displays only.

| Quantity | Display | Exact role |
| --- | ---: | --- |
| A_z | 62.864877700805664 | Existing coefficient absolute sum; initial potential-only criterion |
| U_1 | 827208.1111688614 | Existing derivative coefficient sum; coarse-envelope comparison only |
| U_e | 62.59602928161621 | Exactly `32818347/524288`; actual jump magnitudes |
| R_- | 0.7987791726070741 | Retained omitted-mass lower, not actual total tail mass |
| h | 1.6623334744459064 | Retained positive headroom, not actual reference direction |
| Potential-only early-envelope floor | 0.5680962629864924 | Less than R_-: this initial sufficient exclusion predicate FAILED |
| Actual-jump early-envelope floor | 91.47695443949308 | Exactly `3231131699437227/35321811042304`, strictly greater than R_- |
| w_259 R_- | 1.6518034762273857 | Strictly below h, uniformly bounds K_L for L>=260 |
| epsilon | 0.01052999821852064 | Strict positive floor on every reported B_L |

The first declared check used the same fixed split 260 to test two possible early-range sufficient predicates. The potential-only predicate failed, while the explicit coarse-variation substitution passed. The latter alone would exclude only that substituted coarse envelope, not the exact-D(q) family. This distinction was preserved rather than treating an upper on D(q) as a lower.

The second predeclared check used the actual-jump lower (2), exact odd endpoint trace, retained tau ordering and the same fixed split. It passed (3)-(4), strengthening the conclusion to the original exact-D(q) family. Neither check computed D(q), E_L at a selected target index, new source moments, another trial, a matrix, a precision ladder or an actual reference sign.

## Independent review of the obstruction

A second read-only mathematical review checked monotonicity and the fixed-split algebra, and separately checked the actual-jump strengthening. It confirmed the four distinct breakpoints, the signed jump values, the lower-bound direction on D(q), the factor 12/514, the boundary weight w_259 and the positive uniform floor. It explicitly distinguished the failed potential-only predicate, the narrower coarse fallback and the stronger actual-jump criterion. Reviewers performed no numerical executions; the exact retained-data predicates were executed by the authoring process below. This is argument review plus exact bookkeeping, not independent source-enclosure reconstruction.

## Reproducible fixed small checks

Inputs, unchanged:

- Original SYS-6.4 packet: `computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json`, SHA-256 `44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b`.
- Accepted source packet: `computations/2026-10-22T185054Z-directional-source-validation/data/source-validation-1024.json`, SHA-256 `9b9a1a0a0b420df0147f07c6fa1f5d9ee9005fb68dc8213cd8880d98556dd843`.
- Retained scalar audit: `computations/2026-10-23T105408Z-directional-loss-review/data/loss-audit.json`, SHA-256 `0a2458b5ead5245a439647b2a127ef267e7c8c98f11b9d4cfdb63b2bd49bcc18`.

Pass each exact block below to the locked project interpreter with `python -c` from the repository root; `uv run --locked python -c` is the environment-managed equivalent. Both use only the standard library and retained inputs. The first reports conditional predicates; its false potential-only predicate is an observed limitation, not a process failure. The second asserts the actual-jump certificate. Full exact rational outputs are emitted as JSON.

### Initial fixed-split and coarse-substitution check

```python
import hashlib,json,time
from pathlib import Path
from fractions import Fraction as Q
start=time.perf_counter()
paths={
 'original':('computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json','44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b'),
 'source':('computations/2026-10-22T185054Z-directional-source-validation/data/source-validation-1024.json','9b9a1a0a0b420df0147f07c6fa1f5d9ee9005fb68dc8213cd8880d98556dd843'),
 'audit':('computations/2026-10-23T105408Z-directional-loss-review/data/loss-audit.json','0a2458b5ead5245a439647b2a127ef267e7c8c98f11b9d4cfdb63b2bd49bcc18')}
p={}
for key,(name,digest) in paths.items():
 raw=Path(name).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
 p[key]=json.loads(raw)
o,s,a=p['original'],p['source'],p['audit']['exact']
assert (o['support'],o['dimension'],o['K'],o['active_terms'])==('3/5',192,32,[2,3])
z=list(map(Q,o['trial_rational_vector']))
assert len(z)==192 and z[-1]!=0 and all(not z[j] for j in range(0,192,2))
for packet in (o,s):
 for name,digest in packet['source_sha256'].items():
  assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest
A=sum(map(abs,z),Q());U1=sum((abs(c)*Q(j*(j+1),2) for j,c in enumerate(z)),Q());Ue=abs(sum(z,Q()))
mu=Q(o['mu_lower_exact']);R=Q(a['omitted_mass_lower']);h=Q(a['prefix_only_reference_upper'])
assert mu>0 and R>0 and h>0 and s['residual_image_degree']==223
H=lambda n:sum((Q(1,j) for j in range(1,n+1)),Q())
S=260;k=S-1;eta=1-Q(191*192,k*(k+1))
Vfloor=2*A*A/(eta*eta*k*k)
far=R/(mu+H(k)-H(192))
Sc=sum((Q(s['arithmetic_constants_reference'][str(m)]['coefficient'][0]) for m in (2,3)),Q())
assert Sc>1
coarse_floor=Q(27)*U1*U1/(2*(k-2))
exact={name:str(v) for name,v in {'A_z':A,'U1':U1,'Ue':Ue,'R_minus':R,'headroom':h,'mu':mu,'eta_259':eta,'potential_floor_near':Vfloor,'far_ceiling':far,'headroom_minus_far_ceiling':h-far,'coarse_variation_floor_near':coarse_floor,'arithmetic_coefficient_sum_lower':Sc}.items()}
checks={'near_potential_floor_ge_R':Vfloor>=R,'far_ceiling_strictly_below_headroom':far<h,'near_coarse_variation_floor_ge_R':coarse_floor>=R}
print(json.dumps({'format':'source-tail-fixed-split-assessment-v1','split':S,'near_interval':[224,259],'exact':exact,'display':{n:float(Q(v)) for n,v in exact.items()},'predicates':checks,'optimistic_envelope_cannot_resolve':checks['near_potential_floor_ge_R'] and checks['far_ceiling_strictly_below_headroom'],'coarse_variation_envelope_cannot_resolve':checks['near_coarse_variation_floor_ge_R'] and checks['far_ceiling_strictly_below_headroom'],'new_source_moments':False,'source_reassembly':False,'internal_seconds':time.perf_counter()-start},indent=2))
```

### Actual-jump strengthening at the same fixed split

```python
import hashlib,json,time
from pathlib import Path
from fractions import Fraction as Q
start=time.perf_counter()
paths=[
('computations/2026-10-18T090311Z-sys6-selective-support/data/T-3-5-N192-probe.json','44aced61e482fb7876070bc25245e0df512f4af5cbee3f36d9c7bb23b606f15b'),
('computations/2026-10-22T185054Z-directional-source-validation/data/source-validation-1024.json','9b9a1a0a0b420df0147f07c6fa1f5d9ee9005fb68dc8213cd8880d98556dd843'),
('computations/2026-10-23T105408Z-directional-loss-review/data/loss-audit.json','0a2458b5ead5245a439647b2a127ef267e7c8c98f11b9d4cfdb63b2bd49bcc18')]
p=[]
for name,digest in paths:
 raw=Path(name).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest;p.append(json.loads(raw))
o,s,a=p[0],p[1],p[2]['exact']
z=list(map(Q,o['trial_rational_vector']))
assert len(z)==192 and all(not z[j] for j in range(0,192,2))
Ue=abs(sum(z,Q()));R=Q(a['omitted_mass_lower']);h=Q(a['prefix_only_reference_upper']);mu=Q(o['mu_lower_exact'])
assert Ue>0 and R>0 and h>0 and mu>0
c=s['arithmetic_constants_reference']
t2=tuple(map(Q,c['2']['tau']));t3=tuple(map(Q,c['3']['tau']))
assert Q(1)<t2[0]<=t2[1]<t3[0]<=t3[1]<Q(2)
Sc=sum((Q(c[str(m)]['coefficient'][0]) for m in (2,3)),Q());assert Sc>1
S=260
# pi>3 and actual weighted jump variation D(q)>2 Ue.
near_floor=12*Ue*Ue/Q(2*(S-3))
H=lambda n:sum((Q(1,j) for j in range(1,n+1)),Q())
far_ceiling=R/(mu+H(S-1)-H(192));gap=h-far_ceiling
assert near_floor>R and gap>0
exact={n:str(v) for n,v in {'Ue':Ue,'R_minus':R,'headroom':h,'coefficient_sum_lower':Sc,'jump_variation_lower_relaxed':2*Ue,'envelope_floor_near_relaxed':near_floor,'far_ceiling':far_ceiling,'uniform_reported_upper_floor':gap}.items()}
print(json.dumps({'format':'source-tail-jump-obstruction-v1','split':S,'near_interval':[224,259],'exact':exact,'display':{n:float(Q(v)) for n,v in exact.items()},'strict_tau_order':True,'strict_near_floor_above_retained_mass_lower':True,'strict_uniform_reported_upper_floor':True,'source_moments_evaluated':False,'actual_reference_sign':'UNDETERMINED','internal_seconds':time.perf_counter()-start},indent=2))
```

### Observed execution and cost

Both blocks executed once as separate direct Python children in the existing locked environment, CPython 3.14.0. Both returned exit 0, empty stderr, confirmed owned-process exit, no timeout or retry, and no descendants. Their exact executed text is retained above.

- Initial check, 2026-10-23T17:06:14Z: internal 0.06277449999470264 seconds; whole-process/charged 0.2976322000613436 seconds.
- Actual-jump check, 2026-10-23T17:08:02Z: internal 0.006207200000062585 seconds; whole-process/charged 0.12381280004046857 seconds.
- New charged execution: 0.4214450001018122 seconds. Including the earlier qualification control, cumulative analytical-check charge is **2.181619500159286/180 seconds**. Each check was capped at 60 seconds. Argument review and file/identity checks are not substantial source evaluations.

No target source evaluation, source implementation, permanent test, test suite, new evaluator, Rust theorem replay or Lean build occurred. The first block's failed predicate is retained; it was not retried with another split. The second tests an additional source-structural consequence of the same estimate at the same split, not another method or parameter chase.

## Dependencies, circularity and limits

Dependencies: C-0063 through C-0065 for the source/operator setup; C-0072 for the fixed harmonic reference; C-0074 for the retained h and R_-; C-0075 for the reviewed envelope/concentration formula. Source code inspected includes `scripts/cert/prime_power_terms.py:422-447` for signed combined cells, and the source/domain and residual arguments cited in the earlier qualification. Existing Suzuki source R-0028 and Arb/source premises remain unchanged; no external result or code import is added.

The obstruction concerns the same retained h,R_-,mu and the same envelope on the same trial. It does not exclude new inequalities or better analytical information. Equation (1) bounds reported uppers, not actual J from above or actual s0 from below. A positive reported upper proves no actual positivity. The exact diagonal-reference, true Schur and Weil signs remain unresolved. This result assumes no RH-equivalent cancellation, source positivity or unbounded support family. It does not establish RH, a global no-go or a new finite-support positivity theorem. Admissions remain eight frozen v1, zero v2 and one v3 C-0067.
