//! Unit tests for exact rational matrix linear algebra and LDL^T verification.

use num_bigint::BigInt;
use num_rational::BigRational;
use rh_cert::interval::RationalInterval;
use rh_cert::ldl::RationalIntervalMatrix;

#[test]
fn test_identity_matrix() {
    let eye = RationalIntervalMatrix::identity(3);
    assert!(eye.is_symmetric());
    let report = eye.verify_positivity();
    assert!(report.is_positive_definite);
    assert_eq!(report.min_diagonal_lower_bound, BigRational::from_integer(BigInt::from(1)));
    assert_eq!(report.diagonal_intervals.len(), 3);
}

#[test]
fn test_2x2_positive_definite_matrix() {
    // [[4, 1], [1, 3]]
    // D0 = 4, L10 = 1/4, D1 = 3 - 1/4 = 11/4 > 0
    let rows = vec![
        vec![
            RationalInterval::from_integer(4),
            RationalInterval::from_integer(1),
        ],
        vec![
            RationalInterval::from_integer(1),
            RationalInterval::from_integer(3),
        ],
    ];
    let mat = RationalIntervalMatrix::new(2, rows).unwrap();
    assert!(mat.is_symmetric());
    let (l, d, is_pos) = mat.exact_ldl().unwrap();
    assert!(is_pos);
    assert_eq!(d[0].lo, BigRational::from_integer(BigInt::from(4)));
    assert_eq!(d[1].lo, BigRational::new(BigInt::from(11), BigInt::from(4)));
    assert_eq!(l[1][0].lo, BigRational::new(BigInt::from(1), BigInt::from(4)));
}

#[test]
fn test_2x2_indefinite_matrix() {
    // [[1, 2], [2, 1]] -> D0 = 1, L10 = 2, D1 = 1 - 4 = -3 < 0
    let rows = vec![
        vec![
            RationalInterval::from_integer(1),
            RationalInterval::from_integer(2),
        ],
        vec![
            RationalInterval::from_integer(2),
            RationalInterval::from_integer(1),
        ],
    ];
    let mat = RationalIntervalMatrix::new(2, rows).unwrap();
    let report = mat.verify_positivity();
    assert!(!report.is_positive_definite);
    assert!(report.failure_reason.is_some());
}

#[test]
fn test_non_symmetric_matrix_rejection() {
    let rows = vec![
        vec![
            RationalInterval::from_integer(2),
            RationalInterval::from_integer(1),
        ],
        vec![
            RationalInterval::from_integer(3),
            RationalInterval::from_integer(2),
        ],
    ];
    let mat = RationalIntervalMatrix::new(2, rows).unwrap();
    assert!(!mat.is_symmetric());
    let report = mat.verify_positivity();
    assert!(!report.is_positive_definite);
    assert!(!report.is_symmetric);
}

#[test]
fn test_3x3_positive_definite_matrix() {
    // A = [[2, -1, 0], [-1, 2, -1], [0, -1, 2]] (tridiagonal 2, -1)
    // D0 = 2
    // L10 = -1/2, D1 = 2 - 1/2 = 3/2
    // L20 = 0, L21 = (-1 - 0) / (3/2) = -2/3, D2 = 2 - (-2/3)^2 * (3/2) = 2 - 2/3 = 4/3
    let rows = vec![
        vec![
            RationalInterval::from_integer(2),
            RationalInterval::from_integer(-1),
            RationalInterval::from_integer(0),
        ],
        vec![
            RationalInterval::from_integer(-1),
            RationalInterval::from_integer(2),
            RationalInterval::from_integer(-1),
        ],
        vec![
            RationalInterval::from_integer(0),
            RationalInterval::from_integer(-1),
            RationalInterval::from_integer(2),
        ],
    ];
    let mat = RationalIntervalMatrix::new(3, rows).unwrap();
    let report = mat.verify_positivity();
    assert!(report.is_positive_definite);
    assert_eq!(report.diagonal_intervals[0].lo, BigRational::from_integer(BigInt::from(2)));
    assert_eq!(report.diagonal_intervals[1].lo, BigRational::new(BigInt::from(3), BigInt::from(2)));
    assert_eq!(report.diagonal_intervals[2].lo, BigRational::new(BigInt::from(4), BigInt::from(3)));
}
