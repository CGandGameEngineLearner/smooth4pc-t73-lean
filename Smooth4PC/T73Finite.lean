import Mathlib
import Smooth4PC.AugmentationCocone

namespace Smooth4PC.T73

/-!
This module checks only the finite T73 algebra.  It does not supply any of the
geometric hypotheses needed to identify these matrices or rows with a smooth
four-manifold construction.
-/

/-- A three-by-three integer matrix, addressed by row and then column. -/
abbrev Matrix3 := Fin 3 → Fin 3 → Int

/-- The Leibniz formula for a three-by-three determinant. -/
def det3 (matrix : Matrix3) : Int :=
  let a := matrix 0 0
  let b := matrix 0 1
  let c := matrix 0 2
  let d := matrix 1 0
  let e := matrix 1 1
  let f := matrix 1 2
  let g := matrix 2 0
  let h := matrix 2 1
  let i := matrix 2 2
  a * (e * i - f * h)
    - b * (d * i - f * g)
    + c * (d * h - e * g)

/-- The row-major T73 matrix. -/
def matrixA : Matrix3 := fun row column =>
  match row.val, column.val with
  | 0, 0 => 0
  | 0, 1 => 269
  | 0, 2 => 1240
  | 1, 0 => 0
  | 1, 1 => 41
  | 1, 2 => 189
  | 2, 0 => 1
  | 2, 1 => 0
  | 2, 2 => 32
  | _, _ => 0

/-- One entry of the three-by-three identity matrix. -/
def identityEntry (row column : Fin 3) : Int :=
  if row = column then 1 else 0

/-- `A-I`, generated entrywise from `matrixA` and the identity. -/
def matrixAMinusI : Matrix3 := fun row column =>
  matrixA row column - identityEntry row column

/-- The three chosen sphere columns, stored as columns of this row-major matrix. -/
def sphereColumns : Matrix3 := fun row column =>
  match row.val, column.val with
  | 0, 0 => -1311
  | 0, 1 => -189
  | 0, 2 => 41
  | 1, 0 => 8608
  | 1, 1 => 1241
  | 1, 2 => -269
  | 2, 0 => -1
  | 2, 1 => 0
  | 2, 2 => 1
  | _, _ => 0

def detA : Int := det3 matrixA
def detAMinusI : Int := det3 matrixAMinusI
def sphereDet : Int := det3 sphereColumns

theorem detA_eq_one : detA = 1 := by
  norm_num [detA, det3, matrixA]

theorem detAMinusI_eq_one : detAMinusI = 1 := by
  norm_num [detAMinusI, det3, matrixAMinusI, matrixA, identityEntry, Fin.ext_iff]

theorem sphereDet_eq_one : sphereDet = 1 := by
  norm_num [sphereDet, det3, sphereColumns]

def cubicBase : Int := 7384
def substitutionLinear : Int := -2

/-- The cubic after substituting the linear coefficient. -/
def computedCubic : Int := substitutionLinear ^ 3 * cubicBase

theorem computedCubic_eq_neg59072 : computedCubic = -59072 := by
  norm_num [computedCubic, substitutionLinear, cubicBase]

theorem computedCubic_ne_zero : computedCubic ≠ 0 := by
  norm_num [computedCubic, substitutionLinear, cubicBase]

def degreeMinus44 : Int := -44
def degreePlus227 : Int := 227
def degreePlus315 : Int := 315
def degreeMinus4 : Int := -4

/-- The degree computed from its four signed contributions. -/
def computedDegree : Int :=
  degreeMinus44 + degreePlus227 + degreePlus315 + degreeMinus4

theorem computedDegree_eq_494 : computedDegree = 494 := by
  norm_num [computedDegree, degreeMinus44, degreePlus227, degreePlus315,
    degreeMinus4]

theorem computedDegree_ne_zero : computedDegree ≠ 0 := by
  norm_num [computedDegree, degreeMinus44, degreePlus227, degreePlus315,
    degreeMinus4]

noncomputable section

/-- General undotted-zero row equation, re-exported without a geometric instance. -/
theorem undottedRow_eq_zero {C : Type*} [AddCommGroup C] [Module ℚ C]
    (row : C →ₗ[ℚ] ℚ) (b : Nat) (hb : 0 < b) :
    (Smooth4PC.targetCounitRow b row).comp
        (Smooth4PC.canonicalInsertion b .one) = 0 :=
  Smooth4PC.targetRow_undotted_eq_zero row b hb

/-- General dotted-identity row equation, re-exported without a geometric instance. -/
theorem dottedRow_eq_source {C : Type*} [AddCommGroup C] [Module ℚ C]
    (row : C →ₗ[ℚ] ℚ) (b : Nat) (hb : 0 < b) :
    (Smooth4PC.targetCounitRow b row).comp
        (Smooth4PC.canonicalInsertion b .X) = row :=
  Smooth4PC.targetRow_dotted_eq_source row b hb

end

end Smooth4PC.T73
