# Complete finite polynomial exterior alternative

- **Created:** 2026-10-26T18:34:38Z
- **Last updated:** 2026-10-26T18:34:38Z
- **Scope:** Same frozen endpoint-order4 witnesses and Omega256. This adds no source, support, projection, coefficient or frequency search.

For a polynomial f of exact degree d, integration by parts terminates exactly. Its physical transform has a finite boundary expansion and therefore, writing a_k=|f^(k)(1)|+|f^(k)(-1)| and Z=T*Omega=192,

    |J f_phys(t)|<=sqrt(T) sum_(k=4)^d a_k/(T|t|)^(k+1).

The lower endpoint traces vanish exactly. There is no omitted derivative integral after degree d. With the same complete logarithmic exterior envelope, full-line integration gives

    E_endpoint<=1/pi sum_(k,l=4)^d a_k a_l Z^(-k-l-1)
                          [1/(k+l+1)^2+1/(2(k+l+1))].

The factor1/pi pays BOTH frequency tails. All polynomial coefficients, endpoint derivatives and rational weights are exact. The already declared Sobolev bound remains valid independently. Publish BOTH complete bounds and use their minimum; no scientific outcome is discarded. This is an alternative complete analytic enclosure, not an assertion that a finite Fourier grid has no tail. The source is certified only after exact polynomial/source reconstruction, not from the floating proposal.
