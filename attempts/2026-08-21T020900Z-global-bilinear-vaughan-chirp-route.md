# Global Vaughan/Heath-Brown bilinear decomposition of the Laguerre prime chirp

- **Attempt ID:** `A-20260821-001`
- **Created:** `2026-08-21T02:09:00Z`
- **Last updated:** `2026-08-21T02:09:00Z`
- **Status:** `COMPLETE`
- **Success target:** Determine whether a Vaughan/Heath-Brown divisor decomposition of `Lambda` can exploit genuinely two-dimensional oscillation in the nonlinear Laguerre chirp and beat the one-dimensional exponential-length barrier found in `A-006` without importing RH-strength arithmetic cancellation.

## Question / goal

`A-006` reduced a fixed-interior chirp cell to a smooth critical-half-weight prime Dirichlet polynomial, but showed that generic one-dimensional mean-value estimates retain a positive exponential root scale.

The planned next idea was to avoid estimating frequency cells independently and instead apply a global Vaughan/Heath-Brown-type identity to `Lambda(m)`, writing product variables such as

```text
m=a b
```

and studying Type I/II bilinear sums with phase

```text
Phi_n(log a + log b).
```

The hope was that mixed curvature or bilinear averaging might create cancellation unavailable to the one-dimensional Dirichlet-polynomial formulation.

This attempt tests that hope at the exact exponential-root scale.

## Dependencies and known results

Repository claims:

- `C-0010` — `RH <=> limsup |S_n|^(1/n)<=1`;
- `C-0011` — exact pole-subtracted `d(psi-x)` Laguerre transform;
- `C-0023` — fixed-interior critical-half-weight nonlinear chirp;
- `C-0028` — microlocal critical-half-weight Dirichlet reduction;
- `C-0029` — one-dimensional Montgomery-Vaughan exponential-length barrier;
- `C-0030` — independent matched-cell subexponentiality is zero-sensitive.

External sources:

- `R-0021` — Helfgott's explicit presentation of Vaughan's identity and Type I/II decomposition;
- `R-0022` — Graham-Kolesnik two-dimensional van der Corput framework;
- `R-0023` — Montgomery-Vaughan modern treatment of exponential sums over primes and bilinear forms.

Computation:

- `X-20260821-001` — deterministic bilinear chirp geometry and separability diagnostics.

## Mathematical setup

Fix `s0>1`,

```text
A=2s0-1,
y=log x,
u=A y/(4n),
```

and on the fixed-interior pre-turning range define

```text
Phi_n(y)=4n xi(Ay/(4n))-3pi/4,
xi(u)=1/2[sqrt(u-u^2)+asin(sqrt(u))].
```

Then

```text
Phi_n'(y)
= A/2 sqrt((1-u)/u),
```

and

```text
Phi_n''(y)
= -A^2/[16n u^(3/2)sqrt(1-u)].
```

Thus on every compact subinterval

```text
epsilon <= u <= 1-delta
```

we have

```text
Phi_n''(y)=O_(epsilon,delta,A)(1/n).
```

A Vaughan Type-II term has the schematic phase

```text
F(a,b)=Phi_n(log a+log b).
```

For a `k`-fold convolution write

```text
m=a_1 ... a_k,
r_j=log a_j,
F_k(r_1,...,r_k)=Phi_n(r_1+...+r_k).
```

## Derivation / argument

### Step 1 — Vaughan decomposition introduces arithmetic variables, not new phase variables

Vaughan's identity expresses `Lambda` as a finite sum of Dirichlet convolutions and is conventionally separated into Type I and Type II sums.

For this problem, every convolution term still evaluates the same weight at the product of its factors. Hence for a bilinear term

```text
F(r,s)=Phi_n(r+s),
r=log a,
s=log b.
```

The logarithmic derivatives are

```text
F_rr=Phi_n''(r+s),
F_rs=Phi_n''(r+s),
F_ss=Phi_n''(r+s).
```

Therefore

```text
Hess_(r,s) F
= Phi_n''(r+s) [[1,1],[1,1]],
```

and

```text
det Hess_(r,s) F = 0.
```

There is one oscillatory direction, `r+s`, and one exactly flat direction, `r-s`, along which the product `ab` stays fixed.

### Step 2 — the rank-one geometry persists for every finite divisor identity

For

```text
F_k(r_1,...,r_k)=Phi_n(r_1+...+r_k),
```

we have

```text
Hess F_k
= Phi_n'' * 1 1^T,
```

where `1` is the all-ones column vector.

Hence

```text
rank(Hess F_k) <= 1
```

for every finite `k`.

Thus replacing Vaughan's identity by Heath-Brown's identity, or by another finite multiplicative convolution decomposition of `Lambda`, cannot create independent oscillatory curvature in the new factor variables. It produces `k-1` exactly flat logarithmic directions corresponding to redistribution of factors with the product fixed.

This does not rule out arithmetic cancellation in the convolution coefficients. It rules out the hoped-for mechanism in which the divisor identity itself creates genuinely multidimensional phase oscillation.

### Step 3 — standard dyadic Type-II boxes are asymptotically separable

