//! Zero-float independent exact rational certificate verifier for the Riemann Hypothesis research harness.
//!
//! This crate implements exact rational interval arithmetic and verified LDL^T matrix
//! decomposition to validate mathematical certificates produced by Python/Arb without
//! using any floating-point numbers or native GMP/MPFR bindings.

#![deny(clippy::float_arithmetic)]

pub mod cert;
pub mod dispatch;
pub mod gershgorin;
pub mod interval;
pub mod ldl;
pub mod v2;

pub use cert::{CertificateError, CertificateJson, VerificationOutcome, EXPECTED_FORMAT_V1};
pub use dispatch::DispatchedCertificate;
pub use gershgorin::{GershgorinBlockReport, GershgorinError};
pub use interval::{IntervalError, RationalInterval};
pub use ldl::{LdlError, LdlVerificationReport, RationalIntervalMatrix};
pub use v2::{CertificateV2, EXPECTED_FORMAT_V2, V2_ALLOWED_CONFIGURATIONS};
