import Mathlib

namespace Smooth4PC

/-!
This module constructs coefficient `HH₀` for a small rational-linear category.
The quotient and every descended map are concrete `Submodule` constructions;
no quotient universal property is stored as an external field.
-/

/-- A small category whose hom spaces and composition are rational-linear. -/
structure SmallQLinearCategory where
  Obj : Type
  Hom : Obj → Obj → ModuleCat ℚ
  id : ∀ x, Hom x x
  comp : ∀ {x y z}, Hom y z →ₗ[ℚ] (Hom x y →ₗ[ℚ] Hom x z)
  comp_id : ∀ {x y} (f : Hom x y), comp (id y) f = f
  id_comp : ∀ {x y} (f : Hom x y), comp f (id x) = f
  assoc : ∀ {w x y z} (h : Hom y z) (g : Hom x y) (f : Hom w x),
    comp h (comp g f) = comp (comp h g) f

/-- A rational-linear bimodule over `C`.  The first object variable is
contravariant and the second is covariant. -/
structure CoefficientBimodule (C : SmallQLinearCategory) where
  M : C.Obj → C.Obj → ModuleCat ℚ
  leftAction : ∀ {x y z}, C.Hom x y →ₗ[ℚ] (M y z →ₗ[ℚ] M x z)
  rightAction : ∀ {x y z}, C.Hom y z →ₗ[ℚ] (M x y →ₗ[ℚ] M x z)
  left_id : ∀ {x z} (m : M x z), leftAction (C.id x) m = m
  right_id : ∀ {x y} (m : M x y), rightAction (C.id y) m = m
  left_comp : ∀ {w x y z} (g : C.Hom x y) (f : C.Hom w x)
    (m : M y z),
      leftAction (C.comp g f) m = leftAction f (leftAction g m)
  right_comp : ∀ {w x y z} (g : C.Hom y z) (f : C.Hom x y)
    (m : M w x),
      rightAction (C.comp g f) m = rightAction g (rightAction f m)
  actions_commute : ∀ {w x y z} (f : C.Hom w x) (g : C.Hom y z)
    (m : M x y),
      leftAction f (rightAction g m) = rightAction g (leftAction f m)

variable {C : SmallQLinearCategory}

/-- The algebraic direct sum of the diagonal coefficient spaces. -/
abbrev CoefficientRaw (B : CoefficientBimodule C) :=
  Π₀ x : C.Obj, B.M x x

/-- One typed cyclic relation is determined by `f : x → y` and
`m ∈ M(y,x)`. -/
structure CyclicGenerator (B : CoefficientBimodule C) where
  x : C.Obj
  y : C.Obj
  f : C.Hom x y
  m : B.M y x

noncomputable section

local instance : DecidableEq C.Obj := Classical.decEq C.Obj

/-- The raw vector `single x (f·m) - single y (m·f)`. -/
def cyclicGeneratorVector (B : CoefficientBimodule C)
    (g : CyclicGenerator B) : CoefficientRaw B := by
  classical
  exact DFinsupp.single g.x (B.leftAction g.f g.m) -
    DFinsupp.single g.y (B.rightAction g.f g.m)

/-- The set of all typed cyclic generator vectors. -/
def cyclicGeneratorSet (B : CoefficientBimodule C) : Set (CoefficientRaw B) :=
  Set.range (cyclicGeneratorVector B)

/-- The coefficient-HH₀ relation submodule. -/
def cyclicRelation (B : CoefficientBimodule C) : Submodule ℚ (CoefficientRaw B) :=
  Submodule.span ℚ (cyclicGeneratorSet B)

/-- Coefficient `HH₀(C;B)`. -/
abbrev CoefficientHH0 (B : CoefficientBimodule C) :=
  CoefficientRaw B ⧸ cyclicRelation B

/-- The concrete quotient map from diagonal raw coefficients. -/
def coefficientHH0Quotient (B : CoefficientBimodule C) :
    CoefficientRaw B →ₗ[ℚ] CoefficientHH0 B :=
  (cyclicRelation B).mkQ

/-- A family of diagonal shadow rows satisfying the cyclic trace identity. -/
structure DiagonalShadow (B : CoefficientBimodule C) where
  row : ∀ x, B.M x x →ₗ[ℚ] ℚ
  cyclicity : ∀ {x y} (f : C.Hom x y) (m : B.M y x),
    row x (B.leftAction f m) = row y (B.rightAction f m)

