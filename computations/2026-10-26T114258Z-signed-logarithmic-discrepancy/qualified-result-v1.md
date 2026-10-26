# Qualified signed logarithmic discrepancy bound at T3/4

- **Created:** `2026-10-26T11:42:58Z`
- **Last updated:** `2026-10-26T12:12:12Z`
- **Scope:** one already accepted support and its full infinite complement; not a new low-space sign or support extension

## 1. The previously missing kind of estimate is established at this fixed case

With the exact complete signed discrepancy D_E and shifted logarithmic form d_A of C-0107, the executed enclosure and independent verifier prove

    <f,D_E f> <= (1/4)d_A[f] +(873/1024)||f||²,
    T=3/4,  f in H_T intersect the logarithmic form domain.

The scalar coefficient beta=873/1024 is not an assumed norm bound or a derivative majorant. It follows from a uniform proof of rho_T(t)-(1/4)w(t)<=beta over every real frequency, including zero and both infinite tails. The full unbounded energy remains in the inequality.

This is a useful energy-relative inequality at one fixed support, not an all-support estimate or an assertion that its constants scale favorably. C-0109's rejected derivative argument is not reused. C-0108's scalar-plus-compact obstruction is not contradicted: the right side retains an unbounded logarithmic form with nonzero coefficient.

## 2. What was actually enclosed

The [analytic contract](signed-symbol-contract-v1.md) derives the complete symbol and closed-interval/infinite-tail bounds. The producer uses a complex exponential quotient for the continuum and a coarse global derivative constant; an independent384-bit checker reconstructs the real trigonometric quotient, a sharper continuum derivative integral, and lower energy bounds from128 positive difference-series terms plus the proved explicit logarithmic remainder. Shared Arb/FLINT correctness remains a premise.

Exactly2371 positive-length dyadic leaf intervals cover[0,256] without a gap. Each midpoint value is supplemented by a proved interval Lipschitz payment and a monotone endpoint energy bound. The verified finite supremum enclosure has lower/upper displays0.8478898444883236 and0.8517810378023383, gap below1/256. The producer's analytic upper for both infinite tails is about0.4464542510, below the finite lower witness. Publishing the nonnegative maximum upward on the declared1/1024 grid gives beta873/1024.

These statements concern a pointwise symbol bound for fixed alpha1/4. They do not claim optimal alpha or the best compressed-form estimate. A finite sample mesh alone is not the proof: exact leaf coverage, analytic interval envelopes and the infinite-tail inequality are necessary and were independently checked.

## 3. A positive complete outside lower at the existing projection

At the unchanged N312, C-0107 gives the full reference lower

    mu_N(R)=1+[w(R)-1][1-(2TR/pi)E_N(TR)]

when the displayed leakage is below1. The original fixed-source frequency R=256 has c=192 and a valid geometric ratio192²/(625*627)<1. This is an uncertainty/reference-tail estimate, not a truncation of the unbounded energy.

Using the signed identity Q_W=d_A+(A0-1)||f||²+<f,L_T f>-d_E and L_T>=0 gives

    Q_W[f] >= [(3/4)mu_312(256)+A0-1-873/1024]||f||²
            >= (1/3)||f||²,
    f in Q_312 H_(3/4) intersect the logarithmic form domain.

The independent conservative lower endpoint is about0.33486747806, strictly above the exact rational1/3. The proof includes the full infinite complement and both signed pole sectors through the exact discrepancy identity. It is not a full-form spectral minimum or a new finite low/cross positivity result.

The earlier scalar-reference complete outside lower at this case is63/32-4e-49, numerically larger than1/3. The new result qualifies a different energy-relative interface; it does not improve the known local coercivity.

Before any scalar execution, the qualified inputs declared both the inherited closed-policy reference anchor R416/3 and the already-qualified fixed-source anchor256. Both outcomes are retained. The former gives a sufficient lower about-0.125016 and does not certify positivity by that weaker reference estimate. It is not evidence of a negative true tail. The latter uses the sharper available exact E_N bound at the same support and projection. No support/dimension/alpha search or matrix run is performed.

## 4. Distinct roles and limitations

The frequency boundary256 in the symbol proof separates interval certification from an analytic infinity bound. The reference anchor256 bounds Fourier leakage from the Legendre tail. The old bounded minorant also used numerical cutoff256, but the present construction does not discard high-frequency logarithmic energy or replace it by a compact band. These roles must not be conflated.

This result qualifies a derivative-free discrepancy-to-energy interface and a useful complete outside lower at the retained control case. It does not accept a new complete reference proof system: finite low/cross source enclosures and their sufficient Schur sign remain independent, with their own domain/error obligations. Earlier positive packets cannot simply be relabeled as those inputs. No comparison proving superiority to the older complete criterion, new support reach, global family, universal precision/cost advantage, literature originality or production admission is claimed.
