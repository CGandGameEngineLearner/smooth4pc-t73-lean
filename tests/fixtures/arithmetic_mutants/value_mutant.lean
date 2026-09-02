import AuditArithmetic

namespace Smooth4PC.Mutants

def valueMutantOneHandleActualCapH3 : Int := -59071

theorem valueMutant_h3_should_fail :
    (-8 : Int) * (-328) = valueMutantOneHandleActualCapH3 := by
  norm_num [valueMutantOneHandleActualCapH3]

end Smooth4PC.Mutants
