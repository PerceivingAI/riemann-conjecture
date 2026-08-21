"""Certificate generation and rigorous interval verification tooling.

This package implements rigorous numerical certificate generation using
python-flint (Arb/ACB/FMPQ). Standard floating-point types (float, numpy)
are strictly prohibited for proof claims and are reserved solely for
preconditioning, heuristic plotting, and basis reconnaissance.
"""

from __future__ import annotations

__version__ = "0.1.0"
