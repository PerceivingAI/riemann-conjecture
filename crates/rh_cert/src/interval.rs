//! Exact rational interval arithmetic for zero-float certificate verification.

use std::cmp::{max, min};
use std::fmt;
use std::ops::{Add, Mul, Neg, Sub};
use std::str::FromStr;

use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, Zero};
use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Error, Clone, PartialEq, Eq)]
pub enum IntervalError {
    #[error("invalid interval: lower bound {lo} is strictly greater than upper bound {hi}")]
    InvalidBounds { lo: String, hi: String },

    #[error("cannot divide by interval containing zero: [{lo}, {hi}]")]
    DivisionByZero { lo: String, hi: String },

    #[error("invalid rational representation: {0}")]
    ParseError(String),
}

fn is_canonical_integer(value: &str) -> bool {
    let digits = value.strip_prefix('-').unwrap_or(value);
    if digits.is_empty() || !digits.bytes().all(|byte| byte.is_ascii_digit()) {
        return false;
    }
    if digits == "0" {
        return value == "0";
    }
    !digits.starts_with('0')
}

fn is_canonical_positive_integer(value: &str) -> bool {
    !value.is_empty() && !value.starts_with('0') && value.bytes().all(|byte| byte.is_ascii_digit())
}

pub(crate) fn parse_canonical_rational(
    numerator: &str,
    denominator: &str,
    field: &str,
) -> Result<BigRational, IntervalError> {
    if !is_canonical_integer(numerator) {
        return Err(IntervalError::ParseError(format!(
            "{field} numerator is not a canonical integer: '{numerator}'"
        )));
    }
    if !is_canonical_positive_integer(denominator) {
        return Err(IntervalError::ParseError(format!(
            "{field} denominator must be a canonical positive integer: '{denominator}'"
        )));
    }

    let num = BigInt::from_str(numerator).map_err(|error| {
        IntervalError::ParseError(format!("invalid {field} numerator '{numerator}': {error}"))
    })?;
    let den = BigInt::from_str(denominator).map_err(|error| {
        IntervalError::ParseError(format!(
            "invalid {field} denominator '{denominator}': {error}"
        ))
    })?;
    let rational = BigRational::new(num, den);
    if rational.numer().to_string() != numerator || rational.denom().to_string() != denominator {
        return Err(IntervalError::ParseError(format!(
            "{field} must be a reduced canonical rational"
        )));
    }
    Ok(rational)
}

/// An exact rational interval `[lo, hi]` backed by arbitrary-precision `BigRational`.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct RationalInterval {
    pub lo: BigRational,
    pub hi: BigRational,
}

impl RationalInterval {
    /// Create a new interval `[lo, hi]`. Enforces `lo <= hi`.
    pub fn new(lo: BigRational, hi: BigRational) -> Result<Self, IntervalError> {
        if lo > hi {
            return Err(IntervalError::InvalidBounds {
                lo: lo.to_string(),
                hi: hi.to_string(),
            });
        }
        Ok(Self { lo, hi })
    }

    /// Create a degenerate point interval `[val, val]`.
    pub fn point(val: BigRational) -> Self {
        Self {
            lo: val.clone(),
            hi: val,
        }
    }

    /// Create a point interval from an integer `[val, val]`.
    pub fn from_integer(val: i64) -> Self {
        let r = BigRational::from_integer(BigInt::from(val));
        Self::point(r)
    }

    /// Create an interval from integer bounds `[lo, hi]`.
    pub fn from_integers(lo: i64, hi: i64) -> Result<Self, IntervalError> {
        let lo_r = BigRational::from_integer(BigInt::from(lo));
        let hi_r = BigRational::from_integer(BigInt::from(hi));
        Self::new(lo_r, hi_r)
    }

    /// Construct an interval from canonical, reduced string fractions.
    pub fn from_fraction_strings(
        lo_num: &str,
        lo_den: &str,
        hi_num: &str,
        hi_den: &str,
    ) -> Result<Self, IntervalError> {
        let lo = parse_canonical_rational(lo_num, lo_den, "lo endpoint")?;
        let hi = parse_canonical_rational(hi_num, hi_den, "hi endpoint")?;
        Self::new(lo, hi)
    }

    /// Check if the interval contains zero.
    pub fn contains_zero(&self) -> bool {
        self.lo <= BigRational::zero() && self.hi >= BigRational::zero()
    }

    /// Check if the interval contains a given rational point.
    pub fn contains(&self, point: &BigRational) -> bool {
        &self.lo <= point && point <= &self.hi
    }

    /// Check if this interval contains another interval `other`.
    pub fn contains_interval(&self, other: &Self) -> bool {
        self.lo <= other.lo && other.hi <= self.hi
    }

    /// Check if every element in the interval is strictly positive (`lo > 0`).
    pub fn is_strictly_positive(&self) -> bool {
        self.lo > BigRational::zero()
    }

    /// Check if every element in the interval is strictly negative (`hi < 0`).
    pub fn is_strictly_negative(&self) -> bool {
        self.hi < BigRational::zero()
    }

    /// Compute the midpoint of the interval `(lo + hi) / 2`.
    pub fn midpoint(&self) -> BigRational {
        (&self.lo + &self.hi) / BigRational::from_integer(BigInt::from(2))
    }