namespace DiagonalShadow

/-- Sum the diagonal shadow rows over the finite support. -/
def rawRow {B : CoefficientBimodule C} (shadow : DiagonalShadow B) :
    CoefficientRaw B →ₗ[ℚ] ℚ := by
  classical
  exact DFinsupp.lsum ℚ shadow.row

@[simp] theorem rawRow_single {B : CoefficientBimodule C}
    (shadow : DiagonalShadow B) (x : C.Obj) (m : B.M x x) :
    shadow.rawRow (DFinsupp.single x m) = shadow.row x m := by
  classical
  simp [rawRow]

/-- Cyclicity kills each displayed generator on the whole diagonal raw sum. -/
theorem rawRow_cyclicGenerator_eq_zero {B : CoefficientBimodule C}
    (shadow : DiagonalShadow B) (g : CyclicGenerator B) :
    shadow.rawRow (cyclicGeneratorVector B g) = 0 := by
  classical
  simp [cyclicGeneratorVector, shadow.cyclicity]

/-- Hence the raw shadow row kills the full span of cyclic relations. -/
theorem cyclicRelation_le_ker {B : CoefficientBimodule C}
    (shadow : DiagonalShadow B) :
    cyclicRelation B ≤ LinearMap.ker shadow.rawRow := by
  refine Submodule.span_le.2 ?_
  rintro _ ⟨g, rfl⟩
  show shadow.rawRow (cyclicGeneratorVector B g) = 0
  exact shadow.rawRow_cyclicGenerator_eq_zero g

/-- The shadow row descended through the concrete coefficient-HH₀ quotient. -/
def descendedRow {B : CoefficientBimodule C} (shadow : DiagonalShadow B) :
    CoefficientHH0 B →ₗ[ℚ] ℚ :=
  (cyclicRelation B).liftQ shadow.rawRow shadow.cyclicRelation_le_ker

theorem descendedRow_comp_quotient {B : CoefficientBimodule C}
    (shadow : DiagonalShadow B) :
    shadow.descendedRow.comp (coefficientHH0Quotient B) = shadow.rawRow := by
  exact Submodule.liftQ_mkQ _ _ _

end DiagonalShadow

/-- A rational-linear surface/coefficient morphism on one fixed category. -/
structure CoefficientBimoduleMorphism
    (B D : CoefficientBimodule C) where
  component : ∀ x y, B.M x y →ₗ[ℚ] D.M x y
  left_naturality : ∀ {x y z} (f : C.Hom x y) (m : B.M y z),
    component x z (B.leftAction f m) =
      D.leftAction f (component y z m)
  right_naturality : ∀ {x y z} (f : C.Hom y z) (m : B.M x y),
    component x z (B.rightAction f m) =
      D.rightAction f (component x y m)

namespace CyclicGenerator

/-- Apply a coefficient morphism to the coefficient entry of a generator. -/
def map {B D : CoefficientBimodule C}
    (F : CoefficientBimoduleMorphism B D) (g : CyclicGenerator B) :
    CyclicGenerator D where
  x := g.x
  y := g.y
  f := g.f
  m := F.component g.y g.x g.m

end CyclicGenerator

namespace CoefficientBimoduleMorphism

/-- The objectwise coefficient map on the diagonal finite direct sum. -/
def rawMap {B D : CoefficientBimodule C}
    (F : CoefficientBimoduleMorphism B D) :
    CoefficientRaw B →ₗ[ℚ] CoefficientRaw D :=
  DFinsupp.mapRange.linearMap fun x => F.component x x

@[simp] theorem rawMap_single {B D : CoefficientBimodule C}
    (F : CoefficientBimoduleMorphism B D) (x : C.Obj) (m : B.M x x) :
    F.rawMap (DFinsupp.single x m) =
      DFinsupp.single x (F.component x x m) := by
  classical
  simp [rawMap]

/-- The raw map sends every source cyclic generator to the corresponding
target cyclic generator. -/
theorem rawMap_cyclicGenerator {B D : CoefficientBimodule C}
    (F : CoefficientBimoduleMorphism B D) (g : CyclicGenerator B) :
    F.rawMap (cyclicGeneratorVector B g) =
      cyclicGeneratorVector D (g.map F) := by
  classical
  simp [cyclicGeneratorVector, CyclicGenerator.map,
    F.left_naturality, F.right_naturality]
  rfl

