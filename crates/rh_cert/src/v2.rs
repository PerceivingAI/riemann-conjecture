//! Independent zero-float verifier for \`rh-weil-certificate-v2\`.
//!
//! This module verifies exact rational interval proof arithmetic. It deliberately
//! does not claim to independently establish the transcendental Arb enclosures
//! serialized by the generator. A separate rigorous Rust transcendental layer
//! would be required for that stronger trust boundary.

use std::fs;
use std::path::Path;

use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, Zero};
use serde::Deserialize;

use crate::cert::{CertificateError, SchurVerificationReport, VerificationOutcome};
use crate::gershgorin::verify_congruence_gershgorin;
use crate::interval::{parse_canonical_rational, RationalInterval};
use crate::ldl::RationalIntervalMatrix;

pub const EXPECTED_FORMAT_V2: &str = "rh-weil-certificate-v2";
pub const EXPECTED_PROFILE_V2: &str = "multi_prime_power_legendre_schur";

/// Production theorem admission for v2.
///
/// P7 intentionally does not admit any theorem pair. Future admission must be
/// an explicit change to this closed list, separate from verifier implementation.
pub const V2_ALLOWED_CONFIGURATIONS: &[(i64, i64, usize)] = &[];

const ACTIVE_SET_RULE: &str = "prime_powers_with_log_m_lt_2T";
const COMPLEMENT_RULE: &str = "H_N-c_T-sum(c_m*b_m)-rho_R";
const TAIL_TYPE: &str = "multi_prime_power_legendre_component_gram_schur";
const FACTOR_CLAIM: &str = "C-0059";

fn validation_error(field: &str, message: impl Into<String>) -> CertificateError {
    CertificateError::Validation {
        field: field.to_string(),
        message: message.into(),
    }
}

fn canonical_fraction(value: &BigRational) -> String {
    format!("{}/{}", value.numer(), value.denom())
}

