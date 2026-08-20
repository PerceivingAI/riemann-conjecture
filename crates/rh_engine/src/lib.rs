//! High-performance native calculation engine for Riemann Hypothesis prime-trace and turning-scale investigations.

pub mod bins;
pub mod laguerre;
pub mod sieve;
pub mod summation;
pub mod trace;

pub use bins::{compute_range_bins, BinEntry, RangeBinResult};
pub use laguerre::{laguerre_alpha, laguerre_l1, laguerre_l1_batch};
pub use sieve::{higher_prime_powers, sieve_segment, simple_sieve, PrimePower};
pub use summation::NeumaierSum;
pub use trace::{compute_prime_trace, TraceEntry, TraceResult};
