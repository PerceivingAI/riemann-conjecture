//! v3 full mixed-Gram Schur research verifier: exact rational, zero floats.
//! The analytical source inputs MUST be independently verified by a separate
//! evaluator; this module never treats source fingerprints as mathematical proof.
//! The production admission list stays empty.

use std::fs;
use std::path::Path;

use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, Zero};
use serde::{Deserialize, Serialize};

use crate::cert::CertificateError;
use crate::interval::RationalInterval;

pub const EXPECTED_FORMAT_V3: &str = "rh-weil-certificate-v3";
pub const EXPECTED_PROFILE_V3: &str = "combined_multi_prime_legendre_schur";
pub const V3_ALLOWED_CONFIGURATIONS: &[(i64, i64, usize)] = &[];

const N: usize = 192;
const BITS: u32 = 352;
const WBITS: u32 = 48;
const ETA_DEN: i64 = 16_777_216;

fn invalid(field: &str, message: impl Into<String>) -> CertificateError {
    CertificateError::Validation {
        field: field.to_owned(),
        message: message.into(),
    }
}

fn decimal_integer(value: &str, field: &str) -> Result<BigInt, CertificateError> {
    let digits = value.strip_prefix('-').unwrap_or(value);
    if digits.is_empty()
        || !digits.bytes().all(|byte| byte.is_ascii_digit())
        || (digits.starts_with('0') && digits.len() > 1)
        || (digits == "0" && value.starts_with('-'))
    {
        return Err(invalid(field, "noncanonical signed integer"));
    }
    BigInt::parse_bytes(value.as_bytes(), 10).ok_or_else(|| invalid(field, "invalid integer"))
}

fn dyadic_point(value: &str, bits: u32, field: &str) -> Result<BigRational, CertificateError> {
    Ok(BigRational::new(
        decimal_integer(value, field)?,
        BigInt::one() << bits,
    ))
}

fn dyadic_pair(pair: &[String; 2], field: &str) -> Result<RationalInterval, CertificateError> {
    let lo = dyadic_point(&pair[0], BITS, field)?;
    let hi = dyadic_point(&pair[1], BITS, field)?;
    RationalInterval::new(lo, hi).map_err(CertificateError::from)
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct Support {
    num: String,
    den: String,
    frac: String,
}
#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct Basis {
    #[serde(rename = "type")]
    kind: String,
    dimension: usize,
    domain: String,
    normalization: String,
    norm_sq: String,
}
#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct Eta {
    num: String,
    den: String,
}
#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct Provenance {
    status: String,
    original_packet_sha256: String,
    original_witness_sha256: String,
    independent_input_audit_sha256: String,
    independent_auditor_sha256: String,
}
#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct Versions {
    python: String,
    flint: String,
}
#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct Metadata {
    script: String,
    git_commit: String,
    git_dirty: bool,
    timestamp_utc: String,
    precision_bits: usize,
    independent_precision_bits: usize,
    versions: Versions,
}
#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct Doc {
    format: String,
    claim: String,
    claim_profile: String,
    #[serde(rename = "support_T")]
    support_t: Support,
    basis: Basis,
    parity_sector: String,
    dimension: usize,
    residual_order: usize,
    active_terms: Vec<usize>,
    eta: Eta,
    dyadic_bits: usize,
    #[serde(rename = "low_A_triangular")]
    low_a_triangular: Vec<Vec<[String; 2]>>,
    truncated_gram_triangular: Vec<Vec<[String; 2]>>,
    mu_dyadic: [String; 2],
    delta_dyadic: [String; 2],
    witness_bits: usize,
    witness_numerators: Vec<Vec<String>>,
    provenance: Provenance,
    generator_metadata: Metadata,
}

#[derive(Debug, Clone)]
pub struct CertificateV3 {
    document: Doc,
}

#[derive(Debug, Clone, Serialize)]
pub struct V3ResearchReport {
    pub format: String,
    pub claim: String,
    pub classification: String,
    pub mathematical_status: String,
    pub admission_status: String,
    pub dimension: usize,
    pub support_t: String,
    pub exact_margin: String,
    pub exact_margin_positive: bool,
    pub analytic_inputs_independently_verified_here: bool,
    pub theorem_admitted: bool,
}

