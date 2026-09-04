import Mathlib

namespace Smooth4PC

/-!
Filtered cubic naturality for a pairing `ell(h) A(h) u(h)`.

If `A(h) ∈ h^3 End(E)`, `u(h) = u0 + O(h)` and `ell(h) = ell0 + O(h)`, then
the coefficient of `h^3` is `ell0 (A3 u0)`.  Simultaneous conjugation by a
degree-zero isomorphism leaves that scalar unchanged.

This file contains no geometric assertion.
-/

noncomputable section

/-- Coefficients through order three of an `E`-valued series. -/
structure FilteredVec (V : Type*) [AddCommGroup V] [Module ℚ V] where
  c0 : V
  c1 : V
  c2 : V
  c3 : V

/-- Coefficients through order three of an endomorphism series. -/
structure FilteredEnd (V : Type*) [AddCommGroup V] [Module ℚ V] where
  c0 : V →ₗ[ℚ] V
  c1 : V →ₗ[ℚ] V
  c2 : V →ₗ[ℚ] V
  c3 : V →ₗ[ℚ] V

/-- Coefficients through order three of a covector series. -/
structure FilteredRow (V : Type*) [AddCommGroup V] [Module ℚ V] where
  c0 : V →ₗ[ℚ] ℚ
  c1 : V →ₗ[ℚ] ℚ
  c2 : V →ₗ[ℚ] ℚ
  c3 : V →ₗ[ℚ] ℚ

/-- An endomorphism series begins in order three. -/
def FilteredEnd.StartsAtThree {V : Type*}
    [AddCommGroup V] [Module ℚ V] (A : FilteredEnd V) : Prop :=
  A.c0 = 0 ∧ A.c1 = 0 ∧ A.c2 = 0

/-- The degree-three coefficient of `ell(h) A(h) u(h)`. -/
def cubicScalar {V : Type*}
    [AddCommGroup V] [Module ℚ V]
    (A : FilteredEnd V) (u : FilteredVec V) (ell : FilteredRow V) : ℚ :=
  ell.c0 (A.c0 u.c3 + A.c1 u.c2 + A.c2 u.c1 + A.c3 u.c0) +
    ell.c1 (A.c0 u.c2 + A.c1 u.c1 + A.c2 u.c0) +
      ell.c2 (A.c0 u.c1 + A.c1 u.c0) +
        ell.c3 (A.c0 u.c0)

/-- If `A(h) ∈ h^3 End(E)`, then `[h^3] ell(h) A(h) u(h) = ell0 (A3 u0)`. -/
theorem cubicScalar_of_order_three {V : Type*}
    [AddCommGroup V] [Module ℚ V]
    (A : FilteredEnd V) (u : FilteredVec V) (ell : FilteredRow V)
    (hA : A.StartsAtThree) :
    cubicScalar A u ell = ell.c0 (A.c3 u.c0) := by
  rcases hA with ⟨h0, h1, h2⟩
  simp [cubicScalar, h0, h1, h2]

/-- Public operator `P ∘ A ∘ P⁻¹`. -/
def conjugateEnd {V : Type*}
    [AddCommGroup V] [Module ℚ V]
    (P : V ≃ₗ[ℚ] V) (A : V →ₗ[ℚ] V) : V →ₗ[ℚ] V :=
  P.toLinearMap.comp (A.comp P.symm.toLinearMap)

/-- `W_public = P W_geometric P⁻¹`, `u_public = P u_geometric`,
`ell_public = ell_geometric P⁻¹` leave the pairing unchanged. -/
theorem simultaneousConjugation_pairing {V : Type*}
    [AddCommGroup V] [Module ℚ V]
    (P : V ≃ₗ[ℚ] V) (A : V →ₗ[ℚ] V) (u : V) (ell : V →ₗ[ℚ] ℚ) :
    (ell.comp P.symm.toLinearMap) (conjugateEnd P A (P u)) = ell (A u) := by
  simp [conjugateEnd]

/-- Conjugation of a cubic-leading endomorphism remains cubic-leading, and the
degree-three pairing is invariant. -/
theorem cubicScalar_conjugation_invariant {V : Type*}
    [AddCommGroup V] [Module ℚ V]
    (P : V ≃ₗ[ℚ] V) (A : FilteredEnd V) (u : FilteredVec V) (ell : FilteredRow V)
    (hA : A.StartsAtThree) :
    cubicScalar
        { c0 := conjugateEnd P A.c0
          c1 := conjugateEnd P A.c1
          c2 := conjugateEnd P A.c2
          c3 := conjugateEnd P A.c3 }
        { c0 := P u.c0
          c1 := P u.c1
          c2 := P u.c2
          c3 := P u.c3 }
        { c0 := ell.c0.comp P.symm.toLinearMap
          c1 := ell.c1.comp P.symm.toLinearMap
          c2 := ell.c2.comp P.symm.toLinearMap
          c3 := ell.c3.comp P.symm.toLinearMap }
      = ell.c0 (A.c3 u.c0) := by
  rcases hA with ⟨h0, h1, h2⟩
  let A' : FilteredEnd V :=
    { c0 := conjugateEnd P A.c0
      c1 := conjugateEnd P A.c1
      c2 := conjugateEnd P A.c2
      c3 := conjugateEnd P A.c3 }
  let u' : FilteredVec V :=
    { c0 := P u.c0, c1 := P u.c1, c2 := P u.c2, c3 := P u.c3 }
  let ell' : FilteredRow V :=
    { c0 := ell.c0.comp P.symm.toLinearMap
      c1 := ell.c1.comp P.symm.toLinearMap
      c2 := ell.c2.comp P.symm.toLinearMap
      c3 := ell.c3.comp P.symm.toLinearMap }
  have hA' : A'.StartsAtThree := by
    refine ⟨?_, ?_, ?_⟩
    · simp [A', conjugateEnd, h0]
    · simp [A', conjugateEnd, h1]
    · simp [A', conjugateEnd, h2]
  calc
    cubicScalar
        { c0 := conjugateEnd P A.c0
          c1 := conjugateEnd P A.c1
          c2 := conjugateEnd P A.c2
          c3 := conjugateEnd P A.c3 }
        { c0 := P u.c0
          c1 := P u.c1
          c2 := P u.c2
          c3 := P u.c3 }
        { c0 := ell.c0.comp P.symm.toLinearMap
          c1 := ell.c1.comp P.symm.toLinearMap
          c2 := ell.c2.comp P.symm.toLinearMap
          c3 := ell.c3.comp P.symm.toLinearMap }
      = cubicScalar A' u' ell' := rfl
    _ = ell'.c0 (A'.c3 u'.c0) := cubicScalar_of_order_three A' u' ell' hA'
    _ = (ell.c0.comp P.symm.toLinearMap) (conjugateEnd P A.c3 (P u.c0)) := rfl
    _ = ell.c0 (A.c3 u.c0) := simultaneousConjugation_pairing P A.c3 u.c0 ell.c0

end

end Smooth4PC