Let

```text
a in [M,2M],
b in [N,2N]
```

with `MN` lying in a fixed-interior product range. Then both logarithmic widths are at most `log 2`.

For `r_0,s_0` in the box define the four-corner cross defect

```text
Delta F
= F(r,s)-F(r,s_0)-F(r_0,s)+F(r_0,s_0).
```

By two applications of the fundamental theorem of calculus,

```text
Delta F
= integral_(r_0)^r integral_(s_0)^s
    Phi_n''(alpha+beta) d beta d alpha.
```

Therefore

```text
|Delta F|
<= sup_box |Phi_n''| |r-r_0||s-s_0|
<= C_(epsilon,delta,A) (log 2)^2/n.
```

Consequently

```text
exp(iF(r,s))
= C_0 P(r)Q(s)[1+O(1/n)]
```

uniformly on every fixed-interior dyadic box, for suitable unimodular one-variable factors `P,Q,C_0`.

So the Type-II phase becomes asymptotically multiplicatively separable on precisely the dyadic boxes used by the standard Vaughan method.

### Step 4 — generic phase-only bilinear estimates cannot have an exponential saving

The previous step yields more than a small-curvature observation.

Suppose a bilinear estimate is uniform over arbitrary bounded coefficient sequences. On a dyadic box choose coefficient phases that cancel the one-variable factors `P(r)` and `Q(s)` in the separable approximation. The bilinear kernel is then constant up to `O(1/n)` phase error.

Therefore no estimate based only on the phase geometry and arbitrary coefficient norms can produce an exponential saving relative to the trivial half-weighted mass on such boxes.

Any successful Type-II estimate must use **special arithmetic information about the actual Vaughan coefficients** (`mu`, truncated divisor convolutions, `Lambda`, etc.), not merely mixed oscillation of the Laguerre phase.

### Step 5 — unit bilinear nonseparability requires logarithmic blocks of square-root-n scale

On a fixed interior range,

```text
|Phi_n''| ~ c(u,A)/n.
```

For logarithmic factor widths `H_r,H_s`, the cross-phase variation has scale

```text
|Delta F| ~ |Phi_n''| H_r H_s.
```

Hence an `O(1)` cross phase requires

```text
H_r H_s ~ n.
```

In the balanced case,

```text
H_r ~ H_s ~ sqrt(n).
```

These are multiplicative factor ranges of ratio

```text
exp(c sqrt(n)),
```

which is subexponential but enormously wider than dyadic ranges.

Even on such blocks the induced cross phase is only `O(1)`, not exponentially oscillatory. To obtain a growing number of bilinear phase oscillations one must use still wider logarithmic blocks.

The numerical diagnostics `X-20260821-001` verify the `1/n` dyadic cross-defect scaling and `sqrt(n)` unit-cross-phase width.

### Step 6 — the pre-turning phase itself has only linear-in-n complexity

The deterministic phase function satisfies

```text
xi(0)=0,
xi(1)=pi/4.
```

Hence its total formal pre-turning excursion is exactly

```text
4n[xi(1)-xi(0)] = pi n.
```

That is only

```text
n/2
```

full `2pi` phase cycles across the entire pre-turning logarithmic range.

Thus the phase complexity grows polynomially with `n`, whereas each fixed-interior prime scale is

```text
X=exp(c n).
```

The enormous amount of cancellation required at root scale cannot come from an exponentially large number of independent phase oscillations: they do not exist.

The phase acts as a slowly varying Mellin character whose frequency changes over `O(n)` logarithmic distance.

### Step 7 — the exact saving threshold is square-root scale in X

Fix an interior scale

```text
X=exp(4n u/A),
0<u<1.
```

Ignoring only algebraic and subexponential factors, the critical half-weight contributes `X^(-1/2)`.

Suppose an arithmetic Type I/II argument gives an unweighted prime discrepancy estimate of the form

```text
|P(X)| <= X^(1-delta+o(1)).
```

After the critical half-weight, its contribution is still

```text
X^(1/2-delta+o(1)).
```

To reach the required

```text
X^o(1)=exp(o(n))
```

root scale, one needs

```text
delta >= 1/2.
```

Therefore any conventional fixed power saving strictly smaller than square-root cancellation still leaves a positive exponential root.

This is the central scale obstruction: the route does not merely need a nontrivial prime exponential-sum estimate. It needs essentially square-root cancellation at exponentially large `X`.

### Step 8 — standard Type I/II triangle estimates therefore do not escape the RH-scale barrier

A standard Vaughan argument bounds finitely many Type I/II pieces separately and combines them by triangle inequality.

Here:

1. dyadic Type-II phase geometry is asymptotically separable;
2. finite higher convolution identities retain rank-one phase geometry;
3. phase-only arbitrary-coefficient bilinear estimates cannot give exponential saving;
4. even an arithmetic power saving `X^(1-delta)` is insufficient unless `delta>=1/2`;
5. `A-006` already showed that independently forcing every Mellin-frequency cell to be subexponential is zero-sensitive.

