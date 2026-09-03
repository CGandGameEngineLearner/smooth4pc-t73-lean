-- Generated from scripts/factor_t73_matrix_johnson.py.
-- Regenerate with scripts/generate_t73_lean_geometry.py --write; do not edit.

import Smooth4PC.T73Finite

namespace Smooth4PC.T73

/-!
Compressed Johnson `alpha_ij` row additions whose product is `matrixA`.
This is the linear monodromy of the E13 PL automorphism `psi`, not a
4-manifold triangulation and not an inhabitant of `ExternalGeometry`.
-/

/-- Add `coefficient` times the source row to the target row. -/
structure RowAdd where
  target : Fin 3
  source : Fin 3
  coefficient : Int
  deriving DecidableEq, Repr

def applyRowAdd (m : Matrix3) (op : RowAdd) : Matrix3 :=
  fun row col =>
    if row = op.target then m row col + op.coefficient * m op.source col
    else m row col

def applyRowAdds (ops : List RowAdd) (m : Matrix3) : Matrix3 :=
  ops.foldl applyRowAdd m

def identity3 : Matrix3 := identityEntry

/-- Construction transvections: start from the identity and recover `A`. -/
def johnsonConstructionTransvections : List RowAdd :=
  [⟨1, 2, 4⟩,
  ⟨0, 2, 32⟩,
  ⟨1, 2, -1⟩,
  ⟨2, 1, 1⟩,
  ⟨1, 2, -1⟩,
  ⟨1, 2, -2⟩,
  ⟨1, 2, -1⟩,
  ⟨2, 1, 1⟩,
  ⟨1, 2, -1⟩,
  ⟨1, 2, -3⟩,
  ⟨1, 2, -1⟩,
  ⟨2, 1, 1⟩,
  ⟨1, 2, -1⟩,
  ⟨1, 2, -5⟩,
  ⟨1, 2, -1⟩,
  ⟨2, 1, 1⟩,
  ⟨1, 2, -1⟩,
  ⟨1, 2, -3⟩,
  ⟨1, 2, -1⟩,
  ⟨2, 1, 1⟩,
  ⟨1, 2, -1⟩,
  ⟨1, 2, -2⟩,
  ⟨1, 2, -1⟩,
  ⟨2, 1, 1⟩,
  ⟨1, 2, -1⟩,
  ⟨1, 2, -2⟩,
  ⟨1, 2, -1⟩,
  ⟨2, 1, 1⟩,
  ⟨1, 2, -1⟩,
  ⟨1, 2, -2⟩,
  ⟨1, 2, -1⟩,
  ⟨2, 1, 1⟩,
  ⟨1, 2, -1⟩,
  ⟨1, 2, -2⟩,
  ⟨1, 2, -1⟩,
  ⟨2, 1, 1⟩,
  ⟨1, 2, -1⟩,
  ⟨1, 2, -2⟩,
  ⟨1, 2, -1⟩,
  ⟨2, 1, 1⟩,
  ⟨1, 2, -1⟩,
  ⟨1, 2, -1⟩,
  ⟨0, 2, -1⟩,
  ⟨2, 0, 1⟩,
  ⟨0, 2, -1⟩]

def johnsonCompressedMoveCount : Nat :=
  johnsonConstructionTransvections.length

def johnsonUnitAlphaMoveCount : Nat :=
  (johnsonConstructionTransvections.map fun op => op.coefficient.natAbs).sum

theorem johnsonCompressedMoveCount_eq_45 :
    johnsonCompressedMoveCount = 45 :=
  rfl

theorem johnsonUnitAlphaMoveCount_eq_93 :
    johnsonUnitAlphaMoveCount = 93 :=
  rfl

theorem johnsonConstruction_eq_matrixA :
    applyRowAdds johnsonConstructionTransvections identity3 = matrixA := by
  ext row col
  fin_cases row <;> fin_cases col <;> decide

end Smooth4PC.T73
