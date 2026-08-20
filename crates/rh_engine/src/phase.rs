//! Stationary-phase and zero-height mappings for Laguerre-weighted oscillatory integrals.

/// Stationary phase point $t_*(\gamma, n) = n \cdot A^2 / \gamma^2$ where $A = 2s_0 - 1$.
///
/// Matches the high-degree Laguerre frequency $\frac{d}{dt}[2\sqrt{nt}] = \sqrt{n/t}$
/// with the zero mode frequency $\frac{\gamma}{A}$.
#[inline]
pub fn stationary_t_from_gamma(gamma: f64, n: usize, s0: f64) -> f64 {
    assert!(gamma > 0.0, "gamma must be > 0");
    assert!(n >= 1, "n must be >= 1");
    assert!(s0 > 1.0, "s0 must be > 1");
    let a = 2.0 * s0 - 1.0;
    (n as f64) * (a * a) / (gamma * gamma)
}

/// Stationary point in uniform variable $u = t / (4n)$:
/// $u_*(\gamma) = \frac{A^2}{4 \gamma^2}$.
#[inline]
pub fn stationary_u_from_gamma(gamma: f64, s0: f64) -> f64 {
    assert!(gamma > 0.0, "gamma must be > 0");
    assert!(s0 > 1.0, "s0 must be > 1");
    let a = 2.0 * s0 - 1.0;
    (a * a) / (4.0 * gamma * gamma)
}

/// Inverse mapping: given stationary location $u$, return corresponding zero height $\gamma$.
#[inline]
pub fn gamma_from_stationary_u(u: f64, s0: f64) -> f64 {
    assert!(u > 0.0, "u must be > 0");
    assert!(s0 > 1.0, "s0 must be > 1");
    let a = 2.0 * s0 - 1.0;
    a / (2.0 * u.sqrt())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_stationary_phase_inversion() {
        let s0 = 3.0;
        let gamma = 14.134725;
        let u = stationary_u_from_gamma(gamma, s0);
        let recovered_gamma = gamma_from_stationary_u(u, s0);
        assert!((gamma - recovered_gamma).abs() < 1e-12);
    }

    #[test]
    fn test_stationary_t_and_u_relation() {
        let s0 = 3.0;
        let n = 16;
        let gamma = 25.0;
        let t_star = stationary_t_from_gamma(gamma, n, s0);
        let u_star = stationary_u_from_gamma(gamma, s0);
        assert!((t_star / (4.0 * n as f64) - u_star).abs() < 1e-12);
    }
}
