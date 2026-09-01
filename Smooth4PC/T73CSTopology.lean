import Smooth4PC.T73External
import Smooth4PC.T73CSAlgebra
import Mathlib.AlgebraicTopology.FundamentalGroupoid.SimplyConnected
import Mathlib.AlgebraicTopology.SingularHomology.Basic

namespace Smooth4PC.T73

/-- A geometric realization of every manifold label as an actual topological
space.  The topology predicates below are therefore not free proposition
fields. -/
structure TopologicalUniverse extends Universe where
  Carrier : toUniverse.Manifold → Type
  topology : ∀ M, TopologicalSpace (Carrier M)

def TopologicalUniverse.SimplyConnected
    (u : TopologicalUniverse) (M : u.toUniverse.Manifold) : Prop :=
  @SimplyConnectedSpace (u.Carrier M) (u.topology M)

noncomputable def TopologicalUniverse.SingularH
    (u : TopologicalUniverse) (M : u.toUniverse.Manifold) (n : Nat) :
    ModuleCat Int := by
  letI : TopologicalSpace (u.Carrier M) := u.topology M
  exact ((AlgebraicTopology.singularHomologyFunctor (ModuleCat Int) n).obj
    (ModuleCat.of Int Int)).obj (TopCat.of (u.Carrier M))

def TopologicalUniverse.H2Zero
    (u : TopologicalUniverse) (M : u.toUniverse.Manifold) : Prop :=
  CategoryTheory.Limits.IsZero (u.SingularH M 2)

/-- The actual integral singular-homology profile of a four-sphere. -/
def TopologicalUniverse.IntegralHomologyFourSphere
    (u : TopologicalUniverse) (M : u.toUniverse.Manifold) : Prop :=
  Nonempty (u.SingularH M 0 ≅ ModuleCat.of Int Int) ∧
    Nonempty (u.SingularH M 4 ≅ ModuleCat.of Int Int) ∧
      ∀ n : Nat, n ≠ 0 → n ≠ 4 →
        CategoryTheory.Limits.IsZero (u.SingularH M n)

/-- The genuinely topological remainder of the Cappell--Shaneson argument.
All candidate-specific lattice calculations have been removed from this
interface and proved in `T73CSAlgebra`. -/
structure CSTopologyData (u : TopologicalUniverse) where
  vanKampen :
    Function.Surjective aMinusIMap →
      u.SimplyConnected u.toUniverse.candidate
  wangMayerVietorisPoincare :
    Function.Injective aMinusIMap →
      Function.Surjective hTwoMinusIMap →
        u.IntegralHomologyFourSphere u.toUniverse.candidate
  hurewiczWhitehead :
    u.SimplyConnected u.toUniverse.candidate →
      u.IntegralHomologyFourSphere u.toUniverse.candidate →
        u.toUniverse.IsHomotopySphere u.toUniverse.candidate

theorem t73IsHomotopySphere_of_topology {u : TopologicalUniverse}
    (topology : CSTopologyData u) :
    u.toUniverse.IsHomotopySphere u.toUniverse.candidate :=
  topology.hurewiczWhitehead
    (topology.vanKampen aMinusIMap_surjective)
    (topology.wangMayerVietorisPoincare aMinusIEquiv.injective
      hTwoMinusIMap_surjective)

end Smooth4PC.T73
