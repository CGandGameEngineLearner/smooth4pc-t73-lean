import Mathlib
import Smooth4PC.Arithmetic

namespace Smooth4PC

/-- The single linear category used by every staged external interface. -/
abbrev QMod := ModuleCat.{0} ℚ

inductive PsiRelationKind where
  | psi0
  | psi1

inductive SphereMapKind where
  | sigma0
  | sigma1MinusId

/-- The ambient geometric surface; `G` is the only graded-module functor. -/
structure AuditUniverse where
  Manifold : Type
  G : Manifold → ℤ → QMod
  candidate : Manifold
  S4 : Manifold
  IsHomotopySphere : Manifold → Prop
  Diffeomorphic : Manifold → Manifold → Prop
  SphereDatum : Type
  IsEmbedded : SphereDatum → Manifold → Prop
  PairwiseDisjoint : SphereDatum → SphereDatum → SphereDatum → Prop
  IsClassCoordinate : ∀ {W : QMod}, SphereDatum → W → Prop
  IsActualHH0 : ∀ {HHRaw W0 : QMod}, Submodule ℚ HHRaw → (HHRaw →ₗ[ℚ] W0) → Prop
  IsActualCapAtOrder : ∀ {HHRaw : QMod}, Nat → (HHRaw →ₗ[ℚ] ℚ) → Prop
  IsActualBetaRelation : ∀ {Level : Type} {Source W0 : QMod}, Level → (Source →ₗ[ℚ] W0) → Prop
  IsActualPsiRelation : ∀ {Source W0 : QMod}, PsiRelationKind → (Source →ₗ[ℚ] W0) → Prop
  IsActualSphereMap : ∀ {Source W1 : QMod}, SphereMapKind → SphereDatum → (Source →ₗ[ℚ] W1) → Prop
  IsHJReplacement : SphereDatum → SphereDatum → SphereDatum → Prop
  IsActualMWWCoequalizer :
    ∀ {W1 W2 : QMod}, SphereDatum → SphereDatum → SphereDatum → (W1 →ₗ[ℚ] W2) → Prop
  IsActualMWWTransport : ∀ {W2 W3 : QMod}, (W2 ≃ₗ[ℚ] W3) → Prop
  IsActualFourHandle : ∀ {W3 : QMod}, (W3 ≃ₗ[ℚ] G candidate 494) → Prop

/-- One-handle data: actual cap is raw; Task 5 derives `ell0` through the HH0 UP. -/
structure OneHandleInterface (u : AuditUniverse) (W0 : QMod) where
  HHRaw : QMod
  hh0Relation : Submodule ℚ HHRaw
  hh0Quotient : HHRaw →ₗ[ℚ] W0
  hh0Binding : u.IsActualHH0 hh0Relation hh0Quotient
  hh0Kernel : ∀ x : HHRaw, x ∈ hh0Relation → hh0Quotient x = 0
  hh0Lift : ∀ {Target : QMod} (f : HHRaw →ₗ[ℚ] Target),
    (∀ x : HHRaw, x ∈ hh0Relation → f x = 0) →
      ∃ g : W0 →ₗ[ℚ] Target, f = g.comp hh0Quotient
  hh0LiftCommutes : ∀ {Target : QMod} (f : HHRaw →ₗ[ℚ] Target)
    (compatible : ∀ x : HHRaw, x ∈ hh0Relation → f x = 0),
      ∀ g : W0 →ₗ[ℚ] Target, f = g.comp hh0Quotient →
        ∀ x : HHRaw, f x = g (hh0Quotient x)
  hh0LiftUnique : ∀ {Target : QMod} (f : HHRaw →ₗ[ℚ] Target)
    (compatible : ∀ x : HHRaw, x ∈ hh0Relation → f x = 0)
    (g h : W0 →ₗ[ℚ] Target),
      f = g.comp hh0Quotient → f = h.comp hh0Quotient → g = h
  chosenRaw : HHRaw
  chosenClass : W0
  chosenBinding : hh0Quotient chosenRaw = chosenClass
  traceAnomalyOrder : Nat
  traceAnomalyOrderEq : traceAnomalyOrder = 3
  rawCap : HHRaw →ₗ[ℚ] ℚ
  rawCapBinding : u.IsActualCapAtOrder traceAnomalyOrder rawCap
  rawCapKillsHH0 : ∀ x : HHRaw, x ∈ hh0Relation → rawCap x = 0
  rawCapChosen : rawCap chosenRaw = (-59072 : ℚ)

