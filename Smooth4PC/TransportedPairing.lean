import Mathlib

namespace Smooth4PC

/-!
Simultaneous coordinate transport for an operator, vector and covector.  This
is the algebra required by physical-copy Reynolds normalization; transporting
only one of the three objects is deliberately not represented.
-/

noncomputable section

def transportedEndomorphism {V : Type*}
    [AddCommGroup V] [Module ℚ V]
    (Q : V ≃ₗ[ℚ] V) (K : V →ₗ[ℚ] V) : V →ₗ[ℚ] V :=
  Q.symm.toLinearMap.comp (K.comp Q.toLinearMap)

def transportedVector {V : Type*}
    [AddCommGroup V] [Module ℚ V]
    (Q : V ≃ₗ[ℚ] V) (value : V) : V :=
  Q.symm value

def transportedRow {V : Type*}
    [AddCommGroup V] [Module ℚ V]
    (Q : V ≃ₗ[ℚ] V) (row : V →ₗ[ℚ] ℚ) : V →ₗ[ℚ] ℚ :=
  row.comp Q.toLinearMap

/-- A matrix coefficient is exactly invariant when the operator, vector and
row are transported together. -/
theorem simultaneousTransport_pairing
    {V : Type*} [AddCommGroup V] [Module ℚ V]
    (Q : V ≃ₗ[ℚ] V) (K : V →ₗ[ℚ] V) (row : V →ₗ[ℚ] ℚ) (value : V) :
    transportedRow Q row
        (transportedEndomorphism Q K (transportedVector Q value)) =
      row (K value) := by
  simp [transportedRow, transportedEndomorphism, transportedVector]

/-- The normalized average of a nonempty finite family of identical rational
values is that value. -/
theorem normalized_identical_average
    (count : Nat) (hcount : 0 < count) (value : ℚ) :
    (count : ℚ)⁻¹ * (∑ _index ∈ Finset.range count, value) = value := by
  rw [Finset.sum_const, Finset.card_range, nsmul_eq_mul]
  field_simp

end

end Smooth4PC
