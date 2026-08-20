//! Cross-validation of the native Rust engine against mathematical invariants.

use rh_engine::bins::compute_range_bins;
use rh_engine::laguerre::laguerre_alpha;
use rh_engine::sieve::{higher_prime_powers, simple_sieve};
use rh_engine::trace::compute_prime_trace;

#[test]
fn test_prime_count_invariants() {
    // Prime counting function pi(x)
    assert_eq!(simple_sieve(10).len(), 4); // 2, 3, 5, 7
    assert_eq!(simple_sieve(100).len(), 25);
    assert_eq!(simple_sieve(1000).len(), 168);
    assert_eq!(simple_sieve(10000).len(), 1229);
}

#[test]
fn test_laguerre_contiguous_relations() {
    // L_n^(0)(t) = L_n^(1)(t) - L_{n-1}^(1)(t)
    for n in 1..=20 {
        for &t in &[0.0, 0.5, 1.2, 5.0, 15.0] {
            let l0 = laguerre_alpha(n, 0, t);
            let l1_curr = laguerre_alpha(n, 1, t);
            let l1_prev = laguerre_alpha(n - 1, 1, t);
            let diff = (l0 - (l1_curr - l1_prev)).abs();
            assert!(diff < 1e-11 * (1.0 + l0.abs()));
        }
    }
}

#[test]
fn test_trace_degree_one_matches_prime_sum() {
    let s0 = 3.0;
    let cutoff = 1000;
    let res = compute_prime_trace(s0, 1, cutoff, 1024);

    let a = 2.0 * s0 - 1.0;
    let primes = simple_sieve(cutoff as usize);
    let mut manual_sum = 0.0;

    for p in primes {
        let p_f = p as f64;
        let ln_p = p_f.ln();
        manual_sum += a * ln_p * (-s0 * ln_p).exp();
    }

    let powers = higher_prime_powers(cutoff);
    for power in powers {
        let m_f = power.m as f64;
        let ln_m = m_f.ln();
        manual_sum += a * power.log_p * (-s0 * ln_m).exp();
    }

    let diff = (res.entries[0].p_n - manual_sum).abs();
    assert!(diff < 1e-12);
}

#[test]
fn test_range_bins_partition_consistency() {
    let s0 = 3.0;
    let n = 8;
    let max_m = 10_000;
    let u_bins = vec![0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0];
    let res = compute_range_bins(s0, n, max_m, &u_bins, 500);

    let sum_of_bins: f64 = res.bins.iter().map(|b| b.discrete_sum).sum();
    let diff = (res.total_discrete - sum_of_bins).abs();
    assert!(diff < 1e-12);
}
