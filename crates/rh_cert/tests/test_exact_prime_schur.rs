use rh_cert::cert::CertificateJson;
use serde_json::{json, Value};

fn interval_entry(row: usize, col: usize, value: i64) -> Value {
    json!({
        "row": row,
        "col": col,
        "lo_num": value.to_string(),
        "lo_den": "1",
        "hi_num": value.to_string(),
        "hi_den": "1"
    })
}

fn interval_matrix(dimension: usize, diagonal: i64) -> Value {
    let mut entries = Vec::with_capacity(dimension * dimension);
    for row in 0..dimension {
        for col in 0..dimension {
            entries.push(interval_entry(
                row,
                col,
                if row == col { diagonal } else { 0 },
            ));
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

fn point_interval(value: i64) -> Value {
    json!({
        "lo_num": value.to_string(),
        "lo_den": "1",
        "hi_num": value.to_string(),
        "hi_den": "1"
    })
}

fn exact_prime_fixture_for(
    support_num: &str,
    support_den: &str,
    support_frac: &str,
    dimension: usize,
) -> Value {
    json!({
        "format": "rh-weil-certificate-v1",
        "claim": "synthetic exact-prime verifier fixture",
        "claim_profile": "exact_prime_legendre_schur",
        "support_T": {"num": support_num, "den": support_den, "frac": support_frac},
        "basis": {"type": "legendre", "dimension": dimension, "domain": "[-1, 1]"},
        "parity_sector": "both",
        "dimension": dimension,
        "constants": {
            "c2": point_interval(0),
            "c_T": point_interval(0),
            "rho_R": point_interval(0)
        },
        "matrix": interval_matrix(dimension, 1),
        "tail_bound": {
            "type": "legendre_component_gram_schur",
            "harmonic_index": dimension,
            "factor": {"num": "3", "den": "1"}
        },
        "schur_proof": {
            "residual_order": 32,
            "GV": interval_matrix(dimension, 0),
            "G2": interval_matrix(dimension, 0),
            "GR": interval_matrix(dimension, 0),
            "even_witness": exact_identity(dimension / 2),
            "odd_witness": exact_identity(dimension / 2)
        },
        "generator_metadata": {
            "generator": "rust-test",
            "script": "test_exact_prime_schur.rs",
            "version": "1",
            "git_commit": "0000000000000000000000000000000000000000",
            "git_dirty": false,
            "flint_version": "test",
            "python_flint_version": "test",
            "prec_bits": 64,
            "timestamp_utc": "2026-08-21T00:00:00Z"
        }
    })
}

fn exact_prime_fixture() -> Value {
    exact_prime_fixture_for("7", "20", "7/20", 32)
}

#[test]
fn exact_prime_admission_matches_shared_test_corpus() {
    let corpus: Value = serde_json::from_str(include_str!(
        "../../../tests/data/exact-prime-admission-v1.json"
    ))
    .expect("admission corpus must be valid JSON");
    assert_eq!(corpus["format"], "exact-prime-admission-corpus-v1");
    assert_eq!(corpus["purpose"], "test-only");

    for (bucket, expected_allowed) in [("allowed", true), ("forbidden", false)] {
        let cases = corpus[bucket]
            .as_array()
            .expect("corpus bucket must be an array");
        for case in cases {
            let support = case["support_T"].as_str().expect("support_T string");
            let (num, den) = support.split_once('/').expect("canonical support fraction");
            let dimension = case["dimension"].as_u64().expect("dimension integer") as usize;
            let fixture = exact_prime_fixture_for(num, den, support, dimension);
            let accepted = CertificateJson::from_json_str(&fixture.to_string()).is_ok();
            assert_eq!(
                accepted, expected_allowed,
                "Rust exact-prime admission drift for T={support},N={dimension}"
            );
        }
    }
}

#[test]
fn exact_prime_profile_recomputes_schur_and_passes() {
    let fixture = exact_prime_fixture();
    let certificate = CertificateJson::from_json_str(&fixture.to_string()).expect("valid fixture");
    let outcome = certificate.verify().expect("verification runs");
    assert!(outcome.passed);
    assert!(outcome.ldl_report.is_none());
    let report = outcome.schur_report.expect("Schur report");
    assert!(report.is_positive_definite);
    assert_eq!(report.even.dimension, 16);
    assert_eq!(report.odd.dimension, 16);
}

#[test]
fn exact_prime_profile_accepts_t_two_fifths_dimension_40() {
    let fixture = exact_prime_fixture_for("2", "5", "2/5", 40);
    let certificate = CertificateJson::from_json_str(&fixture.to_string()).expect("valid fixture");
    let outcome = certificate.verify().expect("verification runs");
    assert!(outcome.passed);
    assert_eq!(outcome.dimension, 40);
    assert_eq!(outcome.support_t, "2/5");
    assert_eq!(outcome.verified_scope, "localized_weil_positivity_T_2_5");
    let report = outcome.schur_report.expect("Schur report");
    assert_eq!(report.even.dimension, 20);
    assert_eq!(report.odd.dimension, 20);
}

#[test]
fn exact_prime_profile_accepts_seventeen_fortieths_dimension_48() {
    let fixture = exact_prime_fixture_for("17", "40", "17/40", 48);
    let certificate = CertificateJson::from_json_str(&fixture.to_string()).expect("valid fixture");
    let outcome = certificate.verify().expect("verification runs");
    assert!(outcome.passed);
    assert_eq!(outcome.dimension, 48);
    assert_eq!(outcome.support_t, "17/40");
    assert_eq!(outcome.verified_scope, "localized_weil_positivity_T_17_40");
    let report = outcome.schur_report.expect("Schur report");
    assert_eq!(report.even.dimension, 24);
    assert_eq!(report.odd.dimension, 24);
}

#[test]
fn exact_prime_profile_accepts_nine_twentieths_dimension_56() {
    let fixture = exact_prime_fixture_for("9", "20", "9/20", 56);
    let certificate = CertificateJson::from_json_str(&fixture.to_string()).expect("valid fixture");
    let outcome = certificate.verify().expect("verification runs");
    assert!(outcome.passed);
    assert_eq!(outcome.dimension, 56);
    assert_eq!(outcome.support_t, "9/20");
    assert_eq!(outcome.verified_scope, "localized_weil_positivity_T_9_20");
    let report = outcome.schur_report.expect("Schur report");
    assert_eq!(report.even.dimension, 28);
    assert_eq!(report.odd.dimension, 28);
}

#[test]
fn exact_prime_profile_accepts_nineteen_fortieths_dimension_68() {
    let fixture = exact_prime_fixture_for("19", "40", "19/40", 68);
    let certificate = CertificateJson::from_json_str(&fixture.to_string()).expect("valid fixture");
    let outcome = certificate.verify().expect("verification runs");
    assert!(outcome.passed);
    assert_eq!(outcome.dimension, 68);
    assert_eq!(outcome.support_t, "19/40");
    assert_eq!(outcome.verified_scope, "localized_weil_positivity_T_19_40");
    let report = outcome.schur_report.expect("Schur report");
    assert_eq!(report.even.dimension, 34);
    assert_eq!(report.odd.dimension, 34);
}

#[test]
fn exact_prime_profile_rejects_mixed_whitelist_pair() {
    let fixture = exact_prime_fixture_for("2", "5", "2/5", 32);
    assert!(CertificateJson::from_json_str(&fixture.to_string()).is_err());
}

#[test]
fn exact_prime_profile_rejects_mixed_seventeen_fortieths_pair() {
    let fixture = exact_prime_fixture_for("17", "40", "17/40", 40);
    assert!(CertificateJson::from_json_str(&fixture.to_string()).is_err());
}

#[test]
fn exact_prime_profile_rejects_mixed_nine_twentieths_pair() {
    let fixture = exact_prime_fixture_for("9", "20", "9/20", 48);
    assert!(CertificateJson::from_json_str(&fixture.to_string()).is_err());
}

#[test]
fn exact_prime_profile_rejects_mixed_nineteen_fortieths_pair() {
    let fixture = exact_prime_fixture_for("19", "40", "19/40", 64);
    assert!(CertificateJson::from_json_str(&fixture.to_string()).is_err());
}

#[test]
fn exact_prime_profile_rejects_wrong_factor() {
    let mut fixture = exact_prime_fixture();
    fixture["tail_bound"]["factor"]["num"] = json!("2");
    assert!(CertificateJson::from_json_str(&fixture.to_string()).is_err());
}

#[test]
fn exact_prime_profile_rejects_nonzero_cross_parity_entry() {
    let mut fixture = exact_prime_fixture();
    let entries = fixture["matrix"]["entries"]
        .as_array_mut()
        .expect("entries");
    let index_01 = 1;
    entries[index_01]["lo_num"] = json!("1");
    entries[index_01]["hi_num"] = json!("1");
    let index_10 = 32;
    entries[index_10]["lo_num"] = json!("1");
    entries[index_10]["hi_num"] = json!("1");
    assert!(CertificateJson::from_json_str(&fixture.to_string()).is_err());
}

#[test]
fn exact_prime_profile_rejects_singular_witness() {
    let mut fixture = exact_prime_fixture();
    fixture["schur_proof"]["even_witness"]["entries"][0]["num"] = json!("0");
    assert!(CertificateJson::from_json_str(&fixture.to_string()).is_err());
}

#[test]
fn exact_prime_profile_rejects_nonpositive_complement_bound() {
    let mut fixture = exact_prime_fixture();
    fixture["constants"]["c_T"] = point_interval(10);
    assert!(CertificateJson::from_json_str(&fixture.to_string()).is_err());
}

#[test]
fn exact_prime_profile_distinguishes_theorem_failure() {
    let mut fixture = exact_prime_fixture();
    fixture["matrix"]["entries"][0]["lo_num"] = json!("-1");
    fixture["matrix"]["entries"][0]["hi_num"] = json!("-1");
    let certificate = CertificateJson::from_json_str(&fixture.to_string()).expect("valid contract");
    let outcome = certificate.verify().expect("verification runs");
    assert!(!outcome.passed);
    assert!(outcome.schur_report.is_some());
}
