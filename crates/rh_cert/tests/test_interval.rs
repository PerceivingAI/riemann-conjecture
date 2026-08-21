//! Unit tests for exact rational interval arithmetic.

use num_bigint::BigInt;
use num_rational::BigRational;
use rh_cert::interval::{IntervalError, RationalInterval};

#[test]
fn test_interval_construction() {
    let r1 = RationalInterval::from_integers(1, 3).unwrap();
    assert_eq!(r1.lo, BigRational::from_integer(BigInt::from(1)));
    assert_eq!(r1.hi, BigRational::from_integer(BigInt::from(3)));

    let err = RationalInterval::from_integers(5, 2);
    assert!(matches!(err, Err(IntervalError::InvalidBounds { .. })));
}

#[test]
fn test_fraction_string_parsing() {
    let interval = RationalInterval::from_fraction_strings("1", "2", "3", "4").unwrap();
    assert_eq!(interval.lo, BigRational::new(BigInt::from(1), BigInt::from(2)));
    assert_eq!(interval.hi, BigRational::new(BigInt::from(3), BigInt::from(4)));

    let err = RationalInterval::from_fraction_strings("1", "0", "3", "4");
    assert!(matches!(err, Err(IntervalError::ParseError(_))));
}

#[test]
fn test_arithmetic_operations() {
    let i1 = RationalInterval::from_fraction_strings("1", "2", "3", "4").unwrap(); // [1/2, 3/4]
    let i2 = RationalInterval::from_fraction_strings("1", "4", "1", "2").unwrap(); // [1/4, 1/2]

    // Addition: [1/2 + 1/4, 3/4 + 1/2] = [3/4, 5/4]
    let add = &i1 + &i2;
    assert_eq!(add.lo, BigRational::new(BigInt::from(3), BigInt::from(4)));
    assert_eq!(add.hi, BigRational::new(BigInt::from(5), BigInt::from(4)));

    // Subtraction: [1/2 - 1/2, 3/4 - 1/4] = [0, 1/2]
    let sub = &i1 - &i2;
    assert_eq!(sub.lo, BigRational::from_integer(BigInt::from(0)));
    assert_eq!(sub.hi, BigRational::new(BigInt::from(1), BigInt::from(2)));

    // Multiplication: [1/2 * 1/4, 3/4 * 1/2] = [1/8, 3/8]
    let mul = &i1 * &i2;
    assert_eq!(mul.lo, BigRational::new(BigInt::from(1), BigInt::from(8)));
    assert_eq!(mul.hi, BigRational::new(BigInt::from(3), BigInt::from(8)));

    // Division: [1/2 / (1/2), 3/4 / (1/4)] = [1, 3]
    let div = i1.checked_div(&i2).unwrap();
    assert_eq!(div.lo, BigRational::from_integer(BigInt::from(1)));
    assert_eq!(div.hi, BigRational::from_integer(BigInt::from(3)));
}

#[test]
fn test_division_by_zero_fails() {
    let i1 = RationalInterval::from_integers(1, 2).unwrap();
    let i_zero = RationalInterval::from_integers(-1, 1).unwrap();
    let res = i1.checked_div(&i_zero);
    assert!(matches!(res, Err(IntervalError::DivisionByZero { .. })));
}

#[test]
fn test_interval_squaring() {
    // Strictly positive interval [2, 3] -> [4, 9]
    let i_pos = RationalInterval::from_integers(2, 3).unwrap();
    let sq_pos = i_pos.sqr();
    assert_eq!(sq_pos.lo, BigRational::from_integer(BigInt::from(4)));
    assert_eq!(sq_pos.hi, BigRational::from_integer(BigInt::from(9)));

    // Interval containing zero [-2, 3] -> [0, 9]
    let i_zero = RationalInterval::from_integers(-2, 3).unwrap();
    let sq_zero = i_zero.sqr();
    assert_eq!(sq_zero.lo, BigRational::from_integer(BigInt::from(0)));
    assert_eq!(sq_zero.hi, BigRational::from_integer(BigInt::from(9)));

    // Strictly negative interval [-4, -2] -> [4, 16]
    let i_neg = RationalInterval::from_integers(-4, -2).unwrap();
    let sq_neg = i_neg.sqr();
    assert_eq!(sq_neg.lo, BigRational::from_integer(BigInt::from(4)));
    assert_eq!(sq_neg.hi, BigRational::from_integer(BigInt::from(16)));
}

#[test]
fn test_predicates() {
    let i_pos = RationalInterval::from_integers(1, 5).unwrap();
    assert!(i_pos.is_strictly_positive());
    assert!(!i_pos.contains_zero());
    assert!(!i_pos.is_strictly_negative());

    let i_neg = RationalInterval::from_integers(-5, -1).unwrap();
    assert!(i_neg.is_strictly_negative());
    assert!(!i_neg.contains_zero());
    assert!(!i_neg.is_strictly_positive());

    let i_zero = RationalInterval::from_integers(-1, 1).unwrap();
    assert!(i_zero.contains_zero());
    assert!(!i_zero.is_strictly_positive());
    assert!(!i_zero.is_strictly_negative());
}
