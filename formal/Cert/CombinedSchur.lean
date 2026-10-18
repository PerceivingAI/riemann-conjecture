import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

/-!
Elementary finite-dimensional inequalities supporting the separately versioned
combined mixed-Gram Schur reduction.

These are scalar soundness lemmas used in row-radius Loewner inflation and
the Young residual bound. This file does NOT formalize Suzuki's transcendental
source identity, Arb semantics, or an admitted Weil-form theorem.
-/

namespace CombinedSchurCert

theorem two_mul_le_squares (x y : ℝ) :
    2 * x * y ≤ x ^ 2 + y ^ 2 := by
  nlinarith [sq_nonneg (x - y)]

theorem abs_twice_mul_le_squares (x y : ℝ) :
    2 * |x * y| ≤ x ^ 2 + y ^ 2 := by
  rw [abs_mul]
  have h := two_mul_le_squares (|x|) (|y|)
  nlinarith [sq_abs x, sq_abs y]

theorem young_exact (η x y : ℝ) (hη : 0 < η) :
    (x + y) ^ 2 ≤ (1 + η) * x ^ 2 + (1 + η⁻¹) * y ^ 2 := by
  have hne : η ≠ 0 := ne_of_gt hη
  have hs : 0 ≤ (η * x - y) ^ 2 / η := div_nonneg (sq_nonneg _) hη.le
  have heq : (1 + η) * x ^ 2 + (1 + η⁻¹) * y ^ 2 -
      (x + y) ^ 2 = (η * x - y) ^ 2 / η := by
    field_simp
    ring
  linarith

end CombinedSchurCert
