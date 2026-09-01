import Smooth4PC.T73External

namespace Smooth4PC.T73

/-- A concrete zero-dimensional rational module. -/
abbrev ZeroQModule := ModuleCat.of ℚ (Fin 0 → ℚ)

/-- The rational empty-link module, concentrated in quantum degree zero. -/
def EmptyKhQ (q : Int) : ModuleCat ℚ :=
  if q = 0 then ModuleCat.of ℚ ℚ else ZeroQModule

/-- The two precise reductions needed for the standard-sphere support claim. -/
structure S4ReductionData (u : Universe) where
  B4 : u.Manifold
  evalB4 : ∀ q : Int, u.G B4 q ≃ₗ[ℚ] EmptyKhQ q
  attach4 : ∀ q : Int, u.G B4 q ≃ₗ[ℚ] u.G u.S4 q

theorem emptyKhQ_subsingleton (q : Int) (hq : q ≠ 0) :
    Subsingleton (EmptyKhQ q) := by
  rw [EmptyKhQ, if_neg hq]
  infer_instance

/-- Evaluation in `B⁴`, followed by the four-handle equivalence, forces every
nonzero quantum degree of the standard `S⁴` module to vanish. -/
theorem s4DegreeZero_of_reduction {u : Universe}
    (data : S4ReductionData u) (q : Int) (hq : q ≠ 0)
    (x : u.G u.S4 q) : x = 0 := by
  let y : u.G data.B4 q := (data.attach4 q).symm x
  have hTarget : data.evalB4 q y = 0 := by
    letI : Subsingleton (EmptyKhQ q) := emptyKhQ_subsingleton q hq
    exact Subsingleton.elim _ _
  have hy : y = 0 := by
    apply (data.evalB4 q).injective
    simpa using hTarget
  calc
    x = data.attach4 q y := by simp [y]
    _ = 0 := by rw [hy]; simp

theorem s4ComputedDegreeZero_of_reduction {u : Universe}
    (data : S4ReductionData u) (x : u.G u.S4 computedDegree) : x = 0 :=
  s4DegreeZero_of_reduction data computedDegree computedDegree_ne_zero x

end Smooth4PC.T73
