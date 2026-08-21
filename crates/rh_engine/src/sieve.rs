//! Segmented bit-sieve and von Mangoldt prime-power generation.

/// Generate primes up to `limit` using a standard odd-only sieve.
pub fn simple_sieve(limit: usize) -> Vec<usize> {
    if limit < 2 {
        return Vec::new();
    }
    let mut primes = Vec::new();
    primes.push(2);
    if limit == 2 {
        return primes;
    }

    let num_odds = (limit - 1) / 2;
    // is_composite[i] represents 2*i + 3
    let mut is_composite = vec![false; num_odds];
    let sqrt_limit = (limit as f64).sqrt() as usize;

    for i in 0..num_odds {
        if !is_composite[i] {
            let p = 2 * i + 3;
            primes.push(p);
            if p <= sqrt_limit {
                // p*p = (2*i + 3)^2 = 4*i^2 + 12*i + 9
                // Index of p*p: (p*p - 3) / 2 = 2*i^2 + 6*i + 3
                let mut j = 2 * i * i + 6 * i + 3;
                while j < num_odds {
                    is_composite[j] = true;
                    j += p;
                }
            }
        }
    }
    primes
}

/// A prime power item: $(m, \Lambda(m)) = (p^k, \ln p)$.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct PrimePower {
    pub m: u64,
    pub log_p: f64,
}

/// Collect all higher prime powers $p^k \le \text{limit}$ with $k \ge 2$.
///
/// For $X = 10^8$, there are only ~3,800 such prime powers.
pub fn higher_prime_powers(limit: u64) -> Vec<PrimePower> {
    let mut powers = Vec::new();
    if limit < 4 {
        return powers;
    }
    let sqrt_limit = (limit as f64).sqrt() as usize;
    let base_primes = simple_sieve(sqrt_limit);

    for &p in &base_primes {
        let p_u64 = p as u64;
        let log_p = (p as f64).ln();
        let mut cur = p_u64.checked_mul(p_u64);

        while let Some(m) = cur {
            if m > limit {
                break;
            }
            powers.push(PrimePower { m, log_p });
            cur = m.checked_mul(p_u64);
        }
    }

    powers.sort_by_key(|item| item.m);
    powers
}

/// Sieve segment helper for parallel processing.
///
/// Sieves odd numbers in the range `[low, high]` (both inclusive) using base primes.
pub fn sieve_segment<F>(low: u64, high: u64, base_primes: &[usize], mut on_prime: F)
where
    F: FnMut(u64),
{
    if low > high {
        return;
    }
    // Adjust low/high to odd boundaries
    let odd_low = if low.is_multiple_of(2) { low + 1 } else { low };
    let odd_high = if high.is_multiple_of(2) { high.saturating_sub(1) } else { high };

    if odd_low > odd_high {
        return;
    }

    // Special case for 2 if in range
    if low <= 2 && high >= 2 {
        on_prime(2);
    }
    if odd_high < 3 {
        return;
    }
    let start_odd = odd_low.max(3);
    let num_odds = ((odd_high - start_odd) / 2 + 1) as usize;
    let mut is_composite = vec![false; num_odds];

    for &p_usize in base_primes {
        let p = p_usize as u64;
        if p == 2 {
            continue;
        }
        if p * p > odd_high {
            break;
        }

        // Find smallest odd multiple of p >= start_odd
        let mut first_mult = start_odd.div_ceil(p) * p;
        if first_mult.is_multiple_of(2) {
            first_mult += p;
        }
        if first_mult < p * p {
            first_mult = p * p;
        }

        while first_mult <= odd_high {
            let idx = ((first_mult - start_odd) / 2) as usize;
            if idx < num_odds {
                is_composite[idx] = true;
            }
            first_mult += 2 * p;
        }
    }

    for (i, &comp) in is_composite.iter().enumerate() {
        if !comp {
            let p = start_odd + 2 * (i as u64);
            on_prime(p);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_sieve() {
        let primes = simple_sieve(30);
        assert_eq!(primes, vec![2, 3, 5, 7, 11, 13, 17, 19, 23, 29]);
    }

    #[test]
    fn test_higher_prime_powers() {
        let powers = higher_prime_powers(35);
        let ms: Vec<u64> = powers.iter().map(|p| p.m).collect();
        // 4=2^2, 8=2^3, 9=3^2, 16=2^4, 25=5^2, 27=3^3, 32=2^5
        assert_eq!(ms, vec![4, 8, 9, 16, 25, 27, 32]);
    }

    #[test]
    fn test_sieve_segment_matches_simple() {
        let limit = 1000;
        let base_primes = simple_sieve((limit as f64).sqrt() as usize);
        let mut segmented_primes = Vec::new();

        sieve_segment(1, 1000, &base_primes, |p| {
            segmented_primes.push(p);
        });

        let expected: Vec<u64> = simple_sieve(1000).into_iter().map(|x| x as u64).collect();
        assert_eq!(segmented_primes, expected);
    }
}
