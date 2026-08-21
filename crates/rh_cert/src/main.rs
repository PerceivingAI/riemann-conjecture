//! CLI binary for independent exact rational certificate verification.

use std::path::PathBuf;
use std::process::ExitCode;

use clap::{Parser, Subcommand};
use rh_cert::cert::CertificateJson;

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
}

fn main() -> ExitCode {
    let cli = Cli::parse();

    match cli.command {
        Commands::Verify { cert, json } => match CertificateJson::from_file(&cert) {
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
