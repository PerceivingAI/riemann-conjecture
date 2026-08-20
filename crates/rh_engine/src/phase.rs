//! Phase diagnostics for Laguerre-weighted oscillatory integrals.
//!
//! The `small_u_*` helpers encode the approximation obtained by matching
//! d/dt[2 sqrt(n t)] = sqrt(n/t) to the zero-mode frequency gamma/A.
//! The `uniform_preturning_*` helpers use the DLMF uniform Bessel phase for
//! L_(n-1)^(1)(4 n u): xi(u)=1/2(sqrt(u-u^2)+asin(sqrt(u))).

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

/// DLMF phase coordinate xi(u), valid for 0 <= u <= 1.
#[inline]
pub fn laguerre_uniform_xi(u: f64) -> f64 {
    assert!((0.0..=1.0).contains(&u), "u must lie in [0,1]");
    0.5 * ((u * (1.0 - u)).sqrt() + u.sqrt().asin())
}

/// Uniform pre-turning stationary coordinate u_gamma=A^2/(A^2+4 gamma^2).
#[inline]
pub fn uniform_preturning_stationary_u_from_gamma(gamma: f64, s0: f64) -> f64 {
    assert!(gamma > 0.0, "gamma must be > 0");
    assert!(s0 > 1.0, "s0 must be > 1");
    let a = 2.0 * s0 - 1.0;
    (a * a) / (a * a + 4.0 * gamma * gamma)
}

/// Uniform pre-turning stationary t coordinate, t_gamma=4n*u_gamma.
#[inline]
pub fn uniform_preturning_stationary_t_from_gamma(gamma: f64, n: usize, s0: f64) -> f64 {
    assert!(n >= 1, "n must be >= 1");
    4.0 * (n as f64) * uniform_preturning_stationary_u_from_gamma(gamma, s0)
}

/// Inverse uniform pre-turning map gamma=A/2*sqrt((1-u)/u).
#[inline]
pub fn gamma_from_uniform_preturning_u(u: f64, s0: f64) -> f64 {
    assert!(u > 0.0 && u < 1.0, "u must lie in (0,1)");
    assert!(s0 > 1.0, "s0 must be > 1");
    let a = 2.0 * s0 - 1.0;
    0.5 * a * ((1.0 - u) / u).sqrt()
}

/// Principal phase per coefficient n of z_rho^(-1) for rho=1/2+i gamma.
#[inline]
pub fn critical_cayley_phase_per_n(gamma: f64, s0: f64) -> f64 {
    assert!(gamma > 0.0, "gamma must be > 0");
    assert!(s0 > 1.0, "s0 must be > 1");
    let a = 2.0 * s0 - 1.0;
    -2.0 * (a / (2.0 * gamma)).atan()
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
    fn test_uniform_formula_inversion() {
        let s0 = 3.0;
        for gamma in [1.0, 5.0, 14.134725, 50.0, 500.0] {
            let u = uniform_preturning_stationary_u_from_gamma(gamma, s0);
            let recovered_gamma = gamma_from_uniform_preturning_u(u, s0);
            assert!((gamma - recovered_gamma).abs() < 1e-12 * gamma.max(1.0));
        }
    }

    #[test]
    fn test_uniform_phase_matches_critical_cayley_phase() {
        let s0 = 3.0;
        let gamma = 14.134725;
        let a = 2.0 * s0 - 1.0;
        let u = uniform_preturning_stationary_u_from_gamma(gamma, s0);
        let xi = laguerre_uniform_xi(u);
        let saddle_phase_per_n = 4.0 * (gamma * u / a - xi);
        let cayley_phase = critical_cayley_phase_per_n(gamma, s0);
        assert!((saddle_phase_per_n - cayley_phase).abs() < 1e-12);
    }

    #[test]
    fn test_uniform_t_and_u_relation() {
        let s0 = 3.0;
        let n = 16;
        let gamma = 25.0;
        let t_star = uniform_preturning_stationary_t_from_gamma(gamma, n, s0);
        let u_star = uniform_preturning_stationary_u_from_gamma(gamma, s0);
        assert!((t_star / (4.0 * n as f64) - u_star).abs() < 1e-12);
    }
}
