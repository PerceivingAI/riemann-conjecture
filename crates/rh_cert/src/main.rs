//! CLI binary for independent exact rational certificate verification.

use std::path::PathBuf;
use std::process::ExitCode;

use clap::{Parser, Subcommand};
use rh_cert::{CertificateV3, DispatchedCertificate};

#[derive(Parser, Debug)]
#[command(name = "rh_cert")]
#[command(about = "Zero-float independent exact rational certificate verifier")]
#[command(version = "0.1.0")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Verify a mathematical certificate JSON file
    Verify {
        /// Path to the certificate JSON file
        #[arg(short, long, value_name = "FILE")]
        cert: PathBuf,

        /// Output verification outcome as raw JSON
        #[arg(long)]
        json: bool,
    },
    /// Research-only v3 exact arithmetic; NEVER admits a theorem or proves source enclosures
    VerifyCandidateV3 {
        #[arg(short, long, value_name = "FILE")]
        cert: PathBuf,
        #[arg(long)]
        json: bool,
    },
}

fn main() -> ExitCode {
    let cli = Cli::parse();

    match cli.command {
        Commands::VerifyCandidateV3 { cert, json } => {
            match CertificateV3::from_file(&cert).and_then(|c| c.verify_research_arithmetic()) {
                Ok(report) => {
                    if json {
                        println!(
                            "{}",
                            serde_json::to_string_pretty(&report)
                                .unwrap_or_else(|_| "{}".to_string())
                        );
                    } else {
                        println!(
                            "V3 RESEARCH-ONLY rational Schur: {}",
                            report.mathematical_status
                        );
                        println!("Exact margin: {}", report.exact_margin);
                        println!("UNADMITTED; SOURCE ANALYTIC ENCLOSURES NOT CHECKED BY RUST");
                    }
                    if report.exact_margin_positive {
                        ExitCode::SUCCESS
                    } else {
                        ExitCode::from(1)
                    }
                }
                Err(err) => {
                    eprintln!("v3 research rational verification error: {err}");
                    ExitCode::from(2)
                }
            }
        }
        Commands::Verify { cert, json } => match DispatchedCertificate::from_file(&cert) {
            Ok(cert_obj) => match cert_obj.verify() {
                Ok(outcome) => {
                    if json {
                        println!(
                            "{}",
                            serde_json::to_string_pretty(&outcome)
                                .unwrap_or_else(|_| "{}".to_string())
                        );
                    } else {
                        println!("============================================================");
                        println!("RH Exact Rational Certificate Verifier (rh_cert)");
                        println!("============================================================");
                        println!("Certificate: {:?}", cert);
                        println!("Claim:       {}", outcome.claim);
                        println!("Format:      {}", outcome.format);
                        println!("Dimension:   {}x{}", outcome.dimension, outcome.dimension);
                        println!("Support T:   {}", outcome.support_t);
                        println!("Profile:     {}", outcome.claim_profile);
                        println!("Scope:       {}", outcome.verified_scope);
                        println!("Basis:       {}", outcome.basis_type);
                        println!("Parity:      {}", outcome.parity_sector);
                        println!("Tail rule:   {}", outcome.tail_rule);
                        println!("Tail bound:  {}", outcome.tail_lower_bound);
                        if let Some(report) = &outcome.ldl_report {
                            println!("Symmetric:   {}", report.is_symmetric);
                            println!("Positive:    {}", report.is_positive_definite);
                            println!("Min D bound: {}", report.min_diagonal_lower_bound);
                        }
                        if let Some(report) = &outcome.schur_report {
                            println!("Schur positive: {}", report.is_positive_definite);
                            println!("Schur factor:   {}", report.schur_factor);
                            println!("Even margin:    {}", report.even.min_margin);
                            println!("Odd margin:     {}", report.odd.min_margin);
                        }
                        println!("------------------------------------------------------------");
                        for note in &outcome.notes {
                            println!("{}", note);
                        }
                        println!("============================================================");
                        if outcome.passed {
                            println!("VERIFICATION RESULT: [ PASS ]");
                        } else {
                            println!("VERIFICATION RESULT: [ FAIL ]");
                        }
                        println!("============================================================");
                    }

                    if outcome.passed {
                        ExitCode::SUCCESS
                    } else {
                        ExitCode::from(1)
                    }
                }
                Err(err) => {
                    eprintln!("ERROR during verification execution: {err}");
                    ExitCode::from(2)
                }
            },
            Err(err) => {
                eprintln!("ERROR loading/parsing certificate from '{:?}': {err}", cert);
                ExitCode::from(2)
            }
        },
    }
}
