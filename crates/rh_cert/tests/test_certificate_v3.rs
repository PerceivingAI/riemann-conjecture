//! v3 closed admission, malformed inputs and mathematically negative exact control.
//! The full 192-dimensional positive replay is an explicit bounded integration run.

use std::fs;
use std::path::Path;

use num_bigint::BigInt;
use num_rational::BigRational;
use serde_json::Value;

use rh_cert::gershgorin::verify_congruence_gershgorin;
use rh_cert::{CertificateV3, DispatchedCertificate, RationalInterval, RationalIntervalMatrix};

fn read_actual_research() -> Value {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let path = root.join(
        "computations/2026-10-17T222400Z-v3-research-bundle/data/certificate-v3-research.json",
    );
    serde_json::from_str(&fs::read_to_string(path).expect("v3 research fixture")).unwrap()
}

#[test]
fn actual_v3_research_structure_does_not_admit_theorem() {
    let doc = read_actual_research();
    let text = doc.to_string();
    let cert = CertificateV3::from_json_str(&text).expect("research structure");
    assert!(cert.verify().is_err());
    let dispatched = DispatchedCertificate::from_json_str(&text).expect("v3 dispatch");
    assert!(dispatched.verify().is_err());
}

#[test]
fn altered_v3_mathematical_parameters_rejected() {
    let mut doc = read_actual_research();
    doc["eta"]["num"] = Value::String("3".to_string());
    assert!(CertificateV3::from_json_str(&doc.to_string()).is_err());
    let mut doc = read_actual_research();
    doc["active_terms"] = serde_json::json!([2]);
    assert!(CertificateV3::from_json_str(&doc.to_string()).is_err());
    let mut doc = read_actual_research();
    doc["generator_metadata"]["git_dirty"] = serde_json::json!(false);
    assert!(CertificateV3::from_json_str(&doc.to_string()).is_err());
}

#[test]
fn altered_v3_matrix_and_witness_rejected() {
    let mut doc = read_actual_research();
    doc["low_A_triangular"][0][1] = serde_json::json!(["1", "1"]);
    assert!(CertificateV3::from_json_str(&doc.to_string()).is_err());
    let mut doc = read_actual_research();
    doc["mu_dyadic"][0] = Value::String("0".to_string());
    assert!(CertificateV3::from_json_str(&doc.to_string()).is_err());
    let mut doc = read_actual_research();
    doc["witness_numerators"][0][1] = Value::String("1".to_string());
    assert!(CertificateV3::from_json_str(&doc.to_string()).is_err());
}

#[test]
fn valid_negative_exact_matrix_is_mathematical_failure_not_parse_failure() {
    // Test the exact rational primitive used by v3, with structurally valid
    // mathematical NEGATIVE data. The admission/source gates are not bypassed.
    let negative = RationalInterval::new(
        BigRational::from_integer(BigInt::from(-1)),
        BigRational::from_integer(BigInt::from(-1)),
    )
    .unwrap();
    let matrix = RationalIntervalMatrix::new(1, vec![vec![negative]]).unwrap();
    let witness = vec![vec![BigRational::from_integer(BigInt::from(1))]];
    let outcome = verify_congruence_gershgorin(&matrix, &witness).unwrap();
    assert!(!outcome.is_positive_definite);
}
