Overall correctness: correct.

Actual pinned-reuse implementation checks both ancestor byte hashes, accepted receipt binding, unchanged low payload and source fingerprints, copied reference containment, and the exact complement condition. It freshly reconstructs residual polynomials and all new heads, while explicitly retaining ancestor provenance.

The native integer contraction’s error bound includes center/radius cross terms, radius products, and weight uncertainty. Its head denominator \(2^{3B+4}\), `wm*G` alignment by `B+4`, and outward-rounding shift `2*B+4` are correct. Wider intervals remain valid through the subsequent Loewner conversion.

Confidence: 0.96. No additional defects found; no execution performed.
