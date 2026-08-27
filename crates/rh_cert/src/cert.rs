//! Strict parser and whole-certificate verifier for `rh-weil-certificate-v1`.

use std::fs;
use std::path::Path;

use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::Zero;
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::gershgorin::{verify_congruence_gershgorin, GershgorinBlockReport, GershgorinError};
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

    #[error("Gershgorin certificate error: {0}")]
    Gershgorin(#[from] GershgorinError),
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
    ExactPrimeLegendreSchur,
}

impl ClaimProfile {
    fn as_str(self) -> &'static str {
        match self {
            Self::SyntheticMatrix => "synthetic_matrix",
            Self::DigammaFiniteBlock => "digamma_finite_block",
            Self::ExactPrimeLegendreSchur => "exact_prime_legendre_schur",
        }
    }

    fn verified_scope(self, support_frac: &str) -> String {
        match self {
            Self::SyntheticMatrix => "synthetic_matrix".to_string(),
            Self::DigammaFiniteBlock => "finite_basis_full_digamma_series".to_string(),
            Self::ExactPrimeLegendreSchur => format!(
                "localized_weil_positivity_T_{}",
                support_frac.replace('/', "_")
            ),
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
    #[serde(rename = "rho_R")]
    rho_r: Option<RationalIntervalJson>,
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
            self.rho_r.is_some(),
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
            self.rho_r.as_ref(),
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
#[serde(deny_unknown_fields)]
struct ExactMatrixJson {
    dimension: usize,
    entries: Vec<ExactMatrixEntryJson>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct ExactMatrixEntryJson {
    row: usize,
    col: usize,
    num: String,
    den: String,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct SchurProofJson {
    residual_order: usize,
    #[serde(rename = "GV")]
    gv: MatrixJson,
    #[serde(rename = "G2")]
    g2: MatrixJson,
    #[serde(rename = "GR")]
    gr: MatrixJson,
    even_witness: ExactMatrixJson,
    odd_witness: ExactMatrixJson,
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
    #[serde(rename = "legendre_component_gram_schur")]
    LegendreComponentGramSchur {
        harmonic_index: usize,
        factor: ExactRationalJson,
    },
}

impl TailBoundJson {
    fn rule_name(&self) -> &'static str {
        match self {
            Self::ExactScalarIdentity { .. } => "exact_scalar_identity",
            Self::NonnegativeDigammaRemainder { .. } => "nonnegative_digamma_remainder",
            Self::LegendreComponentGramSchur { .. } => "legendre_component_gram_schur",
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
    schur_proof: Option<SchurProofJson>,
    generator_metadata: GeneratorMetadataJson,
}

/// Parsed certificate with all semantic checks and exact rational conversions completed.
#[derive(Debug, Clone)]
pub struct CertificateJson {
    document: CertificateDocument,
    matrix: RationalIntervalMatrix,
    tail_lower_bound: BigRational,
    schur_proof: Option<ValidatedSchurProof>,
}

#[derive(Debug, Clone)]
struct ValidatedSchurProof {
    gv: RationalIntervalMatrix,
    g2: RationalIntervalMatrix,
    gr: RationalIntervalMatrix,
    even_witness: Vec<Vec<BigRational>>,
    odd_witness: Vec<Vec<BigRational>>,
    factor: BigRational,
}

#[derive(Debug, Clone, Serialize)]
pub struct SchurVerificationReport {
    pub is_positive_definite: bool,
    pub complement_lower_bound: String,
    pub schur_factor: String,
    pub even: GershgorinBlockReport,
    pub odd: GershgorinBlockReport,
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
    pub ldl_report: Option<LdlVerificationReport>,
    pub schur_report: Option<SchurVerificationReport>,
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

fn harmonic_rational(n: usize) -> BigRational {
    let mut total = BigRational::zero();
    for k in 1..=n {
        total += BigRational::new(BigInt::from(1), BigInt::from(k));
    }
    total
}

fn allowed_exact_prime_configuration(support: &BigRational, dimension: usize) -> bool {
    (dimension == 32 && *support == BigRational::new(BigInt::from(7), BigInt::from(20)))
        || (dimension == 40 && *support == BigRational::new(BigInt::from(2), BigInt::from(5)))
        || (dimension == 48 && *support == BigRational::new(BigInt::from(17), BigInt::from(40)))
        || (dimension == 56 && *support == BigRational::new(BigInt::from(9), BigInt::from(20)))
        || (dimension == 68 && *support == BigRational::new(BigInt::from(19), BigInt::from(40)))
}

fn extract_interval_matrix(
    matrix_json: &MatrixJson,
    dimension: usize,
) -> Result<RationalIntervalMatrix, CertificateError> {
    if matrix_json.dimension != dimension {
        return Err(CertificateError::DimensionMismatch {
            header_dim: dimension,
            matrix_dim: matrix_json.dimension,
        });
    }
    let expected = dimension
        .checked_mul(dimension)
        .ok_or_else(|| validation_error("$.dimension", "dimension squared overflows usize"))?;
    if matrix_json.entries.len() != expected {
        return Err(CertificateError::EntryCountMismatch {
            expected,
            found: matrix_json.entries.len(),
        });
    }

    let mut grid = vec![vec![None; dimension]; dimension];
    for entry in &matrix_json.entries {
        if entry.row >= dimension || entry.col >= dimension {
            return Err(CertificateError::CoordinateOutOfRange {
                row: entry.row,
                col: entry.col,
                dimension,
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

    let mut rows = Vec::with_capacity(dimension);
    for (row_index, grid_row) in grid.into_iter().enumerate() {
        let mut row = Vec::with_capacity(dimension);
        for (col_index, cell) in grid_row.into_iter().enumerate() {
            row.push(cell.ok_or(CertificateError::MissingEntry {
                row: row_index,
                col: col_index,
            })?);
        }
        rows.push(row);
    }
    let matrix = RationalIntervalMatrix::new(dimension, rows)?;
    for row in 0..dimension {
        for col in (row + 1)..dimension {
            if matrix.rows[row][col] != matrix.rows[col][row] {
                return Err(CertificateError::NonSymmetric { row, col });
            }
        }
    }
    Ok(matrix)
}

fn extract_exact_matrix(
    matrix_json: &ExactMatrixJson,
    dimension: usize,
    field: &str,
) -> Result<Vec<Vec<BigRational>>, CertificateError> {
    if matrix_json.dimension != dimension {
        return Err(validation_error(
            field,
            format!("dimension must equal {dimension}"),
        ));
    }
    let expected = dimension
        .checked_mul(dimension)
        .ok_or_else(|| validation_error(field, "dimension squared overflows usize"))?;
    if matrix_json.entries.len() != expected {
        return Err(validation_error(
            field,
            format!("must contain exactly {expected} entries"),
        ));
    }

    let mut grid = vec![vec![None; dimension]; dimension];
    for entry in &matrix_json.entries {
        if entry.row >= dimension || entry.col >= dimension {
            return Err(validation_error(field, "matrix coordinate is out of range"));
        }
        if grid[entry.row][entry.col].is_some() {
            return Err(validation_error(field, "duplicate matrix coordinate"));
        }
        let value = parse_canonical_rational(&entry.num, &entry.den, field)?;
        grid[entry.row][entry.col] = Some(value);
    }

    let mut rows = Vec::with_capacity(dimension);
    for grid_row in grid {
        let mut row = Vec::with_capacity(dimension);
        for cell in grid_row {
            row.push(cell.ok_or_else(|| validation_error(field, "missing matrix coordinate"))?);
        }
        rows.push(row);
    }

    for (row_index, row_values) in rows.iter().enumerate() {
        for value in row_values.iter().skip(row_index + 1) {
            if !value.is_zero() {
                return Err(validation_error(field, "witness must be lower triangular"));
            }
        }
        if row_values[row_index].is_zero() {
            return Err(validation_error(field, "witness diagonal must be nonzero"));
        }
    }
    Ok(rows)
}

fn require_parity_block_diagonal(
    matrix: &RationalIntervalMatrix,
    field: &str,
) -> Result<(), CertificateError> {
    for row in 0..matrix.dim {
        for col in 0..matrix.dim {
            if (row % 2) != (col % 2) {
                let value = &matrix.rows[row][col];
                if !value.lo.is_zero() || !value.hi.is_zero() {
                    return Err(validation_error(
                        field,
                        format!("opposite-parity entry ({row}, {col}) must be exactly zero"),
                    ));
                }
            }
        }
    }
    Ok(())
}

fn build_schur_parity_block(
    matrix: &RationalIntervalMatrix,
    gv: &RationalIntervalMatrix,
    g2: &RationalIntervalMatrix,
    gr: &RationalIntervalMatrix,
    coefficient: &BigRational,
    parity: usize,
) -> Result<RationalIntervalMatrix, CertificateError> {
    let block_dim = matrix.dim / 2;
    let mut rows = vec![vec![RationalInterval::zero(); block_dim]; block_dim];

    // Full matrices have already been validated symmetric and exactly parity
    // block diagonal. Construct only the requested Schur block, and only one
    // triangle of it, instead of materializing the full N x N Schur matrix and
    // copying parity blocks out afterward.
    let mut block_row = 0;
    while block_row < block_dim {
        let row_index = parity + 2 * block_row;
        let mut block_col = block_row;
        while block_col < block_dim {
            let col_index = parity + 2 * block_col;
            let gram = &gv.rows[row_index][col_index] + &g2.rows[row_index][col_index];
            let gram = &gram + &gr.rows[row_index][col_index];
            let value = &matrix.rows[row_index][col_index] - gram.scale_by(coefficient);
            rows[block_row][block_col] = value.clone();
            rows[block_col][block_row] = value;
            block_col += 1;
        }
        block_row += 1;
    }

    Ok(RationalIntervalMatrix::new(block_dim, rows)?)
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

    fn validate_standard_tail(&self) -> Result<BigRational, CertificateError> {
        self.constants.validate_intervals()?;
        if self.schur_proof.is_some() {
            return Err(validation_error(
                "$.schur_proof",
                "is only valid for exact_prime_legendre_schur",
            ));
        }
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
            (ClaimProfile::ExactPrimeLegendreSchur, _) => Err(validation_error(
                "$.tail_bound",
                "exact-prime profile is validated by its dedicated Schur rule",
            )),
        }
    }

    fn validate_exact_prime_schur(
        &self,
        matrix: &RationalIntervalMatrix,
    ) -> Result<(BigRational, ValidatedSchurProof), CertificateError> {
        self.constants.validate_intervals()?;
        if self.dimension != 32
            && self.dimension != 40
            && self.dimension != 48
            && self.dimension != 56
            && self.dimension != 68
        {
            return Err(validation_error(
                "$.dimension",
                "v1 exact-prime profile allows only dimensions 32, 40, 48, 56, and 68",
            ));
        }
        if self.basis.r#type != BasisType::Legendre
            || self.basis.domain != BasisDomain::ScaledUnitInterval
            || self.parity_sector != ParitySector::Both
        {
            return Err(validation_error(
                "$.basis",
                "exact-prime profile requires Legendre basis on [-1, 1] with both parity sectors",
            ));
        }
        if self.constants.present_count() != 3
            || self.constants.c2.is_none()
            || self.constants.c_t.is_none()
            || self.constants.rho_r.is_none()
        {
            return Err(validation_error(
                "$.constants",
                "exact-prime profile requires exactly c2, c_T, and rho_R",
            ));
        }

        let (harmonic_index, factor_json) = match &self.tail_bound {
            TailBoundJson::LegendreComponentGramSchur {
                harmonic_index,
                factor,
            } => (*harmonic_index, factor),
            _ => {
                return Err(validation_error(
                    "$.tail_bound",
                    "exact-prime profile requires legendre_component_gram_schur",
                ));
            }
        };
        if harmonic_index != self.dimension {
            return Err(validation_error(
                "$.tail_bound.harmonic_index",
                "must equal the finite dimension",
            ));
        }
        let factor = factor_json.parse("$.tail_bound.factor")?;
        if factor != BigRational::from_integer(BigInt::from(3)) {
            return Err(validation_error(
                "$.tail_bound.factor",
                "v1 exact-prime profile is locked to factor 3",
            ));
        }

        let proof = self.schur_proof.as_ref().ok_or_else(|| {
            validation_error("$.schur_proof", "is required for exact-prime profile")
        })?;
        if proof.residual_order != 32 {
            return Err(validation_error(
                "$.schur_proof.residual_order",
                "v1 exact-prime profile is locked to residual order 32",
            ));
        }
        let gv = extract_interval_matrix(&proof.gv, self.dimension)?;
        let g2 = extract_interval_matrix(&proof.g2, self.dimension)?;
        let gr = extract_interval_matrix(&proof.gr, self.dimension)?;
        require_parity_block_diagonal(matrix, "$.matrix")?;
        require_parity_block_diagonal(&gv, "$.schur_proof.GV")?;
        require_parity_block_diagonal(&g2, "$.schur_proof.G2")?;
        require_parity_block_diagonal(&gr, "$.schur_proof.GR")?;

        let half = self.dimension / 2;
        let even_witness =
            extract_exact_matrix(&proof.even_witness, half, "$.schur_proof.even_witness")?;
        let odd_witness =
            extract_exact_matrix(&proof.odd_witness, half, "$.schur_proof.odd_witness")?;

        let c2 = self.constants.c2.as_ref().expect("validated c2").parse()?;
        let c_t = self
            .constants
            .c_t
            .as_ref()
            .expect("validated c_T")
            .parse()?;
        let rho_r = self
            .constants
            .rho_r
            .as_ref()
            .expect("validated rho_R")
            .parse()?;
        let mu_lower = harmonic_rational(self.dimension) - c_t.hi - c2.hi - rho_r.hi;
        if mu_lower <= BigRational::zero() {
            return Err(validation_error(
                "$.constants",
                "derived Legendre complement lower bound must be strictly positive",
            ));
        }

        Ok((
            mu_lower,
            ValidatedSchurProof {
                gv,
                g2,
                gr,
                even_witness,
                odd_witness,
                factor,
            },
        ))
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
        if self.claim_profile == ClaimProfile::ExactPrimeLegendreSchur
            && !allowed_exact_prime_configuration(&support, self.dimension)
        {
            return Err(validation_error(
                "$.support_T",
                "v1 exact-prime profile allows only (T=7/20,N=32), (T=2/5,N=40), (T=17/40,N=48), (T=9/20,N=56), or (T=19/40,N=68)",
            ));
        }
        if self.basis.dimension != self.dimension {
            return Err(validation_error(
                "$.basis.dimension",
                "must equal the certificate dimension",
            ));
        }
        self.validate_metadata()?;
        let matrix = extract_interval_matrix(&self.matrix, self.dimension)?;
        let (tail_lower_bound, schur_proof) =
            if self.claim_profile == ClaimProfile::ExactPrimeLegendreSchur {
                let (mu, proof) = self.validate_exact_prime_schur(&matrix)?;
                (mu, Some(proof))
            } else {
                (self.validate_standard_tail()?, None)
            };
        Ok(CertificateJson {
            document: self,
            matrix,
            tail_lower_bound,
            schur_proof,
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

    fn verify_exact_prime_schur(
        &self,
        proof: &ValidatedSchurProof,
    ) -> Result<SchurVerificationReport, CertificateError> {
        let coefficient = &proof.factor / &self.tail_lower_bound;
        let even_block = build_schur_parity_block(
            &self.matrix,
            &proof.gv,
            &proof.g2,
            &proof.gr,
            &coefficient,
            0,
        )?;
        let odd_block = build_schur_parity_block(
            &self.matrix,
            &proof.gv,
            &proof.g2,
            &proof.gr,
            &coefficient,
            1,
        )?;
        let even = verify_congruence_gershgorin(&even_block, &proof.even_witness)?;
        let odd = verify_congruence_gershgorin(&odd_block, &proof.odd_witness)?;
        Ok(SchurVerificationReport {
            is_positive_definite: even.is_positive_definite && odd.is_positive_definite,
            complement_lower_bound: canonical_fraction(&self.tail_lower_bound),
            schur_factor: canonical_fraction(&coefficient),
            even,
            odd,
        })
    }

    /// Verify the complete closed certificate profile using exact rational arithmetic.
    pub fn verify(&self) -> Result<VerificationOutcome, CertificateError> {
        let mut notes = vec![format!(
            "Generator working tree dirty at generation: {}",
            self.document.generator_metadata.git_dirty
        )];

        let (passed, ldl_report, schur_report) = match &self.schur_proof {
            Some(proof) => {
                let report = self.verify_exact_prime_schur(proof)?;
                if report.is_positive_definite {
                    notes.push(format!(
                        "PASS: exact-prime Schur certificate has even/odd Gershgorin margins {} and {}",
                        report.even.min_margin, report.odd.min_margin
                    ));
                } else {
                    notes.push(
                        "FAILURE: one or both exact congruence/Gershgorin parity blocks are not strictly positive"
                            .to_string(),
                    );
                }
                (report.is_positive_definite, None, Some(report))
            }
            None => {
                let adjusted = self.matrix.with_diagonal_shift(&self.tail_lower_bound);
                let report = adjusted.verify_positivity();
                let standard_passed = report.is_symmetric && report.is_positive_definite;
                notes.insert(
                    0,
                    format!(
                        "Tail rule '{}' produced exact lower bound {} and was absorbed before LDL",
                        self.document.tail_bound.rule_name(),
                        canonical_fraction(&self.tail_lower_bound)
                    ),
                );
                if standard_passed {
                    notes.push(format!(
                        "PASS: adjusted exact interval LDL has minimum diagonal lower bound {}",
                        report.min_diagonal_lower_bound
                    ));
                } else {
                    notes.push(
                        "FAILURE: adjusted LDL diagonal intervals are not strictly positive"
                            .to_string(),
                    );
                }
                (standard_passed, Some(report), None)
            }
        };

        Ok(VerificationOutcome {
            passed,
            claim: self.document.claim.clone(),
            format: self.document.format.clone(),
            basis_type: self.document.basis.r#type.as_str().to_string(),
            parity_sector: self.document.parity_sector.as_str().to_string(),
            claim_profile: self.document.claim_profile.as_str().to_string(),
            verified_scope: self
                .document
                .claim_profile
                .verified_scope(&self.document.support_t.frac),
            dimension: self.document.dimension,
            support_t: self.document.support_t.frac.clone(),
            tail_rule: self.document.tail_bound.rule_name().to_string(),
            tail_lower_bound: canonical_fraction(&self.tail_lower_bound),
            ldl_report,
            schur_report,
            notes,
        })
    }
}
