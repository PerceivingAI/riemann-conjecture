use std::fs;
use std::process::Command;

use rh_cert::dispatch::DispatchedCertificate;
use rh_cert::v2::{CertificateV2, V2_ALLOWED_CONFIGURATIONS};
use serde_json::{json, Value};

fn interval(value: &str) -> Value {
    json!({
        "lo_num": value,
        "lo_den": "1",
        "hi_num": value,
        "hi_den": "1"
    })
}

fn rational_interval(lo_num: &str, lo_den: &str, hi_num: &str, hi_den: &str) -> Value {
    json!({
        "lo_num": lo_num,
        "lo_den": lo_den,
        "hi_num": hi_num,
        "hi_den": hi_den
    })
}

fn matrix(dimension: usize, diagonal: i64) -> Value {
    let mut entries = Vec::with_capacity(dimension * dimension);
    for row in 0..dimension {
        for col in 0..dimension {
            let value = if row == col { diagonal } else { 0 };
            entries.push(json!({
                "row": row,
                "col": col,
                "lo_num": value.to_string(),
                "lo_den": "1",
                "hi_num": value.to_string(),
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
        "log_m": interval("1"),
        "tau": rational_interval("3", "2", "3", "2"),
        "von_mangoldt": interval("1"),
        "coefficient": rational_interval("1", "10", "1", "10"),
        "compressed_shift_norm_bound": interval("1"),
        "complement_contribution": rational_interval("1", "10", "1", "10")
    })
}

fn fixture() -> Value {
    let dimension = 4usize;
    json!({
        "format": "rh-weil-certificate-v2",
        "claim": "rust-v2-integration-fixture",
        "claim_profile": "multi_prime_power_legendre_schur",
        "support_T": {"num": "2", "den": "3", "frac": "2/3"},
        "basis": {"type": "legendre", "dimension": dimension, "domain": "[-1, 1]"},
        "parity_sector": "both",
        "dimension": dimension,
        "constants": {"c_T": interval("0"), "rho_R": interval("0")},
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
            "generator": "rust-integration-test",
            "script": "test_certificate_v2.rs",
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
fn v2_production_theorem_whitelist_is_empty() {
    assert!(V2_ALLOWED_CONFIGURATIONS.is_empty());
}

#[test]
fn dispatch_accepts_v2_structure_but_verify_rejects_unauthorized_pair() {
    let cert =
        DispatchedCertificate::from_json_str(&fixture().to_string()).expect("valid v2 structure");
    let error = cert
        .verify()
        .expect_err("v2 whitelist is intentionally empty");
    assert!(error.to_string().contains("not admitted"));
}

#[test]
fn v2_rejects_missing_term() {
    let mut value = fixture();
    value["arithmetic_terms"]
        .as_array_mut()
        .expect("terms")
        .pop();
    let error = CertificateV2::from_json_str(&value.to_string()).expect_err("missing term");
    assert!(error.to_string().contains("exactly two active terms"));
}

#[test]
fn v2_rejects_duplicate_term() {
    let mut value = fixture();
    value["arithmetic_terms"][1] = term(2);
    let error = CertificateV2::from_json_str(&value.to_string()).expect_err("duplicate term");
    assert!(error.to_string().contains("strictly increasing"));
}

#[test]
fn v2_rejects_substituted_term() {
    let mut value = fixture();
    value["arithmetic_terms"][1] = json!({
        "m": 5,
        "base_prime": 5,
        "exponent": 1,
        "log_m": interval("1"),
        "tau": rational_interval("3", "2", "3", "2"),
        "von_mangoldt": interval("1"),
        "coefficient": rational_interval("1", "10", "1", "10"),
        "compressed_shift_norm_bound": interval("1"),
        "complement_contribution": rational_interval("1", "10", "1", "10")
    });
    let error = CertificateV2::from_json_str(&value.to_string()).expect_err("substituted term");
    assert!(error.to_string().contains("exactly active terms [2,3]"));
}

#[test]
fn v2_rejects_unsorted_terms() {
    let mut value = fixture();
    value["arithmetic_terms"] = json!([term(3), term(2)]);
    let error = CertificateV2::from_json_str(&value.to_string()).expect_err("unsorted terms");
    assert!(error.to_string().contains("strictly increasing"));
}

#[test]
fn v2_rejects_wrong_prime_power_identity() {
    let mut value = fixture();
    value["arithmetic_terms"][1]["base_prime"] = json!(2);
    let error = CertificateV2::from_json_str(&value.to_string()).expect_err("wrong identity");
    assert!(error.to_string().contains("base_prime^exponent"));
}

#[test]
fn v2_rejects_understated_serialized_prime_loss() {
    let mut value = fixture();
    value["arithmetic_terms"][0]["complement_contribution"] =
        rational_interval("1", "100", "1", "100");
    let error = CertificateV2::from_json_str(&value.to_string()).expect_err("understated loss");
    assert!(error.to_string().contains("independently derived"));
}

#[test]
fn v2_rejects_nonpositive_independently_derived_mu() {
    let mut value = fixture();
    value["constants"]["c_T"] = interval("10");
    let error = CertificateV2::from_json_str(&value.to_string()).expect_err("nonpositive mu");
    assert!(error.to_string().contains("mu_N must be strictly positive"));
}

#[test]
fn v2_rejects_nonzero_cross_parity_entry() {
    let mut value = fixture();
    value["matrix"]["entries"][1]["lo_num"] = json!("1");
    value["matrix"]["entries"][1]["hi_num"] = json!("1");
    value["matrix"]["entries"][4]["lo_num"] = json!("1");
    value["matrix"]["entries"][4]["hi_num"] = json!("1");
    let error = CertificateV2::from_json_str(&value.to_string()).expect_err("cross parity");
    assert!(error.to_string().contains("opposite-parity"));
}

#[test]
fn v2_rejects_singular_exact_witness() {
    let mut value = fixture();
    value["schur_proof"]["even_witness"]["entries"][0]["num"] = json!("0");
    let error = CertificateV2::from_json_str(&value.to_string()).expect_err("singular witness");
    assert!(error.to_string().contains("diagonal must be nonzero"));
}

#[test]
fn v2_rejects_wrong_factor_or_unverified_factor_claim() {
    let mut value = fixture();
    value["tail_bound"]["factor"]["num"] = json!("2");
    assert!(CertificateV2::from_json_str(&value.to_string()).is_err());

    let mut value = fixture();
    value["tail_bound"]["factor_claim"] = json!("unverified");
    assert!(CertificateV2::from_json_str(&value.to_string()).is_err());
}

#[test]
fn cli_dispatch_returns_contract_failure_for_structurally_valid_but_unauthorized_v2() {
    let executable = env!("CARGO_BIN_EXE_rh_cert");
    let path = std::env::temp_dir().join(format!(
        "rh-cert-v2-unauthorized-{}.json",
        std::process::id()
    ));
    fs::write(&path, fixture().to_string()).expect("write fixture");
    let output = Command::new(executable)
        .args(["verify", "--cert"])
        .arg(&path)
        .arg("--json")
        .output()
        .expect("run verifier");
    assert_eq!(output.status.code(), Some(2));
    assert!(String::from_utf8_lossy(&output.stderr).contains("not admitted"));
    fs::remove_file(path).expect("remove fixture");
}
