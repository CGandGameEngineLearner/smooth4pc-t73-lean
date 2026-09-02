import Mathlib

namespace Smooth4PC

/-!
The local comparison between the normalized weight-one `U_q(sl_2)` braid
operator and the unreduced Burau block used by the public T73 computation.
No candidate-specific geometry is asserted here.
-/

/-- The normalized weight-one checked R-matrix, written on the two basis
vectors whose single down-spin is in the left or right position. -/
def normalizedWeightOneR {K : Type*} [Field K] (q : K) (value : K × K) : K × K :=
  ((1 - q⁻¹ * q⁻¹) * value.1 + q⁻¹ * value.2, q⁻¹ * value.1)

/-- The position-dependent basis scaling from the tensor basis to the Burau
basis. -/
def burauBasisToTensor {K : Type*} [Field K] (q : K) (value : K × K) : K × K :=
  (value.1, q⁻¹ * value.2)

def tensorBasisToBurau {K : Type*} [Field K] (q : K) (value : K × K) : K × K :=
  (value.1, q * value.2)

/-- After `t=q^-2` and the displayed diagonal basis change, the normalized
R-matrix is exactly the positive unreduced Burau block. -/
theorem normalizedWeightOneR_eq_burau
    {K : Type*} [Field K] (q : K) (hq : q ≠ 0) (x y : K) :
    tensorBasisToBurau q
        (normalizedWeightOneR q (burauBasisToTensor q (x, y))) =
      ((1 - q⁻¹ * q⁻¹) * x + (q⁻¹ * q⁻¹) * y, x) := by
  simp [tensorBasisToBurau, normalizedWeightOneR, burauBasisToTensor, hq]
  field_simp

/-- The block used for a positive Artin generator. -/
def burauPositive {K : Type*} [Field K] (t : K) (value : K × K) : K × K :=
  ((1 - t) * value.1 + t * value.2, value.1)

/-- The block used by the public script for a negative Artin generator. -/
def burauNegative {K : Type*} [Field K] (t : K) (value : K × K) : K × K :=
  (value.2, t⁻¹ * value.1 + (1 - t⁻¹) * value.2)

theorem burauPositive_at_one
    {K : Type*} [Field K] (value : K × K) :
    burauPositive 1 value = (value.2, value.1) := by
  rcases value with ⟨x, y⟩
  simp [burauPositive]

theorem burauNegative_at_one
    {K : Type*} [Field K] (value : K × K) :
    burauNegative 1 value = (value.2, value.1) := by
  rcases value with ⟨x, y⟩
  simp [burauNegative]

theorem burauPositive_negative_cancel
    {K : Type*} [Field K] (t : K) (ht : t ≠ 0) (value : K × K) :
    burauPositive t (burauNegative t value) = value := by
  rcases value with ⟨x, y⟩
  simp [burauPositive, burauNegative]
  field_simp
  ring

theorem burauNegative_positive_cancel
    {K : Type*} [Field K] (t : K) (ht : t ≠ 0) (value : K × K) :
    burauNegative t (burauPositive t value) = value := by
  rcases value with ⟨x, y⟩
  simp [burauPositive, burauNegative]
  field_simp
  ring

end Smooth4PC
