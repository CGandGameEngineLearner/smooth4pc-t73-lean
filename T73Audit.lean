import Smooth4PC.T73Conditional
import Smooth4PC.T73SphereQuotient
import Smooth4PC.T73S4Control
import Smooth4PC.T73S4Inhabitant
import Smooth4PC.T73GeometryPack
import Smooth4PC.CoefficientTrace
import Smooth4PC.QuotientEquiv
import Smooth4PC.FilteredCubicNaturality
import Smooth4PC.LocalStabilization
import Smooth4PC.ReynoldsCableCocone

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
  `Smooth4PC.T73.computedCubic_eq_2624,
  `Smooth4PC.T73.computedCubic_ne_zero,
  `Smooth4PC.T73.computedDegree_eq_494,
  `Smooth4PC.T73.computedDegree_ne_zero,
  `Smooth4PC.T73.undottedRow_eq_zero,
  `Smooth4PC.T73.dottedRow_eq_source,
  `Smooth4PC.T73.epsilonWords_splitTreeWords,
  `Smooth4PC.T73.splitTree_wholeSource_undotted_eq_zero,
  `Smooth4PC.T73.splitTree_wholeSource_dotted_eq_source,
  `Smooth4PC.T73.splitTree_directQ_undotted_row_eq_zero,
  `Smooth4PC.T73.splitTree_directQ_dotted_row_eq_source,
  `Smooth4PC.T73.SphereChart.ell_comp_undotted_eq_zero,
  `Smooth4PC.T73.SphereChart.ell_comp_dottedMinusId_eq_zero,
  `Smooth4PC.T73.sphereRelation_le_ker,
  `Smooth4PC.T73.descendedSphereRow_comp_quotient,
  `Smooth4PC.T73.sphereClass_ne_zero,
  `Smooth4PC.DiagonalShadow.cyclicRelation_le_ker,
  `Smooth4PC.DiagonalShadow.descendedRow_comp_quotient,
  `Smooth4PC.CoefficientBimoduleMorphism.cyclicRelation_le_comap,
  `Smooth4PC.ShadowMorphism.descendedRow_naturality,
  `Smooth4PC.quotientLinearEquiv_apply_mk,
  `Smooth4PC.quotientLinearEquiv_symm_apply_mk,
  `Smooth4PC.T73.aMinusIInverse_left,
  `Smooth4PC.T73.aMinusIInverse_right,
  `Smooth4PC.T73.aMinusICokernel_eq_zero,
  `Smooth4PC.T73.hTwoMinusIInverse_left,
  `Smooth4PC.T73.hTwoMinusIInverse_right,
  `Smooth4PC.T73.hTwoMinusICokernel_eq_zero,
  `Smooth4PC.T73.t73CSLinearObstructionsVanish,
  `Smooth4PC.T73.t73IsHomotopySphere_of_topology,
  `Smooth4PC.T73.s4DegreeZero_of_reduction,
  `Smooth4PC.T73.conditionalNotStandard,
  `Smooth4PC.T73.conditionalIsHomotopySphere,
  `Smooth4PC.T73.conditionalCounterexample,
  `Smooth4PC.T73.conditionalCounterexample_of_topology,
  `Smooth4PC.T73.emptyLink_s4ComputedDegreeZero,
  `Smooth4PC.T73.detectorLine_not_linearEquiv_emptyKhQ,
  `Smooth4PC.T73.detectorTransport_on_emptyLink_impossible,
  `Smooth4PC.T73.conditionalCounterexample_of_pack,
  `Smooth4PC.localStabilization,
  `Smooth4PC.localStabilization_psi0,
  `Smooth4PC.localStabilization_psi1,
  `Smooth4PC.doubleCounitDelta_one,
  `Smooth4PC.doubleCounitDelta_X,
  `Smooth4PC.reynoldsAverage_const,
  `Smooth4PC.reynoldsAverage_orbitConst
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
#print axioms computedCubic_eq_2624
#print axioms computedCubic_ne_zero
#print axioms computedDegree_eq_494
#print axioms computedDegree_ne_zero
#print axioms undottedRow_eq_zero
#print axioms dottedRow_eq_source
#print axioms epsilonWords_splitTreeWords
#print axioms splitTree_wholeSource_undotted_eq_zero
#print axioms splitTree_wholeSource_dotted_eq_source
#print axioms splitTree_directQ_undotted_row_eq_zero
#print axioms splitTree_directQ_dotted_row_eq_source
#print axioms SphereChart.ell_comp_undotted_eq_zero
#print axioms SphereChart.ell_comp_dottedMinusId_eq_zero
#print axioms sphereRelation_le_ker
#print axioms descendedSphereRow_comp_quotient
#print axioms sphereClass_ne_zero
#print axioms Smooth4PC.DiagonalShadow.cyclicRelation_le_ker
#print axioms Smooth4PC.DiagonalShadow.descendedRow_comp_quotient
#print axioms Smooth4PC.CoefficientBimoduleMorphism.cyclicRelation_le_comap
#print axioms Smooth4PC.ShadowMorphism.descendedRow_naturality
#print axioms Smooth4PC.quotientLinearEquiv_apply_mk
#print axioms Smooth4PC.quotientLinearEquiv_symm_apply_mk
#print axioms aMinusIInverse_left
#print axioms aMinusIInverse_right
#print axioms aMinusICokernel_eq_zero
#print axioms hTwoMinusIInverse_left
#print axioms hTwoMinusIInverse_right
#print axioms hTwoMinusICokernel_eq_zero
#print axioms t73CSLinearObstructionsVanish
#print axioms t73IsHomotopySphere_of_topology
#print axioms s4DegreeZero_of_reduction
#print axioms conditionalNotStandard
#print axioms conditionalIsHomotopySphere
#print axioms conditionalCounterexample
#print axioms conditionalCounterexample_of_topology
#print axioms emptyLink_s4ComputedDegreeZero
#print axioms detectorLine_not_linearEquiv_emptyKhQ
#print axioms detectorTransport_on_emptyLink_impossible
#print axioms conditionalCounterexample_of_pack
#print axioms Smooth4PC.cubicScalar_of_order_three
#print axioms Smooth4PC.simultaneousConjugation_pairing
#print axioms Smooth4PC.cubicScalar_conjugation_invariant
#print axioms Smooth4PC.localStabilization
#print axioms Smooth4PC.localStabilization_psi0
#print axioms Smooth4PC.localStabilization_psi1
#print axioms Smooth4PC.doubleCounitDelta_one
#print axioms Smooth4PC.doubleCounitDelta_X
#print axioms Smooth4PC.reynoldsAverage_const
#print axioms Smooth4PC.reynoldsAverage_orbitConst

end Smooth4PC.T73
