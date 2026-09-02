import Mathlib

namespace Smooth4PC

/-!
The cubic associated-graded calculation used by the T73 comparison.  This
file contains no geometric assertion: it proves that an operator or row whose
first nonzero coefficient is cubic is insensitive, at cubic order, to a
transport whose degree-zero term is the identity.
-/

noncomputable section

/-- Coefficients through order three of a rational-linear map. -/
structure CubicLinearJet (V W : Type*)
    [AddCommGroup V] [Module ℚ V] [AddCommGroup W] [Module ℚ W] where
  c0 : V →ₗ[ℚ] W
  c1 : V →ₗ[ℚ] W
  c2 : V →ₗ[ℚ] W
  c3 : V →ₗ[ℚ] W

/-- The degree-three coefficient of the composite of two jets. -/
def cubicComposite {U V W : Type*}
    [AddCommGroup U] [Module ℚ U]
    [AddCommGroup V] [Module ℚ V]
    [AddCommGroup W] [Module ℚ W]
    (left : CubicLinearJet V W) (right : CubicLinearJet U V) : U →ₗ[ℚ] W :=
  left.c0.comp right.c3 +
    left.c1.comp right.c2 +
      left.c2.comp right.c1 +
        left.c3.comp right.c0

/-- A jet begins in order three. -/
def CubicLinearJet.StartsAtThree {V W : Type*}
    [AddCommGroup V] [Module ℚ V] [AddCommGroup W] [Module ℚ W]
    (jet : CubicLinearJet V W) : Prop :=
  jet.c0 = 0 ∧ jet.c1 = 0 ∧ jet.c2 = 0

/-- An endomorphism jet has the identity in degree zero. -/
def CubicLinearJet.IdentityConstant {V : Type*}
    [AddCommGroup V] [Module ℚ V] (jet : CubicLinearJet V V) : Prop :=
  jet.c0 = LinearMap.id

/-- Postcomposing a cubic-leading map by `Id + O(h)` does not alter its
degree-three coefficient. -/
theorem cubicComposite_right_identity_transport
    {V W : Type*}
    [AddCommGroup V] [Module ℚ V]
    [AddCommGroup W] [Module ℚ W]
    (anomaly : CubicLinearJet V W) (transport : CubicLinearJet V V)
    (ha : anomaly.StartsAtThree) (ht : transport.IdentityConstant) :
    cubicComposite anomaly transport = anomaly.c3 := by
  rcases ha with ⟨h0, h1, h2⟩
  rw [CubicLinearJet.IdentityConstant] at ht
  simp [cubicComposite, h0, h1, h2, ht]

/-- Precomposing a cubic-leading endomorphism by `Id + O(h)` does not alter
its degree-three coefficient. -/
theorem cubicComposite_left_identity_transport
    {V W : Type*}
    [AddCommGroup V] [Module ℚ V]
    [AddCommGroup W] [Module ℚ W]
    (transport : CubicLinearJet W W) (anomaly : CubicLinearJet V W)
    (ht : transport.IdentityConstant) (ha : anomaly.StartsAtThree) :
    cubicComposite transport anomaly = anomaly.c3 := by
  rcases ha with ⟨h0, h1, h2⟩
  rw [CubicLinearJet.IdentityConstant] at ht
  simp [cubicComposite, h0, h1, h2, ht]

/-- Both a source transport and a target transport that are the identity in
degree zero
target transport are invisible to the cubic leading coefficient. -/
theorem cubicComposite_two_identity_transports
    {V W : Type*}
    [AddCommGroup V] [Module ℚ V]
    [AddCommGroup W] [Module ℚ W]
    (targetTransport : CubicLinearJet W W)
    (anomaly : CubicLinearJet V W)
    (sourceTransport : CubicLinearJet V V)
    (ht : targetTransport.IdentityConstant)
    (ha : anomaly.StartsAtThree)
    (hs : sourceTransport.IdentityConstant) :
    cubicComposite targetTransport
        { c0 := (0 : V →ₗ[ℚ] W)
          c1 := 0
          c2 := 0
          c3 := cubicComposite anomaly sourceTransport } = anomaly.c3 := by
  have hright := cubicComposite_right_identity_transport anomaly sourceTransport ha hs
  have hinner :
      CubicLinearJet.StartsAtThree
        { c0 := (0 : V →ₗ[ℚ] W)
          c1 := 0
          c2 := 0
          c3 := cubicComposite anomaly sourceTransport } := by
    simp [CubicLinearJet.StartsAtThree]
  have hleft := cubicComposite_left_identity_transport targetTransport
    { c0 := (0 : V →ₗ[ℚ] W)
      c1 := 0
      c2 := 0
      c3 := cubicComposite anomaly sourceTransport } ht hinner
  exact hleft.trans hright

end

end Smooth4PC
