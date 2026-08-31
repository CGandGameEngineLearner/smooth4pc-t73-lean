import Mathlib

namespace Smooth4PC

/-! A narrow typed interface for the balanced Hattori input.

The transported-annulus geometry is data in `BalancedHattoriGeometry`.  This
module proves only consequences of those typed fields and elementary defect
and integer arithmetic.
-/

inductive FrobeniusLabel where
  | one
  | X
  deriving DecidableEq, Repr

/-- The 227 labels are independent indexed tensor factors. -/
abbrev SeparateXLabels := Fin 227 → FrobeniusLabel

def allX : SeparateXLabels := fun _ => .X

universe u v w

/-- Visible geometric inputs for the two-sided balanced Hattori cut. -/
structure BalancedHattoriGeometry where
  Obj : Type u
  Hom : Obj → Obj → Type v
  Coeff : Obj → Obj → Type w
  B : Obj → Obj
  BInv : Obj → Obj
  B_BInv : ∀ T, B (BInv T) = T
  BInv_B : ∀ T, BInv (B T) = T
  idHom : ∀ T, Hom T T
  H : ∀ T T', Coeff T T' ≃
    (Hom (B T) (B T') × SeparateXLabels)

def chosenT (g : BalancedHattoriGeometry) (U : g.Obj) : g.Obj :=
  g.BInv U

theorem B_chosenT_eq_U (g : BalancedHattoriGeometry) (U : g.Obj) :
    g.B (chosenT g U) = U :=
  g.B_BInv U

def diagonalTarget (g : BalancedHattoriGeometry) (U : g.Obj) :
    g.Hom (g.B (chosenT g U)) (g.B (chosenT g U)) × SeparateXLabels :=
  (g.idHom _, allX)

def vT (g : BalancedHattoriGeometry) (U : g.Obj) :
    g.Coeff (chosenT g U) (chosenT g U) :=
  (g.H (chosenT g U) (chosenT g U)).symm (diagonalTarget g U)

theorem vT_binding (g : BalancedHattoriGeometry) (U : g.Obj) :
    g.H (chosenT g U) (chosenT g U) (vT g U) = diagonalTarget g U :=
  Equiv.apply_symm_apply _ _

def selectedInput (g : BalancedHattoriGeometry) (U : g.Obj) := vT g U

theorem selectedInput_eq_vT (g : BalancedHattoriGeometry) (U : g.Obj) :
    selectedInput g U = vT g U := rfl

/-! ### Positive endpoint source -/

abbrev M1_88 := Fin 88 → ℚ

def basisVector (i : Fin 88) : M1_88 :=
  fun j => if j = i then 1 else 0

def cupVector : M1_88 := basisVector 0 - basisVector 5

inductive EndpointSource where
  | M1_88
  deriving DecidableEq, Repr

def positiveSource : EndpointSource := .M1_88

theorem positiveSource_is_M1_88 : positiveSource = EndpointSource.M1_88 := rfl

/-! ### Intrinsic relative defect -/

structure PhysicalState where
  addedLabels : List FrobeniusLabel
  deriving Repr

def mandatoryDefect : Nat := 1

def addedDefect : List FrobeniusLabel → Nat
  | [] => 0
  | .one :: rest => 1 + addedDefect rest
  | .X :: rest => addedDefect rest

def totalDefect (s : PhysicalState) : Nat :=
  mandatoryDefect + addedDefect s.addedLabels

def relativeNu (s : PhysicalState) : Nat :=
  totalDefect s - mandatoryDefect

def baseState : PhysicalState := ⟨[]⟩

def cupState : PhysicalState := baseState

def dottedX (s : PhysicalState) : PhysicalState :=
  ⟨.X :: s.addedLabels⟩

def undottedOne (s : PhysicalState) : PhysicalState :=
  ⟨.one :: s.addedLabels⟩

theorem relativeNu_eq_addedDefect (s : PhysicalState) :
    relativeNu s = addedDefect s.addedLabels := by
  simp [relativeNu, totalDefect, mandatoryDefect]

theorem relativeNu_base : relativeNu baseState = 0 := by
  rfl

theorem relativeNu_cup : relativeNu cupState = 0 := by
  rfl

theorem relativeNu_dottedX (s : PhysicalState) :
    relativeNu (dottedX s) = relativeNu s := by
  simp [relativeNu_eq_addedDefect, dottedX, addedDefect]

theorem relativeNu_undottedOne (s : PhysicalState) :
    relativeNu (undottedOne s) = relativeNu s + 1 := by
  simp [relativeNu_eq_addedDefect, undottedOne, addedDefect, Nat.add_comm]

def headRow (s : PhysicalState) : ℚ :=
  if relativeNu s = 0 then 1 else 0

theorem headRow_zero_of_relativeNu_ge_one (s : PhysicalState)
    (h : 1 ≤ relativeNu s) : headRow s = 0 := by
  simp [headRow, Nat.ne_of_gt h]

def cupCoordinateRow : M1_88 →ₗ[ℚ] ℚ where
  toFun v := v 0 - v 5
  map_add' _ _ := by simp; ring
  map_smul' _ _ := by simp; ring

def relativeHeadRow (s : PhysicalState) : M1_88 →ₗ[ℚ] ℚ :=
  if relativeNu s = 0 then cupCoordinateRow else 0

theorem relativeHeadRow_zero_of_relativeNu_ge_one (s : PhysicalState)
    (h : 1 ≤ relativeNu s) : relativeHeadRow s = 0 := by
  simp [relativeHeadRow, Nat.ne_of_gt h]

/-! ### Exact finite arithmetic -/

def cubicValue : ℤ := -59072

theorem degree_ledger_eq_494 : (183 : ℤ) + 315 - 4 = 494 := by
  norm_num

theorem cubic_arithmetic_eq_neg59072 : (-8 : ℤ) * 7384 = -59072 := by
  norm_num

theorem neg59072_ne_zero : (-59072 : ℤ) ≠ 0 := by
  norm_num

theorem cubicValue_eq_neg59072 : cubicValue = (-59072 : ℤ) := by
  rfl

end Smooth4PC
