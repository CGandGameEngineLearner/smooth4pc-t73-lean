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

noncomputable def TopologicalUniverse.SingularH2
    (u : TopologicalUniverse) (M : u.toUniverse.Manifold) : ModuleCat Int := by
  letI : TopologicalSpace (u.Carrier M) := u.topology M
  exact ((AlgebraicTopology.singularHomologyFunctor (ModuleCat Int) 2).obj
    (ModuleCat.of Int Int)).obj (TopCat.of (u.Carrier M))

def TopologicalUniverse.H2Zero
    (u : TopologicalUniverse) (M : u.toUniverse.Manifold) : Prop :=
  CategoryTheory.Limits.IsZero (u.SingularH2 M)

/-- The genuinely topological remainder of the Cappell--Shaneson argument.
All candidate-specific lattice calculations have been removed from this
interface and proved in `T73CSAlgebra`. -/
structure CSTopologyData (u : TopologicalUniverse) where
  vanKampen :
    Function.Surjective aMinusIMap →
      u.SimplyConnected u.toUniverse.candidate
  wangMayerVietoris :
    Function.Injective aMinusIMap →
      Function.Surjective hTwoMinusIMap →
        u.H2Zero u.toUniverse.candidate
  hurewiczWhitehead :
    u.SimplyConnected u.toUniverse.candidate →
      u.H2Zero u.toUniverse.candidate →
        u.toUniverse.IsHomotopySphere u.toUniverse.candidate

theorem t73IsHomotopySphere_of_topology {u : TopologicalUniverse}
    (topology : CSTopologyData u) :
    u.toUniverse.IsHomotopySphere u.toUniverse.candidate :=
  topology.hurewiczWhitehead
    (topology.vanKampen aMinusIMap_surjective)
    (topology.wangMayerVietoris aMinusIEquiv.injective
      hTwoMinusIMap_surjective)

end Smooth4PC.T73
