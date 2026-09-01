import Smooth4PC.T73CSTopology

namespace Smooth4PC.T73

/-- The selected class transported through both quotients and both equivalences. -/
def selectedClass {u : Universe} (geom : ExternalGeometry u) :
    u.G u.candidate computedDegree :=
  geom.fourIso (geom.transport (geom.q12 (geom.q01 geom.x0)))

theorem selectedClass_ne_zero {u : Universe} (geom : ExternalGeometry u) :
    selectedClass geom ≠ 0 := by
  have hcubic : (computedCubic : ℚ) ≠ 0 := by
    exact_mod_cast computedCubic_ne_zero
  intro hzero
  have hW3 : geom.transport (geom.q12 (geom.q01 geom.x0)) = 0 := by
    apply geom.fourIso.injective
    simpa [selectedClass] using hzero
  have hW2 : geom.q12 (geom.q01 geom.x0) = 0 := by
    apply geom.transport.injective
    simpa using hW3
  have h01 := LinearMap.congr_fun geom.ell1_comp_q01 geom.x0
  change geom.ell1 (geom.q01 geom.x0) = geom.ell0 geom.x0 at h01
  have h12 := LinearMap.congr_fun geom.ell2_comp_q12 (geom.q01 geom.x0)
  change geom.ell2 (geom.q12 (geom.q01 geom.x0)) =
    geom.ell1 (geom.q01 geom.x0) at h12
  have hvalue : geom.ell2 (geom.q12 (geom.q01 geom.x0)) =
      (computedCubic : ℚ) :=
    h12.trans (h01.trans geom.ell0_x0)
  apply hcubic
  exact hvalue.symm.trans (by simp [hW2])

theorem conditionalNotStandard {u : Universe}
    (geom : ExternalGeometry u) :
    ¬ u.Diffeomorphic u.candidate u.S4 := by
  intro hdiffeomorphic
  let e := geom.diffeomorphismEquiv hdiffeomorphic
  have hsphere : e (selectedClass geom) = 0 :=
    geom.s4DegreeZero (e (selectedClass geom))
  apply selectedClass_ne_zero geom
  apply e.injective
  simpa using hsphere

theorem conditionalIsHomotopySphere {u : Universe}
    (cs : CSExternalGeometry u) :
    u.IsHomotopySphere u.candidate :=
  cs.matrixConditionsToHomotopySphere detA_eq_one detAMinusI_eq_one

theorem conditionalCounterexample {u : Universe}
    (geom : ExternalGeometry u) (cs : CSExternalGeometry u) :
    u.IsHomotopySphere u.candidate ∧ ¬ u.Diffeomorphic u.candidate u.S4 :=
  ⟨conditionalIsHomotopySphere cs, conditionalNotStandard geom⟩

/-- The joined conclusion with all candidate-specific Cappell--Shaneson
lattice algebra discharged internally. -/
theorem conditionalCounterexample_of_topology {u : TopologicalUniverse}
    (geom : ExternalGeometry u.toUniverse) (topology : CSTopologyData u) :
    u.toUniverse.IsHomotopySphere u.toUniverse.candidate ∧
      ¬ u.toUniverse.Diffeomorphic u.toUniverse.candidate u.toUniverse.S4 :=
  ⟨t73IsHomotopySphere_of_topology topology, conditionalNotStandard geom⟩

end Smooth4PC.T73
