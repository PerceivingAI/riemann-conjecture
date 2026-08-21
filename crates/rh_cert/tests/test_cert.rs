//! Unit tests for JSON certificate parsing and verification.

use rh_cert::cert::{CertificateError, CertificateJson, EXPECTED_FORMAT_V1};

#[test]
fn test_valid_certificate_verification() {
    let json_str = r#"{
        "format": "rh-weil-certificate-v1",
        "claim": "Synthetic positive 2x2 test matrix",
        "support_T": { "num": 7, "den": 20, "frac": "7/20" },
        "basis": { "type": "legendre", "dimension": 2, "domain": "[-T, T]" },
        "parity_sector": "both",
        "dimension": 2,
        "constants": {},
        "matrix": {
            "dimension": 2,
            "is_symmetric": true,
            "entries": [
                { "row": 0, "col": 0, "lo_num": "4", "lo_den": "1", "hi_num": "4", "hi_den": "1" },
                { "row": 0, "col": 1, "lo_num": "1", "lo_den": "1", "hi_num": "1", "hi_den": "1" },
                { "row": 1, "col": 0, "lo_num": "1", "lo_den": "1", "hi_num": "1", "hi_den": "1" },
                { "row": 1, "col": 1, "lo_num": "3", "lo_den": "1", "hi_num": "3", "hi_den": "1" }
            ]
        },
        "tail_bound": { "type": "none" }
    }"#;

    let cert = CertificateJson::from_json_str(json_str).unwrap();
    assert_eq!(cert.format, EXPECTED_FORMAT_V1);
    assert_eq!(cert.dimension, 2);

    let outcome = cert.verify().unwrap();
    assert!(outcome.passed);
    assert!(outcome.ldl_report.is_positive_definite);
    assert!(outcome.ldl_report.is_symmetric);
}

#[test]
fn test_unsupported_format_rejection() {
    let json_str = r#"{
        "format": "rh-weil-certificate-v0",
        "claim": "Outdated certificate",
        "support_T": { "num": 7, "den": 20, "frac": "7/20" },
        "basis": { "type": "legendre", "dimension": 1, "domain": "[-T, T]" },
        "parity_sector": "both",
        "dimension": 1,
        "constants": {},
        "matrix": {
            "dimension": 1,
            "is_symmetric": true,
            "entries": [
                { "row": 0, "col": 0, "lo_num": "1", "lo_den": "1", "hi_num": "1", "hi_den": "1" }
            ]
        },
        "tail_bound": { "type": "none" }
    }"#;

    let err = CertificateJson::from_json_str(json_str);
    assert!(matches!(err, Err(CertificateError::UnsupportedFormat(_))));
}

#[test]
fn test_dimension_mismatch_rejection() {
    let json_str = r#"{
        "format": "rh-weil-certificate-v1",
        "claim": "Mismatched dimension",
        "support_T": { "num": 7, "den": 20, "frac": "7/20" },
        "basis": { "type": "legendre", "dimension": 2, "domain": "[-T, T]" },
        "parity_sector": "both",
        "dimension": 2,
        "constants": {},
        "matrix": {
            "dimension": 1,
            "is_symmetric": true,
            "entries": [
                { "row": 0, "col": 0, "lo_num": "1", "lo_den": "1", "hi_num": "1", "hi_den": "1" }
            ]
        },
        "tail_bound": { "type": "none" }
    }"#;

    let err = CertificateJson::from_json_str(json_str);
    assert!(matches!(err, Err(CertificateError::DimensionMismatch { .. })));
}

#[test]
fn test_indefinite_certificate_failure() {
    let json_str = r#"{
        "format": "rh-weil-certificate-v1",
        "claim": "Indefinite 2x2 matrix",
        "support_T": { "num": 7, "den": 20, "frac": "7/20" },
        "basis": { "type": "legendre", "dimension": 2, "domain": "[-T, T]" },
        "parity_sector": "both",
        "dimension": 2,
        "constants": {},
        "matrix": {
            "dimension": 2,
            "is_symmetric": true,
            "entries": [
                { "row": 0, "col": 0, "lo_num": "1", "lo_den": "1", "hi_num": "1", "hi_den": "1" },
                { "row": 0, "col": 1, "lo_num": "2", "lo_den": "1", "hi_num": "2", "hi_den": "1" },
                { "row": 1, "col": 0, "lo_num": "2", "lo_den": "1", "hi_num": "2", "hi_den": "1" },
                { "row": 1, "col": 1, "lo_num": "1", "lo_den": "1", "hi_num": "1", "hi_den": "1" }
            ]
        },
        "tail_bound": { "type": "none" }
    }"#;

    let cert = CertificateJson::from_json_str(json_str).unwrap();
    let outcome = cert.verify().unwrap();
    assert!(!outcome.passed);
    assert!(!outcome.ldl_report.is_positive_definite);
}
