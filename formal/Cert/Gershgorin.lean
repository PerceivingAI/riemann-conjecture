import Cert.LDL
import Mathlib.Analysis.Matrix.PosDef
import Mathlib.LinearAlgebra.Matrix.Gershgorin

/-!
Soundness of the strict Gershgorin positivity judge used by the exact-prime
Schur certificate.

The executable verifier first applies an exact rational invertible congruence
witness and then proves every resulting symmetric interval matrix has a
strictly positive row Gershgorin margin.  This file records the underlying
finite-dimensional theorem: a real symmetric matrix whose diagonal entry in
every row exceeds the sum of the absolute off-diagonal entries is positive
definite; positive definiteness is preserved backwards through an invertible
congruence.
-/

open Matrix
open scoped BigOperators

namespace GershgorinCert

variable {n : Type*} [Fintype n] [DecidableEq n]

def StrictPositiveRowDominant (A : Matrix n n ℝ) : Prop :=
  ∀ i, (∑ j ∈ Finset.univ.erase i, |A i j|) < A i i

 theorem strictPositiveRowDominant_posDef
    {A : Matrix n n ℝ}
    (hSymm : A.IsSymm)
    (hDom : StrictPositiveRowDominant A) :
    A.PosDef := by
  have hHerm : A.IsHermitian := by
    simpa using hSymm
  rw [hHerm.posDef_iff_eigenvalues_pos]
  intro i
  let lam : ℝ := hHerm.eigenvalues i
  have hspec : lam ∈ spectrum ℝ A := by
    simpa [lam] using hHerm.eigenvalues_mem_spectrum_real i
  have hspecLin : lam ∈ spectrum ℝ A.toLin' := by
    simpa using hspec
  have hlam : Module.End.HasEigenvalue A.toLin' lam :=
    (Module.End.hasEigenvalue_iff_mem_spectrum).2 hspecLin
  obtain ⟨k, hk⟩ := eigenvalue_mem_ball hlam
  have hk' : |lam - A k k| ≤ ∑ j ∈ Finset.univ.erase k, |A k j| := by
    simpa [Real.dist_eq] using hk
  have hrow := hDom k
  have hlower : A k k - (∑ j ∈ Finset.univ.erase k, |A k j|) ≤ lam := by
    have habs : A k k - lam ≤ ∑ j ∈ Finset.univ.erase k, |A k j| := by
      exact (le_abs_self (A k k - lam)).trans (by simpa [abs_sub_comm] using hk')
    linarith
  dsimp [lam] at hlower ⊢
  linarith

 theorem posDef_of_invertible_congruence
    {A C : Matrix n n ℝ}
    (hC : IsUnit C)
    (hCong : (C * A * C.transpose).PosDef) :
    A.PosDef := by
  apply (hC.posDef_star_right_conjugate_iff (x := A)).mp
  simpa [star_eq_conjTranspose] using hCong

end GershgorinCert
