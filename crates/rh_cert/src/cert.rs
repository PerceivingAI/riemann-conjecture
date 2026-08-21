//! Strict parser and whole-certificate verifier for `rh-weil-certificate-v1`.

use std::fs;
use std::path::Path;

use num_rational::BigRational;
use num_traits::Zero;
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::interval::{parse_canonical_rational, IntervalError, RationalInterval};
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

    #[error("certificate validation failed at {field}: {message}")]
    Validation { field: String, message: String },

    #[error("dimension mismatch: header dimension {header_dim} != matrix dimension {matrix_dim}")]
    DimensionMismatch {
        header_dim: usize,
        matrix_dim: usize,
    },

    #[error("entry count mismatch: expected {expected} entries, found {found}")]
    EntryCountMismatch { expected: usize, found: usize },

    #[error("matrix coordinate ({row}, {col}) is outside dimension {dimension}")]
    CoordinateOutOfRange {
        row: usize,
        col: usize,
        dimension: usize,
    },

    #[error("duplicate matrix entry for position ({row}, {col})")]
    DuplicateEntry { row: usize, col: usize },

    #[error("missing matrix entry for position ({row}, {col})")]
    MissingEntry { row: usize, col: usize },

    #[error("matrix is not exactly symmetric at ({row}, {col})")]
    NonSymmetric { row: usize, col: usize },

    #[error("interval error in certificate: {0}")]
    Interval(#[from] IntervalError),

    #[error("LDL error in certificate: {0}")]
    Ldl(#[from] LdlError),
}

fn validation_error(field: &str, message: impl Into<String>) -> CertificateError {
    CertificateError::Validation {
        field: field.to_string(),
        message: message.into(),
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "snake_case")]
enum ClaimProfile {
    SyntheticMatrix,
    DigammaFiniteBlock,
}

impl ClaimProfile {
    fn as_str(self) -> &'static str {
        match self {
            Self::SyntheticMatrix => "synthetic_matrix",
            Self::DigammaFiniteBlock => "digamma_finite_block",
        }
    }

    fn verified_scope(self) -> &'static str {
        match self {
            Self::SyntheticMatrix => "synthetic_matrix",
            Self::DigammaFiniteBlock => "finite_basis_full_digamma_series",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "snake_case")]
enum BasisType {
    Legendre,
    Chebyshev,
    Monomial,
}

