//! Shared conformance and whole-certificate verification tests.

use std::fs;
use std::path::Path;
use std::process::Command;

use rh_cert::cert::CertificateJson;
use serde_json::Value;

fn apply_operations(base: &Value, operations: &[Value]) -> Value {
    let mut certificate = base.clone();
    for operation in operations {
        let path = operation["path"].as_array().expect("operation path");
        let (last, parents) = path.split_last().expect("non-empty operation path");
        let mut target = &mut certificate;
        for part in parents {
            target = match part {
                Value::String(key) => target
                    .as_object_mut()
                    .and_then(|object| object.get_mut(key))
                    .expect("object path"),
                Value::Number(index) => target
                    .as_array_mut()
                    .and_then(|array| array.get_mut(index.as_u64().expect("array index") as usize))
                    .expect("array path"),
                _ => panic!("unsupported path element"),
            };
        }

        match operation["op"].as_str().expect("operation name") {
            "set" => match last {
                Value::String(key) => {
                    target
                        .as_object_mut()
                        .expect("set object")
                        .insert(key.clone(), operation["value"].clone());
                }
                Value::Number(index) => {
                    target.as_array_mut().expect("set array")
                        [index.as_u64().expect("array index") as usize] =
                        operation["value"].clone();
                }
                _ => panic!("unsupported set path"),
            },
            "delete" => match last {
                Value::String(key) => {
                    target.as_object_mut().expect("delete object").remove(key);
                }
                Value::Number(index) => {
                    target
                        .as_array_mut()
                        .expect("delete array")
                        .remove(index.as_u64().expect("array index") as usize);
                }
                _ => panic!("unsupported delete path"),
            },
            other => panic!("unknown operation: {other}"),
        }
    }
    certificate
}

fn conformance_corpus_text() -> String {
    let path = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("..")
        .join("tests")
        .join("certificate_conformance.json");
    fs::read_to_string(path).expect("read conformance corpus")
}

#[test]
fn shared_conformance_corpus_matches_rust_validator() {
    let corpus_text = conformance_corpus_text();
    let corpus: Value = serde_json::from_str(&corpus_text).expect("parse conformance corpus");
    let base = &corpus["base_certificate"];

    for case in corpus["cases"].as_array().expect("cases") {
        let name = case["name"].as_str().expect("case name");
        let certificate = apply_operations(
            base,
            case["operations"].as_array().expect("case operations"),
        );
        let serialized = serde_json::to_string(&certificate).expect("serialize certificate");
        let parsed = CertificateJson::from_json_str(&serialized);
        let expected_valid = case["valid"].as_bool().expect("valid flag");
        assert_eq!(parsed.is_ok(), expected_valid, "{name}: {parsed:?}");

        if let Ok(certificate) = parsed {
            let outcome = certificate.verify().expect("verification runs");
            let expected_pass = case["verification_passes"]
                .as_bool()
                .expect("valid case has verification_passes");
            assert_eq!(outcome.passed, expected_pass, "{name}: {outcome:?}");
        }
    }
}

#[test]
fn tail_lower_bound_is_absorbed_before_ldl() {
    let corpus_text = conformance_corpus_text();
    let corpus: Value = serde_json::from_str(&corpus_text).expect("parse conformance corpus");
    let case = corpus["cases"]
        .as_array()
        .expect("cases")
        .iter()
        .find(|case| case["name"] == "tail absorption destroys positivity")
        .expect("tail regression case");
    let certificate = apply_operations(
        &corpus["base_certificate"],
        case["operations"].as_array().expect("operations"),
    );

    let certificate =
        CertificateJson::from_json_str(&certificate.to_string()).expect("valid certificate");
    let outcome = certificate.verify().expect("verification runs");
    assert!(!outcome.passed);
    assert_eq!(outcome.tail_lower_bound, "-2/1");
    assert_eq!(
        outcome
            .ldl_report
            .as_ref()
            .expect("LDL report")
            .min_diagonal_lower_bound
            .to_string(),
        "-1"
    );
}

#[test]
fn cli_exit_codes_distinguish_theorem_failure_from_contract_error() {
    let corpus_text = conformance_corpus_text();
    let corpus: Value = serde_json::from_str(&corpus_text).expect("parse conformance corpus");
    let cases = corpus["cases"].as_array().expect("cases");
    let executable = env!("CARGO_BIN_EXE_rh_cert");
    let temp_root = std::env::temp_dir();

    let theorem_case = cases
        .iter()
        .find(|case| case["name"] == "tail absorption destroys positivity")
        .expect("theorem failure case");
    let theorem_certificate = apply_operations(
        &corpus["base_certificate"],
        theorem_case["operations"].as_array().expect("operations"),
    );
    let theorem_path = temp_root.join(format!(
        "rh-cert-theorem-failure-{}.json",
        std::process::id()
    ));
    fs::write(&theorem_path, theorem_certificate.to_string()).expect("write theorem fixture");
    let theorem_output = Command::new(executable)
        .args(["verify", "--cert"])
        .arg(&theorem_path)
        .arg("--json")
        .output()
        .expect("run theorem failure");
    assert_eq!(theorem_output.status.code(), Some(1));
    let theorem_json: Value =
        serde_json::from_slice(&theorem_output.stdout).expect("parse theorem output");
    assert_eq!(theorem_json["passed"], false);

    let invalid_case = cases
        .iter()
        .find(|case| case["name"] == "unknown basis")
        .expect("contract failure case");
    let invalid_certificate = apply_operations(
        &corpus["base_certificate"],
        invalid_case["operations"].as_array().expect("operations"),
    );
    let invalid_path = temp_root.join(format!(
        "rh-cert-contract-failure-{}.json",
        std::process::id()
    ));
    fs::write(&invalid_path, invalid_certificate.to_string()).expect("write invalid fixture");
    let invalid_output = Command::new(executable)
        .args(["verify", "--cert"])
        .arg(&invalid_path)
        .output()
        .expect("run contract failure");
    assert_eq!(invalid_output.status.code(), Some(2));

    fs::remove_file(theorem_path).expect("remove theorem fixture");
    fs::remove_file(invalid_path).expect("remove invalid fixture");
}