fn harmonic_rational(n: usize) -> BigRational {
    let mut total = BigRational::zero();
    for k in 1..=n {
        total += BigRational::new(BigInt::from(1), BigInt::from(k));
    }
    total
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

fn is_prime(value: usize) -> bool {
    if value < 2 {
        return false;
    }
    if value == 2 {
        return true;
    }
    if value.is_multiple_of(2) {
        return false;
    }
    let mut divisor = 3usize;
    while divisor <= value / divisor {
        if value.is_multiple_of(divisor) {
            return false;
        }
        divisor += 2;
    }
    true
}

fn matches_prime_power(m: usize, prime: usize, exponent: usize) -> bool {
    if exponent == 0 || !is_prime(prime) {
        return false;
    }
    let mut remaining = m;
    let mut actual_exponent = 0usize;
    while remaining > 1 && remaining.is_multiple_of(prime) {
        remaining /= prime;
        actual_exponent += 1;
    }
    remaining == 1 && actual_exponent == exponent
}

pub fn is_allowed_v2_configuration(support: &BigRational, dimension: usize) -> bool {
    V2_ALLOWED_CONFIGURATIONS.iter().any(|(num, den, dim)| {
        dimension == *dim && *support == BigRational::new(BigInt::from(*num), BigInt::from(*den))
    })
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
    fn parse(&self, field: &str) -> Result<RationalInterval, CertificateError> {
        let lo = parse_canonical_rational(&self.lo_num, &self.lo_den, field)?;
        let hi = parse_canonical_rational(&self.hi_num, &self.hi_den, field)?;
        RationalInterval::new(lo, hi).map_err(CertificateError::from)
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
struct SupportTJson {
    num: String,
    den: String,
    frac: String,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct BasisJson {
    #[serde(rename = "type")]
    kind: String,
    dimension: usize,
    domain: String,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct ConstantsJson {
    #[serde(rename = "c_T")]
    c_t: RationalIntervalJson,
    #[serde(rename = "rho_R")]
    rho_r: RationalIntervalJson,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct ArithmeticTermJson {
    m: usize,
    base_prime: usize,
    exponent: usize,
    log_m: RationalIntervalJson,
    tau: RationalIntervalJson,
    von_mangoldt: RationalIntervalJson,
    coefficient: RationalIntervalJson,
    compressed_shift_norm_bound: RationalIntervalJson,
    complement_contribution: RationalIntervalJson,
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
    fn parse(&self, field: &str) -> Result<RationalInterval, CertificateError> {
        let lo = parse_canonical_rational(&self.lo_num, &self.lo_den, field)?;
        let hi = parse_canonical_rational(&self.hi_num, &self.hi_den, field)?;
        RationalInterval::new(lo, hi).map_err(CertificateError::from)
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
    #[serde(rename = "GP")]
    gp: MatrixJson,
    #[serde(rename = "GR")]
    gr: MatrixJson,
    even_witness: ExactMatrixJson,
    odd_witness: ExactMatrixJson,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct TailBoundJson {
    #[serde(rename = "type")]
    kind: String,
    harmonic_index: usize,
    active_set_rule: String,
    complement_rule: String,
    grouped_components: Vec<String>,
    factor: ExactRationalJson,
    factor_claim: String,
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
struct CertificateDocumentV2 {
    format: String,
    claim: String,
    claim_profile: String,
    #[serde(rename = "support_T")]
    support_t: SupportTJson,
    basis: BasisJson,
    parity_sector: String,
    dimension: usize,
    constants: ConstantsJson,
    arithmetic_terms: Vec<ArithmeticTermJson>,
    matrix: MatrixJson,
    tail_bound: TailBoundJson,
    schur_proof: SchurProofJson,
    generator_metadata: GeneratorMetadataJson,
}

#[derive(Debug, Clone)]
struct ValidatedSchurProofV2 {
    gv: RationalIntervalMatrix,
    gp: RationalIntervalMatrix,
    gr: RationalIntervalMatrix,
    even_witness: Vec<Vec<BigRational>>,
    odd_witness: Vec<Vec<BigRational>>,
    factor: BigRational,
}

#[derive(Debug, Clone)]
pub struct CertificateV2 {
    document: CertificateDocumentV2,
    support: BigRational,
    matrix: RationalIntervalMatrix,
    complement_lower_bound: BigRational,
    proof: ValidatedSchurProofV2,
}

fn extract_interval_matrix(
    matrix_json: &MatrixJson,
    dimension: usize,
    field: &str,
) -> Result<RationalIntervalMatrix, CertificateError> {
    if matrix_json.dimension != dimension {
        return Err(validation_error(
            &format!("{field}.dimension"),
            format!("must equal {dimension}"),
        ));
    }
    let expected = dimension
        .checked_mul(dimension)
        .ok_or_else(|| validation_error("$.dimension", "dimension squared overflows usize"))?;
    if matrix_json.entries.len() != expected {
        return Err(validation_error(
            &format!("{field}.entries"),
            format!("must contain exactly {expected} entries"),
        ));
    }

    let mut grid = vec![vec![None; dimension]; dimension];
    for (index, entry) in matrix_json.entries.iter().enumerate() {
        if entry.row >= dimension || entry.col >= dimension {
            return Err(validation_error(
                &format!("{field}.entries[{index}]"),
                "matrix coordinate is out of range",
            ));
        }
        if grid[entry.row][entry.col].is_some() {
            return Err(validation_error(
                &format!("{field}.entries[{index}]"),
                "duplicate matrix coordinate",
            ));
        }
        grid[entry.row][entry.col] = Some(entry.parse(&format!("{field}.entries[{index}]"))?);
    }

    let mut rows = Vec::with_capacity(dimension);
    for (row_index, grid_row) in grid.into_iter().enumerate() {
        let mut row = Vec::with_capacity(dimension);
        for (col_index, cell) in grid_row.into_iter().enumerate() {
            row.push(cell.ok_or_else(|| {
                validation_error(
                    &format!("{field}.entries"),
                    format!("missing matrix coordinate ({row_index}, {col_index})"),
                )
            })?);
        }
        rows.push(row);
    }

    let matrix = RationalIntervalMatrix::new(dimension, rows)?;
    if !matrix.is_symmetric() {
        return Err(validation_error(field, "matrix must be exactly symmetric"));
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
            &format!("{field}.dimension"),
            format!("must equal {dimension}"),
        ));
    }
    let expected = dimension
        .checked_mul(dimension)
        .ok_or_else(|| validation_error(field, "dimension squared overflows usize"))?;
    if matrix_json.entries.len() != expected {
        return Err(validation_error(
            &format!("{field}.entries"),
            format!("must contain exactly {expected} entries"),
        ));
    }

    let mut grid = vec![vec![None; dimension]; dimension];
    for (index, entry) in matrix_json.entries.iter().enumerate() {
        if entry.row >= dimension || entry.col >= dimension {
            return Err(validation_error(
                &format!("{field}.entries[{index}]"),
                "matrix coordinate is out of range",
            ));
        }
        if grid[entry.row][entry.col].is_some() {
            return Err(validation_error(
                &format!("{field}.entries[{index}]"),
                "duplicate matrix coordinate",
            ));
        }
        let value =
            parse_canonical_rational(&entry.num, &entry.den, &format!("{field}.entries[{index}]"))?;
        grid[entry.row][entry.col] = Some(value);
    }

    let mut rows = Vec::with_capacity(dimension);
    for grid_row in grid {
        let mut row = Vec::with_capacity(dimension);
        for cell in grid_row {
            row.push(cell.ok_or_else(|| {
                validation_error(&format!("{field}.entries"), "missing matrix coordinate")
            })?);
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
    gp: &RationalIntervalMatrix,
    gr: &RationalIntervalMatrix,
    coefficient: &BigRational,
    parity: usize,
) -> Result<RationalIntervalMatrix, CertificateError> {
    let indices: Vec<usize> = (parity..matrix.dim).step_by(2).collect();
    let block_dim = indices.len();
    let mut rows = vec![vec![RationalInterval::zero(); block_dim]; block_dim];

    for block_row in 0..block_dim {
        let row_index = indices[block_row];
        for block_col in block_row..block_dim {
            let col_index = indices[block_col];
            let gram = &gv.rows[row_index][col_index] + &gp.rows[row_index][col_index];
            let gram = &gram + &gr.rows[row_index][col_index];
            let value = &matrix.rows[row_index][col_index] - gram.scale_by(coefficient);
            rows[block_row][block_col] = value.clone();
            rows[block_col][block_row] = value;
        }
    }

    Ok(RationalIntervalMatrix::new(block_dim, rows)?)
}

fn validate_metadata(metadata: &GeneratorMetadataJson) -> Result<(), CertificateError> {
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

fn validate_arithmetic_terms(
    terms: &[ArithmeticTermJson],
    support: &BigRational,
) -> Result<Vec<RationalInterval>, CertificateError> {
    if terms.len() != 2 {
        return Err(validation_error(
            "$.arithmetic_terms",
            "first v2 structural window requires exactly two active terms {2,3}",
        ));
    }

    if terms.windows(2).any(|pair| pair[0].m >= pair[1].m) {
        return Err(validation_error(
            "$.arithmetic_terms",
            "terms must be strictly increasing by m and therefore unique",
        ));
    }
    if terms[0].m != 2 || terms[1].m != 3 {
        return Err(validation_error(
            "$.arithmetic_terms",
            "first v2 structural window requires exactly active terms [2,3]",
        ));
    }

    let support_inverse = support.recip();
    let one = BigRational::one();
    let two = BigRational::from_integer(BigInt::from(2));
    let mut prime_losses = Vec::with_capacity(2);
    let mut log_intervals = Vec::with_capacity(2);

    for (index, term) in terms.iter().enumerate() {
        let field = format!("$.arithmetic_terms[{index}]");
        if !matches_prime_power(term.m, term.base_prime, term.exponent) {
            return Err(validation_error(
                &field,
                "term identity must satisfy m = base_prime^exponent with prime base",
            ));
        }

        let log_m = term.log_m.parse(&format!("{field}.log_m"))?;
        let tau = term.tau.parse(&format!("{field}.tau"))?;
        let von_mangoldt = term.von_mangoldt.parse(&format!("{field}.von_mangoldt"))?;
        let coefficient = term.coefficient.parse(&format!("{field}.coefficient"))?;
        let norm_bound = term
            .compressed_shift_norm_bound
            .parse(&format!("{field}.compressed_shift_norm_bound"))?;
        let declared_loss = term
            .complement_contribution
            .parse(&format!("{field}.complement_contribution"))?;

        if log_m.lo <= BigRational::zero() {
            return Err(validation_error(
                &format!("{field}.log_m"),
                "must be strictly positive",
            ));
        }
        if tau.lo <= one || tau.hi >= two {
            return Err(validation_error(
                &format!("{field}.tau"),
                "first v2 structural window requires the certified tau interval strictly inside (1,2)",
            ));
        }
        if von_mangoldt.lo <= BigRational::zero() {
            return Err(validation_error(
                &format!("{field}.von_mangoldt"),
                "must be strictly positive",
            ));
        }
        if coefficient.lo <= BigRational::zero() {
            return Err(validation_error(
                &format!("{field}.coefficient"),
                "must be strictly positive",
            ));
        }
        if norm_bound.lo != one || norm_bound.hi != one {
            return Err(validation_error(
                &format!("{field}.compressed_shift_norm_bound"),
                "first v2 structural window is locked to the exact bound b_m=1",
            ));
        }

        let derived_tau = log_m.scale_by(&support_inverse);
        if !tau.contains_interval(&derived_tau) {
            return Err(validation_error(
                &format!("{field}.tau"),
                "must contain the exact-rational interval derived as log_m / T",
            ));
        }

        let inverse_exponent = BigRational::new(BigInt::from(1), BigInt::from(term.exponent));
        let derived_lambda = log_m.scale_by(&inverse_exponent);
        if !von_mangoldt.contains_interval(&derived_lambda) {
            return Err(validation_error(
                &format!("{field}.von_mangoldt"),
                "must contain the interval derived as log_m / exponent",
            ));
        }

        let derived_loss = &coefficient * &norm_bound;
        if !declared_loss.contains_interval(&derived_loss) {
            return Err(validation_error(
                &format!("{field}.complement_contribution"),
                "must enclose the independently derived coefficient * compressed_shift_norm_bound interval",
            ));
        }
        log_intervals.push(log_m);
        prime_losses.push(derived_loss);
    }

    // Prove the strict first structural window from exact rational interval
    // endpoints carried by the certificate. For m=3, T > log(3)/2 is proven
    // only if T exceeds the upper endpoint. For m=2, log(4)/2 = log(2), so
    // T < log(4)/2 is proven only if T lies below the lower log(2) endpoint.
    let lower_threshold_upper = &log_intervals[1].hi / &two;
    if support <= &lower_threshold_upper {
        return Err(validation_error(
            "$.support_T",
            "must be provably strictly greater than log(3)/2",
        ));
    }
    let upper_threshold_lower = &log_intervals[0].lo;
    if support >= upper_threshold_lower {
        return Err(validation_error(
            "$.support_T",
            "must be provably strictly less than log(4)/2",
        ));
    }

    Ok(prime_losses)
}

impl CertificateDocumentV2 {
    fn validate(self) -> Result<CertificateV2, CertificateError> {
        if self.format != EXPECTED_FORMAT_V2 {
            return Err(validation_error(
                "$.format",
                format!("must equal {EXPECTED_FORMAT_V2}"),
            ));
        }
        if self.claim.is_empty() {
            return Err(validation_error("$.claim", "must not be empty"));
        }
        if self.claim_profile != EXPECTED_PROFILE_V2 {
            return Err(validation_error(
                "$.claim_profile",
                format!("must equal {EXPECTED_PROFILE_V2}"),
            ));
        }
        if self.dimension < 2 {
            return Err(validation_error("$.dimension", "must be at least 2"));
        }
        if self.basis.kind != "legendre"
            || self.basis.domain != "[-1, 1]"
            || self.parity_sector != "both"
        {
            return Err(validation_error(
                "$.basis",
                "v2 profile requires Legendre basis on [-1, 1] with both parity sectors",
            ));
        }
        if self.basis.dimension != self.dimension {
            return Err(validation_error(
                "$.basis.dimension",
                "must equal the certificate dimension",
            ));
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
        validate_metadata(&self.generator_metadata)?;

        if self.tail_bound.kind != TAIL_TYPE {
            return Err(validation_error(
                "$.tail_bound.type",
                format!("must equal {TAIL_TYPE}"),
            ));
        }
        if self.tail_bound.harmonic_index != self.dimension {
            return Err(validation_error(
                "$.tail_bound.harmonic_index",
                "must equal the finite dimension",
            ));
        }
        if self.tail_bound.active_set_rule != ACTIVE_SET_RULE {
            return Err(validation_error(
                "$.tail_bound.active_set_rule",
                format!("must equal {ACTIVE_SET_RULE}"),
            ));
        }
        if self.tail_bound.complement_rule != COMPLEMENT_RULE {
            return Err(validation_error(
                "$.tail_bound.complement_rule",
                format!("must equal {COMPLEMENT_RULE}"),
            ));
        }
        if self.tail_bound.grouped_components != ["V", "P", "R"] {
            return Err(validation_error(
                "$.tail_bound.grouped_components",
                "must equal [V,P,R] in that order",
            ));
        }
        if self.tail_bound.factor_claim != FACTOR_CLAIM {
            return Err(validation_error(
                "$.tail_bound.factor_claim",
                format!("must equal verified claim {FACTOR_CLAIM}"),
            ));
        }
        let factor = self.tail_bound.factor.parse("$.tail_bound.factor")?;
        if factor != BigRational::from_integer(BigInt::from(3)) {
            return Err(validation_error(
                "$.tail_bound.factor",
                "v2 multi-prime-power profile is locked to factor 3 by C-0059",
            ));
        }

        let c_t = self.constants.c_t.parse("$.constants.c_T")?;
        let rho_r = self.constants.rho_r.parse("$.constants.rho_R")?;
        if rho_r.lo < BigRational::zero() {
            return Err(validation_error("$.constants.rho_R", "must be nonnegative"));
        }

        let prime_losses = validate_arithmetic_terms(&self.arithmetic_terms, &support)?;

        if self.schur_proof.residual_order != 32 {
            return Err(validation_error(
                "$.schur_proof.residual_order",
                "v2 profile is locked to residual order 32",
            ));
        }

        let matrix = extract_interval_matrix(&self.matrix, self.dimension, "$.matrix")?;
        let gv = extract_interval_matrix(&self.schur_proof.gv, self.dimension, "$.schur_proof.GV")?;
        let gp = extract_interval_matrix(&self.schur_proof.gp, self.dimension, "$.schur_proof.GP")?;
        let gr = extract_interval_matrix(&self.schur_proof.gr, self.dimension, "$.schur_proof.GR")?;
        require_parity_block_diagonal(&matrix, "$.matrix")?;
        require_parity_block_diagonal(&gv, "$.schur_proof.GV")?;
        require_parity_block_diagonal(&gp, "$.schur_proof.GP")?;
        require_parity_block_diagonal(&gr, "$.schur_proof.GR")?;

        let even_dimension = self.dimension.div_ceil(2);
        let odd_dimension = self.dimension / 2;
        let even_witness = extract_exact_matrix(
            &self.schur_proof.even_witness,
            even_dimension,
            "$.schur_proof.even_witness",
        )?;
        let odd_witness = extract_exact_matrix(
            &self.schur_proof.odd_witness,
            odd_dimension,
            "$.schur_proof.odd_witness",
        )?;

        let mut mu_lower = harmonic_rational(self.dimension) - c_t.hi - rho_r.hi;
        for loss in &prime_losses {
            mu_lower -= &loss.hi;
        }
        if mu_lower <= BigRational::zero() {
            return Err(validation_error(
                "$.arithmetic_terms",
                "independently derived complement lower bound mu_N must be strictly positive",
            ));
        }

        Ok(CertificateV2 {
            document: self,
            support,
            matrix,
            complement_lower_bound: mu_lower,
            proof: ValidatedSchurProofV2 {
                gv,
                gp,
                gr,
                even_witness,
                odd_witness,
                factor,
            },
        })
    }
}

impl CertificateV2 {
    pub fn from_file<P: AsRef<Path>>(path: P) -> Result<Self, CertificateError> {
        let content = fs::read_to_string(path)?;
        Self::from_json_str(&content)
    }

    pub fn from_json_str(json_str: &str) -> Result<Self, CertificateError> {
        let document: CertificateDocumentV2 = serde_json::from_str(json_str)?;
        document.validate()
    }

    fn verify_arithmetic(&self) -> Result<VerificationOutcome, CertificateError> {
        let coefficient = &self.proof.factor / &self.complement_lower_bound;
        let even_block = build_schur_parity_block(
            &self.matrix,
            &self.proof.gv,
            &self.proof.gp,
            &self.proof.gr,
            &coefficient,
            0,
        )?;
        let odd_block = build_schur_parity_block(
            &self.matrix,
            &self.proof.gv,
            &self.proof.gp,
            &self.proof.gr,
            &coefficient,
            1,
        )?;
        let even = verify_congruence_gershgorin(&even_block, &self.proof.even_witness)?;
        let odd = verify_congruence_gershgorin(&odd_block, &self.proof.odd_witness)?;
        let passed = even.is_positive_definite && odd.is_positive_definite;

        let report = SchurVerificationReport {
            is_positive_definite: passed,
            complement_lower_bound: canonical_fraction(&self.complement_lower_bound),
            schur_factor: canonical_fraction(&coefficient),
            even,
            odd,
        };

        let mut notes = vec![
            format!(
                "Generator working tree dirty at generation: {}",
                self.document.generator_metadata.git_dirty
            ),
            "Trust boundary: Rust v2 verifies exact rational interval proof arithmetic and serialized interval consistency; it does not independently establish the underlying transcendental Arb enclosures.".to_string(),
            "Active arithmetic set independently enforced as exactly [2,3] for the first v2 structural window.".to_string(),
        ];
        if passed {
            notes.push(format!(
                "PASS: v2 exact congruence/Gershgorin certificate has even/odd margins {} and {}",
                report.even.min_margin, report.odd.min_margin
            ));
        } else {
            notes.push(
                "FAILURE: one or both v2 exact congruence/Gershgorin parity blocks are not strictly positive"
                    .to_string(),
            );
        }

        Ok(VerificationOutcome {
            passed,
            claim: self.document.claim.clone(),
            format: self.document.format.clone(),
            claim_profile: self.document.claim_profile.clone(),
            verified_scope: format!(
                "localized_weil_positivity_T_{}",
                self.document.support_t.frac.replace('/', "_")
            ),
            basis_type: self.document.basis.kind.clone(),
            parity_sector: self.document.parity_sector.clone(),
            dimension: self.document.dimension,
            support_t: self.document.support_t.frac.clone(),
            tail_rule: self.document.tail_bound.kind.clone(),
            tail_lower_bound: canonical_fraction(&self.complement_lower_bound),
            ldl_report: None,
            schur_report: Some(report),
            notes,
        })
    }

    /// Verify an admitted v2 theorem certificate.
    ///
    /// P7 leaves the production whitelist empty, so production calls currently
    /// fail closed here even when the exact rational structure is otherwise valid.
    pub fn verify(&self) -> Result<VerificationOutcome, CertificateError> {
        if !is_allowed_v2_configuration(&self.support, self.document.dimension) {
            return Err(validation_error(
                "$.support_T",
                "v2 theorem configuration is not admitted; the production v2 whitelist is empty",
            ));
        }
        self.verify_arithmetic()
    }
}

#[cfg(test)]
mod tests {
    use serde_json::{json, Value};

    use super::CertificateV2;

    fn interval(value: i64) -> Value {
        json!({
            "lo_num": value.to_string(),
            "lo_den": "1",
            "hi_num": value.to_string(),
            "hi_den": "1"
        })
    }

    fn matrix(dimension: usize, diagonal: i64) -> Value {
        let mut entries = Vec::with_capacity(dimension * dimension);
        for row in 0..dimension {
            for col in 0..dimension {
                entries.push(json!({
                    "row": row,
                    "col": col,
                    "lo_num": if row == col { diagonal.to_string() } else { "0".to_string() },
                    "lo_den": "1",
                    "hi_num": if row == col { diagonal.to_string() } else { "0".to_string() },
                    "hi_den": "1"
                }));
            }
        }
        json!({"dimension": dimension, "entries": entries})
    }

    fn exact_identity(dimension: usize) -> Value {
        let mut entries = Vec::with_capacity(dimension * dimension);
        for row in 0..dimension {
            for col in 0..dimension {
                entries.push(json!({
                    "row": row,
                    "col": col,
                    "num": if row == col { "1" } else { "0" },
                    "den": "1"
                }));
            }
        }
        json!({"dimension": dimension, "entries": entries})
    }

    fn term(m: usize) -> Value {
        json!({
            "m": m,
            "base_prime": m,
            "exponent": 1,
            "log_m": interval(1),
            "tau": {
                "lo_num": "3", "lo_den": "2",
                "hi_num": "3", "hi_den": "2"
            },
            "von_mangoldt": interval(1),
            "coefficient": {
                "lo_num": "1", "lo_den": "10",
                "hi_num": "1", "hi_den": "10"
            },
            "compressed_shift_norm_bound": interval(1),
            "complement_contribution": {
                "lo_num": "1", "lo_den": "10",
                "hi_num": "1", "hi_den": "10"
            }
        })
    }

    fn fixture() -> Value {
        let dimension = 4usize;
        json!({
            "format": "rh-weil-certificate-v2",
            "claim": "rust-v2-unit-fixture",
            "claim_profile": "multi_prime_power_legendre_schur",
            "support_T": {"num": "2", "den": "3", "frac": "2/3"},
            "basis": {"type": "legendre", "dimension": dimension, "domain": "[-1, 1]"},
            "parity_sector": "both",
            "dimension": dimension,
            "constants": {"c_T": interval(0), "rho_R": interval(0)},
            "arithmetic_terms": [term(2), term(3)],
            "matrix": matrix(dimension, 1),
            "tail_bound": {
                "type": "multi_prime_power_legendre_component_gram_schur",
                "harmonic_index": dimension,
                "active_set_rule": "prime_powers_with_log_m_lt_2T",
                "complement_rule": "H_N-c_T-sum(c_m*b_m)-rho_R",
                "grouped_components": ["V", "P", "R"],
                "factor": {"num": "3", "den": "1"},
                "factor_claim": "C-0059"
            },
            "schur_proof": {
                "residual_order": 32,
                "GV": matrix(dimension, 0),
                "GP": matrix(dimension, 0),
                "GR": matrix(dimension, 0),
                "even_witness": exact_identity(2),
                "odd_witness": exact_identity(2)
            },
            "generator_metadata": {
                "generator": "rust-unit-test",
                "script": "v2.rs",
                "version": "1",
                "git_commit": "0000000000000000000000000000000000000000",
                "git_dirty": false,
                "flint_version": "test",
                "python_flint_version": "test",
                "prec_bits": 128,
                "timestamp_utc": "2026-10-01T00:00:00Z"
            }
        })
    }

    #[test]
    fn authorized_arithmetic_path_passes_positive_fixture() {
        let cert =
            CertificateV2::from_json_str(&fixture().to_string()).expect("valid v2 structure");
        let outcome = cert.verify_arithmetic().expect("arithmetic verification");
        assert!(outcome.passed);
        assert_eq!(outcome.format, "rh-weil-certificate-v2");
    }

    #[test]
    fn authorized_arithmetic_path_returns_theorem_failure_for_nonpositive_schur() {
        let mut value = fixture();
        value["matrix"]["entries"][0]["lo_num"] = json!("-1");
        value["matrix"]["entries"][0]["hi_num"] = json!("-1");
        let cert = CertificateV2::from_json_str(&value.to_string()).expect("valid v2 structure");
        let outcome = cert.verify_arithmetic().expect("arithmetic verification");
        assert!(!outcome.passed);
        assert!(outcome.schur_report.is_some());
    }
}
