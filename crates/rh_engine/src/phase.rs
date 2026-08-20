//! Small-u Bessel-phase diagnostics for Laguerre-weighted oscillatory integrals.
//!
//! These helpers encode the approximation obtained by matching
//! d/dt[2 sqrt(n t)] = sqrt(n/t) to the zero-mode frequency gamma/A.
//! They are NOT the uniform stationary-phase map for arbitrary fixed 0<u<1.
//! A-20260820-005 must derive that uniform pre-turning phase before this API is
//! generalized.

/// Small-u diagnostic location t ~= n A^2 / gamma^2, A=2s0-1.
#[inline]
pub fn small_u_stationary_t_from_gamma(gamma: f64, n: usize, s0: f64) -> f64 {
    assert!(gamma > 0.0, "gamma must be > 0");
    assert!(n >= 1, "n must be >= 1");
    assert!(s0 > 1.0, "s0 must be > 1");
    let a = 2.0 * s0 - 1.0;
    (n as f64) * (a * a) / (gamma * gamma)
}

/// Small-u diagnostic coordinate u ~= A^2/(4 gamma^2), from u=t/(4n).
#[inline]
pub fn small_u_stationary_u_from_gamma(gamma: f64, s0: f64) -> f64 {
    assert!(gamma > 0.0, "gamma must be > 0");
    assert!(s0 > 1.0, "s0 must be > 1");
    let a = 2.0 * s0 - 1.0;
    (a * a) / (4.0 * gamma * gamma)
}

/// Algebraic inverse of `small_u_stationary_u_from_gamma` only.
#[inline]
pub fn gamma_from_small_u_stationary_u(u: f64, s0: f64) -> f64 {
    assert!(u > 0.0, "u must be > 0");
    assert!(s0 > 1.0, "s0 must be > 1");
    let a = 2.0 * s0 - 1.0;
    a / (2.0 * u.sqrt())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_small_u_formula_inversion() {
        let s0 = 3.0;
        let gamma = 14.134725;
        let u = small_u_stationary_u_from_gamma(gamma, s0);
        let recovered_gamma = gamma_from_small_u_stationary_u(u, s0);
        assert!((gamma - recovered_gamma).abs() < 1e-12);
    }

    #[test]
    fn test_small_u_t_and_u_relation() {
        let s0 = 3.0;
        let n = 16;
        let gamma = 25.0;
        let t_star = small_u_stationary_t_from_gamma(gamma, n, s0);
        let u_star = small_u_stationary_u_from_gamma(gamma, s0);
        assert!((t_star / (4.0 * n as f64) - u_star).abs() < 1e-12);
    }
}
