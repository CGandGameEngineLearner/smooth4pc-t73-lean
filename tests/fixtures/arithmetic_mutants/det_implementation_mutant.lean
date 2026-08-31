import AuditArithmetic

namespace Smooth4PC.Mutants

def det3Mutant : List (List Int) -> Int
  | [[a, b, c], [d, e, f], [g, h, i]] =>
      a * (e * i - f * h)
        + b * (d * i - f * g)
        + c * (d * h - e * g)
  | _ => 0

theorem detImplementationMutant_should_fail : det3Mutant matrixA = 1 := by
  norm_num [det3Mutant, matrixA]

end Smooth4PC.Mutants
