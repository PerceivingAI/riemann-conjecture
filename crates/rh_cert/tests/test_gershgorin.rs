//! Regression tests for exact rational congruence/Gershgorin verification.

use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::Zero;
use rh_cert::gershgorin::exact_interval_congruence;
use rh_cert::interval::RationalInterval;
use rh_cert::ldl::RationalIntervalMatrix;

fn q(num: i64, den: i64) -> BigRational {
    BigRational::new(BigInt::from(num), BigInt::from(den))
}

fn naive_congruence(
    matrix: &RationalIntervalMatrix,
    witness: &[Vec<BigRational>],
) -> RationalIntervalMatrix {
    let n = matrix.dim;
    let mut left = vec![vec![RationalInterval::zero(); n]; n];
    for (i, left_row) in left.iter_mut().enumerate() {
        for (j, cell) in left_row.iter_mut().enumerate() {
            let mut total = RationalInterval::zero();
            for (k, witness_value) in witness[i].iter().enumerate() {
                let coefficient = RationalInterval::point(witness_value.clone());
                total = total + (&coefficient * &matrix.rows[k][j]);
            }
            *cell = total;
        }
    }

    let mut rows = vec![vec![RationalInterval::zero(); n]; n];
    for (i, row) in rows.iter_mut().enumerate() {
        for (j, cell) in row.iter_mut().enumerate() {
            let mut total = RationalInterval::zero();
            for (k, left_value) in left[i].iter().enumerate() {
                let coefficient = RationalInterval::point(witness[j][k].clone());
                total = total + (left_value * &coefficient);
            }
            *cell = total;
        }
    }
    RationalIntervalMatrix::new(n, rows).unwrap()
}

#[test]
fn optimized_generic_congruence_preserves_nonsymmetric_inputs() {
    let matrix = RationalIntervalMatrix::new(
        2,
        vec![
            vec![
                RationalInterval::from_integer(2),
                RationalInterval::from_integer(3),
            ],
            vec![
                RationalInterval::from_integer(-1),
                RationalInterval::from_integer(5),
            ],
        ],
    )
    .unwrap();
    let witness = vec![vec![q(1, 1), q(0, 1)], vec![q(2, 3), q(4, 5)]];

    let expected = naive_congruence(&matrix, &witness);
    let actual = exact_interval_congruence(&matrix, &witness).unwrap();
    assert_eq!(actual, expected);
    assert_ne!(actual.rows[0][1], actual.rows[1][0]);
}

#[test]
fn optimized_congruence_matches_naive_dense_reference_exactly() {
    let matrix = RationalIntervalMatrix::new(
        3,
        vec![
            vec![
                RationalInterval::new(q(2, 1), q(5, 2)).unwrap(),
                RationalInterval::new(q(-1, 3), q(1, 4)).unwrap(),
                RationalInterval::new(q(2, 5), q(3, 5)).unwrap(),
            ],
            vec![
                RationalInterval::new(q(-1, 3), q(1, 4)).unwrap(),
                RationalInterval::new(q(7, 4), q(2, 1)).unwrap(),
                RationalInterval::new(q(-2, 7), q(1, 6)).unwrap(),
            ],
            vec![
                RationalInterval::new(q(2, 5), q(3, 5)).unwrap(),
                RationalInterval::new(q(-2, 7), q(1, 6)).unwrap(),
                RationalInterval::new(q(11, 6), q(13, 6)).unwrap(),
            ],
        ],
    )
    .unwrap();
    let witness = vec![
        vec![q(1, 1), q(0, 1), q(0, 1)],
        vec![q(-2, 3), q(5, 4), q(0, 1)],
        vec![q(1, 5), q(-7, 6), q(9, 8)],
    ];

    let expected = naive_congruence(&matrix, &witness);
    let actual = exact_interval_congruence(&matrix, &witness).unwrap();
    assert_eq!(actual, expected);
}
