//! Compensated floating-point summation to prevent catastrophic precision loss.

use std::iter::Sum;
use std::ops::AddAssign;

/// Neumaier compensated summation accumulator.
///
/// An improvement over Kahan summation that handles the case where the next
/// term is larger than the current running sum.
#[derive(Debug, Clone, Copy, Default, PartialEq)]
pub struct NeumaierSum {
    sum: f64,
    compensation: f64,
}

impl NeumaierSum {
    #[inline]
    pub fn new() -> Self {
        Self {
            sum: 0.0,
            compensation: 0.0,
        }
    }

    #[inline]
    pub fn add(&mut self, term: f64) {
        let t = self.sum + term;
        let c = if self.sum.abs() >= term.abs() {
            (self.sum - t) + term
        } else {
            (term - t) + self.sum
        };
        self.sum = t;
        self.compensation += c;
    }

    #[inline]
    pub fn total(&self) -> f64 {
        self.sum + self.compensation
    }

    #[inline]
    pub fn merge(&mut self, other: Self) {
        self.add(other.sum);
        self.add(other.compensation);
    }
}

impl AddAssign<f64> for NeumaierSum {
    #[inline]
    fn add_assign(&mut self, rhs: f64) {
        self.add(rhs);
    }
}

impl AddAssign<NeumaierSum> for NeumaierSum {
    #[inline]
    fn add_assign(&mut self, rhs: NeumaierSum) {
        self.merge(rhs);
    }
}

impl Sum<f64> for NeumaierSum {
    fn sum<I: Iterator<Item = f64>>(iter: I) -> Self {
        let mut acc = Self::new();
        for item in iter {
            acc.add(item);
        }
        acc
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_neumaier_precision() {
        // Adding 1.0 and 1e-16 a million times
        let mut naive = 1.0;
        let mut neumaier = NeumaierSum::new();
        neumaier.add(1.0);

        for _ in 0..1_000_000 {
            naive += 1e-16;
            neumaier.add(1e-16);
        }

        // Naive sum completely loses 1e-16 due to binary64 mantissa limit (53 bits ~ 15-17 digits)
        assert_eq!(naive, 1.0);
        // Neumaier tracks the exact compensation
        assert!((neumaier.total() - (1.0 + 1e-10)).abs() < 1e-15);
    }
}
