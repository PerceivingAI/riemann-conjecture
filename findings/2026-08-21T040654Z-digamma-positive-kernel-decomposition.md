# Positive-kernel decomposition of the archimedean digamma multiplier

- **Finding ID:** `F-20260821-013`
- **Created:** `2026-08-21T04:06:54Z`
- **Last updated:** `2026-08-21T04:06:54Z`
- **Type:** `DERIVED_RESULT`
- **Status:** `VERIFIED`

## Statement

Let

```text
a_k=k+1/4,
m_0=psi(1/4)-log pi.
```

Then

```text
Re psi(1/4+i xi/2)-log pi
=m_0
+sum_(k>=0)
 [1/a_k - 4a_k/(xi^2+4a_k^2)].
```

Consequently, with `fhat(xi)=integral f(t)e^(i xi t)dt`, the corresponding quadratic form is

```text
m_0||f||_2^2
+sum_(k>=0)
 [ (1/a_k)||f||_2^2
   - double_integral e^(-2a_k|t-s|)
       f(t)conj(f(s)) dt ds ].
```

Every bracket is nonnegative.

## Derivation

The standard digamma representation gives

```text
psi(z)+EulerGamma
=sum_(k>=0)[1/(k+1)-1/(k+z)].
```

Subtract the value at `z=1/4`, take the real part at `z=1/4+i xi/2`, and simplify. The bracket multiplier is

```text
xi^2/[a_k(xi^2+4a_k^2)] >= 0.
```

Since

```text
Fourier[e^(-2a|t|)]
=4a/(xi^2+4a^2),
```

Plancherel gives the kernel form.

Finite partial sums therefore give monotone lower bounds for the pure digamma-multiplier component.

## Important limitation

This decomposition does **not** include Suzuki's separate finite-support residual kernel. It is one component of the full finite-support certificate, not the full operator.

## Dependencies

- `R-0030`
- `A-20260821-003`