/-- Beta/psi descent exposes exact generators; Task 5 proves the kernel inclusion by span. -/
structure BetaPsiInterface (u : AuditUniverse) (W0 W1 : QMod) (ell0 : W0 →ₗ[ℚ] ℚ) where
  Level : Type
  betaSource : Level → QMod
  betaRelation : ∀ level : Level, betaSource level →ₗ[ℚ] W0
  betaRelationBinding : ∀ level : Level, u.IsActualBetaRelation level (betaRelation level)
  betaRelationEquation : ∀ level : Level, ell0.comp (betaRelation level) = 0
  psi0Source : QMod
  psi0Relation : psi0Source →ₗ[ℚ] W0
  psi0Binding : u.IsActualPsiRelation PsiRelationKind.psi0 psi0Relation
  psi0Equation : ell0.comp psi0Relation = 0
  psi1Source : QMod
  psi1Relation : psi1Source →ₗ[ℚ] W0
  psi1Binding : u.IsActualPsiRelation PsiRelationKind.psi1 psi1Relation
  psi1Equation : ell0.comp psi1Relation = 0
  R01GeneratorSet : Set W0
  R01GeneratorSet_eq :
    R01GeneratorSet =
      (Set.iUnion fun level : Level => (LinearMap.range (betaRelation level) : Set W0)) ∪
        (LinearMap.range psi0Relation : Set W0) ∪
          (LinearMap.range psi1Relation : Set W0)
  R01 : Submodule ℚ W0
  R01_eq_span : R01 = Submodule.span ℚ R01GeneratorSet
  q01 : W0 →ₗ[ℚ] W1
  q01Kernel : ∀ x : W0, x ∈ R01 → q01 x = 0
  quotientLift : ∀ {Target : QMod} (f : W0 →ₗ[ℚ] Target),
    (∀ x : W0, x ∈ R01 → f x = 0) →
      ∃ g : W1 →ₗ[ℚ] Target, f = g.comp q01
  quotientLiftCommutes : ∀ {Target : QMod} (f : W0 →ₗ[ℚ] Target)
    (compatible : ∀ x : W0, x ∈ R01 → f x = 0),
      ∀ g : W1 →ₗ[ℚ] Target, f = g.comp q01 →
        ∀ x : W0, f x = g (q01 x)
  quotientLiftUnique : ∀ {Target : QMod} (f : W0 →ₗ[ℚ] Target)
    (compatible : ∀ x : W0, x ∈ R01 → f x = 0)
    (g h : W1 →ₗ[ℚ] Target),
      f = g.comp q01 → f = h.comp q01 → g = h

/-- One selected sphere: two actual maps into `W1`, killed by the derived `ell1`. -/
structure SphereLocalInterface (u : AuditUniverse) (W1 : QMod) (ell1 : W1 →ₗ[ℚ] ℚ) where
  Source : QMod
  sphere : u.SphereDatum
  embedded : u.IsEmbedded sphere u.candidate
  classCoordinate : W1
  classBinding : u.IsClassCoordinate sphere classCoordinate
  sigma0 : Source →ₗ[ℚ] W1
  sigma0Binding : u.IsActualSphereMap SphereMapKind.sigma0 sphere sigma0
  sigma0Equation : ell1.comp sigma0 = 0
  sigma1MinusId : Source →ₗ[ℚ] W1
  sigma1MinusIdBinding : u.IsActualSphereMap SphereMapKind.sigma1MinusId sphere sigma1MinusId
  sigma1MinusIdEquation : ell1.comp sigma1MinusId = 0

