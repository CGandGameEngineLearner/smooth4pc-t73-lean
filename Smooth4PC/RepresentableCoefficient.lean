import Smooth4PC.CoefficientTrace
import Smooth4PC.QuotientEquiv

namespace Smooth4PC

/-!
The coefficient bimodule `(x,y) ↦ Hom(Bx,By)` of a linear autoequivalence
is canonically equivalent to the regular coefficient bimodule.  This is the
abstract Hattori reduction used after, but not in place of, the geometric
product-annulus comparison.
-/

noncomputable section

variable (C : SmallQLinearCategory)

/-- The regular coefficient bimodule of a linear category. -/
def regularCoefficient : CoefficientBimodule C where
  M := C.Hom
  leftAction := LinearMap.flip C.comp
  rightAction := C.comp
  left_id := by
    intro x z m
    exact C.id_comp m
  right_id := by
    intro x y m
    exact C.comp_id m
  left_comp := by
    intro w x y z g f m
    exact C.assoc m g f
  right_comp := by
    intro w x y z g f m
    exact (C.assoc g f m).symm
  actions_commute := by
    intro w x y z f g m
    exact (C.assoc g m f).symm

/-- A rational-linear autofunctor, presented by equivalences on every hom
space.  Object-surjectivity is unnecessary for the coefficient comparison. -/
structure LinearHomAutofunctor where
  obj : C.Obj → C.Obj
  mapEquiv : ∀ {x y}, C.Hom x y ≃ₗ[ℚ] C.Hom (obj x) (obj y)
  map_id : ∀ x, mapEquiv (C.id x) = C.id (obj x)
  map_comp : ∀ {x y z} (g : C.Hom y z) (f : C.Hom x y),
    mapEquiv (C.comp g f) = C.comp (mapEquiv g) (mapEquiv f)

variable {C}

namespace LinearHomAutofunctor

/-- The regular coefficient bimodule transported along `B`. -/
def transportedCoefficient (B : LinearHomAutofunctor C) :
    CoefficientBimodule C where
  M := fun x y => C.Hom (B.obj x) (B.obj y)
  leftAction := by
    intro x y z
    exact (LinearMap.flip C.comp).comp B.mapEquiv.toLinearMap
  rightAction := by
    intro x y z
    exact C.comp.comp B.mapEquiv.toLinearMap
  left_id := by
    intro x z m
    change C.comp m (B.mapEquiv (C.id x)) = m
    rw [B.map_id]
    exact C.id_comp m
  right_id := by
    intro x y m
    change C.comp (B.mapEquiv (C.id y)) m = m
    rw [B.map_id]
    exact C.comp_id m
  left_comp := by
    intro w x y z g f m
    change C.comp m (B.mapEquiv (C.comp g f)) =
      C.comp (C.comp m (B.mapEquiv g)) (B.mapEquiv f)
    rw [B.map_comp]
    exact C.assoc m (B.mapEquiv g) (B.mapEquiv f)
  right_comp := by
    intro w x y z g f m
    change C.comp (B.mapEquiv (C.comp g f)) m =
      C.comp (B.mapEquiv g) (C.comp (B.mapEquiv f) m)
    rw [B.map_comp]
    exact (C.assoc (B.mapEquiv g) (B.mapEquiv f) m).symm
  actions_commute := by
    intro w x y z f g m
    simp only [LinearMap.comp_apply, LinearMap.flip_apply]
    exact (C.assoc (B.mapEquiv g) m (B.mapEquiv f)).symm

theorem symm_comp_map_left (B : LinearHomAutofunctor C)
    {x y z} (f : C.Hom x y) (m : C.Hom (B.obj y) (B.obj z)) :
    B.mapEquiv.symm (C.comp m (B.mapEquiv f)) =
      C.comp (B.mapEquiv.symm m) f := by
  apply B.mapEquiv.injective
  rw [B.mapEquiv.apply_symm_apply, B.map_comp, B.mapEquiv.apply_symm_apply]

theorem symm_comp_map_right (B : LinearHomAutofunctor C)
    {x y z} (f : C.Hom y z) (m : C.Hom (B.obj x) (B.obj y)) :
    B.mapEquiv.symm (C.comp (B.mapEquiv f) m) =
      C.comp f (B.mapEquiv.symm m) := by
  apply B.mapEquiv.injective
  rw [B.mapEquiv.apply_symm_apply, B.map_comp, B.mapEquiv.apply_symm_apply]

/-- Forget the simultaneous `B` transport on both endpoints. -/
def toRegular (B : LinearHomAutofunctor C) :
    CoefficientBimoduleMorphism B.transportedCoefficient (regularCoefficient C) where
  component := fun _ _ => B.mapEquiv.symm.toLinearMap
  left_naturality := by
    intro x y z f m
    exact B.symm_comp_map_left f m
  right_naturality := by
    intro x y z f m
    exact B.symm_comp_map_right f m

/-- Apply `B` simultaneously to both endpoints. -/
def fromRegular (B : LinearHomAutofunctor C) :
    CoefficientBimoduleMorphism (regularCoefficient C) B.transportedCoefficient where
  component := fun _ _ => B.mapEquiv.toLinearMap
  left_naturality := by
    intro x y z f m
    exact B.map_comp m f
  right_naturality := by
    intro x y z f m
    exact B.map_comp f m

theorem rawMap_to_from (B : LinearHomAutofunctor C)
    (x : CoefficientRaw (regularCoefficient C)) :
    B.toRegular.rawMap (B.fromRegular.rawMap x) = x := by
  classical
  apply DFinsupp.ext
  intro i
  change B.mapEquiv.symm (B.mapEquiv (x i)) = x i
  exact B.mapEquiv.symm_apply_apply (x i)

theorem rawMap_from_to (B : LinearHomAutofunctor C)
    (x : CoefficientRaw B.transportedCoefficient) :
    B.fromRegular.rawMap (B.toRegular.rawMap x) = x := by
  classical
  apply DFinsupp.ext
  intro i
  change B.mapEquiv (B.mapEquiv.symm (x i)) = x i
  exact B.mapEquiv.apply_symm_apply (x i)

/-- Canonical coefficient-HH0 equivalence for a representable transported
coefficient.  Candidate geometry is needed only to identify its actual
coefficient bimodule with the source of this equivalence. -/
def coefficientHH0Equiv (B : LinearHomAutofunctor C) :
    CoefficientHH0 B.transportedCoefficient ≃ₗ[ℚ]
      CoefficientHH0 (regularCoefficient C) :=
  quotientLinearEquiv
    (cyclicRelation B.transportedCoefficient)
    (cyclicRelation (regularCoefficient C))
    B.toRegular.rawMap B.fromRegular.rawMap
    B.toRegular.cyclicRelation_le_comap
    B.fromRegular.cyclicRelation_le_comap
    (fun x => by rw [B.rawMap_from_to x, sub_self]; exact Submodule.zero_mem _)
    (fun x => by rw [B.rawMap_to_from x, sub_self]; exact Submodule.zero_mem _)

@[simp] theorem coefficientHH0Equiv_apply_mk
    (B : LinearHomAutofunctor C)
    (x : CoefficientRaw B.transportedCoefficient) :
    B.coefficientHH0Equiv (coefficientHH0Quotient B.transportedCoefficient x) =
      coefficientHH0Quotient (regularCoefficient C) (B.toRegular.rawMap x) := by
  rfl

end LinearHomAutofunctor

end

end Smooth4PC
