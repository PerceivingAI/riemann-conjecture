//! Parallel multi-threaded prime-Laguerre trace calculation.

use rayon::prelude::*;
use serde::{Deserialize, Serialize};

use crate::laguerre::laguerre_l1_batch;
use crate::sieve::{higher_prime_powers, sieve_segment, simple_sieve};
use crate::summation::NeumaierSum;

/// Result entry for a single polynomial degree $n$.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TraceEntry {
    pub n: usize,
    pub p_n: f64,
    pub pole_term: f64,
    pub s_n: f64,
    pub s_n_root: f64,
    pub p_n_root: f64,
}

/// Full calculation result across all degrees $n = 1 \dots N$ at a given cutoff $X$.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TraceResult {
    pub s0: f64,
    pub a: f64,
    pub q: f64,
    pub cutoff: u64,
    pub max_n: usize,
    pub elapsed_secs: f64,
    pub entries: Vec<TraceEntry>,
}

/// Compute the prime-Laguerre trace $P_n(X)$ and $S_n(X)$ for $n = 1 \dots N$.
pub fn compute_prime_trace(s0: f64, max_n: usize, cutoff: u64, segment_size: usize) -> TraceResult {
    assert!(s0 > 1.0, "s0 must be > 1");
    assert!(max_n >= 1, "max_n must be >= 1");
    assert!(cutoff >= 2, "cutoff must be >= 2");

    let start_time = std::time::Instant::now();

    let a = 2.0 * s0 - 1.0;
    let q = -s0 / (s0 - 1.0);

    // 1. Precompute base primes for the segmented sieve
    let sqrt_limit = (cutoff as f64).sqrt().ceil() as usize;
    let base_primes = simple_sieve(sqrt_limit);

    // 2. Prepare segment ranges for parallel processing
    let seg_size = (segment_size as u64).max(32_768);
    let mut ranges = Vec::new();
    let mut cur_low = 2u64;
    while cur_low <= cutoff {
        let cur_high = (cur_low + seg_size - 1).min(cutoff);
        ranges.push((cur_low, cur_high));
        cur_low = cur_high + 1;
    }

    // 3. Parallel segment reduction
    let prime_sums: Vec<NeumaierSum> = ranges
        .into_par_iter()
        .map(|(low, high)| {
            let mut local_sums = vec![NeumaierSum::new(); max_n];
            let mut lag_buf = vec![0.0; max_n];

            sieve_segment(low, high, &base_primes, |p| {
                let p_f = p as f64;
                let ln_p = p_f.ln();
                let t = a * ln_p;
                let m_pow = (-s0 * ln_p).exp(); // p^{-s0}
                let weight = a * ln_p * m_pow;

                laguerre_l1_batch(max_n - 1, t, &mut lag_buf);

                for n in 0..max_n {
                    local_sums[n].add(weight * lag_buf[n]);
                }
            });

            local_sums
        })
        .reduce(
            || vec![NeumaierSum::new(); max_n],
            |mut acc, item| {
                for i in 0..max_n {
                    acc[i].merge(item[i]);
                }
                acc
            },
        );

    // 4. Add higher prime powers m = p^k (k >= 2)
    let mut total_sums = prime_sums;
    let higher_powers = higher_prime_powers(cutoff);
    let mut lag_buf = vec![0.0; max_n];

    for power in higher_powers {
        let m_f = power.m as f64;
        let ln_m = m_f.ln();
        let t = a * ln_m;
        let m_pow = (-s0 * ln_m).exp(); // m^{-s0}
        let weight = a * power.log_p * m_pow; // A * ln(p) * m^{-s0}

        laguerre_l1_batch(max_n - 1, t, &mut lag_buf);

        for n in 0..max_n {
            total_sums[n].add(weight * lag_buf[n]);
        }
    }

    let elapsed = start_time.elapsed().as_secs_f64();

    // 5. Construct results
    let mut entries = Vec::with_capacity(max_n);
    for deg in 1..=max_n {
        let p_n = total_sums[deg - 1].total();
        let pole = 1.0 - q.powi(deg as i32);
        let s_n = p_n - pole;

        let s_n_root = if s_n.abs() > 0.0 {
            s_n.abs().powf(1.0 / deg as f64)
        } else {
            0.0
        };

        let p_n_root = if p_n.abs() > 0.0 {
            p_n.abs().powf(1.0 / deg as f64)
        } else {
            0.0
        };

        entries.push(TraceEntry {
            n: deg,
            p_n,
            pole_term: pole,
            s_n,
            s_n_root,
            p_n_root,
        });
    }

    TraceResult {
        s0,
        a,
        q,
        cutoff,
        max_n,
        elapsed_secs: elapsed,
        entries,
    }
}