/-- The sphere/HJ/MWW package is available for every derived `ell1`. -/
structure SphereMWWFamily
    (u : AuditUniverse) (W1 W2 W3 : QMod) (ell1 : W1 →ₗ[ℚ] ℚ) where
  th1 : SphereLocalInterface u W1 ell1
  th2 : SphereLocalInterface u W1 ell1
  thxy : SphereLocalInterface u W1 ell1
  pairwiseDisjoint : u.PairwiseDisjoint th1.sphere th2.sphere thxy.sphere
  hjBinding : u.IsHJReplacement th1.sphere th2.sphere thxy.sphere
  R12GeneratorSet : Set W1
  R12GeneratorSet_eq :
    R12GeneratorSet =
      (LinearMap.range th1.sigma0 : Set W1) ∪
        (LinearMap.range th1.sigma1MinusId : Set W1) ∪
          (LinearMap.range th2.sigma0 : Set W1) ∪
            (LinearMap.range th2.sigma1MinusId : Set W1) ∪
              (LinearMap.range thxy.sigma0 : Set W1) ∪
                (LinearMap.range thxy.sigma1MinusId : Set W1)
  R12 : Submodule ℚ W1
  R12_eq_span : R12 = Submodule.span ℚ R12GeneratorSet
  q12 : W1 →ₗ[ℚ] W2
  q12Kernel : ∀ x : W1, x ∈ R12 → q12 x = 0
  quotientLift : ∀ {Target : QMod} (f : W1 →ₗ[ℚ] Target),
    (∀ x : W1, x ∈ R12 → f x = 0) →
      ∃ g : W2 →ₗ[ℚ] Target, f = g.comp q12
  quotientLiftCommutes : ∀ {Target : QMod} (f : W1 →ₗ[ℚ] Target)
    (compatible : ∀ x : W1, x ∈ R12 → f x = 0),
      ∀ g : W2 →ₗ[ℚ] Target, f = g.comp q12 →
        ∀ x : W1, f x = g (q12 x)
  quotientLiftUnique : ∀ {Target : QMod} (f : W1 →ₗ[ℚ] Target)
    (compatible : ∀ x : W1, x ∈ R12 → f x = 0)
    (g h : W2 →ₗ[ℚ] Target),
      f = g.comp q12 → f = h.comp q12 → g = h
  mwwCoequalizerBinding : u.IsActualMWWCoequalizer th1.sphere th2.sphere thxy.sphere q12
  mwwTransport : W2 ≃ₗ[ℚ] W3
  transportBinding : u.IsActualMWWTransport mwwTransport

/-- Four-handle data is exactly a linear equivalence into degree 494 of the candidate. -/
structure FourHandleInterface (u : AuditUniverse) (W3 : QMod) where
  fourIso : W3 ≃ₗ[ℚ] u.G u.candidate 494
  fourHandleBinding : u.IsActualFourHandle fourIso

/-- Standard-sphere support: every nonzero degree is zero. -/
structure S4ControlInterface (u : AuditUniverse) where
  degreeSupport : ∀ q : ℤ, q ≠ 0 → ∀ x : u.G u.S4 q, x = 0

/-- Diffeomorphism invariance supplies only induced linear equivalences. -/
structure DiffeomorphismInvarianceInterface (u : AuditUniverse) where
  preservesGradedObject : ∀ {left right : u.Manifold},
    u.Diffeomorphic left right → ∀ q : ℤ,
      u.G left q ≃ₗ[ℚ] u.G right q

/-- All non-CS interfaces needed by the not-standard branch. -/
structure NotStandardInterfaces (u : AuditUniverse) (W0 W1 W2 W3 : QMod) where
  oneHandle : OneHandleInterface u W0
  betaPsi : ∀ ell0 : W0 →ₗ[ℚ] ℚ,
    ell0.comp oneHandle.hh0Quotient = oneHandle.rawCap → BetaPsiInterface u W0 W1 ell0
  sphereMWW : ∀ ell0 : W0 →ₗ[ℚ] ℚ,
    (h0 : ell0.comp oneHandle.hh0Quotient = oneHandle.rawCap) →
      ∀ ell1 : W1 →ₗ[ℚ] ℚ, ell1.comp (betaPsi ell0 h0).q01 = ell0 →
        SphereMWWFamily u W1 W2 W3 ell1
  fourHandle : FourHandleInterface u W3
  s4Control : S4ControlInterface u
  diffeomorphismInvariance : DiffeomorphismInvarianceInterface u

/-- The local Cappell--Shaneson bridge consumes only the two determinant facts. -/
structure CappellShanesonInterface (u : AuditUniverse) where
  matrixConditionsToHomotopySphere :
    det3 matrixA = 1 → det3 matrixAMinusI = 1 → u.IsHomotopySphere u.candidate

/-- Frozen body for the not-standard conditional theorem; CS is intentionally absent. -/
def conditionalNotStandardSignature
    (u : AuditUniverse) (W0 W1 W2 W3 : QMod) : Prop :=
  NotStandardInterfaces u W0 W1 W2 W3 → ¬ u.Diffeomorphic u.candidate u.S4

/-- Frozen body for the homotopy-sphere conditional theorem. -/
def conditionalIsHomotopySphereSignature (u : AuditUniverse) : Prop :=
  CappellShanesonInterface u → u.IsHomotopySphere u.candidate

/-- Frozen body for joining the not-standard and homotopy-sphere branches. -/
def conditionalCounterexampleSignature
    (u : AuditUniverse) (W0 W1 W2 W3 : QMod) : Prop :=
  NotStandardInterfaces u W0 W1 W2 W3 →
    CappellShanesonInterface u →
      u.IsHomotopySphere u.candidate ∧ ¬ u.Diffeomorphic u.candidate u.S4

end Smooth4PC
