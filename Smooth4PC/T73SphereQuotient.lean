import Smooth4PC.T73SplitMovie
import Smooth4PC.Interfaces

namespace Smooth4PC.T73

noncomputable section

/-- One raw sphere movie together with endpoint comparison maps and a positive
split-tree normal form.  The naturality fields are whole-source bindings to the
purely combinatorial model; this structure makes no actual-T73 claim. -/
structure SphereChart (W : QMod) (ell : W →ₗ[ℚ] ℚ) where
  Old : QMod
  Source : QMod
  Target : QMod
  EndpointSource : QMod
  EndpointTarget : QMod
  tree : PositiveNewNewSplitTree
  thetaSource : Source →ₗ[ℚ] EndpointSource
  thetaTarget : Target →ₗ[ℚ] EndpointTarget
  sourceCoords : EndpointSource ≃ₗ[ℚ] Old
  targetCoords : EndpointTarget ≃ₗ[ℚ] TensorTarget Old tree.leafCount
  oldRow : Old →ₗ[ℚ] ℚ
  sourceInto : Source →ₗ[ℚ] W
  targetInto : Target →ₗ[ℚ] W
  rawSigma0 : Source →ₗ[ℚ] Target
  rawSigma1 : Source →ₗ[ℚ] Target
  undottedNaturality :
    thetaTarget.comp rawSigma0 =
      (conjugatedSplitTreeInsertion sourceCoords tree targetCoords .one).comp
        thetaSource
  dottedNaturality :
    thetaTarget.comp rawSigma1 =
      (conjugatedSplitTreeInsertion sourceCoords tree targetCoords .X).comp
        thetaSource
  ell_source :
    ell.comp sourceInto = (actualSourceRow sourceCoords oldRow).comp thetaSource
  ell_target : ell.comp targetInto =
    (actualTargetRow tree.leafCount targetCoords oldRow).comp thetaTarget

