import Smooth4PC.T73Conditional
import Smooth4PC.T73S4Inhabitant

namespace Smooth4PC.T73

/-!
Certificate-parameterized packaging of the remaining lasagna maps.  The
empty-link `S4ReductionData` inhabitant discharges `s4DegreeZero` on any
universe that supplies those two equivalences.  The candidate transport
maps `q01`, `q12`, `transport`, `fourIso` and graded diffeomorphism
invariance remain parameters.  No global inhabitant of `ExternalGeometry`
or `CSTopologyData` is constructed.
-/

abbrev DetectorLine : ModuleCat ℚ := ModuleCat.of ℚ ℚ

/-- Remaining detector-to-candidate maps after the finite cubic and, when
packaged below, the empty-link `S^4` vanishing. -/
structure DetectorTransport (u : Universe) where
  W0 : ModuleCat ℚ
  W1 : ModuleCat ℚ
  W2 : ModuleCat ℚ
  W3 : ModuleCat ℚ
  x0 : W0
  ell0 : W0 →ₗ[ℚ] ℚ
  ell0_x0 : ell0 x0 = (computedCubic : ℚ)
  q01 : W0 →ₗ[ℚ] W1
  ell1 : W1 →ₗ[ℚ] ℚ
  ell1_comp_q01 : ell1.comp q01 = ell0
  q12 : W1 →ₗ[ℚ] W2
  ell2 : W2 →ₗ[ℚ] ℚ
  ell2_comp_q12 : ell2.comp q12 = ell1
  transport : W2 ≃ₗ[ℚ] W3
  fourIso : W3 ≃ₗ[ℚ] u.G u.candidate computedDegree
  diffeomorphismEquiv :
    u.Diffeomorphic u.candidate u.S4 →
      u.G u.candidate computedDegree ≃ₗ[ℚ] u.G u.S4 computedDegree

noncomputable def packExternalGeometry {u : Universe}
    (maps : DetectorTransport u) (s4 : S4ReductionData u) :
    ExternalGeometry u where
  W0 := maps.W0
  W1 := maps.W1
  W2 := maps.W2
  W3 := maps.W3
  x0 := maps.x0
  ell0 := maps.ell0
  ell0_x0 := maps.ell0_x0
  q01 := maps.q01
  ell1 := maps.ell1
  ell1_comp_q01 := maps.ell1_comp_q01
  q12 := maps.q12
  ell2 := maps.ell2
  ell2_comp_q12 := maps.ell2_comp_q12
  transport := maps.transport
  fourIso := maps.fourIso
  s4DegreeZero := s4ComputedDegreeZero_of_reduction s4
  diffeomorphismEquiv := maps.diffeomorphismEquiv

def csExternalGeometry_of {u : Universe}
    (h : detA = 1 → detAMinusI = 1 → u.IsHomotopySphere u.candidate) :
    CSExternalGeometry u where
  matrixConditionsToHomotopySphere := h

theorem emptyKhQ_computedDegree_eq_zeroModule :
    EmptyKhQ computedDegree = ZeroQModule := by
  unfold EmptyKhQ
  rw [if_neg computedDegree_ne_zero]

theorem detectorLine_not_linearEquiv_emptyKhQ :
    IsEmpty (DetectorLine ≃ₗ[ℚ] EmptyKhQ computedDegree) := by
  refine ⟨fun e => ?_⟩
  haveI : Subsingleton (EmptyKhQ computedDegree) :=
    emptyKhQ_subsingleton computedDegree computedDegree_ne_zero
  have h10 : e 1 = e 0 := Subsingleton.elim _ _
  have hone : (1 : ℚ) = 0 := e.injective h10
  exact (one_ne_zero : (1 : ℚ) ≠ 0) hone

/-- The empty-link control cannot carry the nonzero cubic class.  In
particular it is not a universe for the Johnson candidate. -/
theorem detectorTransport_on_emptyLink_impossible
    (maps : DetectorTransport emptyLinkUniverse) : False := by
  haveI : Subsingleton
      (emptyLinkUniverse.G emptyLinkUniverse.candidate computedDegree) := by
    simpa [emptyLink_candidate_module] using
      emptyKhQ_subsingleton computedDegree computedDegree_ne_zero
  have hcubic : (computedCubic : ℚ) ≠ 0 := by
    exact_mod_cast computedCubic_ne_zero
  have hW3 :
      maps.transport (maps.q12 (maps.q01 maps.x0)) = 0 := by
    apply maps.fourIso.injective
    have : maps.fourIso (maps.transport (maps.q12 (maps.q01 maps.x0))) = 0 :=
      Subsingleton.elim _ _
    simpa using this
  have hW2 : maps.q12 (maps.q01 maps.x0) = 0 := by
    apply maps.transport.injective
    simpa using hW3
  have h01 := LinearMap.congr_fun maps.ell1_comp_q01 maps.x0
  change maps.ell1 (maps.q01 maps.x0) = maps.ell0 maps.x0 at h01
  have h12 := LinearMap.congr_fun maps.ell2_comp_q12 (maps.q01 maps.x0)
  change maps.ell2 (maps.q12 (maps.q01 maps.x0)) =
    maps.ell1 (maps.q01 maps.x0) at h12
  have hvalue : maps.ell2 (maps.q12 (maps.q01 maps.x0)) =
      (computedCubic : ℚ) :=
    h12.trans (h01.trans maps.ell0_x0)
  apply hcubic
  exact hvalue.symm.trans (by simp [hW2])

theorem conditionalCounterexample_of_pack {u : Universe}
    (maps : DetectorTransport u) (s4 : S4ReductionData u)
    (cs : CSExternalGeometry u) :
    u.IsHomotopySphere u.candidate ∧ ¬ u.Diffeomorphic u.candidate u.S4 :=
  conditionalCounterexample (packExternalGeometry maps s4) cs

end Smooth4PC.T73
