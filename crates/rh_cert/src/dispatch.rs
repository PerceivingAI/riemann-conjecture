//! Certificate-format dispatch without changing the frozen v1 verifier path.

use std::fs;
use std::path::Path;

use serde_json::Value;

use crate::cert::{CertificateError, CertificateJson, VerificationOutcome, EXPECTED_FORMAT_V1};
use crate::v2::{CertificateV2, EXPECTED_FORMAT_V2};

#[derive(Debug, Clone)]
pub enum DispatchedCertificate {
    V1(Box<CertificateJson>),
    V2(Box<CertificateV2>),
}

impl DispatchedCertificate {
    pub fn from_file<P: AsRef<Path>>(path: P) -> Result<Self, CertificateError> {
        let content = fs::read_to_string(path)?;
        Self::from_json_str(&content)
    }

    pub fn from_json_str(json_str: &str) -> Result<Self, CertificateError> {
        let header: Value = serde_json::from_str(json_str)?;
        let format = header
            .get("format")
            .and_then(Value::as_str)
            .ok_or_else(|| CertificateError::Validation {
                field: "$.format".to_string(),
                message: "must be a string".to_string(),
            })?;

        match format {
            EXPECTED_FORMAT_V1 => CertificateJson::from_json_str(json_str)
                .map(Box::new)
                .map(Self::V1),
            EXPECTED_FORMAT_V2 => CertificateV2::from_json_str(json_str)
                .map(Box::new)
                .map(Self::V2),
            other => Err(CertificateError::Validation {
                field: "$.format".to_string(),
                message: format!(
                    "unsupported certificate format '{other}'; expected {EXPECTED_FORMAT_V1} or {EXPECTED_FORMAT_V2}"
                ),
            }),
        }
    }

    pub fn verify(&self) -> Result<VerificationOutcome, CertificateError> {
        match self {
            Self::V1(certificate) => certificate.verify(),
            Self::V2(certificate) => certificate.verify(),
        }
    }
}
