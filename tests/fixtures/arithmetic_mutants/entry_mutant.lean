import AuditArithmetic

namespace Smooth4PC.Mutants

def entryMutantMatrixA : List (List Int) :=
  [[0, 269, 1241], [0, 41, 189], [1, 0, 32]]

theorem entryMutant_det_should_fail : det3 entryMutantMatrixA = 1 := by
  norm_num [det3, entryMutantMatrixA]

end Smooth4PC.Mutants