Thus a conventional Vaughan/Heath-Brown decomposition plus separate Type I/II bounds does not produce a demonstrably weaker intermediate target than the square-root prime cancellation already known to sit at the RH boundary.

This does not prove that no sophisticated arithmetic use of the convolution coefficients could ever help. It does establish that the hoped-for **new bilinear oscillatory mechanism** is absent.

## Checks performed

### Algebraic / analytic

- differentiated `F(r,s)=Phi_n(r+s)` and computed the rank-one logarithmic Hessian;
- generalized the Hessian calculation to arbitrary finite multiplicative convolutions;
- proved the dyadic four-corner defect bound by double integration of `Phi_n''`;
- derived the balanced unit-cross-phase scale `H~sqrt(n)`;
- evaluated the total phase excursion `pi n`;
- derived the root-scale saving threshold `delta>=1/2`.

### Numerical

`scripts/bilinear_chirp_geometry.py` was run for `s0=2,3,4` at `n=1024`, and for `s0=3` at `n=256,1024,4096`.

At `s0=3`, `u=0.25`, a dyadic logarithmic box gives cross defects

```text
n=256:  2.7090e-2
n=1024: 6.7722e-3
n=4096: 1.6931e-3,
```

consistent with exact `1/n` scaling.

At `s0=3`, `n=1024`, the balanced logarithmic half-width needed for unit cross phase is approximately

```text
u=0.10: Hcrit=4.434...
u=0.25: Hcrit=8.423...
u=0.50: Hcrit=12.8,
```

all proportional to `sqrt(n)` with the analytic constants recorded in `X-20260821-001`.

The total formal pre-turning phase cycles are exactly `n/2`; the script returns `512` cycles at `n=1024`.

### Literature cross-check

- Helfgott's treatment of Vaughan's identity was checked directly, including the convolution formula and the standard Type I/II split;
- Graham-Kolesnik was checked as a standard reference for one- and two-dimensional van der Corput methods;
- Montgomery-Vaughan's modern volume was checked for the standard framework of exponential sums over primes and bilinear forms.

## Circularity check

No RH-strength estimate is assumed.

The following are explicitly **not** treated as free inputs:

1. square-root cancellation for the weighted/unweighted prime discrepancy;
2. a Type-II theorem whose arithmetic hypotheses already imply square-root PNT error;
3. independent subexponential bounds for every matched Mellin cell;
4. a generic arbitrary-coefficient bilinear estimate claimed to derive exponential saving from the Laguerre phase alone, which is impossible on dyadic boxes by the separability argument.

## Result

The planned Vaughan/Heath-Brown bilinear route is closed as a new **phase-based** mechanism.

Established:

1. every finite multiplicative convolution retains a rank-one logarithmic phase Hessian;
2. the kernel is asymptotically separable on fixed-interior dyadic Type-II boxes, with cross defect `O(1/n)`;
3. generic phase-only bilinear estimates cannot provide exponential saving there;
4. `O(1)` bilinear nonseparability requires logarithmic widths whose product is `~n`, balanced width `~sqrt(n)`;
5. the full pre-turning phase has only `n/2` formal oscillation cycles;
6. a fixed power-saving prime estimate `X^(1-delta)` reaches the required root scale only when `delta>=1/2`.

Therefore standard Vaughan/Heath-Brown factorization does not weaken the core arithmetic requirement: the branch still needs essentially square-root prime cancellation, or a fundamentally different mechanism that avoids estimating prime discrepancies by magnitude.

No proof of RH has been obtained.

## Obstruction / unresolved step

The Li/Laguerre prime-cancellation branch is now blocked at the following boundary:

> Any direct fixed-interior prime-sum strategy must recover essentially square-root cancellation at `X=exp(cn)`, while multiplicative divisor decompositions do not create additional oscillatory dimensions capable of supplying that saving by phase geometry alone.

Further rearrangements of `Lambda` into finitely many multiplicative convolution variables are not a justified next step unless they introduce a genuinely new arithmetic principle.

## Findings produced

- `F-20260821-001` — finite multiplicative convolutions preserve rank-one chirp geometry.
- `F-20260821-002` — dyadic Type-II chirp kernels are asymptotically separable.
- `F-20260821-003` — unit bilinear nonseparability occurs only on `sqrt(n)` logarithmic scale; total phase excursion is `pi n`.
- `F-20260821-004` — direct prime-sum estimates require square-root saving `delta>=1/2` at root scale.
- `F-20260821-005` — generic Vaughan/Heath-Brown phase-only route is blocked.

## Claims affected

Created `C-0031` through `C-0035`.

## Next action

Do **not** iterate another finite divisor identity on the same prime chirp.

Create `A-20260821-002` as a **mechanism pivot**: investigate whether the Cayley/Li zero moments admit a positivity or moment-matrix formulation whose prime/archimedean side has structure stronger than direct cancellation. The first target should be to derive the exact Toeplitz/Herglotz or Weil-quadratic-form object generated by the generalized Cayley moments, then determine whether that formulation offers any unconditional positivity mechanism or is merely another immediate RH equivalent.

## Timestamped addenda / corrections

None.
