import Smooth4PC.AugmentationCocone

namespace Smooth4PC

/-!
Local stabilization–retraction in the pre-quotient foam category.

For one extra framed tensor factor the identities are
`χ_{i, r+e_i} ∘ ψ_i^[0] = 0` and `χ_{i, r+e_i} ∘ ψ_i^[1] = χ_{i, r}`.
They are the rank-two Frobenius counit evaluations
`(ε ⊗ ε)Δ(1) = 0` and `(ε ⊗ ε)Δ(X) = 1`, together with their iterated
forms.  No split-unknot hypothesis is used, and nothing here identifies a
tensor factor with an embedded T73 component.
-/

/-- Local closure of one tensor factor by the rank-two Frobenius counit. -/
def localCounit : FrobeniusBasis → ℚ := epsilon

@[simp] theorem localCounit_one : localCounit .one = 0 := rfl

@[simp] theorem localCounit_X : localCounit .X = 1 := rfl

/-- The MWW pair-addition core `(ε ⊗ ε) Δ`. -/
def doubleCounitDelta (basis : FrobeniusBasis) : ℚ :=
  epsilonWords (delta basis)

theorem doubleCounitDelta_one : doubleCounitDelta .one = 0 := by
  simp [doubleCounitDelta, delta, epsilonWords, epsilonTensor, epsilon]

theorem doubleCounitDelta_X : doubleCounitDelta .X = 1 := by
  simp [doubleCounitDelta, delta, epsilonWords, epsilonTensor, epsilon]

/-- Undotted local insertion is killed by every positive iterated counit. -/
theorem localStabilization_psi0 (b : Nat) (hb : 0 < b) :
    epsilonWords (iteratedDelta b .one) = 0 :=
  epsilon_iteratedDelta_one_eq_zero b hb

/-- Dotted local insertion recovers the previous counit state. -/
theorem localStabilization_psi1 (b : Nat) (hb : 0 < b) :
    epsilonWords (iteratedDelta b .X) = 1 :=
  epsilon_iteratedDelta_X_eq_one b hb

/-- The two local stabilization–retraction identities, packaged. -/
theorem localStabilization (b : Nat) (hb : 0 < b) :
    epsilonWords (iteratedDelta b .one) = 0 ∧
      epsilonWords (iteratedDelta b .X) = 1 :=
  ⟨localStabilization_psi0 b hb, localStabilization_psi1 b hb⟩

end Smooth4PC
