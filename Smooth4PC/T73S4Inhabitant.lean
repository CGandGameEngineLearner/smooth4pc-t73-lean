import Smooth4PC.T73S4Control

namespace Smooth4PC.T73

/-!
Empty-link control packaging of E12.  The graded functor is `EmptyKhQ` on
every label, so this is the standard-sphere reduction, not the Johnson
candidate.  `IsHomotopySphere` is `False` on every label: this universe
does not supply Iwaki's homotopy-sphere conclusion.  `ExternalGeometry`
remains uninhabited.
-/

inductive EmptyLinkManifold where
  | ball
  | sphere
  | unusedLabel
  deriving DecidableEq, Repr

noncomputable def emptyLinkUniverse : Universe where
  Manifold := EmptyLinkManifold
  G := fun _ q => EmptyKhQ q
  candidate := EmptyLinkManifold.unusedLabel
  S4 := EmptyLinkManifold.sphere
  IsHomotopySphere := fun _ => False
  Diffeomorphic := fun x y => x = y

noncomputable def emptyLinkS4Reduction :
    S4ReductionData emptyLinkUniverse where
  B4 := EmptyLinkManifold.ball
  evalB4 := fun q => LinearEquiv.refl ℚ (EmptyKhQ q)
  attach4 := fun q => LinearEquiv.refl ℚ (EmptyKhQ q)

theorem emptyLink_s4ComputedDegreeZero
    (x : emptyLinkUniverse.G emptyLinkUniverse.S4 computedDegree) :
    x = 0 :=
  s4ComputedDegreeZero_of_reduction emptyLinkS4Reduction x

theorem emptyLink_candidate_module (q : Int) :
    emptyLinkUniverse.G emptyLinkUniverse.candidate q = EmptyKhQ q :=
  rfl

theorem emptyLink_sphere_module (q : Int) :
    emptyLinkUniverse.G emptyLinkUniverse.S4 q = EmptyKhQ q :=
  rfl

end Smooth4PC.T73
