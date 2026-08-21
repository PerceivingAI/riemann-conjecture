import Mathlib

/-!
Exact rational intervals and enclosure-preserving operations used by the certificate verifier.
-/

structure RatInterval where
  lo : ℚ
  hi : ℚ
  valid : lo ≤ hi
deriving Repr, DecidableEq

namespace RatInterval

def contains (I : RatInterval) (x : ℚ) : Prop :=
  I.lo ≤ x ∧ x ≤ I.hi

def point (x : ℚ) : RatInterval :=
  ⟨x, x, le_rfl⟩

def neg (I : RatInterval) : RatInterval :=
  ⟨-I.hi, -I.lo, neg_le_neg I.valid⟩

def add (I J : RatInterval) : RatInterval :=
  ⟨I.lo + J.lo, I.hi + J.hi, add_le_add I.valid J.valid⟩

def sub (I J : RatInterval) : RatInterval :=
  ⟨I.lo - J.hi, I.hi - J.lo, sub_le_sub I.valid J.valid⟩

def absBound (I : RatInterval) : ℚ :=
  max |I.lo| |I.hi|

theorem absBound_nonneg (I : RatInterval) : 0 ≤ I.absBound :=
  le_max_of_le_left (abs_nonneg I.lo)

theorem abs_le_absBound {I : RatInterval} {x : ℚ} (hx : I.contains x) :
    |x| ≤ I.absBound :=
  abs_le_max_abs_abs hx.1 hx.2

def mul (I J : RatInterval) : RatInterval where
  lo := -(I.absBound * J.absBound)
  hi := I.absBound * J.absBound
  valid := by
    have h := mul_nonneg I.absBound_nonneg J.absBound_nonneg
    linarith

def inv (I : RatInterval) (hzero : ¬ I.contains 0) : RatInterval where
  lo := 1 / I.hi
  hi := 1 / I.lo
  valid := by
    by_cases hpos : 0 < I.lo
    · exact one_div_le_one_div_of_le hpos I.valid
    · have hneg : I.hi < 0 := by
        by_contra hn
        apply hzero
        constructor <;> linarith
      exact one_div_le_one_div_of_neg_of_le hneg I.valid

def div (I J : RatInterval) (hzero : ¬ J.contains 0) : RatInterval :=
  I.mul (J.inv hzero)

def sqr (I : RatInterval) : RatInterval :=
  I.mul I

def isStrictlyPositive (I : RatInterval) : Prop :=
  0 < I.lo

theorem point_contains (x : ℚ) : (point x).contains x :=
  ⟨le_rfl, le_rfl⟩

theorem neg_contains {I : RatInterval} {x : ℚ} (hx : I.contains x) :
    I.neg.contains (-x) :=
  ⟨neg_le_neg hx.2, neg_le_neg hx.1⟩

theorem add_contains {I J : RatInterval} {x y : ℚ}
    (hx : I.contains x) (hy : J.contains y) :
    (I.add J).contains (x + y) :=
  ⟨add_le_add hx.1 hy.1, add_le_add hx.2 hy.2⟩

theorem sub_contains {I J : RatInterval} {x y : ℚ}
    (hx : I.contains x) (hy : J.contains y) :
    (I.sub J).contains (x - y) :=
  ⟨sub_le_sub hx.1 hy.2, sub_le_sub hx.2 hy.1⟩

theorem mul_contains {I J : RatInterval} {x y : ℚ}
    (hx : I.contains x) (hy : J.contains y) :
    (I.mul J).contains (x * y) := by
  have hxabs : |x| ≤ I.absBound := abs_le_absBound hx
  have hyabs : |y| ≤ J.absBound := abs_le_absBound hy
  have hproduct : |x * y| ≤ I.absBound * J.absBound := by
    rw [abs_mul]
    exact mul_le_mul hxabs hyabs (abs_nonneg y) I.absBound_nonneg
  exact abs_le.mp hproduct

theorem inv_contains {I : RatInterval} {x : ℚ}
    (hx : I.contains x) (hzero : ¬ I.contains 0) :
    (I.inv hzero).contains (1 / x) := by
  by_cases hpos : 0 < I.lo
  · have hxpos : 0 < x := hpos.trans_le hx.1
    exact
      ⟨one_div_le_one_div_of_le hxpos hx.2,
       one_div_le_one_div_of_le hpos hx.1⟩
  · have hineg : I.hi < 0 := by
      by_contra hn
      apply hzero
      constructor <;> linarith
    have hxneg : x < 0 := hx.2.trans_lt hineg
    exact
      ⟨one_div_le_one_div_of_neg_of_le hineg hx.2,
       one_div_le_one_div_of_neg_of_le hxneg hx.1⟩

theorem div_contains {I J : RatInterval} {x y : ℚ}
    (hx : I.contains x) (hy : J.contains y) (hzero : ¬ J.contains 0) :
    (I.div J hzero).contains (x / y) := by
  simpa [div, div_eq_mul_inv] using
    mul_contains hx (inv_contains hy hzero)

theorem sqr_contains {I : RatInterval} {x : ℚ} (hx : I.contains x) :
    I.sqr.contains (x ^ 2) := by
  simpa [sqr, pow_two] using mul_contains hx hx

theorem strictly_positive_sound {I : RatInterval} {x : ℚ}
    (hx : I.contains x) (hpos : I.isStrictlyPositive) :
    0 < x :=
  hpos.trans_le hx.1

end RatInterval
