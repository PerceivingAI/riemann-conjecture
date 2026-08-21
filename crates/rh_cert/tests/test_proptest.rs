//! Property-based testing with `proptest` for interval arithmetic invariants and matrix decomposition.

use num_bigint::BigInt;
use num_rational::BigRational;
use proptest::prelude::*;
use rh_cert::interval::RationalInterval;
use rh_cert::ldl::RationalIntervalMatrix;

prop_compose! {
    fn arb_rational()(num in -10000i64..10000i64, den in 1i64..10000i64) -> BigRational {
        BigRational::new(BigInt::from(num), BigInt::from(den))
    }
}

prop_compose! {
    fn arb_interval()(r1 in arb_rational(), r2 in arb_rational()) -> (RationalInterval, BigRational) {
        let (lo, hi) = if r1 <= r2 { (r1, r2) } else { (r2, r1) };
        let point = (&lo + &hi) / BigRational::from_integer(BigInt::from(2));
        (RationalInterval::new(lo, hi).unwrap(), point)
    }
}

proptest! {
    #[test]
    fn prop_interval_addition_inclusion(
        (i1, p1) in arb_interval(),
        (i2, p2) in arb_interval(),
    ) {
        let sum_interval = &i1 + &i2;
        let sum_point = &p1 + &p2;
        prop_assert!(sum_interval.contains(&sum_point));
    }

    #[test]
    fn prop_interval_subtraction_inclusion(
        (i1, p1) in arb_interval(),
        (i2, p2) in arb_interval(),
    ) {
        let sub_interval = &i1 - &i2;
        let sub_point = &p1 - &p2;
        prop_assert!(sub_interval.contains(&sub_point));
    }

    #[test]
    fn prop_interval_multiplication_inclusion(
        (i1, p1) in arb_interval(),
        (i2, p2) in arb_interval(),
    ) {
        let mul_interval = &i1 * &i2;
        let mul_point = &p1 * &p2;
        prop_assert!(mul_interval.contains(&mul_point));
    }

    #[test]
    fn prop_interval_squaring_inclusion(
        (i, p) in arb_interval(),
    ) {
        let sqr_interval = i.sqr();
        let sqr_point = &p * &p;
        prop_assert!(sqr_interval.contains(&sqr_point));
    }

    #[test]
    fn prop_interval_division_inclusion(
        (i1, p1) in arb_interval(),
        num in 1i64..1000i64,
        den in 1i64..1000i64,
        extra in 0i64..500i64,
    ) {
        // Construct strictly positive divisor interval
        let lo = BigRational::new(BigInt::from(num), BigInt::from(den));
        let hi = &lo + BigRational::new(BigInt::from(extra), BigInt::from(den));
        let i2 = RationalInterval::new(lo, hi).unwrap();
        let p2 = i2.midpoint();

        let div_interval = i1.checked_div(&i2).unwrap();
        let div_point = &p1 / &p2;
        prop_assert!(div_interval.contains(&div_point));
    }

    #[test]
    fn prop_diagonally_dominant_matrices_are_positive_definite(
        a in 10i64..100i64,
        b in -5i64..5i64,
        c in -5i64..5i64,
        d in 10i64..100i64,
        e in -5i64..5i64,
        f in 10i64..100i64,
    ) {
        // Construct 3x3 diagonally dominant symmetric matrix:
        // row 0: [a + |b| + |c| + 1, b, c]
        // row 1: [b, d + |b| + |e| + 1, e]
        // row 2: [c, e, f + |c| + |e| + 1]
        let a_diag = a.abs() + b.abs() + c.abs() + 1;
        let d_diag = d.abs() + b.abs() + e.abs() + 1;
        let f_diag = f.abs() + c.abs() + e.abs() + 1;

        let rows = vec![
            vec![
                RationalInterval::from_integer(a_diag),
                RationalInterval::from_integer(b),
                RationalInterval::from_integer(c),
            ],
            vec![
                RationalInterval::from_integer(b),
                RationalInterval::from_integer(d_diag),
                RationalInterval::from_integer(e),
            ],
            vec![
                RationalInterval::from_integer(c),
                RationalInterval::from_integer(e),
                RationalInterval::from_integer(f_diag),
            ],
        ];

        let mat = RationalIntervalMatrix::new(3, rows).unwrap();
        let report = mat.verify_positivity();
        prop_assert!(report.is_positive_definite);
        prop_assert!(report.is_symmetric);
    }
}
