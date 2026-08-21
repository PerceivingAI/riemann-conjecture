import Cert.Interval
import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.LinearAlgebra.Matrix.Nondegenerate

/-!
Arbitrary finite-dimensional soundness of exact and interval-certified LDL factorizations.
-/

open Matrix

namespace LDL

variable {n : Type*} [Fintype n] [LinearOrder n]

def IsUnitLowerTriangular (L : Matrix n n ℚ) : Prop :=
  Matrix.IsLowerTriangular L ∧ ∀ i, L i i = 1

def RationalPosDef (A : Matrix n n ℚ) : Prop :=
  ∀ ⦃x : n → ℚ⦄, x ≠ 0 → 0 < x ⬝ᵥ (A *ᵥ x)

theorem unitLower_mulVec_injective
    {L : Matrix n n ℚ} (hL : IsUnitLowerTriangular L) :
    Function.Injective L.mulVec := by
  have hdet : L.det ≠ 0 := by
    rw [Matrix.det_of_isLowerTriangular L hL.1]
    simp [hL.2]
  exact Matrix.mulVec_injective_of_det_ne_zero hdet

theorem unitLower_transpose_mulVec_injective
    {L : Matrix n n ℚ} (hL : IsUnitLowerTriangular L) :
    Function.Injective L.transpose.mulVec := by
  have hdet : L.transpose.det ≠ 0 := by
    rw [Matrix.det_transpose]
    rw [Matrix.det_of_isLowerTriangular L hL.1]
    simp [hL.2]
  exact Matrix.mulVec_injective_of_det_ne_zero hdet

theorem diagonal_quadratic_form
    (d y : n → ℚ) :
    y ⬝ᵥ (Matrix.diagonal d *ᵥ y) = ∑ i, d i * (y i) ^ 2 := by
  simp only [dotProduct, Matrix.mulVec_diagonal, pow_two]
  apply Finset.sum_congr rfl
  intro i _
  ring

theorem diagonal_quadratic_form_positive
    {d y : n → ℚ} (hd : ∀ i, 0 < d i) (hy : y ≠ 0) :
    0 < y ⬝ᵥ (Matrix.diagonal d *ᵥ y) := by
  rw [diagonal_quadratic_form]
  obtain ⟨i, hi⟩ := Function.ne_iff.mp hy
  exact Finset.sum_pos'
    (fun j _ => mul_nonneg (hd j).le (sq_nonneg (y j)))
    ⟨i, Finset.mem_univ i, mul_pos (hd i) (sq_pos_of_ne_zero hi)⟩

theorem ldl_posDef
    {A L : Matrix n n ℚ} {d : n → ℚ}
    (hfactor : A = L * Matrix.diagonal d * L.transpose)
    (hL : IsUnitLowerTriangular L)
    (hd : ∀ i, 0 < d i) :
    RationalPosDef A := by
  intro x hx
  let y := L.transpose *ᵥ x
  have hy : y ≠ 0 := by
    intro hyzero
    apply hx
    apply unitLower_transpose_mulVec_injective hL
    simpa [y] using hyzero
  have hpositive := diagonal_quadratic_form_positive hd hy
  rw [hfactor, ← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec,
    Matrix.dotProduct_mulVec, ← Matrix.mulVec_transpose]
  exact hpositive

omit [Fintype n] [LinearOrder n] in
theorem interval_diagonal_positive
    {d : n → ℚ} {D : n → RatInterval}
    (henclosed : ∀ i, RatInterval.contains (D i) (d i))
    (hstrict : ∀ i, RatInterval.isStrictlyPositive (D i)) :
    ∀ i, 0 < d i :=
  fun i => RatInterval.strictly_positive_sound (henclosed i) (hstrict i)

theorem interval_ldl_posDef
    {A L : Matrix n n ℚ} {d : n → ℚ} {D : n → RatInterval}
    (hfactor : A = L * Matrix.diagonal d * L.transpose)
    (hL : IsUnitLowerTriangular L)
    (henclosed : ∀ i, RatInterval.contains (D i) (d i))
    (hstrict : ∀ i, RatInterval.isStrictlyPositive (D i)) :
    RationalPosDef A :=
  ldl_posDef hfactor hL (interval_diagonal_positive henclosed hstrict)


end LDL
