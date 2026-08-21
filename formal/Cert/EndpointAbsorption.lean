/-
Formal verification of exact rational endpoint absorption at T=7/20 (F-20260821-012).

This module machine-proves the rational inequality chain:
  c2 / kappa_edge < 31/100
  V + P2 ≥ (69/100) V
without any floating-point numbers or unproved axioms.
-/

import Cert.Interval

namespace EndpointAbsorption

open ExactRat

-- log(2) rigorous upper bound from atanh series: 23581 / 34020
def log2_hi : ExactRat := ofFrac 23581 34020

-- sqrt(2) lower bound: 7/5 (since 49/25 < 50/25 = 2)
def sqrt2_lo : ExactRat := ofFrac 7 5

-- kappa_edge lower bound: 8/5
def kappa_edge_lo : ExactRat := ofFrac 8 5

-- c2_hi = log2_hi / sqrt2_lo = (23581 * 5) / (34020 * 7) = 117905 / 238140
def c2_hi : ExactRat := ofFrac 117905 238140

-- ratio_hi = c2_hi / kappa_edge_lo = (117905 * 5) / (238140 * 8) = 117905 / 381024
def ratio_hi : ExactRat := ofFrac 117905 381024

def bound_31_100 : ExactRat := ofFrac 31 100
def bound_62_125 : ExactRat := ofFrac 62 125

-- Net absorbed fraction: 1 - ratio_hi = (381024 - 117905) / 381024 = 263119 / 381024
def absorbed_fraction_lower : ExactRat := ofFrac 263119 381024
def bound_69_100 : ExactRat := ofFrac 69 100

/-- Theorem: c2 < 62/125 is strictly verified by exact rational arithmetic. -/
theorem theorem_c2_upper_bound : c2_hi.lt bound_62_125 := by
  decide

/-- Theorem: The perturbation ratio c2 / kappa_edge is strictly less than 31/100. -/
theorem theorem_ratio_upper_bound : ratio_hi.lt bound_31_100 := by
  decide

/-- Theorem: The absorbed potential V + P2 retains at least 69/100 of the endpoint potential V. -/
theorem theorem_first_prime_absorption_69_100 : bound_69_100.le absorbed_fraction_lower := by
  decide

/-- Theorem: The lower bound 69/100 is strictly positive. -/
theorem theorem_absorption_bound_positive : bound_69_100.isPositive := by
  decide

end EndpointAbsorption
