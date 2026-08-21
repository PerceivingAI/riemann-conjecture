import Mathlib.Analysis.Complex.ExponentialBounds

/-!
Analytic and operator-level endpoint absorption at the exact support `T = 7/20`.
-/

namespace EndpointAbsorption

noncomputable section

def T : ℝ := 7 / 20
def log2Lower : ℝ := 842 / 1215
def log2Upper : ℝ := 23581 / 34020
def tau : ℝ := Real.log 2 / T
def epsilon : ℝ := 2 - tau
def kappaEdge : ℝ := (1 / 2) * Real.log (1 / (2 * epsilon))
def c2 : ℝ := Real.log 2 / Real.sqrt 2

theorem log2_atanh_partial_lower :
    (15757912 / 22733865 : ℝ) ≤ Real.log 2 := by
  have h := Real.sum_range_le_log_div
    (x := (1 / 3 : ℝ)) (by norm_num) (by norm_num) 6
  norm_num at h ⊢
  linarith

theorem log2_atanh_partial_upper :
    Real.log 2 ≤ (189095329 / 272806380 : ℝ) := by
  have h := Real.log_div_le_sum_range_add
    (x := (1 / 3 : ℝ)) (by norm_num) (by norm_num) 6
  norm_num at h ⊢
  linarith

theorem log2_lower_bound : log2Lower < Real.log 2 :=
  (by norm_num [log2Lower] : log2Lower < (15757912 / 22733865 : ℝ)).trans_le
    log2_atanh_partial_lower

theorem log2_upper_bound : Real.log 2 < log2Upper :=
  log2_atanh_partial_upper.trans_lt
    (by norm_num [log2Upper] : (189095329 / 272806380 : ℝ) < log2Upper)

theorem sqrt2_lower_bound : (7 / 5 : ℝ) < Real.sqrt 2 := by
  have hsqrt : (Real.sqrt 2) ^ 2 = 2 := by
    norm_num
  have hsqrt_nonneg : 0 ≤ Real.sqrt 2 := Real.sqrt_nonneg 2
  nlinarith

theorem tau_lower_bound : log2Lower / T < tau := by
  exact div_lt_div_of_pos_right log2_lower_bound (by norm_num [T])

theorem tau_upper_bound : tau < log2Upper / T := by
  exact div_lt_div_of_pos_right log2_upper_bound (by norm_num [T])

theorem epsilon_positive : 0 < epsilon := by
  have hlog : Real.log 2 < 2 * T := log2_upper_bound.trans_le (by norm_num [T, log2Upper])
  have htau : tau < 2 := by
    rw [tau, div_lt_iff₀ (by norm_num [T])]
    linarith
  exact sub_pos.mpr htau

theorem epsilon_upper_bound : epsilon < 34 / 1701 := by
  have htau := tau_lower_bound
  norm_num [epsilon, log2Lower, T] at htau ⊢
  linarith

theorem bridge_log_lower_bound : (1 : ℝ) < Real.log (87 / 32) := by
  apply (Real.lt_log_iff_exp_lt (by norm_num)).2
  exact Real.exp_one_lt_d9.trans (by norm_num)

theorem ratio_log_lower_bound : (16 / 5 : ℝ) < Real.log (1701 / 68) := by
  have hpowers : (87 / 32 : ℝ) ^ 16 < (1701 / 68 : ℝ) ^ 5 := by
    norm_num
  have hlogs := Real.strictMonoOn_log
    (Set.mem_Ioi.mpr (by positivity : (0 : ℝ) < (87 / 32) ^ 16))
    (Set.mem_Ioi.mpr (by positivity : (0 : ℝ) < (1701 / 68) ^ 5))
    hpowers
  rw [Real.log_pow, Real.log_pow] at hlogs
  nlinarith [bridge_log_lower_bound]

theorem kappa_edge_lower_bound : (8 / 5 : ℝ) < kappaEdge := by
  have hratio : (1701 / 68 : ℝ) < 1 / (2 * epsilon) := by
    apply (lt_div_iff₀ (by positivity [epsilon_positive])).2
    nlinarith [epsilon_upper_bound]
  have hlogs := Real.strictMonoOn_log
    (Set.mem_Ioi.mpr (by norm_num : (0 : ℝ) < 1701 / 68))
    (Set.mem_Ioi.mpr (by positivity [epsilon_positive] : (0 : ℝ) < 1 / (2 * epsilon)))
    hratio
  dsimp [kappaEdge]
  nlinarith [ratio_log_lower_bound]

theorem c2_positive : 0 < c2 := by
  exact div_pos (Real.log_pos (by norm_num)) (Real.sqrt_pos.2 (by norm_num))

theorem c2_upper_bound : c2 < 62 / 125 := by
  calc
    c2 < log2Upper / Real.sqrt 2 :=
      div_lt_div_of_pos_right log2_upper_bound (Real.sqrt_pos.2 (by norm_num))
    _ < log2Upper / (7 / 5) :=
      div_lt_div_of_pos_left (by norm_num [log2Upper]) (by norm_num) sqrt2_lower_bound
    _ < 62 / 125 := by norm_num [log2Upper]

theorem perturbation_ratio_bound : c2 / kappaEdge < 31 / 100 := by
  have hkappa : 0 < kappaEdge := (by norm_num : (0 : ℝ) < 8 / 5).trans
    kappa_edge_lower_bound
  calc
    c2 / kappaEdge < (62 / 125) / kappaEdge :=
      div_lt_div_of_pos_right c2_upper_bound hkappa
    _ < (62 / 125) / (8 / 5) :=
      div_lt_div_of_pos_left (by norm_num) (by norm_num) kappa_edge_lower_bound
    _ = 31 / 100 := by norm_num

theorem first_prime_absorption
    {α : Type*}
    (energy endpointPotential firstPrime : α → ℝ)
    (henergy : ∀ f, 0 ≤ energy f)
    (hendpoint : ∀ f, kappaEdge * energy f ≤ endpointPotential f)
    (hprime : ∀ f, -(c2 * energy f) ≤ firstPrime f) :
    ∀ f, (69 / 100 : ℝ) * endpointPotential f
      ≤ endpointPotential f + firstPrime f := by
  intro f
  have hkappa : 0 < kappaEdge := (by norm_num : (0 : ℝ) < 8 / 5).trans
    kappa_edge_lower_bound
  have hV : 0 ≤ endpointPotential f :=
    (mul_nonneg hkappa.le (henergy f)).trans (hendpoint f)
  have henergy_le : energy f ≤ endpointPotential f / kappaEdge :=
    (le_div_iff₀ hkappa).2 (by simpa [mul_comm] using hendpoint f)
  have hscaled :
      -(c2 / kappaEdge * endpointPotential f) ≤ -(c2 * energy f) := by
    rw [neg_le_neg_iff]
    calc
      c2 * energy f ≤ c2 * (endpointPotential f / kappaEdge) :=
        mul_le_mul_of_nonneg_left henergy_le c2_positive.le
      _ = c2 / kappaEdge * endpointPotential f := by ring
  have hrelative :
      -(c2 / kappaEdge * endpointPotential f) ≤ firstPrime f :=
    hscaled.trans (hprime f)
  have hratio :
      c2 / kappaEdge * endpointPotential f
        ≤ (31 / 100 : ℝ) * endpointPotential f :=
    mul_le_mul_of_nonneg_right perturbation_ratio_bound.le hV
  nlinarith

end

end EndpointAbsorption