fn validate_sha256(hash: &str, field: &str) -> Result<(), CertificateError> {
    if hash.len() != 64
        || !hash
            .bytes()
            .all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())
    {
        return Err(invalid(field, "must be lowercase SHA-256 hexadecimal"));
    }
    Ok(())
}

impl CertificateV3 {
    pub fn from_file<P: AsRef<Path>>(path: P) -> Result<Self, CertificateError> {
        Self::from_json_str(&fs::read_to_string(path)?)
    }

    pub fn from_json_str(text: &str) -> Result<Self, CertificateError> {
        let doc: Doc = serde_json::from_str(text)?;
        Self::validate(&doc)?;
        Ok(Self { document: doc })
    }

    fn validate(doc: &Doc) -> Result<(), CertificateError> {
        if doc.format != EXPECTED_FORMAT_V3 || doc.claim_profile != EXPECTED_PROFILE_V3 {
            return Err(invalid("$.format", "unsupported v3 format/profile"));
        }
        if doc.claim != "research-combined-schur-T11-20-N192" {
            return Err(invalid("$.claim", "unknown v3 research identity"));
        }
        if doc.support_t.num != "11" || doc.support_t.den != "20" || doc.support_t.frac != "11/20" {
            return Err(invalid("$.support_T", "v3 support must equal 11/20"));
        }
        if doc.dimension != N
            || doc.basis.dimension != N
            || doc.basis.kind != "legendre"
            || doc.basis.domain != "[-1, 1]"
            || doc.basis.normalization != "P_n(1)=1"
            || doc.basis.norm_sq != "2/(2n+1)"
            || doc.parity_sector != "both"
            || doc.residual_order != 32
            || doc.active_terms != [2, 3]
            || doc.dyadic_bits != BITS as usize
            || doc.eta.num != "1"
            || doc.eta.den != ETA_DEN.to_string()
            || doc.witness_bits != WBITS as usize
        {
            return Err(invalid("$.basis", "unfrozen combined-Schur parameters"));
        }
        for (name, hash) in [
            (
                "original_packet_sha256",
                &doc.provenance.original_packet_sha256,
            ),
            (
                "original_witness_sha256",
                &doc.provenance.original_witness_sha256,
            ),
            (
                "independent_input_audit_sha256",
                &doc.provenance.independent_input_audit_sha256,
            ),
            (
                "independent_auditor_sha256",
                &doc.provenance.independent_auditor_sha256,
            ),
        ] {
            validate_sha256(hash, name)?;
        }
        if doc.generator_metadata.git_commit.len() != 40
            || !doc
                .generator_metadata
                .git_commit
                .bytes()
                .all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())
            || !matches!(
                doc.generator_metadata.script.as_str(),
                "scripts/cert/export_combined_schur_v3.py"
                    | "scripts/cert/export_combined_schur_v3_clean.py"
            )
            || doc.generator_metadata.timestamp_utc.len() < 20
            || !doc.generator_metadata.timestamp_utc.ends_with('Z')
            || doc.generator_metadata.precision_bits != 1024
            || doc.generator_metadata.independent_precision_bits != 2048
            || doc.generator_metadata.versions.python.is_empty()
            || doc.generator_metadata.versions.flint.is_empty()
        {
            return Err(invalid(
                "$.generator_metadata",
                "invalid generator identity and precision",
            ));
        }
        match doc.provenance.status.as_str() {
            "research_uncommitted_not_proof_bearing"
                if doc.generator_metadata.git_dirty
                    && doc.generator_metadata.script
                        == "scripts/cert/export_combined_schur_v3.py" => {}
            "clean_candidate_pending_admission"
                if !doc.generator_metadata.git_dirty
                    && doc.generator_metadata.script
                        == "scripts/cert/export_combined_schur_v3_clean.py" => {}
            _ => {
                return Err(invalid(
                    "$.provenance.status",
                    "provenance and dirty-state mismatch",
                ))
            }
        }
        if doc.low_a_triangular.len() != N || doc.truncated_gram_triangular.len() != N {
            return Err(invalid("$.low_A_triangular", "wrong row count"));
        }
        for (name, rows) in [
            ("low_A_triangular", &doc.low_a_triangular),
            ("truncated_gram_triangular", &doc.truncated_gram_triangular),
        ] {
            for (i, row) in rows.iter().enumerate() {
                if row.len() != N - i {
                    return Err(invalid(name, "nontriangular matrix row length"));
                }
                for (off, pair) in row.iter().enumerate() {
                    let interval = dyadic_pair(pair, name)?;
                    if off % 2 == 1 && (!interval.lo.is_zero() || !interval.hi.is_zero()) {
                        return Err(invalid(
                            name,
                            "opposite parity must be the exact zero interval",
                        ));
                    }
                }
            }
        }
        let mu = dyadic_pair(&doc.mu_dyadic, "$.mu_dyadic")?;
        let delta = dyadic_pair(&doc.delta_dyadic, "$.delta_dyadic")?;
        if mu.lo <= BigRational::zero() || delta.lo < BigRational::zero() {
            return Err(invalid(
                "$.mu_dyadic",
                "nonpositive complement or negative residual",
            ));
        }
        if doc.witness_numerators.len() != N {
            return Err(invalid("$.witness_numerators", "wrong row count"));
        }
        for (i, row) in doc.witness_numerators.iter().enumerate() {
            if row.len() != N {
                return Err(invalid("$.witness_numerators", "wrong column count"));
            }
            for (j, entry) in row.iter().enumerate() {
                let v = decimal_integer(entry, "$.witness_numerators")?;
                if (j > i || (i - j) % 2 == 1) && !v.is_zero() {
                    return Err(invalid(
                        "$.witness_numerators",
                        "not lower triangular or parity preserving",
                    ));
                }
                if i == j && v.is_zero() {
                    return Err(invalid("$.witness_numerators", "singular rational witness"));
                }
            }
        }
        Ok(())
    }

    pub fn verify(&self) -> Result<crate::cert::VerificationOutcome, CertificateError> {
        // Deliberately no admitted configurations. An exact rational result is
        // conditional on independent analytic enclosure acceptance AND an
        // explicit admission decision; neither can be inferred from this JSON.
        Err(invalid(
            "$.support_T",
            "v3 theorem admission is empty; research arithmetic is not an admitted theorem",
        ))
    }

    /// Verify strict rational Schur positivity using a single exact integer
    /// denominator, instead of millions of individually reduced rationals.
    /// The 192-dimensional congruence is exactly a direct sum of two parity blocks.
    // Direct integer indexing is required for symmetric triangular mirroring
    // and separate parity-block congruence contractions.
    #[allow(clippy::needless_range_loop)]
    pub fn verify_research_arithmetic(&self) -> Result<V3ResearchReport, CertificateError> {
        let p = &self.document;
        let e = BigInt::from(ETA_DEN);
        let q = BigInt::one() << BITS;
        let mu = decimal_integer(&p.mu_dyadic[0], "mu")?;
        let delta = decimal_integer(&p.delta_dyadic[1], "delta")?;
        let ep = &e + BigInt::one();
        let mut ra = vec![BigInt::zero(); N];
        let mut rg = vec![BigInt::zero(); N];
        for i in 0..N {
            for j in i..N {
                let aa = &p.low_a_triangular[i][j - i];
                let gg = &p.truncated_gram_triangular[i][j - i];
                let da = decimal_integer(&aa[1], "a high")? - decimal_integer(&aa[0], "a low")?;
                let dg = decimal_integer(&gg[1], "g high")? - decimal_integer(&gg[0], "g low")?;
                ra[i] += &da;
                rg[i] += &dg;
                if i != j {
                    ra[j] += &da;
                    rg[j] += &dg;
                }
            }
        }
        fn gcd(mut a: BigInt, mut b: BigInt) -> BigInt {
            while !b.is_zero() {
                let remainder = &a % &b;
                a = b;
                b = remainder;
            }
            a
        }
        let mut l = BigInt::one();
        for i in 0..N {
            let odd = BigInt::from(2 * i + 1);
            l = (&l / gcd(l.clone(), odd.clone())) * odd;
        }
        // Common strictly positive denominator:
        // D = 2 * 2^352 * eta_den * mu_numerator * lcm(1,3,...,383).
        // Schur entries are exact integer matrix M divided by D.
        let common = BigInt::from(2) * &q * &e * &mu * &l;
        let residue = BigInt::from(4) * &ep * &delta * &delta * &e;
        let am = &e * &mu * &l;
        let gm = &ep * &q * &l;
        let mut matrix = vec![vec![BigInt::zero(); N]; N];
        for i in 0..N {
            for j in i..N {
                let aa = &p.low_a_triangular[i][j - i];
                let gg = &p.truncated_gram_triangular[i][j - i];
                let mut a = decimal_integer(&aa[0], "a low")? + decimal_integer(&aa[1], "a high")?;
                let mut g = decimal_integer(&gg[0], "g low")? + decimal_integer(&gg[1], "g high")?;
                if i == j {
                    a -= &ra[i];
                    g += &rg[i];
                }
                let mut val = &a * &am - &g * &gm;
                if i == j {
                    val -= &residue * (&l / BigInt::from(2 * i + 1));
                }
                matrix[i][j] = val.clone();
                matrix[j][i] = val;
            }
        }
        let mut witness = vec![vec![BigInt::zero(); N]; N];
        for (i, row) in p.witness_numerators.iter().enumerate() {
            for (j, text) in row.iter().enumerate().take(i + 1) {
                witness[i][j] = decimal_integer(text, "witness")?;
            }
        }
        let mut best: Option<BigInt> = None;
        for parity in 0..2 {
            let ids: Vec<usize> = (parity..N).step_by(2).collect();
            let n = ids.len();
            let mut left = vec![vec![BigInt::zero(); n]; n];
            for i in 0..n {
                for j in 0..n {
                    let mut total = BigInt::zero();
                    for k in 0..=i {
                        let coeff = &witness[ids[i]][ids[k]];
                        if !coeff.is_zero() {
                            total += coeff * &matrix[ids[k]][ids[j]];
                        }
                    }
                    left[i][j] = total;
                }
            }
            let mut b = vec![vec![BigInt::zero(); n]; n];
            for i in 0..n {
                for j in i..n {
                    let mut total = BigInt::zero();
                    for k in 0..=j {
                        let coeff = &witness[ids[j]][ids[k]];
                        if !coeff.is_zero() {
                            total += &left[i][k] * coeff;
                        }
                    }
                    b[i][j] = total.clone();
                    b[j][i] = total;
                }
            }
            for i in 0..n {
                let mut margin = b[i][i].clone();
                for j in 0..n {
                    if i != j {
                        let val = &b[i][j];
                        margin -= if val < &BigInt::zero() {
                            -val
                        } else {
                            val.clone()
                        };
                    }
                }
                best = Some(match best {
                    Some(old) => old.min(margin),
                    None => margin,
                });
            }
        }
        let margin = best.ok_or_else(|| invalid("$.witness_numerators", "missing congruence"))?;
        let denominator = common * (BigInt::one() << (WBITS * 2));
        let exact_margin = BigRational::new(margin.clone(), denominator);
        let positive = margin > BigInt::zero();
        Ok(V3ResearchReport {
            format: EXPECTED_FORMAT_V3.to_owned(),
            claim: p.claim.clone(),
            classification: "RESEARCH_EXACT_RATIONAL_ONLY_NOT_A_THEOREM".to_owned(),
            mathematical_status: if positive {
                "POSITIVE_RATIONAL_SCHUR_LOWER".to_owned()
            } else {
                "NONPOSITIVE_RATIONAL_SCHUR_LOWER".to_owned()
            },
            admission_status: "UNADMITTED".to_owned(),
            dimension: N,
            support_t: p.support_t.frac.clone(),
            exact_margin: exact_margin.to_string(),
            exact_margin_positive: positive,
            analytic_inputs_independently_verified_here: false,
            theorem_admitted: false,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn v3_production_whitelist_stays_empty() {
        assert!(V3_ALLOWED_CONFIGURATIONS.is_empty());
    }
    #[test]
    fn reject_noncanonical_integer() {
        for malformed in ["-0", "+1", "01", "", " 1", "1.0", "-01"] {
            assert!(decimal_integer(malformed, "test").is_err(), "{malformed}");
        }
    }
}
