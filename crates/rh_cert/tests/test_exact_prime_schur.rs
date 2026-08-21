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

fn exact_prime_fixture() -> Value {
    json!({
        "format": "rh-weil-certificate-v1",
        "claim": "synthetic exact-prime verifier fixture",
        "claim_profile": "exact_prime_legendre_schur",
        "support_T": {"num": "7", "den": "20", "frac": "7/20"},
        "basis": {"type": "legendre", "dimension": 32, "domain": "[-1, 1]"},
        "parity_sector": "both",
        "dimension": 32,
        "constants": {
            "c2": point_interval(0),
            "c_T": point_interval(0),
            "rho_R": point_interval(0)
        },
        "matrix": interval_matrix(32, 1),
        "tail_bound": {
            "type": "legendre_component_gram_schur",
            "harmonic_index": 32,
            "factor": {"num": "3", "den": "1"}
        },
        "schur_proof": {
            "residual_order": 32,
            "GV": interval_matrix(32, 0),
            "G2": interval_matrix(32, 0),
            "GR": interval_matrix(32, 0),
            "even_witness": exact_identity(16),
            "odd_witness": exact_identity(16)
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