/-- A compatible coefficient morphism carries the source relation span into
the target relation span. -/
theorem cyclicRelation_le_comap {B D : CoefficientBimodule C}
    (F : CoefficientBimoduleMorphism B D) :
    cyclicRelation B ≤ (cyclicRelation D).comap F.rawMap := by
  refine Submodule.span_le.2 ?_
  rintro _ ⟨g, rfl⟩
  change F.rawMap (cyclicGeneratorVector B g) ∈ cyclicRelation D
  rw [F.rawMap_cyclicGenerator]
  apply Submodule.subset_span
  exact ⟨g.map F, rfl⟩

/-- The induced map on the concrete coefficient-HH₀ quotients. -/
def hh0Map {B D : CoefficientBimodule C}
    (F : CoefficientBimoduleMorphism B D) :
    CoefficientHH0 B →ₗ[ℚ] CoefficientHH0 D :=
  (cyclicRelation B).mapQ (cyclicRelation D) F.rawMap
    F.cyclicRelation_le_comap

theorem hh0Map_comp_quotient {B D : CoefficientBimodule C}
    (F : CoefficientBimoduleMorphism B D) :
    F.hh0Map.comp (coefficientHH0Quotient B) =
      (coefficientHH0Quotient D).comp F.rawMap := by
  exact Submodule.mapQ_mkQ _ _ _

end CoefficientBimoduleMorphism

/-- A coefficient morphism compatible with chosen source and target shadows. -/
structure ShadowMorphism {B D : CoefficientBimodule C}
    (source : DiagonalShadow B) (target : DiagonalShadow D) where
  toBimoduleMorphism : CoefficientBimoduleMorphism B D
  row_naturality : ∀ x,
    (target.row x).comp (toBimoduleMorphism.component x x) = source.row x

namespace ShadowMorphism

/-- Shadow naturality already holds on the whole diagonal raw direct sum. -/
theorem rawRow_naturality {B D : CoefficientBimodule C}
    {source : DiagonalShadow B} {target : DiagonalShadow D}
    (F : ShadowMorphism source target) :
    target.rawRow.comp F.toBimoduleMorphism.rawMap = source.rawRow := by
  classical
  apply DFinsupp.lhom_ext'
  intro x
  ext m
  have h := LinearMap.congr_fun (F.row_naturality x) m
  simpa using h

/-- The induced coefficient-HH₀ map commutes with the descended shadow rows. -/
theorem descendedRow_naturality {B D : CoefficientBimodule C}
    {source : DiagonalShadow B} {target : DiagonalShadow D}
    (F : ShadowMorphism source target) :
    target.descendedRow.comp F.toBimoduleMorphism.hh0Map =
      source.descendedRow := by
  apply LinearMap.ext
  rintro ⟨x⟩
  change target.descendedRow
      (F.toBimoduleMorphism.hh0Map (coefficientHH0Quotient B x)) =
    source.descendedRow (coefficientHH0Quotient B x)
  have hMap := LinearMap.congr_fun
    F.toBimoduleMorphism.hh0Map_comp_quotient x
  have hTarget := LinearMap.congr_fun target.descendedRow_comp_quotient
    (F.toBimoduleMorphism.rawMap x)
  have hRaw := LinearMap.congr_fun F.rawRow_naturality x
  have hSource := LinearMap.congr_fun source.descendedRow_comp_quotient x
  calc
    _ = target.descendedRow
        (coefficientHH0Quotient D (F.toBimoduleMorphism.rawMap x)) := by
      rw [show F.toBimoduleMorphism.hh0Map (coefficientHH0Quotient B x) =
        coefficientHH0Quotient D (F.toBimoduleMorphism.rawMap x) by
          simpa using hMap]
    _ = target.rawRow (F.toBimoduleMorphism.rawMap x) := by
      simpa using hTarget
    _ = source.rawRow x := hRaw
    _ = source.descendedRow (coefficientHH0Quotient B x) := by
      symm
      simpa using hSource

end ShadowMorphism

end


end Smooth4PC
