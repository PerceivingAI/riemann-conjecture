//! Exact rational interval matrix linear algebra and LDL^T positivity verifier.

use num_rational::BigRational;
use num_traits::Zero;
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::interval::{IntervalError, RationalInterval};

#[derive(Debug, Error, Clone, PartialEq, Eq)]
pub enum LdlError {
    #[error("matrix dimension mismatch: expected {expected}x{expected}, got {got_rows}x{got_cols}")]
    DimensionMismatch {
        expected: usize,
        got_rows: usize,
        got_cols: usize,
    },

    #[error("matrix is empty")]
    EmptyMatrix,

    #[error("interval error during matrix decomposition: {0}")]
    Interval(#[from] IntervalError),

    #[error("non-symmetric matrix: entry ({row}, {col}) != ({col}, {row})")]
    NonSymmetric { row: usize, col: usize },
}

/// An N x N square matrix of exact rational intervals.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct RationalIntervalMatrix {
    pub dim: usize,
    pub rows: Vec<Vec<RationalInterval>>,
}

/// Type alias for LDL^T decomposition result: `(L, D, is_positive_definite)`.
pub type LdlDecomposition = (Vec<Vec<RationalInterval>>, Vec<RationalInterval>, bool);

/// Report produced by LDL^T positive-definiteness verification.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct LdlVerificationReport {
    pub is_positive_definite: bool,
    pub dimension: usize,
    pub is_symmetric: bool,
    pub diagonal_intervals: Vec<RationalInterval>,
    pub min_diagonal_lower_bound: BigRational,
    pub failure_reason: Option<String>,
}

impl RationalIntervalMatrix {
    /// Create a new N x N matrix from rows.
    pub fn new(dim: usize, rows: Vec<Vec<RationalInterval>>) -> Result<Self, LdlError> {
        if dim == 0 {
            return Err(LdlError::EmptyMatrix);
        }
        if rows.len() != dim {
            return Err(LdlError::DimensionMismatch {
                expected: dim,
                got_rows: rows.len(),
                got_cols: if rows.is_empty() { 0 } else { rows[0].len() },
            });
        }
        for row in &rows {
            if row.len() != dim {
                return Err(LdlError::DimensionMismatch {
                    expected: dim,
                    got_rows: rows.len(),
                    got_cols: row.len(),
                });
            }
        }
        Ok(Self { dim, rows })
    }

    /// Construct an identity matrix of size N x N.
    pub fn identity(dim: usize) -> Self {
        let mut rows = Vec::with_capacity(dim);
        for i in 0..dim {
            let mut row = Vec::with_capacity(dim);
            for j in 0..dim {
                if i == j {
                    row.push(RationalInterval::from_integer(1));
                } else {
                    row.push(RationalInterval::from_integer(0));
                }
            }
            rows.push(row);
        }
        Self { dim, rows }
    }

    /// Construct a zero matrix of size N x N.
    pub fn zeros(dim: usize) -> Self {
        let rows = vec![vec![RationalInterval::from_integer(0); dim]; dim];
        Self { dim, rows }
    }

    /// Check if the matrix is exactly symmetric.
    pub fn is_symmetric(&self) -> bool {
        for i in 0..self.dim {
            for j in (i + 1)..self.dim {
                if self.rows[i][j] != self.rows[j][i] {
                    return false;
                }
            }
        }
        true
    }

    /// Perform exact interval LDL^T decomposition: `A = L * D * L^T`.
    ///
    /// Computes unit lower triangular matrix `L` and diagonal elements `D`.
    /// If at any step `D_j` is not strictly positive (`lo <= 0`), returns early with `is_positive_definite = false`.
    pub fn exact_ldl(&self) -> Result<LdlDecomposition, LdlError> {
        let n = self.dim;
        let mut l = vec![vec![RationalInterval::from_integer(0); n]; n];
        for (i, row) in l.iter_mut().enumerate() {
            row[i] = RationalInterval::from_integer(1);
        }
        let mut d = vec![RationalInterval::from_integer(0); n];

        for j in 0..n {
            // D_j = A_jj - sum_{k=0}^{j-1} L_jk^2 * D_k
            let mut sum_diag = RationalInterval::from_integer(0);
            for k in 0..j {
                let term = l[j][k].sqr() * &d[k];
                sum_diag = sum_diag + term;
            }

            let d_j = &self.rows[j][j] - sum_diag;
            d[j] = d_j.clone();

            if !d_j.is_strictly_positive() {
                return Ok((l, d, false));
            }

            // Compute L_ij for i > j:
            // L_ij = (A_ij - sum_{k=0}^{j-1} L_ik * L_jk * D_k) / D_j
            for i in (j + 1)..n {
                let mut sum_off = RationalInterval::from_integer(0);
                for k in 0..j {
                    let term = &l[i][k] * &l[j][k] * &d[k];
                    sum_off = sum_off + term;
                }

                let diff = &self.rows[i][j] - sum_off;
                let l_ij = diff.checked_div(&d_j)?;
                l[i][j] = l_ij;
            }
        }

        let is_pos_def = d.iter().all(|diag| diag.is_strictly_positive());
        Ok((l, d, is_pos_def))
    }

    /// Run full positive definiteness verification and return a detailed report.
    pub fn verify_positivity(&self) -> LdlVerificationReport {
        let symmetric = self.is_symmetric();
        if !symmetric {
            return LdlVerificationReport {
                is_positive_definite: false,
                dimension: self.dim,
                is_symmetric: false,
                diagonal_intervals: Vec::new(),
                min_diagonal_lower_bound: BigRational::zero(),
                failure_reason: Some("Matrix is not symmetric".to_string()),
            };
        }

        match self.exact_ldl() {
            Ok((_l, d, is_pos)) => {
                let min_lo = d
                    .iter()
                    .map(|interval| interval.lo.clone())
                    .min()
                    .unwrap_or_else(BigRational::zero);

                let reason = if is_pos {
                    None
                } else {
                    Some("One or more LDL^T diagonal intervals fail strict positivity (lo <= 0)".to_string())
                };

                LdlVerificationReport {
                    is_positive_definite: is_pos,
                    dimension: self.dim,
                    is_symmetric: true,
                    diagonal_intervals: d,
                    min_diagonal_lower_bound: min_lo,
                    failure_reason: reason,
                }
            }
            Err(err) => LdlVerificationReport {
                is_positive_definite: false,
                dimension: self.dim,
                is_symmetric: true,
                diagonal_intervals: Vec::new(),
                min_diagonal_lower_bound: BigRational::zero(),
                failure_reason: Some(format!("Decomposition error: {err}")),
            },
        }
    }
}
