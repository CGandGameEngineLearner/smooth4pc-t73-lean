import Smooth4PC.T73Finite
import Smooth4PC.Interfaces

namespace Smooth4PC.T73

noncomputable section

/-- One sphere relation written in actual source/target coordinates.  The only
geometric datum retained here is the choice of the two coordinate inclusions;
the Frobenius maps themselves are definitions. -/
structure SphereChart (W : QMod) (ell : W →ₗ[ℚ] ℚ) where
  Old : QMod
  Source : QMod
  Target : QMod
  newFactors : Nat
  newFactors_pos : 0 < newFactors
  sourceCoords : Source ≃ₗ[ℚ] Old
  targetCoords : Target ≃ₗ[ℚ] TensorTarget Old newFactors
  oldRow : Old →ₗ[ℚ] ℚ
  sourceInto : Source →ₗ[ℚ] W
  targetInto : Target →ₗ[ℚ] W
  ell_source : ell.comp sourceInto = actualSourceRow sourceCoords oldRow
  ell_target : ell.comp targetInto =
    actualTargetRow newFactors targetCoords oldRow

/-- The undotted sphere relation in the ambient state sum. -/
def SphereChart.undottedRelation {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (chart : SphereChart W ell) : chart.Source →ₗ[ℚ] W :=
  chart.targetInto.comp
    (conjugatedInsertion chart.sourceCoords chart.newFactors chart.targetCoords .one)

/-- The once-dotted map minus the identity-cylinder source term. -/
def SphereChart.dottedMinusIdRelation
    {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (chart : SphereChart W ell) : chart.Source →ₗ[ℚ] W :=
  chart.targetInto.comp
      (conjugatedInsertion chart.sourceCoords chart.newFactors chart.targetCoords .X) -
    chart.sourceInto

theorem SphereChart.ell_comp_undotted_eq_zero
    {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (chart : SphereChart W ell) :
    ell.comp chart.undottedRelation = 0 := by
  ext x
  have hTarget := LinearMap.congr_fun chart.ell_target
    ((conjugatedInsertion chart.sourceCoords chart.newFactors
      chart.targetCoords .one) x)
  have hCanonical := LinearMap.congr_fun
    (directQ_undotted_row_eq_zero chart.sourceCoords chart.newFactors
      chart.targetCoords chart.oldRow chart.newFactors_pos) x
  simpa [SphereChart.undottedRelation] using hTarget.trans hCanonical

theorem SphereChart.ell_comp_dottedMinusId_eq_zero
    {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (chart : SphereChart W ell) :
    ell.comp chart.dottedMinusIdRelation = 0 := by
  ext x
  have hTarget := LinearMap.congr_fun chart.ell_target
    ((conjugatedInsertion chart.sourceCoords chart.newFactors
      chart.targetCoords .X) x)
  have hSource := LinearMap.congr_fun chart.ell_source x
  have hCanonical := LinearMap.congr_fun
    (directQ_dotted_row_eq_source chart.sourceCoords chart.newFactors
      chart.targetCoords chart.oldRow chart.newFactors_pos) x
  have ht :
      ell (chart.targetInto
        ((conjugatedInsertion chart.sourceCoords chart.newFactors
          chart.targetCoords .X) x)) =
        actualTargetRow chart.newFactors chart.targetCoords chart.oldRow
          ((conjugatedInsertion chart.sourceCoords chart.newFactors
            chart.targetCoords .X) x) := by
    simpa using hTarget
  have hs : ell (chart.sourceInto x) =
      actualSourceRow chart.sourceCoords chart.oldRow x := by
    simpa using hSource
  have hc :
      actualTargetRow chart.newFactors chart.targetCoords chart.oldRow
          ((conjugatedInsertion chart.sourceCoords chart.newFactors
            chart.targetCoords .X) x) =
        actualSourceRow chart.sourceCoords chart.oldRow x := by
    simpa using hCanonical
  change ell
      (chart.targetInto
        ((conjugatedInsertion chart.sourceCoords chart.newFactors
          chart.targetCoords .X) x) - chart.sourceInto x) = 0
  calc
    _ = ell (chart.targetInto
          ((conjugatedInsertion chart.sourceCoords chart.newFactors
            chart.targetCoords .X) x)) - ell (chart.sourceInto x) := ell.map_sub _ _
    _ = actualTargetRow chart.newFactors chart.targetCoords chart.oldRow
          ((conjugatedInsertion chart.sourceCoords chart.newFactors
            chart.targetCoords .X) x) -
        actualSourceRow chart.sourceCoords chart.oldRow x := by rw [ht, hs]
    _ = 0 := by rw [hc]; simp

/-- The exact obligation which identifies an actual MWW sphere map with the
canonical local Frobenius model.  This is the geometric input; no selected
vector or scalar check appears in it. -/
structure ActualSphereBinding
    (u : AuditUniverse) (W : QMod) (ell : W →ₗ[ℚ] ℚ) where
  model : SphereChart W ell
  sphere : u.SphereDatum
  embedded : u.IsEmbedded sphere u.candidate
  classCoordinate : W
  classBinding : u.IsClassCoordinate sphere classCoordinate
  sigma0 : model.Source →ₗ[ℚ] W
  sigma1MinusId : model.Source →ₗ[ℚ] W
  sigma0Binding : u.IsActualSphereMap SphereMapKind.sigma0 sphere sigma0
  sigma1MinusIdBinding :
    u.IsActualSphereMap SphereMapKind.sigma1MinusId sphere sigma1MinusId
  sigma0_eq : sigma0 = model.undottedRelation
  sigma1MinusId_eq : sigma1MinusId = model.dottedMinusIdRelation

theorem ActualSphereBinding.ell_comp_sigma0_eq_zero
    {u : AuditUniverse} {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (binding : ActualSphereBinding u W ell) :
    ell.comp binding.sigma0 = 0 := by
  rw [binding.sigma0_eq]
  exact binding.model.ell_comp_undotted_eq_zero

theorem ActualSphereBinding.ell_comp_sigma1MinusId_eq_zero
    {u : AuditUniverse} {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (binding : ActualSphereBinding u W ell) :
    ell.comp binding.sigma1MinusId = 0 := by
  rw [binding.sigma1MinusId_eq]
  exact binding.model.ell_comp_dottedMinusId_eq_zero

/-- The three actual chosen sphere slots. -/
structure SphereTriple
    (u : AuditUniverse) (W : QMod) (ell : W →ₗ[ℚ] ℚ) where
  th1 : ActualSphereBinding u W ell
  th2 : ActualSphereBinding u W ell
  thxy : ActualSphereBinding u W ell
  pairwiseDisjoint : u.PairwiseDisjoint th1.sphere th2.sphere thxy.sphere
  hjBinding : u.IsHJReplacement th1.sphere th2.sphere thxy.sphere

/-- The six MWW sphere relations generated by the three chosen spheres. -/
def sphereRelation {u : AuditUniverse} {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (spheres : SphereTriple u W ell) : Submodule ℚ W :=
  LinearMap.range spheres.th1.sigma0 ⊔
    LinearMap.range spheres.th1.sigma1MinusId ⊔
      LinearMap.range spheres.th2.sigma0 ⊔
        LinearMap.range spheres.th2.sigma1MinusId ⊔
          LinearMap.range spheres.thxy.sigma0 ⊔
            LinearMap.range spheres.thxy.sigma1MinusId

theorem range_le_ker_of_comp_eq_zero
    {Source W : QMod} (ell : W →ₗ[ℚ] ℚ) (relation : Source →ₗ[ℚ] W)
    (h : ell.comp relation = 0) :
    LinearMap.range relation ≤ LinearMap.ker ell := by
  rintro y ⟨x, rfl⟩
  rw [LinearMap.mem_ker]
  have hx := LinearMap.congr_fun h x
  simpa using hx

theorem sphereRelation_le_ker
    {u : AuditUniverse} {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (spheres : SphereTriple u W ell) :
    sphereRelation spheres ≤ LinearMap.ker ell := by
  rw [sphereRelation]
  apply sup_le
  · apply sup_le
    · apply sup_le
      · apply sup_le
        · apply sup_le
          · exact range_le_ker_of_comp_eq_zero ell _
              spheres.th1.ell_comp_sigma0_eq_zero
          · exact range_le_ker_of_comp_eq_zero ell _
              spheres.th1.ell_comp_sigma1MinusId_eq_zero
        · exact range_le_ker_of_comp_eq_zero ell _
            spheres.th2.ell_comp_sigma0_eq_zero
      · exact range_le_ker_of_comp_eq_zero ell _
          spheres.th2.ell_comp_sigma1MinusId_eq_zero
    · exact range_le_ker_of_comp_eq_zero ell _
        spheres.thxy.ell_comp_sigma0_eq_zero
  · exact range_le_ker_of_comp_eq_zero ell _
      spheres.thxy.ell_comp_sigma1MinusId_eq_zero

/-- The canonical linear quotient by the ranges of all six bound sphere maps. -/
abbrev SphereQuotient
    {u : AuditUniverse} {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (spheres : SphereTriple u W ell) := W ⧸ sphereRelation spheres

def sphereQuotientMap
    {u : AuditUniverse} {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (spheres : SphereTriple u W ell) : W →ₗ[ℚ] SphereQuotient spheres :=
  (sphereRelation spheres).mkQ

/-- The detector obtained from the quotient universal property. -/
def descendedSphereRow
    {u : AuditUniverse} {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (spheres : SphereTriple u W ell) : SphereQuotient spheres →ₗ[ℚ] ℚ :=
  (sphereRelation spheres).liftQ ell (sphereRelation_le_ker spheres)

theorem descendedSphereRow_comp_quotient
    {u : AuditUniverse} {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (spheres : SphereTriple u W ell) :
    (descendedSphereRow spheres).comp (sphereQuotientMap spheres) = ell := by
  exact Submodule.liftQ_mkQ _ _ _

theorem sphereClass_ne_zero
    {u : AuditUniverse} {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (spheres : SphereTriple u W ell) (x : W) (hx : ell x ≠ 0) :
    sphereQuotientMap spheres x ≠ 0 := by
  intro hzero
  apply hx
  have h := congrArg (descendedSphereRow spheres) hzero
  simpa [descendedSphereRow, sphereQuotientMap] using h

/-- The final external identification still needed to call the formal quotient
the MWW three-handle coequalizer. -/
structure MWWBoundSphereQuotient
    (u : AuditUniverse) (W : QMod) (ell : W →ₗ[ℚ] ℚ) where
  spheres : SphereTriple u W ell
  mwwCoequalizerBinding :
    @u.IsActualMWWCoequalizer W
      (ModuleCat.of ℚ (SphereQuotient spheres))
      spheres.th1.sphere spheres.th2.sphere spheres.thxy.sphere
      (sphereQuotientMap spheres)

end

end Smooth4PC.T73
