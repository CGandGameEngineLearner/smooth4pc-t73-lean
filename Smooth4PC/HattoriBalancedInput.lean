import Mathlib

namespace Smooth4PC

noncomputable section

inductive FrobeniusLabel where
  | one
  | X
  deriving DecidableEq, Repr

/-- Basis of the 227 separate Frobenius tensor factors. -/
abbrev TensorBasis227 := Fin 227 → FrobeniusLabel

/-- Free-module basis model of the 227-fold tensor factor. -/
abbrev Tensor227 := TensorBasis227 →₀ ℚ

def allX : TensorBasis227 := fun _ => .X

def xTensor227 : Tensor227 := Finsupp.single allX 1

universe u

/-- Object-level and linear data supplied by the balanced geometric cut. -/
structure BalancedHattoriGeometry where
  Obj : Type u
  Hom : Obj → Obj → ModuleCat ℚ
  Coeff : Obj → Obj → ModuleCat ℚ
  B : Obj → Obj
  BInv : Obj → Obj
  BDual : Obj → Obj
  B_BInv : ∀ T, B (BInv T) = T
  BInv_B : ∀ T, BInv (B T) = T
  BInvDualBinding : ∀ T, BInv T = BDual T
  idHom : ∀ T, Hom T T
  BMap : ∀ {T T'}, Hom T T' →ₗ[ℚ] Hom (B T) (B T')
  BMap_id : ∀ T, BMap (idHom T) = idHom (B T)
  IsCycle : ∀ {T T'}, Coeff T T' → Prop
  H : ∀ T T', Coeff T T' ≃ₗ[ℚ]
    TensorProduct ℚ (Hom (B T) (B T')) Tensor227

abbrev HattoriTarget (g : BalancedHattoriGeometry) (T T' : g.Obj) :=
  TensorProduct ℚ (g.Hom (g.B T) (g.B T')) Tensor227

/-- Explicit two-sided actions and the two naturality squares.  These are
geometric inputs, not conclusions of this module. -/
structure BalancedHattoriCompatibility (g : BalancedHattoriGeometry) where
  coeffLeft : ∀ {S T T'},
    g.Hom S T →ₗ[ℚ] (g.Coeff T T' →ₗ[ℚ] g.Coeff S T')
  coeffRight : ∀ {T T' U},
    g.Hom T' U →ₗ[ℚ] (g.Coeff T T' →ₗ[ℚ] g.Coeff T U)
  targetLeftByB : ∀ {S T T'},
    g.Hom (g.B S) (g.B T) →ₗ[ℚ]
      (HattoriTarget g T T' →ₗ[ℚ] HattoriTarget g S T')
  targetRightByB : ∀ {T T' U},
    g.Hom (g.B T') (g.B U) →ₗ[ℚ]
      (HattoriTarget g T T' →ₗ[ℚ] HattoriTarget g T U)
  leftNaturality : ∀ {S T T'} (f : g.Hom S T) (x : g.Coeff T T'),
    g.H S T' (coeffLeft f x) = targetLeftByB (g.BMap f) (g.H T T' x)
  rightNaturality : ∀ {T T' U} (f : g.Hom T' U) (x : g.Coeff T T'),
    g.H T U (coeffRight f x) = targetRightByB (g.BMap f) (g.H T T' x)

def chosenT (g : BalancedHattoriGeometry) (U : g.Obj) : g.Obj := g.BInv U

theorem B_chosenT_eq_U (g : BalancedHattoriGeometry) (U : g.Obj) :
    g.B (chosenT g U) = U :=
  g.B_BInv U

def diagonalTarget (g : BalancedHattoriGeometry) (U : g.Obj) :
    HattoriTarget g (chosenT g U) (chosenT g U) :=
  g.idHom _ ⊗ₜ[ℚ] xTensor227

/-- Definitional inverse image only; it is not asserted to be the actual
transported-annulus cycle. -/
def inverseImageVT (g : BalancedHattoriGeometry) (U : g.Obj) :
    g.Coeff (chosenT g U) (chosenT g U) :=
  (g.H (chosenT g U) (chosenT g U)).symm (diagonalTarget g U)

theorem inverseImageVT_binding (g : BalancedHattoriGeometry) (U : g.Obj) :
    g.H (chosenT g U) (chosenT g U) (inverseImageVT g U) =
      diagonalTarget g U :=
  LinearEquiv.apply_symm_apply _ _

/-- The actual diagonal, its cycle witness, and its geometric Hattori binding
are external input data. -/
structure ActualDiagonalInput (g : BalancedHattoriGeometry) (U : g.Obj) where
  actualVT : g.Coeff (chosenT g U) (chosenT g U)
  cycle : g.IsCycle actualVT
  binding : g.H (chosenT g U) (chosenT g U) actualVT = diagonalTarget g U

def selectedInput {g : BalancedHattoriGeometry} {U : g.Obj}
    (actual : ActualDiagonalInput g U) := actual.actualVT

theorem selectedInput_eq_actualVT {g : BalancedHattoriGeometry} {U : g.Obj}
    (actual : ActualDiagonalInput g U) :
    selectedInput actual = actual.actualVT := rfl

theorem selectedInput_isCycle {g : BalancedHattoriGeometry} {U : g.Obj}
    (actual : ActualDiagonalInput g U) :
    g.IsCycle (selectedInput actual) := actual.cycle

theorem selectedInput_binding {g : BalancedHattoriGeometry} {U : g.Obj}
    (actual : ActualDiagonalInput g U) :
    g.H (chosenT g U) (chosenT g U) (selectedInput actual) =
      diagonalTarget g U := actual.binding

/-! ### Positive endpoint source and defect-graded module -/

abbrev M1_88 := Fin 88 → ℚ

def basisVector (i : Fin 88) : M1_88 := fun j => if j = i then 1 else 0

def cupVector : M1_88 := basisVector 2 - basisVector 87

inductive EndpointSource where
  | M1_88
  deriving DecidableEq, Repr

def positiveSource : EndpointSource := .M1_88

theorem positiveSource_is_M1_88 : positiveSource = EndpointSource.M1_88 := rfl

structure DefectBasis where
  endpoint : Fin 88
  addedOneCount : Nat
  addedXCount : Nat
  deriving DecidableEq, Repr

def relativeNuBasis (b : DefectBasis) : Nat := b.addedOneCount

def totalDefectBasis (b : DefectBasis) : Nat := 1 + b.addedOneCount

abbrev DefectModule := DefectBasis →₀ ℚ

def dottedBasis (b : DefectBasis) : DefectBasis :=
  { b with addedXCount := b.addedXCount + 1 }

def undottedBasis (b : DefectBasis) : DefectBasis :=
  { b with addedOneCount := b.addedOneCount + 1 }

def basisPush (f : DefectBasis → DefectBasis) : DefectModule →ₗ[ℚ] DefectModule :=
  (Finsupp.lsum ℚ) (fun b => Finsupp.lsingle (f b))

theorem basisPush_single (f : DefectBasis → DefectBasis)
    (b : DefectBasis) (c : ℚ) :
    basisPush f (Finsupp.single b c) = Finsupp.single (f b) c := by
  classical
  simp [basisPush]

def dottedMap : DefectModule →ₗ[ℚ] DefectModule := basisPush dottedBasis

def undottedMap : DefectModule →ₗ[ℚ] DefectModule := basisPush undottedBasis

/-- A head row with arbitrary endpoint seed, supported exactly at relative
defect zero. -/
def defectHeadRow (baseRow : M1_88 →ₗ[ℚ] ℚ) : DefectModule →ₗ[ℚ] ℚ :=
  (Finsupp.lsum ℚ) (fun b =>
    if relativeNuBasis b = 0 then
      (baseRow (basisVector b.endpoint)) • LinearMap.id
    else 0)

theorem defectHeadRow_comp_dotted (baseRow : M1_88 →ₗ[ℚ] ℚ) :
    (defectHeadRow baseRow).comp dottedMap = defectHeadRow baseRow := by
  classical
  apply Finsupp.lhom_ext'
  intro b
  apply LinearMap.ext
  intro c
  simp [defectHeadRow, dottedMap, basisPush_single, dottedBasis,
    relativeNuBasis]
  rfl

theorem defectHeadRow_comp_undotted (baseRow : M1_88 →ₗ[ℚ] ℚ) :
    (defectHeadRow baseRow).comp undottedMap = 0 := by
  classical
  apply Finsupp.lhom_ext'
  intro b
  apply LinearMap.ext
  intro c
  simp [defectHeadRow, undottedMap, basisPush_single, undottedBasis,
    relativeNuBasis]

structure PhysicalCopyPermutation where
  endpointPerm : Equiv.Perm (Fin 88)

def permuteBasis (p : PhysicalCopyPermutation) (b : DefectBasis) : DefectBasis :=
  { b with endpoint := p.endpointPerm b.endpoint }

def physicalCopyPermutationMap (p : PhysicalCopyPermutation) :
    DefectModule →ₗ[ℚ] DefectModule :=
  basisPush (permuteBasis p)

theorem physicalCopyPermutation_preserves_relativeNu
    (p : PhysicalCopyPermutation) (b : DefectBasis) :
    relativeNuBasis (permuteBasis p b) = relativeNuBasis b := rfl

/-! ### Exact finite arithmetic -/

def cubicValue : ℤ := 2624

theorem degree_ledger_eq_494 : (183 : ℤ) + 315 - 4 = 494 := by norm_num

theorem cubic_arithmetic_eq_2624 : (-8 : ℤ) * (-328) = 2624 := by
  norm_num

theorem cubic2624_ne_zero : (2624 : ℤ) ≠ 0 := by norm_num

theorem cubicValue_eq_2624 : cubicValue = (2624 : ℤ) := by rfl

end

end Smooth4PC