/-- The undotted sphere relation in the ambient state sum. -/
def SphereChart.undottedRelation {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (chart : SphereChart W ell) : chart.Source →ₗ[ℚ] W :=
  chart.targetInto.comp chart.rawSigma0

/-- The once-dotted map minus the identity-cylinder source term. -/
def SphereChart.dottedMinusIdRelation
    {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (chart : SphereChart W ell) : chart.Source →ₗ[ℚ] W :=
  chart.targetInto.comp chart.rawSigma1 -
    chart.sourceInto

theorem SphereChart.ell_comp_undotted_eq_zero
    {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (chart : SphereChart W ell) :
    ell.comp chart.undottedRelation = 0 := by
  ext x
  have hTarget := LinearMap.congr_fun chart.ell_target (chart.rawSigma0 x)
  have hNaturality := LinearMap.congr_fun chart.undottedNaturality x
  have hn :
      chart.thetaTarget (chart.rawSigma0 x) =
        (conjugatedSplitTreeInsertion chart.sourceCoords chart.tree
          chart.targetCoords .one) (chart.thetaSource x) := by
    simpa using hNaturality
  have hCanonical := LinearMap.congr_fun
    (splitTree_directQ_undotted_row_eq_zero chart.sourceCoords chart.tree
      chart.targetCoords chart.oldRow) (chart.thetaSource x)
  change ell (chart.targetInto (chart.rawSigma0 x)) = 0
  calc
    _ = actualTargetRow chart.tree.leafCount chart.targetCoords chart.oldRow
        (chart.thetaTarget (chart.rawSigma0 x)) := by simpa using hTarget
    _ = actualTargetRow chart.tree.leafCount chart.targetCoords chart.oldRow
        ((conjugatedSplitTreeInsertion chart.sourceCoords chart.tree
          chart.targetCoords .one) (chart.thetaSource x)) := by rw [hn]
    _ = 0 := by simpa using hCanonical

theorem SphereChart.ell_comp_dottedMinusId_eq_zero
    {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (chart : SphereChart W ell) :
    ell.comp chart.dottedMinusIdRelation = 0 := by
  ext x
  have hTarget := LinearMap.congr_fun chart.ell_target (chart.rawSigma1 x)
  have hSource := LinearMap.congr_fun chart.ell_source x
  have hNaturality := LinearMap.congr_fun chart.dottedNaturality x
  have hn :
      chart.thetaTarget (chart.rawSigma1 x) =
        (conjugatedSplitTreeInsertion chart.sourceCoords chart.tree
          chart.targetCoords .X) (chart.thetaSource x) := by
    simpa using hNaturality
  have hCanonical := LinearMap.congr_fun
    (splitTree_directQ_dotted_row_eq_source chart.sourceCoords chart.tree
      chart.targetCoords chart.oldRow) (chart.thetaSource x)
  have ht :
      ell (chart.targetInto (chart.rawSigma1 x)) =
        actualTargetRow chart.tree.leafCount chart.targetCoords chart.oldRow
          (chart.thetaTarget (chart.rawSigma1 x)) := by
    simpa using hTarget
  have hs : ell (chart.sourceInto x) =
      actualSourceRow chart.sourceCoords chart.oldRow (chart.thetaSource x) := by
    simpa using hSource
  have hc :
      actualTargetRow chart.tree.leafCount chart.targetCoords chart.oldRow
          ((conjugatedSplitTreeInsertion chart.sourceCoords chart.tree
            chart.targetCoords .X) (chart.thetaSource x)) =
        actualSourceRow chart.sourceCoords chart.oldRow (chart.thetaSource x) := by
    simpa using hCanonical
  change ell
      (chart.targetInto (chart.rawSigma1 x) - chart.sourceInto x) = 0
  calc
    _ = ell (chart.targetInto (chart.rawSigma1 x)) -
        ell (chart.sourceInto x) := ell.map_sub _ _
    _ = actualTargetRow chart.tree.leafCount chart.targetCoords chart.oldRow
          (chart.thetaTarget (chart.rawSigma1 x)) -
        actualSourceRow chart.sourceCoords chart.oldRow
          (chart.thetaSource x) := by rw [ht, hs]
    _ = actualTargetRow chart.tree.leafCount chart.targetCoords chart.oldRow
          ((conjugatedSplitTreeInsertion chart.sourceCoords chart.tree
            chart.targetCoords .X) (chart.thetaSource x)) -
        actualSourceRow chart.sourceCoords chart.oldRow
          (chart.thetaSource x) := by rw [hn]
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
  sigma0Binding :
    u.IsActualSphereMap SphereMapKind.sigma0 sphere model.undottedRelation
  sigma1MinusIdBinding :
    u.IsActualSphereMap SphereMapKind.sigma1MinusId sphere
      model.dottedMinusIdRelation

theorem ActualSphereBinding.ell_comp_sigma0_eq_zero
    {u : AuditUniverse} {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (binding : ActualSphereBinding u W ell) :
    ell.comp binding.model.undottedRelation = 0 :=
  binding.model.ell_comp_undotted_eq_zero

theorem ActualSphereBinding.ell_comp_sigma1MinusId_eq_zero
    {u : AuditUniverse} {W : QMod} {ell : W →ₗ[ℚ] ℚ}
    (binding : ActualSphereBinding u W ell) :
    ell.comp binding.model.dottedMinusIdRelation = 0 :=
  binding.model.ell_comp_dottedMinusId_eq_zero

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
  LinearMap.range spheres.th1.model.undottedRelation ⊔
    LinearMap.range spheres.th1.model.dottedMinusIdRelation ⊔
      LinearMap.range spheres.th2.model.undottedRelation ⊔
        LinearMap.range spheres.th2.model.dottedMinusIdRelation ⊔
          LinearMap.range spheres.thxy.model.undottedRelation ⊔
            LinearMap.range spheres.thxy.model.dottedMinusIdRelation

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
