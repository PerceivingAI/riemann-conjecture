//! Exact rational congruence and Gershgorin positivity certificates.
//!
//! A floating or heuristic process may propose a congruence witness, but the
//! witness is serialized as exact rationals. This module recomputes C A C^T
//! using exact rational interval arithmetic and proves positivity from strict
//! Gershgorin lower bounds. No floating-point operation is used.

use num_rational::BigRational;
use num_traits::{Signed, Zero};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::interval::RationalInterval;
use crate::ldl::RationalIntervalMatrix;

#[derive(Debug, Error, Clone, PartialEq, Eq)]
pub enum GershgorinError {
    #[error("witness dimension mismatch: expected {expected}, got {got}")]
    WitnessDimension { expected: usize, got: usize },

    #[error("witness must be lower triangular; entry ({row}, {col}) is nonzero")]
    WitnessNotLowerTriangular { row: usize, col: usize },

    #[error("witness diagonal entry {index} is zero")]
    SingularWitness { index: usize },
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct GershgorinBlockReport {
    pub dimension: usize,
    pub witness_lower_triangular: bool,
    pub witness_invertible: bool,
    pub min_margin: String,
    pub is_positive_definite: bool,
}

fn sup_abs(interval: &RationalInterval) -> BigRational {
    interval.lo.abs().max(interval.hi.abs())
}

fn validate_witness(witness: &[Vec<BigRational>], dimension: usize) -> Result<(), GershgorinError> {
    if witness.len() != dimension || witness.iter().any(|row| row.len() != dimension) {
        return Err(GershgorinError::WitnessDimension {
            expected: dimension,
            got: witness.len(),
        });
    }
    for (row, values) in witness.iter().enumerate() {
        for (col, value) in values.iter().enumerate() {
            if col > row && !value.is_zero() {
                return Err(GershgorinError::WitnessNotLowerTriangular { row, col });
            }
        }
        if values[row].is_zero() {
            return Err(GershgorinError::SingularWitness { index: row });
        }
    }
    Ok(())
}

fn left_congruence_product(
    matrix: &RationalIntervalMatrix,
    witness: &[Vec<BigRational>],
) -> Vec<Vec<RationalInterval>> {
    let n = matrix.dim;
    let mut left = vec![vec![RationalInterval::zero(); n]; n];
    for (i, left_row) in left.iter_mut().enumerate() {
        for (j, cell) in left_row.iter_mut().enumerate() {
            let mut total = RationalInterval::zero();
            for (k, coefficient) in witness[i].iter().take(i + 1).enumerate() {
                if coefficient.is_zero() {
                    continue;
                }
                total = total + matrix.rows[k][j].scale_by(coefficient);
            }
            *cell = total;
        }
    }
    left
}

fn exact_interval_congruence_validated(
    matrix: &RationalIntervalMatrix,
    witness: &[Vec<BigRational>],
) -> RationalIntervalMatrix {
    let n = matrix.dim;

    // First form L = C A. The witness is already validated lower triangular,
    // so row i has support only in columns 0..=i of C. Scaling an interval by
    // an exact rational is cheaper than constructing a point interval and
    // invoking generic interval multiplication.
    let left = left_congruence_product(matrix, witness);

    // Preserve the public helper's semantics for arbitrary square A: form the
    // complete L C^T product, but exploit the lower-triangular support of C.
    let mut rows = vec![vec![RationalInterval::zero(); n]; n];
    for (i, row) in rows.iter_mut().enumerate() {
        for (j, cell) in row.iter_mut().enumerate() {
            let mut total = RationalInterval::zero();
            for (k, coefficient) in witness[j].iter().take(j + 1).enumerate() {
                if coefficient.is_zero() {
                    continue;
                }
                total = total + left[i][k].scale_by(coefficient);
            }
            *cell = total;
        }
    }

    RationalIntervalMatrix::new(n, rows).expect("internal congruence dimensions are square")
}

fn exact_symmetric_interval_congruence_validated(
    matrix: &RationalIntervalMatrix,
    witness: &[Vec<BigRational>],
) -> RationalIntervalMatrix {
    let n = matrix.dim;
    let left = left_congruence_product(matrix, witness);

    // For symmetric A, A C^T = (C A)^T. Therefore for i <= j we can form
    // B_ij from witness row i and left row j, making the second inner sum only
    // 0..=i. Compute one triangle and mirror it exactly.
    let mut rows = vec![vec![RationalInterval::zero(); n]; n];
    for i in 0..n {
        for j in i..n {
            let mut total = RationalInterval::zero();
            for (k, coefficient) in witness[i].iter().take(i + 1).enumerate() {
                if coefficient.is_zero() {
                    continue;
                }
                total = total + left[j][k].scale_by(coefficient);
            }
            rows[i][j] = total.clone();
            rows[j][i] = total;
        }
    }

    RationalIntervalMatrix::new(n, rows).expect("internal congruence dimensions are square")
}

/// Compute `C A C^T` exactly as a rational interval matrix.
pub fn exact_interval_congruence(
    matrix: &RationalIntervalMatrix,
    witness: &[Vec<BigRational>],
) -> Result<RationalIntervalMatrix, GershgorinError> {
    validate_witness(witness, matrix.dim)?;
    Ok(exact_interval_congruence_validated(matrix, witness))
}

/// Verify strict positive Gershgorin lower bounds after exact congruence.
pub fn verify_congruence_gershgorin(
    matrix: &RationalIntervalMatrix,
    witness: &[Vec<BigRational>],
) -> Result<GershgorinBlockReport, GershgorinError> {
    validate_witness(witness, matrix.dim)?;
    let congruent = if matrix.is_symmetric() {
        exact_symmetric_interval_congruence_validated(matrix, witness)
    } else {
        exact_interval_congruence_validated(matrix, witness)
    };

    let mut min_margin: Option<BigRational> = None;
    let mut all_positive = true;
    for i in 0..congruent.dim {
        let mut radius = BigRational::zero();
        for j in 0..congruent.dim {
            if i != j {
                radius += sup_abs(&congruent.rows[i][j]);
            }
        }
        let margin = &congruent.rows[i][i].lo - radius;
        if margin <= BigRational::zero() {
            all_positive = false;
        }
        min_margin = Some(match min_margin {
            Some(current) => current.min(margin),
            None => margin,
        });
    }

    Ok(GershgorinBlockReport {
        dimension: matrix.dim,
        witness_lower_triangular: true,
        witness_invertible: true,
        min_margin: min_margin.unwrap_or_else(BigRational::zero).to_string(),
        is_positive_definite: all_positive,
    })
}
