import Smooth4PC.Interfaces

open Lean Elab Command Meta

namespace Smooth4PC

/-- The exact declarations whose fully elaborated types are frozen in the manifest. -/
def auditTypeDeclarations : List Name := [
  `Smooth4PC.conditionalNotStandardSignature,
  `Smooth4PC.conditionalIsHomotopySphereSignature,
  `Smooth4PC.conditionalCounterexampleSignature
]

/-- Structures whose projection types are part of the hand-frozen interface surface. -/
def auditInterfaceStructures : List Name := [
  `Smooth4PC.AuditUniverse,
  `Smooth4PC.OneHandleInterface,
  `Smooth4PC.BetaPsiInterface,
  `Smooth4PC.SphereLocalInterface,
  `Smooth4PC.SphereMWWFamily,
  `Smooth4PC.FourHandleInterface,
  `Smooth4PC.S4ControlInterface,
  `Smooth4PC.DiffeomorphismInvarianceInterface,
  `Smooth4PC.NotStandardInterfaces,
  `Smooth4PC.CappellShanesonInterface
]

/-- A real Lean Meta dump.  The Python gate compares this output; it never writes the manifest. -/
elab "dumpInterfaceTypes" : command => do
  Command.liftCoreM <| MetaM.run' do
    let options := (← getOptions).setBool `pp.universes true |>.setBool `pp.explicit true |>.setBool `pp.all true
    withOptions (fun _ => options) do
      for declaration in auditTypeDeclarations do
        let info ← getConstInfo declaration
        let rendered := (← ppExpr info.type).pretty 100000
        logInfo m!"AUDIT_TYPE|{declaration}|{rendered}"
        match info.value? with
        | some value =>
            let expanded ← whnf value
            let body := (← ppExpr expanded).pretty 100000
            logInfo m!"AUDIT_BODY|{declaration}|{body}"
        | none => pure ()

elab "dumpInterfaceProjectionTypes" : command => do
  Command.liftCoreM <| MetaM.run' do
    let options := (← getOptions).setBool `pp.universes true |>.setBool `pp.explicit true |>.setBool `pp.all true
    withOptions (fun _ => options) do
      let environment ← getEnv
      for structureName in auditInterfaceStructures do
        match getStructureInfo? environment structureName with
        | some structureInfo =>
          for fieldInfo in structureInfo.fieldInfo do
            let fieldName := fieldInfo.projFn
            let info ← getConstInfo fieldName
            let rendered := (← ppExpr info.type).pretty 100000
            logInfo m!"AUDIT_FIELD|{fieldName}|{rendered}"
        | none => throwError "expected structure: {structureName}"

dumpInterfaceTypes
dumpInterfaceProjectionTypes

end Smooth4PC
