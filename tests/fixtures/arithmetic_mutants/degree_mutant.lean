import AuditArithmetic

namespace Smooth4PC.Mutants

def degreeMutant : List Int := [0, 493]

theorem degreeMutant_494_should_fail : degreeMutant.getD 1 0 = 494 := by
  norm_num [degreeMutant]

end Smooth4PC.Mutants
