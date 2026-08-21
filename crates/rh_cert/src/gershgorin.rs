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

/// Compute `C A C^T` exactly as a rational interval matrix.
pub fn exact_interval_congruence(
    matrix: &RationalIntervalMatrix,
    witness: &[Vec<BigRational>],
) -> Result<RationalIntervalMatrix, GershgorinError> {
    let n = matrix.dim;
    validate_witness(witness, n)?;

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

    // Dimensions are constructed internally and therefore cannot fail.
    Ok(RationalIntervalMatrix::new(n, rows).expect("internal congruence dimensions are square"))
}

/// Verify strict positive Gershgorin lower bounds after exact congruence.
pub fn verify_congruence_gershgorin(
    matrix: &RationalIntervalMatrix,
    witness: &[Vec<BigRational>],
) -> Result<GershgorinBlockReport, GershgorinError> {
    validate_witness(witness, matrix.dim)?;
    let congruent = exact_interval_congruence(matrix, witness)?;

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
