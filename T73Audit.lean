import Smooth4PC.T73Finite

open Lean Elab Command Meta

namespace Smooth4PC.T73

def finiteAuditDeclarations : List Name := [
  `Smooth4PC.T73.det3,
  `Smooth4PC.T73.matrixAMinusI,
  `Smooth4PC.T73.computedCubic,
  `Smooth4PC.T73.computedDegree,
  `Smooth4PC.T73.detA_eq_one,
  `Smooth4PC.T73.detAMinusI_eq_one,
  `Smooth4PC.T73.sphereDet_eq_one,
  `Smooth4PC.T73.computedCubic_eq_neg59072,
  `Smooth4PC.T73.computedCubic_ne_zero,
  `Smooth4PC.T73.computedDegree_eq_494,
  `Smooth4PC.T73.computedDegree_ne_zero,
  `Smooth4PC.T73.undottedRow_eq_zero,
  `Smooth4PC.T73.dottedRow_eq_source
]

elab "dumpT73Finite" : command => do
  Command.liftCoreM <| MetaM.run' do
    let options := (← getOptions).setBool `pp.universes true
    withOptions (fun _ => options) do
      for declaration in finiteAuditDeclarations do
        let info ← getConstInfo declaration
        let renderedType := (← ppExpr info.type).pretty 100000
        logInfo m!"T73_TYPE|{declaration}|{renderedType}"
        match info.value? with
        | some value =>
            let renderedBody := (← ppExpr value).pretty 100000
            logInfo m!"T73_BODY|{declaration}|{renderedBody}"
        | none => pure ()

dumpT73Finite

#print axioms detA_eq_one
#print axioms detAMinusI_eq_one
#print axioms sphereDet_eq_one
#print axioms computedCubic_eq_neg59072
#print axioms computedCubic_ne_zero
#print axioms computedDegree_eq_494
#print axioms computedDegree_ne_zero
#print axioms undottedRow_eq_zero
#print axioms dottedRow_eq_source

end Smooth4PC.T73
