import Smooth4PC.T73Finite

namespace Smooth4PC.T73

/-- The ambient objects left external to the finite T73 calculation. -/
structure Universe where
  Manifold : Type
  G : Manifold → Int → ModuleCat ℚ
  candidate : Manifold
  S4 : Manifold
  IsHomotopySphere : Manifold → Prop
  Diffeomorphic : Manifold → Manifold → Prop

/-- Explicit geometric input needed to carry the detected class to the candidate. -/
structure ExternalGeometry (u : Universe) where
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
  s4DegreeZero : ∀ x : u.G u.S4 computedDegree, x = 0
  diffeomorphismEquiv :
    u.Diffeomorphic u.candidate u.S4 →
      u.G u.candidate computedDegree ≃ₗ[ℚ] u.G u.S4 computedDegree

/-- The Cappell--Shaneson input consumes exactly the two determinant checks. -/
structure CSExternalGeometry (u : Universe) where
  matrixConditionsToHomotopySphere :
    detA = 1 → detAMinusI = 1 → u.IsHomotopySphere u.candidate

end Smooth4PC.T73
