//! High-performance evaluations of generalized Laguerre polynomials $L_n^{(\alpha)}(t)$.

/// Compute $L_n^{(1)}(t)$ for a single degree.
#[inline]
pub fn laguerre_l1(degree: usize, t: f64) -> f64 {
    if degree == 0 {
        return 1.0;
    }
    let mut prev = 1.0; // L_0^(1)
    let mut cur = 2.0 - t; // L_1^(1)

    for k in 1..degree {
        let k_f = k as f64;
        let next = ((2.0 * k_f + 2.0 - t) * cur - (k_f + 1.0) * prev) / (k_f + 1.0);
        prev = cur;
        cur = next;
    }
    cur
}

/// Compute $L_0^{(1)}(t), L_1^{(1)}(t), \dots, L_{\text{max\_degree}}^{(1)}(t)$ in a single pass.
///
/// Fills the output slice `out` where `out.len() >= max_degree + 1`.
#[inline]
pub fn laguerre_l1_batch(max_degree: usize, t: f64, out: &mut [f64]) {
    assert!(out.len() > max_degree, "Output buffer too small");
    out[0] = 1.0;
    if max_degree == 0 {
        return;
    }
    out[1] = 2.0 - t;

    for k in 1..max_degree {
        let k_f = k as f64;
        out[k + 1] = ((2.0 * k_f + 2.0 - t) * out[k] - (k_f + 1.0) * out[k - 1]) / (k_f + 1.0);
    }
}

/// Compute generalized $L_n^{(\alpha)}(t)$ for arbitrary non-negative integer $\alpha$.
#[inline]
pub fn laguerre_alpha(degree: usize, alpha: usize, t: f64) -> f64 {
    if degree == 0 {
        return 1.0;
    }
    let a_f = alpha as f64;
    let mut prev = 1.0; // L_0^(alpha)
    let mut cur = 1.0 + a_f - t; // L_1^(alpha)

    for k in 1..degree {
        let k_f = k as f64;
        let next = ((2.0 * k_f + 1.0 + a_f - t) * cur - (k_f + a_f) * prev) / (k_f + 1.0);
        prev = cur;
        cur = next;
    }
    cur
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_laguerre_l1_small() {
        let t = 0.5;
        assert_eq!(laguerre_l1(0, t), 1.0);
        assert!((laguerre_l1(1, t) - 1.5).abs() < 1e-14); // 2 - 0.5 = 1.5
        // L_2^(1)(t) = 3 - 3t + 0.5 t^2 = 3 - 1.5 + 0.125 = 1.625
        assert!((laguerre_l1(2, t) - 1.625).abs() < 1e-14);
    }

    #[test]
    fn test_batch_matches_scalar() {
        let t = 2.5;
        let max_n = 32;
        let mut batch = vec![0.0; max_n + 1];
        laguerre_l1_batch(max_n, t, &mut batch);

        for (n, &actual) in batch.iter().enumerate() {
            let scalar = laguerre_l1(n, t);
            assert!((actual - scalar).abs() < 1e-12 * (1.0 + scalar.abs()));
        }
    }

    #[test]
    fn test_contiguous_identity() {
        // L_n^(0)(t) == L_n^(1)(t) - L_{n-1}^(1)(t)
        for n in 1..=20 {
            for &t in &[0.1, 1.0, 3.5, 10.0] {
                let l0 = laguerre_alpha(n, 0, t);
                let l1_curr = laguerre_alpha(n, 1, t);
                let l1_prev = laguerre_alpha(n - 1, 1, t);
                assert!((l0 - (l1_curr - l1_prev)).abs() < 1e-11 * (1.0 + l0.abs()));
            }
        }
    }
}