impl BasisType {
    fn as_str(self) -> &'static str {
        match self {
            Self::Legendre => "legendre",
            Self::Chebyshev => "chebyshev",
            Self::Monomial => "monomial",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
enum BasisDomain {
    #[serde(rename = "[-T, T]")]
    SupportInterval,
    #[serde(rename = "[-1, 1]")]
    ScaledUnitInterval,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "snake_case")]
enum ParitySector {
    Even,
    Odd,
    Both,
}

impl ParitySector {
    fn as_str(self) -> &'static str {
        match self {
            Self::Even => "even",
            Self::Odd => "odd",
            Self::Both => "both",
        }
    }
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct ExactRationalJson {
    num: String,
    den: String,
}

impl ExactRationalJson {
    fn parse(&self, field: &str) -> Result<BigRational, CertificateError> {
        parse_canonical_rational(&self.num, &self.den, field).map_err(CertificateError::from)
    }
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct RationalIntervalJson {
    lo_num: String,
    lo_den: String,
    hi_num: String,
    hi_den: String,
}

impl RationalIntervalJson {
    fn parse(&self) -> Result<RationalInterval, CertificateError> {
        RationalInterval::from_fraction_strings(
            &self.lo_num,
            &self.lo_den,
            &self.hi_num,
            &self.hi_den,
        )
        .map_err(CertificateError::from)
    }
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct SupportTJson {
    num: String,
    den: String,
    frac: String,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct BasisJson {
    r#type: BasisType,
    dimension: usize,
    domain: BasisDomain,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct ConstantsJson {
    log2: Option<RationalIntervalJson>,
    sqrt2: Option<RationalIntervalJson>,
    pi: Option<RationalIntervalJson>,
    euler_gamma: Option<RationalIntervalJson>,
    tau: Option<RationalIntervalJson>,
    c2: Option<RationalIntervalJson>,
    #[serde(rename = "c_T")]
    c_t: Option<RationalIntervalJson>,
    m0_digamma: Option<RationalIntervalJson>,
}

impl ConstantsJson {
    fn present_count(&self) -> usize {
        [
            self.log2.is_some(),
            self.sqrt2.is_some(),
            self.pi.is_some(),
            self.euler_gamma.is_some(),
            self.tau.is_some(),
            self.c2.is_some(),
            self.c_t.is_some(),
            self.m0_digamma.is_some(),
        ]
        .into_iter()
        .filter(|present| *present)
        .count()
    }

    fn validate_intervals(&self) -> Result<(), CertificateError> {
        for interval in [
            self.log2.as_ref(),
            self.sqrt2.as_ref(),
            self.pi.as_ref(),
            self.euler_gamma.as_ref(),
            self.tau.as_ref(),
            self.c2.as_ref(),
            self.c_t.as_ref(),
            self.m0_digamma.as_ref(),
        ]
        .into_iter()
        .flatten()
        {
            interval.parse()?;
        }
        Ok(())
    }
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct MatrixJson {
    dimension: usize,
    entries: Vec<MatrixEntryJson>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct MatrixEntryJson {
    row: usize,
    col: usize,
    lo_num: String,
    lo_den: String,
    hi_num: String,
    hi_den: String,
}

impl MatrixEntryJson {
    fn parse_interval(&self) -> Result<RationalInterval, CertificateError> {
        RationalInterval::from_fraction_strings(
            &self.lo_num,
            &self.lo_den,
            &self.hi_num,
            &self.hi_den,
        )
        .map_err(CertificateError::from)
    }
}

#[derive(Debug, Clone, Deserialize)]
#[serde(tag = "type", deny_unknown_fields)]
enum TailBoundJson {
    #[serde(rename = "exact_scalar_identity")]
    ExactScalarIdentity { lambda: ExactRationalJson },
    #[serde(rename = "nonnegative_digamma_remainder")]
    NonnegativeDigammaRemainder {
        k_max: usize,
        first_omitted_k: usize,
    },
}

impl TailBoundJson {
    fn rule_name(&self) -> &'static str {
        match self {
            Self::ExactScalarIdentity { .. } => "exact_scalar_identity",
            Self::NonnegativeDigammaRemainder { .. } => "nonnegative_digamma_remainder",
        }
    }
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct GeneratorMetadataJson {
    generator: String,
    script: String,
    version: String,
    git_commit: String,
    git_dirty: bool,
    flint_version: String,
    python_flint_version: String,
    prec_bits: usize,
    timestamp_utc: String,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct CertificateDocument {
    format: String,
    claim: String,
    claim_profile: ClaimProfile,
    #[serde(rename = "support_T")]
    support_t: SupportTJson,
    basis: BasisJson,
    parity_sector: ParitySector,
    dimension: usize,
    constants: ConstantsJson,
    matrix: MatrixJson,
    tail_bound: TailBoundJson,
    generator_metadata: GeneratorMetadataJson,
}

/// Parsed certificate with all semantic checks and exact rational conversions completed.
#[derive(Debug, Clone)]
pub struct CertificateJson {
    document: CertificateDocument,
    matrix: RationalIntervalMatrix,
    tail_lower_bound: BigRational,
}

/// Final outcome of whole-certificate verification.
#[derive(Debug, Clone, Serialize)]
pub struct VerificationOutcome {
    pub passed: bool,
    pub claim: String,
    pub format: String,
    pub claim_profile: String,
    pub verified_scope: String,
    pub basis_type: String,
    pub parity_sector: String,
    pub dimension: usize,
    #[serde(rename = "support_T")]
    pub support_t: String,
    pub tail_rule: String,
    pub tail_lower_bound: String,
    pub ldl_report: LdlVerificationReport,
    pub notes: Vec<String>,
}

fn canonical_fraction(value: &BigRational) -> String {
    format!("{}/{}", value.numer(), value.denom())
}

fn valid_git_commit(value: &str) -> bool {
    value.len() == 40
        && value
            .bytes()
            .all(|byte| byte.is_ascii_hexdigit() && !byte.is_ascii_uppercase())
}

fn valid_utc_timestamp(value: &str) -> bool {
    if !value.ends_with('Z') || value.len() < 20 {
        return false;
    }
    let bytes = value.as_bytes();
    if bytes.get(4) != Some(&b'-')
        || bytes.get(7) != Some(&b'-')
        || bytes.get(10) != Some(&b'T')
        || bytes.get(13) != Some(&b':')
        || bytes.get(16) != Some(&b':')
    {
        return false;
    }
    let numeric = |start: usize, end: usize| {
        value
            .get(start..end)
            .and_then(|part| part.parse::<u32>().ok())
    };
    let Some(year) = numeric(0, 4) else {
        return false;
    };
    let Some(month) = numeric(5, 7) else {
        return false;
    };
    let Some(day) = numeric(8, 10) else {
        return false;
    };
    let Some(hour) = numeric(11, 13) else {
        return false;
    };
    let Some(minute) = numeric(14, 16) else {
        return false;
    };
    let Some(second) = numeric(17, 19) else {
        return false;
    };
    let leap_year =
        year.is_multiple_of(4) && (!year.is_multiple_of(100) || year.is_multiple_of(400));
    let days_in_month = match month {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 if leap_year => 29,
        2 => 28,
        _ => return false,
    };
    if day == 0 || day > days_in_month || hour > 23 || minute > 59 || second > 59 {
        return false;
    }
    let suffix = &value[19..value.len() - 1];
    suffix.is_empty()
        || (suffix.starts_with('.')
            && suffix.len() > 1
            && suffix[1..].bytes().all(|byte| byte.is_ascii_digit()))
}

impl CertificateDocument {
    fn validate_metadata(&self) -> Result<(), CertificateError> {
        let metadata = &self.generator_metadata;
        for (field, value) in [
            (
                "$.generator_metadata.generator",
                metadata.generator.as_str(),
            ),
            ("$.generator_metadata.script", metadata.script.as_str()),
            ("$.generator_metadata.version", metadata.version.as_str()),
            (
                "$.generator_metadata.flint_version",
                metadata.flint_version.as_str(),
            ),
            (
                "$.generator_metadata.python_flint_version",
                metadata.python_flint_version.as_str(),
            ),
        ] {
            if value.is_empty() {
                return Err(validation_error(field, "must not be empty"));
            }
        }
        if !valid_git_commit(&metadata.git_commit) {
            return Err(validation_error(
                "$.generator_metadata.git_commit",
                "must be a 40-character lowercase hexadecimal commit",
            ));
        }
        if metadata.prec_bits < 32 {
            return Err(validation_error(
                "$.generator_metadata.prec_bits",
                "must be at least 32",
            ));
        }
        if !valid_utc_timestamp(&metadata.timestamp_utc) {
            return Err(validation_error(
                "$.generator_metadata.timestamp_utc",
                "must be a UTC RFC 3339 timestamp ending in Z",
            ));
        }
        Ok(())
    }

    fn extract_matrix(&self) -> Result<RationalIntervalMatrix, CertificateError> {
        if self.dimension != self.matrix.dimension {
            return Err(CertificateError::DimensionMismatch {
                header_dim: self.dimension,
                matrix_dim: self.matrix.dimension,
            });
        }
        if self.basis.dimension != self.dimension {
            return Err(validation_error(
                "$.basis.dimension",
                "must equal the certificate dimension",
            ));
        }
        let expected = self
            .dimension
            .checked_mul(self.dimension)
            .ok_or_else(|| validation_error("$.dimension", "dimension squared overflows usize"))?;
        if self.matrix.entries.len() != expected {
            return Err(CertificateError::EntryCountMismatch {
                expected,
                found: self.matrix.entries.len(),
            });
        }

        let mut grid = vec![vec![None; self.dimension]; self.dimension];
        for entry in &self.matrix.entries {
            if entry.row >= self.dimension || entry.col >= self.dimension {
                return Err(CertificateError::CoordinateOutOfRange {
                    row: entry.row,
                    col: entry.col,
                    dimension: self.dimension,
                });
            }
            if grid[entry.row][entry.col].is_some() {
                return Err(CertificateError::DuplicateEntry {
                    row: entry.row,
                    col: entry.col,
                });
            }
            grid[entry.row][entry.col] = Some(entry.parse_interval()?);
        }

        let mut rows = Vec::with_capacity(self.dimension);
        for (row_index, grid_row) in grid.into_iter().enumerate() {
            let mut row = Vec::with_capacity(self.dimension);
            for (col_index, cell) in grid_row.into_iter().enumerate() {
                row.push(cell.ok_or(CertificateError::MissingEntry {
                    row: row_index,
                    col: col_index,
                })?);
            }
            rows.push(row);
        }
        let matrix = RationalIntervalMatrix::new(self.dimension, rows)?;
        for row in 0..self.dimension {
            for col in (row + 1)..self.dimension {
                if matrix.rows[row][col] != matrix.rows[col][row] {
                    return Err(CertificateError::NonSymmetric { row, col });
                }
            }
        }
        Ok(matrix)
    }

    fn validate_and_derive_tail(&self) -> Result<BigRational, CertificateError> {
        self.constants.validate_intervals()?;
        match (self.claim_profile, &self.tail_bound) {
            (ClaimProfile::SyntheticMatrix, TailBoundJson::ExactScalarIdentity { lambda }) => {
                if self.constants.present_count() != 0 {
                    return Err(validation_error(
                        "$.constants",
                        "must be empty for synthetic_matrix",
                    ));
                }
                lambda.parse("$.tail_bound.lambda")
            }
            (
                ClaimProfile::DigammaFiniteBlock,
                TailBoundJson::NonnegativeDigammaRemainder {
                    k_max,
                    first_omitted_k,
                },
            ) => {
                if self.constants.present_count() != 1 || self.constants.m0_digamma.is_none() {
                    return Err(validation_error(
                        "$.constants",
                        "must contain only m0_digamma for digamma_finite_block",
                    ));
                }
                if self.basis.domain != BasisDomain::SupportInterval {
                    return Err(validation_error(
                        "$.basis.domain",
                        "must be [-T, T] for digamma_finite_block",
                    ));
                }
                let expected = k_max.checked_add(1).ok_or_else(|| {
                    validation_error("$.tail_bound.k_max", "k_max + 1 overflows usize")
                })?;
                if *first_omitted_k != expected {
                    return Err(validation_error(
                        "$.tail_bound.first_omitted_k",
                        "must equal k_max + 1",
                    ));
                }
                Ok(BigRational::zero())
            }
            (ClaimProfile::SyntheticMatrix, _) => Err(validation_error(
                "$.tail_bound",
                "synthetic_matrix requires exact_scalar_identity",
            )),
            (ClaimProfile::DigammaFiniteBlock, _) => Err(validation_error(
                "$.tail_bound",
                "digamma_finite_block requires nonnegative_digamma_remainder",
            )),
        }
    }

    fn validate(self) -> Result<CertificateJson, CertificateError> {
        if self.format != EXPECTED_FORMAT_V1 {
            return Err(CertificateError::UnsupportedFormat(self.format.clone()));
        }
        if self.claim.is_empty() {
            return Err(validation_error("$.claim", "must not be empty"));
        }
        let support =
            parse_canonical_rational(&self.support_t.num, &self.support_t.den, "$.support_T")?;
        if support <= BigRational::zero() {
            return Err(validation_error("$.support_T", "must be strictly positive"));
        }
        if self.support_t.frac != canonical_fraction(&support) {
            return Err(validation_error(
                "$.support_T.frac",
                "must equal canonical num/den",
            ));
        }
        self.validate_metadata()?;
        let matrix = self.extract_matrix()?;
        let tail_lower_bound = self.validate_and_derive_tail()?;
        Ok(CertificateJson {
            document: self,
            matrix,
            tail_lower_bound,
        })
    }
}

impl CertificateJson {
    /// Load and fully validate a certificate from a file path.
    pub fn from_file<P: AsRef<Path>>(path: P) -> Result<Self, CertificateError> {
        let content = fs::read_to_string(path)?;
        Self::from_json_str(&content)
    }

    /// Parse, structurally validate, and semantically validate a certificate.
    pub fn from_json_str(json_str: &str) -> Result<Self, CertificateError> {
        let document: CertificateDocument = serde_json::from_str(json_str)?;
        document.validate()
    }

    /// Verify the tail-adjusted matrix using zero-float exact interval LDL.
    pub fn verify(&self) -> Result<VerificationOutcome, CertificateError> {
        let adjusted = self.matrix.with_diagonal_shift(&self.tail_lower_bound);
        let report = adjusted.verify_positivity();
        let passed = report.is_symmetric && report.is_positive_definite;
        let mut notes = Vec::new();
        notes.push(format!(
            "Tail rule '{}' produced exact lower bound {} and was absorbed before LDL",
            self.document.tail_bound.rule_name(),
            canonical_fraction(&self.tail_lower_bound)
        ));
        notes.push(format!(
            "Generator working tree dirty at generation: {}",
            self.document.generator_metadata.git_dirty
        ));
        if passed {
            notes.push(format!(
                "PASS: adjusted exact interval LDL has minimum diagonal lower bound {}",
                report.min_diagonal_lower_bound
            ));
        } else {
            notes.push(
                "FAILURE: adjusted LDL diagonal intervals are not strictly positive".to_string(),
            );
        }

        Ok(VerificationOutcome {
            passed,
            claim: self.document.claim.clone(),
            format: self.document.format.clone(),
            basis_type: self.document.basis.r#type.as_str().to_string(),
            parity_sector: self.document.parity_sector.as_str().to_string(),
            claim_profile: self.document.claim_profile.as_str().to_string(),
            verified_scope: self.document.claim_profile.verified_scope().to_string(),
            dimension: self.document.dimension,
            support_t: self.document.support_t.frac.clone(),
            tail_rule: self.document.tail_bound.rule_name().to_string(),
            tail_lower_bound: canonical_fraction(&self.tail_lower_bound),
            ldl_report: report,
            notes,
        })
    }
}
