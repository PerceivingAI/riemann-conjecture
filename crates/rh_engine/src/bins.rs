//! Range decomposition into turning-scale $u = t / (4n)$ bins.

use rayon::prelude::*;
use serde::{Deserialize, Serialize};

use crate::laguerre::laguerre_l1;
use crate::sieve::{higher_prime_powers, sieve_segment, simple_sieve};
use crate::summation::NeumaierSum;

/// Result entry for a single $u$-bin.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BinEntry {
    pub u_lo: f64,
    pub u_hi: f64,
    pub discrete_sum: f64,
    pub continuous_integral: f64,
    pub discrepancy: f64,
    pub count_prime_powers: u64,
}

/// Result for a single degree $n$ across all bins.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RangeBinResult {
    pub s0: f64,
    pub a: f64,
    pub n: usize,
    pub max_m: u64,
    pub elapsed_secs: f64,
    pub total_discrete: f64,
    pub total_continuous: f64,
    pub total_discrepancy: f64,
    pub bins: Vec<BinEntry>,
}

/// Composite Simpson quadrature for continuous main-density integral.
fn composite_simpson<F: Fn(f64) -> f64>(f: F, a: f64, b: f64, steps: usize) -> f64 {
    let n_steps = if steps % 2 == 1 { steps + 1 } else { steps }.max(4);
    let h = (b - a) / (n_steps as f64);
    let mut total = f(a) + f(b);

    for i in 1..n_steps {
        let x = a + (i as f64) * h;
        let factor = if i % 2 == 1 { 4.0 } else { 2.0 };
        total += factor * f(x);
    }
    total * h / 3.0
}

/// Compute range bin decomposition for a given $n$.
pub fn compute_range_bins(
    s0: f64,
    n: usize,
    max_m: u64,
    u_bins: &[f64],
    simpson_steps: usize,
) -> RangeBinResult {
    assert!(s0 > 1.0, "s0 must be > 1");
    assert!(n >= 1, "n must be >= 1");
    assert!(u_bins.len() >= 2, "Must have at least one bin");

    let start_time = std::time::Instant::now();
    let a = 2.0 * s0 - 1.0;
    let p_exp = (s0 - 1.0) / a;

    let num_bins = u_bins.len() - 1;
    let mut bin_sums = vec![NeumaierSum::new(); num_bins];
    let mut bin_counts = vec![0u64; num_bins];

    // Helper to find bin index for a given t
    let bin_index = |t: f64| -> Option<usize> {
        let u = t / (4.0 * n as f64);
        for i in 0..num_bins {
            if u >= u_bins[i] && u < u_bins[i + 1] {
                return Some(i);
            }
        }
        if u >= u_bins[num_bins] {
            return None;
        }
        None
    };

    // 1. Process primes
    let sqrt_limit = (max_m as f64).sqrt().ceil() as usize;
    let base_primes = simple_sieve(sqrt_limit);

    let seg_size = 65_536u64;
    let mut ranges = Vec::new();
    let mut cur_low = 2u64;
    while cur_low <= max_m {
        let cur_high = (cur_low + seg_size - 1).min(max_m);
        ranges.push((cur_low, cur_high));
        cur_low = cur_high + 1;
    }

    let (prime_bin_sums, prime_bin_counts): (Vec<NeumaierSum>, Vec<u64>) = ranges
        .into_par_iter()
        .map(|(low, high)| {
            let mut local_sums = vec![NeumaierSum::new(); num_bins];
            let mut local_counts = vec![0u64; num_bins];

            sieve_segment(low, high, &base_primes, |p| {
                let p_f = p as f64;
                let ln_p = p_f.ln();
                let t = a * ln_p;
                if let Some(idx) = bin_index(t) {
                    let weight = a * ln_p * (-s0 * ln_p).exp();
                    let lag = laguerre_l1(n - 1, t);
                    local_sums[idx].add(weight * lag);
                    local_counts[idx] += 1;
                }
            });

            (local_sums, local_counts)
        })
        .reduce(
            || (vec![NeumaierSum::new(); num_bins], vec![0u64; num_bins]),
            |(mut acc_s, mut acc_c), (item_s, item_c)| {
                for i in 0..num_bins {
                    acc_s[i].merge(item_s[i]);
                    acc_c[i] += item_c[i];
                }
                (acc_s, acc_c)
            },
        );

    for i in 0..num_bins {
        bin_sums[i].merge(prime_bin_sums[i]);
        bin_counts[i] += prime_bin_counts[i];
    }

    // 2. Process higher prime powers
    let higher_powers = higher_prime_powers(max_m);
    for power in higher_powers {
        let m_f = power.m as f64;
        let ln_m = m_f.ln();
        let t = a * ln_m;
        if let Some(idx) = bin_index(t) {
            let weight = a * power.log_p * (-s0 * ln_m).exp();
            let lag = laguerre_l1(n - 1, t);
            bin_sums[idx].add(weight * lag);
            bin_counts[idx] += 1;
        }
    }

    // 3. Compute continuous integrals and discrepancies
    let mut entries = Vec::with_capacity(num_bins);
    let mut total_discrete = 0.0;
    let mut total_continuous = 0.0;

    for i in 0..num_bins {
        let u_lo = u_bins[i];
        let u_hi = u_bins[i + 1];
        let t_lo = 4.0 * (n as f64) * u_lo;
        let t_hi = 4.0 * (n as f64) * u_hi;

        let integrand = |t: f64| -> f64 {
            let env = (-p_exp * t).exp();
            let lag = laguerre_l1(n - 1, t);
            env * lag
        };

        // Note: A * integral_tlo^thi e^{-pt} L_{n-1}^{(1)}(t) dt / A = integral
        // Since dt/x = A / m, the continuous density is exactly A * integral e^{-pt} L_{n-1}^{(1)}(t) dt
        // with p = (s0-1)/A.
        let cont_val = composite_simpson(integrand, t_lo, t_hi, simpson_steps);
        let disc_val = bin_sums[i].total();
        let discrepancy = disc_val - cont_val;

        total_discrete += disc_val;
        total_continuous += cont_val;

        entries.push(BinEntry {
            u_lo,
            u_hi,
            discrete_sum: disc_val,
            continuous_integral: cont_val,
            discrepancy,
            count_prime_powers: bin_counts[i],
        });
    }

    let elapsed = start_time.elapsed().as_secs_f64();

    RangeBinResult {
        s0,
        a,
        n,
        max_m,
        elapsed_secs: elapsed,
        total_discrete,
        total_continuous,
        total_discrepancy: total_discrete - total_continuous,
        bins: entries,
    }
}
