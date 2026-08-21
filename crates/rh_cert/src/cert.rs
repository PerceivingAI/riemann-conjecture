//! Parser and validator for `rh-weil-certificate-v1` format JSON certificates.

use std::fs;
use std::path::Path;

use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::interval::{IntervalError, RationalInterval};
use crate::ldl::{LdlError, LdlVerificationReport, RationalIntervalMatrix};

pub const EXPECTED_FORMAT_V1: &str = "rh-weil-certificate-v1";

#[derive(Debug, Error)]
pub enum CertificateError {
    #[error("unsupported certificate format: '{0}', expected '{EXPECTED_FORMAT_V1}'")]
    UnsupportedFormat(String),

    #[error("JSON deserialization error: {0}")]
    Json(#[from] serde_json::Error),

    #[error("IO error reading certificate: {0}")]
    Io(#[from] std::io::Error),

    #[error("dimension mismatch: header dimension {header_dim} != matrix dimension {matrix_dim}")]
    DimensionMismatch {
        header_dim: usize,
        matrix_dim: usize,
    },

    #[error("entry count mismatch: expected {expected} entries, found {found}")]
    EntryCountMismatch { expected: usize, found: usize },

    #[error("missing matrix entry for position ({row}, {col})")]
    MissingEntry { row: usize, col: usize },

    #[error("interval error in certificate: {0}")]
    Interval(#[from] IntervalError),

    #[error("LDL error in certificate: {0}")]
    Ldl(#[from] LdlError),
}

/// In-memory representation of a `rh-weil-certificate-v1` JSON file.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CertificateJson {
    pub format: String,
    pub claim: String,
    #[serde(rename = "support_T")]
    pub support_t: SupportTJson,
    pub basis: BasisJson,
    pub parity_sector: String,
    pub dimension: usize,
    pub constants: serde_json::Value,
    pub matrix: MatrixJson,
    pub tail_bound: serde_json::Value,
    #[serde(default)]
    pub generator_metadata: serde_json::Value,
    #[serde(default)]
    pub internal_ldl_verification: Option<serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SupportTJson {
    pub num: i64,
    pub den: i64,
    pub frac: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BasisJson {
    pub r#type: String,
    pub dimension: usize,
    pub domain: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MatrixJson {
    pub dimension: usize,
    pub is_symmetric: bool,
    pub entries: Vec<MatrixEntryJson>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MatrixEntryJson {
    pub row: usize,
    pub col: usize,
    pub lo_num: String,
    pub lo_den: String,
    pub hi_num: String,
    pub hi_den: String,
}

/// Final outcome of the independent certificate verification.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerificationOutcome {
    pub passed: bool,
    pub claim: String,
    pub format: String,
    pub dimension: usize,
    #[serde(rename = "support_T")]
    pub support_t: String,
    pub ldl_report: LdlVerificationReport,
    pub notes: Vec<String>,
}

impl CertificateJson {
    /// Load a certificate from a file path.
    pub fn from_file<P: AsRef<Path>>(path: P) -> Result<Self, CertificateError> {
        let content = fs::read_to_string(path)?;
        Self::from_json_str(&content)
    }

    /// Parse a certificate from a JSON string.
    pub fn from_json_str(json_str: &str) -> Result<Self, CertificateError> {
        let cert: Self = serde_json::from_str(json_str)?;
        cert.validate_schema()?;
        Ok(cert)
    }

    /// Validate structural invariants of the certificate format.
    pub fn validate_schema(&self) -> Result<(), CertificateError> {
        if self.format != EXPECTED_FORMAT_V1 {
            return Err(CertificateError::UnsupportedFormat(self.format.clone()));
        }
        if self.dimension != self.matrix.dimension {
            return Err(CertificateError::DimensionMismatch {
                header_dim: self.dimension,
                matrix_dim: self.matrix.dimension,
            });
        }
        let expected_count = self.dimension * self.dimension;
        if self.matrix.entries.len() != expected_count {
            return Err(CertificateError::EntryCountMismatch {
                expected: expected_count,
                found: self.matrix.entries.len(),
            });
        }
        Ok(())
    }

    /// Extract the verified `RationalIntervalMatrix` from serialized entries.
    pub fn extract_matrix(&self) -> Result<RationalIntervalMatrix, CertificateError> {
        let n = self.dimension;
        let mut grid: Vec<Vec<Option<RationalInterval>>> = vec![vec![None; n]; n];

        for entry in &self.matrix.entries {
            if entry.row >= n || entry.col >= n {
                return Err(CertificateError::DimensionMismatch {
                    header_dim: n,
                    matrix_dim: std::cmp::max(entry.row, entry.col) + 1,
                });
            }
            let interval = RationalInterval::from_fraction_strings(
                &entry.lo_num,
                &entry.lo_den,
                &entry.hi_num,
                &entry.hi_den,
            )?;
            grid[entry.row][entry.col] = Some(interval);
        }

        let mut rows = Vec::with_capacity(n);
        for (i, grid_row) in grid.iter_mut().enumerate() {
            let mut row = Vec::with_capacity(n);
            for (j, cell) in grid_row.iter_mut().enumerate() {
                match cell.take() {
                    Some(val) => row.push(val),
                    None => return Err(CertificateError::MissingEntry { row: i, col: j }),
                }
            }
            rows.push(row);
        }

        let matrix = RationalIntervalMatrix::new(n, rows)?;
        Ok(matrix)
    }

    /// Independently verify the certificate using zero-float interval LDL^T decomposition.
    pub fn verify(&self) -> Result<VerificationOutcome, CertificateError> {
        let matrix = self.extract_matrix()?;
        let report = matrix.verify_positivity();

        let passed = report.is_positive_definite && report.is_symmetric;
        let mut notes = Vec::new();

        if !report.is_symmetric {
            notes.push("FAILURE: Matrix entries violate exact symmetry".to_string());
        }
        if !report.is_positive_definite {
            notes.push("FAILURE: LDL^T diagonal intervals fail strict positivity condition (min lo <= 0)".to_string());
        }
        if passed {
            notes.push(format!(
                "PASS: Exact rational LDL^T verified positive definite with min diagonal lower bound = {}",
                report.min_diagonal_lower_bound
            ));
        }

        Ok(VerificationOutcome {
            passed,
            claim: self.claim.clone(),
            format: self.format.clone(),
            dimension: self.dimension,
            support_t: self.support_t.frac.clone(),
            ldl_report: report,
            notes,
        })
    }
}
