//! CLI for the high-performance Riemann Hypothesis calculation engine.

use clap::{Parser, Subcommand};
use std::fs;
use std::path::Path;

use rh_engine::bins::compute_range_bins;
use rh_engine::trace::compute_prime_trace;

#[derive(Parser)]
#[command(name = "rh_engine")]
#[command(about = "High-performance native calculation engine for Riemann Hypothesis prime-trace analysis", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Compute the prime-Laguerre trace P_n(X) and discrepancy S_n(X) across cutoffs
    PrimeTrace {
        #[arg(long, default_value_t = 3.0)]
        s0: f64,

        #[arg(long, default_value_t = 16)]
        n_max: usize,

        #[arg(long, default_value = "10000,100000,1000000")]
        cutoffs: String,

        #[arg(long, default_value_t = 131072)]
        segment_size: usize,

        #[arg(long)]
        output_json: Option<String>,
    },

    /// Compute turning-scale range decomposition into u = t/(4n) bins
    RangeBins {
        #[arg(long, default_value_t = 3.0)]
        s0: f64,

        #[arg(long, default_value = "8,12,16")]
        n: String,

        #[arg(long, default_value_t = 2_000_000)]
        max_m: u64,

        #[arg(long, default_value = "0,0.25,0.5,0.75,1.0,1.25,1.5")]
        u_bins: String,

        #[arg(long, default_value_t = 1000)]
        simpson_steps: usize,

        #[arg(long)]
        output_json: Option<String>,
    },

    /// Benchmark multi-threaded sieving and recurrence throughput
    Benchmark {
        #[arg(long, default_value_t = 3.0)]
        s0: f64,

        #[arg(long, default_value_t = 16)]
        n_max: usize,

        #[arg(long, default_value = "1000000,10000000,50000000")]
        cutoffs: String,
    },
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::PrimeTrace {
            s0,
            n_max,
            cutoffs,
            segment_size,
            output_json,
        } => {
            let cutoff_list: Vec<u64> = cutoffs
                .split(',')
                .filter_map(|s| s.trim().parse().ok())
                .collect();

            let a = 2.0 * s0 - 1.0;
            let q = -s0 / (s0 - 1.0);
            println!("================================================================================");
            println!("PRIME-LAGUERRE TRACE CALCULATOR (Native Rayon Engine)");
            println!("================================================================================");
            println!("s0={s0:.6}  A={a:.6}  q={q:.6}  |q|={:.6}  max_n={n_max}", q.abs());
            println!("Cutoffs: {:?}", cutoff_list);
            println!();

            let mut all_results = Vec::new();

            for &cutoff in &cutoff_list {
                let res = compute_prime_trace(s0, n_max, cutoff, segment_size);
                println!("--- Cutoff X = {cutoff} ({:.3}s) ---", res.elapsed_secs);
                println!("  n |        P_n(X)        |        Pole(1-q^n)   |        S_n(X)        | |S_n|^(1/n) | |P_n|^(1/n)");
                println!("----+----------------------+----------------------+----------------------+-------------+------------");
                for entry in &res.entries {
                    println!(
                        "{:3} | {:20.10e} | {:20.10e} | {:20.10e} | {:11.6} | {:10.6}",
                        entry.n, entry.p_n, entry.pole_term, entry.s_n, entry.s_n_root, entry.p_n_root
                    );
                }
                println!();
                all_results.push(res);
            }

            if let Some(json_path) = output_json {
                if let Some(parent) = Path::new(&json_path).parent() {
                    let _ = fs::create_dir_all(parent);
                }
                if let Ok(serialized) = serde_json::to_string_pretty(&all_results) {
                    let _ = fs::write(&json_path, serialized);
                    println!("Saved JSON output to: {json_path}");
                }
            }
        }

        Commands::RangeBins {
            s0,
            n,
            max_m,
            u_bins,
            simpson_steps,
            output_json,
        } => {
            let n_list: Vec<usize> = n
                .split(',')
                .filter_map(|s| s.trim().parse().ok())
                .collect();
            let bins_list: Vec<f64> = u_bins
                .split(',')
                .filter_map(|s| s.trim().parse().ok())
                .collect();

            println!("================================================================================");
            println!("RANGE DECOMPOSITION IN TURNING-SCALE u=t/(4n) BINS");
            println!("================================================================================");
            println!("s0={s0:.6}  max_m={max_m}  u_bins={:?}", bins_list);
            println!();

            let mut all_results = Vec::new();

            for &deg in &n_list {
                let res = compute_range_bins(s0, deg, max_m, &bins_list, simpson_steps);
                println!("--- n = {deg} ({:.3}s) ---", res.elapsed_secs);
                println!("   u_bin   |  Discrete Sum (Primes) | Continuous Density Int |      Discrepancy       | Prime Count");
                println!("-----------+------------------------+------------------------+------------------------+------------");
                for b in &res.bins {
                    println!(
                        "[{:4.2},{:4.2}) | {:22.12e} | {:22.12e} | {:22.12e} | {:10}",
                        b.u_lo, b.u_hi, b.discrete_sum, b.continuous_integral, b.discrepancy, b.count_prime_powers
                    );
                }
                println!("-----------+------------------------+------------------------+------------------------+------------");
                println!(
                    "TOTAL      | {:22.12e} | {:22.12e} | {:22.12e} |",
                    res.total_discrete, res.total_continuous, res.total_discrepancy
                );
                println!();
                all_results.push(res);
            }

            if let Some(json_path) = output_json {
                if let Some(parent) = Path::new(&json_path).parent() {
                    let _ = fs::create_dir_all(parent);
                }
                if let Ok(serialized) = serde_json::to_string_pretty(&all_results) {
                    let _ = fs::write(&json_path, serialized);
                    println!("Saved JSON output to: {json_path}");
                }
            }
        }

        Commands::Benchmark { s0, n_max, cutoffs } => {
            let cutoff_list: Vec<u64> = cutoffs
                .split(',')
                .filter_map(|s| s.trim().parse().ok())
                .collect();

            println!("================================================================================");
            println!("BENCHMARK: MULTI-THREADED RAYON SIEVE + BATCH LAGUERRE RECURRENCE");
            println!("================================================================================");
            println!("s0={s0:.6}  max_n={n_max}  threads={}", rayon::current_num_threads());
            println!();

            for &cutoff in &cutoff_list {
                let res = compute_prime_trace(s0, n_max, cutoff, 131072);
                let primes_per_sec = (cutoff as f64) / res.elapsed_secs / 1_000_000.0;
                println!(
                    "Cutoff X = {:10}: elapsed = {:7.3}s | throughput = {:6.2} M items/sec",
                    cutoff, res.elapsed_secs, primes_per_sec
                );
            }
        }
    }
}
