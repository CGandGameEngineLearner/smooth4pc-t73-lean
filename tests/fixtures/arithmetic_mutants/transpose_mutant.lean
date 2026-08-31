import AuditArithmetic

namespace Smooth4PC.Mutants

def transposeMutantMatrixA : List (List Int) :=
  [[0, 0, 1], [269, 41, 0], [1240, 189, 32]]

theorem transposeMutant_rowMajorEntry_should_fail :
    matrixEntry transposeMutantMatrixA 0 1 = 269 := by
  norm_num [matrixEntry, transposeMutantMatrixA]

end Smooth4PC.Mutants
