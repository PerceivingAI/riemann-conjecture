/-
Exact rational arithmetic and interval primitives for certificate verification.
-/

structure ExactRat where
  num : Int
  den : Int
  den_pos : 0 < den
deriving Repr, DecidableEq

namespace ExactRat

def ofFrac (n : Int) (d : Int) (h : 0 < d := by decide) : ExactRat :=
  ⟨n, d, h⟩

def lt (a b : ExactRat) : Prop :=
  a.num * b.den < b.num * a.den

def le (a b : ExactRat) : Prop :=
  a.num * b.den ≤ b.num * a.den

instance (a b : ExactRat) : Decidable (a.lt b) :=
  inferInstanceAs (Decidable (a.num * b.den < b.num * a.den))

instance (a b : ExactRat) : Decidable (a.le b) :=
  inferInstanceAs (Decidable (a.num * b.den ≤ b.num * a.den))

def isPositive (a : ExactRat) : Prop :=
  0 < a.num

instance (a : ExactRat) : Decidable (a.isPositive) :=
  inferInstanceAs (Decidable (0 < a.num))

def add (a b : ExactRat) : ExactRat where
  num := a.num * b.den + b.num * a.den
  den := a.den * b.den
  den_pos := Int.mul_pos a.den_pos b.den_pos

def sub (a b : ExactRat) : ExactRat where
  num := a.num * b.den - b.num * a.den
  den := a.den * b.den
  den_pos := Int.mul_pos a.den_pos b.den_pos

def mul (a b : ExactRat) : ExactRat where
  num := a.num * b.num
  den := a.den * b.den
  den_pos := Int.mul_pos a.den_pos b.den_pos

def sqr (a : ExactRat) : ExactRat where
  num := a.num * a.num
  den := a.den * a.den
  den_pos := Int.mul_pos a.den_pos a.den_pos

def neg (a : ExactRat) : ExactRat where
  num := -a.num
  den := a.den
  den_pos := a.den_pos

end ExactRat

structure ExactRatInterval where
  lo : ExactRat
  hi : ExactRat
  valid : lo.le hi
deriving Repr, DecidableEq

namespace ExactRatInterval

def point (x : ExactRat) : ExactRatInterval where
  lo := x
  hi := x
  valid := by
    show x.num * x.den ≤ x.num * x.den
    omega

def contains (I : ExactRatInterval) (x : ExactRat) : Prop :=
  I.lo.le x ∧ x.le I.hi

instance (I : ExactRatInterval) (x : ExactRat) : Decidable (I.contains x) :=
  inferInstanceAs (Decidable (I.lo.le x ∧ x.le I.hi))

def isStrictlyPositive (I : ExactRatInterval) : Prop :=
  I.lo.isPositive

instance (I : ExactRatInterval) : Decidable (I.isStrictlyPositive) :=
  inferInstanceAs (Decidable (I.lo.isPositive))

theorem strictly_positive_point (x : ExactRat) (h : x.isPositive) :
    (point x).isStrictlyPositive :=
  h

end ExactRatInterval
