import Smooth4PC.AugmentationCocone

namespace Smooth4PC

/-!
Reynolds averaging over physical-copy placements.

If every placement returns the same cubic scalar, the orbit-weighted average
equals that scalar.  This is the finite algebra of the cable-state formula
(25) for arbitrary copy-count vectors; it does not construct geometric movies
and does not restrict the average to a finite sample of `r ∈ ℕ^5`.
-/

/-- Weighted sum of placement values. -/
def weightedSum : List (Nat × ℚ) → ℚ
  | [] => 0
  | (w, v) :: rest => (w : ℚ) * v + weightedSum rest

/-- Total orbit weight of a placement list. -/
def weightTotal : List (Nat × ℚ) → Nat
  | [] => 0
  | (w, _) :: rest => w + weightTotal rest

/-- Reynolds average; empty or zero-weight lists are sent to zero. -/
def reynoldsAverage (items : List (Nat × ℚ)) : ℚ :=
  if weightTotal items = 0 then 0
  else weightedSum items / (weightTotal items : ℚ)

theorem weightedSum_const (value : ℚ) :
    ∀ items : List (Nat × ℚ),
      (∀ item ∈ items, item.2 = value) →
        weightedSum items = (weightTotal items : ℚ) * value
  | [], _ => by simp [weightedSum, weightTotal]
  | (w, v) :: rest, h => by
      have hv : v = value := h (w, v) (by simp)
      have hrest :
          weightedSum rest = (weightTotal rest : ℚ) * value :=
        weightedSum_const value rest fun item him =>
          h item (by simp [him])
      simp [weightedSum, weightTotal, hv, hrest, add_mul]

/-- A constant cubic is recovered by any positive-weight Reynolds average. -/
theorem reynoldsAverage_const (value : ℚ) (items : List (Nat × ℚ))
    (hpos : weightTotal items ≠ 0)
    (hconst : ∀ item ∈ items, item.2 = value) :
    reynoldsAverage items = value := by
  have hsum := weightedSum_const value items hconst
  simp [reynoldsAverage, hpos, hsum]

/-- Orbit-weighted Reynolds average of a constant cubic is that cubic. -/
theorem reynoldsAverage_orbitConst (value : ℚ)
    (copyCounts occupancy : List Nat)
    (hpresent : orbitPresent copyCounts occupancy) :
    reynoldsAverage [(orbitSize copyCounts occupancy, value)] = value := by
  apply reynoldsAverage_const
  · simp [weightTotal]
    simpa [orbitPresent] using hpresent
  · intro item him
    simp at him
    simp [him]

end Smooth4PC