    /// Compute the radius of the interval `(hi - lo) / 2`.
    pub fn radius(&self) -> BigRational {
        (&self.hi - &self.lo) / BigRational::from_integer(BigInt::from(2))
    }

    /// Exact interval squaring: `[lo, hi]^2`.
    pub fn sqr(&self) -> Self {
        if self.contains_zero() {
            let s1 = &self.lo * &self.lo;
            let s2 = &self.hi * &self.hi;
            let max_sq = max(s1, s2);
            Self {
                lo: BigRational::zero(),
                hi: max_sq,
            }
        } else {
            let s1 = &self.lo * &self.lo;
            let s2 = &self.hi * &self.hi;
            Self {
                lo: min(s1.clone(), s2.clone()),
                hi: max(s1, s2),
            }
        }
    }

    /// Checked interval division `self / other`.
    pub fn checked_div(&self, other: &Self) -> Result<Self, IntervalError> {
        if other.contains_zero() {
            return Err(IntervalError::DivisionByZero {
                lo: other.lo.to_string(),
                hi: other.hi.to_string(),
            });
        }
        let inv_lo = other.hi.recip();
        let inv_hi = other.lo.recip();
        let inv_other = Self {
            lo: min(inv_lo.clone(), inv_hi.clone()),
            hi: max(inv_lo, inv_hi),
        };
        Ok(self * &inv_other)
    }
}

impl fmt::Display for RationalInterval {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}, {}]", self.lo, self.hi)
    }
}

impl Add<&RationalInterval> for &RationalInterval {
    type Output = RationalInterval;

    fn add(self, rhs: &RationalInterval) -> RationalInterval {
        RationalInterval {
            lo: &self.lo + &rhs.lo,
            hi: &self.hi + &rhs.hi,
        }
    }
}

impl Add<RationalInterval> for RationalInterval {
    type Output = RationalInterval;

    fn add(self, rhs: RationalInterval) -> RationalInterval {
        &self + &rhs
    }
}

impl Add<&RationalInterval> for RationalInterval {
    type Output = RationalInterval;

    fn add(self, rhs: &RationalInterval) -> RationalInterval {
        &self + rhs
    }
}

impl Add<RationalInterval> for &RationalInterval {
    type Output = RationalInterval;

    fn add(self, rhs: RationalInterval) -> RationalInterval {
        self + &rhs
    }
}

impl Neg for &RationalInterval {
    type Output = RationalInterval;

    fn neg(self) -> RationalInterval {
        RationalInterval {
            lo: -&self.hi,
            hi: -&self.lo,
        }
    }
}

impl Neg for RationalInterval {
    type Output = RationalInterval;

    fn neg(self) -> RationalInterval {
        -&self
    }
}

impl Sub<&RationalInterval> for &RationalInterval {
    type Output = RationalInterval;

    fn sub(self, rhs: &RationalInterval) -> RationalInterval {
        RationalInterval {
            lo: &self.lo - &rhs.hi,
            hi: &self.hi - &rhs.lo,
        }
    }
}

impl Sub<RationalInterval> for RationalInterval {
    type Output = RationalInterval;

    fn sub(self, rhs: RationalInterval) -> RationalInterval {
        &self - &rhs
    }
}

impl Sub<&RationalInterval> for RationalInterval {
    type Output = RationalInterval;

    fn sub(self, rhs: &RationalInterval) -> RationalInterval {
        &self - rhs
    }
}

impl Sub<RationalInterval> for &RationalInterval {
    type Output = RationalInterval;

    fn sub(self, rhs: RationalInterval) -> RationalInterval {
        self - &rhs
    }
}

impl Mul<&RationalInterval> for &RationalInterval {
    type Output = RationalInterval;

    fn mul(self, rhs: &RationalInterval) -> RationalInterval {
        let p1 = &self.lo * &rhs.lo;
        let p2 = &self.lo * &rhs.hi;
        let p3 = &self.hi * &rhs.lo;
        let p4 = &self.hi * &rhs.hi;

        let min_p = min(min(p1.clone(), p2.clone()), min(p3.clone(), p4.clone()));
        let max_p = max(max(p1, p2), max(p3, p4));

        RationalInterval {
            lo: min_p,
            hi: max_p,
        }
    }
}

impl Mul<RationalInterval> for RationalInterval {
    type Output = RationalInterval;

    fn mul(self, rhs: RationalInterval) -> RationalInterval {
        &self * &rhs
    }
}

impl Mul<&RationalInterval> for RationalInterval {
    type Output = RationalInterval;

    fn mul(self, rhs: &RationalInterval) -> RationalInterval {
        &self * rhs
    }
}

impl Mul<RationalInterval> for &RationalInterval {
    type Output = RationalInterval;

    fn mul(self, rhs: RationalInterval) -> RationalInterval {
        self * &rhs
    }
}

impl Zero for RationalInterval {
    fn zero() -> Self {
        Self::point(BigRational::zero())
    }

    fn is_zero(&self) -> bool {
        self.lo.is_zero() && self.hi.is_zero()
    }
}

impl One for RationalInterval {
    fn one() -> Self {
        Self::point(BigRational::one())
    }
}
