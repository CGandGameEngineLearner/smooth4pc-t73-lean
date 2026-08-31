import Mathlib.Algebra.Module.LinearMap.Basic
import Mathlib.Algebra.Module.Equiv.Basic
import Mathlib.Algebra.BigOperators.GroupWithZero.Finset
import Mathlib.Data.Fintype.Basic
import Mathlib.Data.List.OfFn
import Mathlib.Data.Rat.BigOperators

namespace Smooth4PC

/-!
This module proves only the finite augmentation algebra used by the candidate
argument.  It does not assert the actual T73 geometric premises that would
identify concrete sphere or psi movies with these abstract maps.
-/

/-- The basis `(1, X)` of the rank-two Frobenius module. -/
inductive FrobeniusBasis where
  | one
  | X
  deriving DecidableEq, Repr

/-- A tensor word with exactly `b` ordered Frobenius factors. -/
abbrev TensorWord (b : Nat) := Fin b → FrobeniusBasis

/-- The tensor word `X ⊗ ... ⊗ X`, represented without an algebra power. -/
def allX (b : Nat) : TensorWord b := fun _ => .X

/-- The tensor word with one `1` at `i` and `X` at every other factor. -/
def oneAt {b : Nat} (i : Fin b) : TensorWord b :=
  fun j => if j = i then .one else .X

/-- The Frobenius counit on the basis. -/
def epsilon : FrobeniusBasis → ℚ
  | .one => 0
  | .X => 1

/-- Apply the counit independently to all factors of one tensor word. -/
def epsilonTensor {b : Nat} (word : TensorWord b) : ℚ :=
  ∏ i, epsilon (word i)

/--
The normal-form support of the `(b-1)`-fold iterated coproduct.  The coproduct
of `1` has one `1` in each possible position; the coproduct of `X` is all `X`.
-/
def iteratedDelta (b : Nat) : FrobeniusBasis → List (TensorWord b)
  | .one => List.ofFn fun i : Fin b => oneAt i
  | .X => [allX b]

/-- The rank-two coproduct `Delta`, as the two-factor case. -/
def delta : FrobeniusBasis → List (TensorWord 2) := iteratedDelta 2

/-- Extend `epsilon^b` linearly over a finite list of tensor words. -/
def epsilonWords {b : Nat} (words : List (TensorWord b)) : ℚ :=
  (words.map epsilonTensor).sum

@[simp] theorem epsilonTensor_allX (b : Nat) : epsilonTensor (allX b) = 1 := by
  simp [epsilonTensor, allX, epsilon]

@[simp] theorem epsilonTensor_oneAt {b : Nat} (i : Fin b) : epsilonTensor (oneAt i) = 0 := by
  classical
  change (∏ j ∈ Finset.univ, epsilon (oneAt i j)) = 0
  apply Finset.prod_eq_zero (Finset.mem_univ i)
  simp [oneAt, epsilon]

/-- `epsilon^b (Delta^(b-1)(1)) = 0` for every positive number of leaves. -/
theorem epsilon_iteratedDelta_one_eq_zero (b : Nat) (_hb : 0 < b) :
    epsilonWords (iteratedDelta b .one) = 0 := by
  simp [epsilonWords, iteratedDelta, Function.comp_def]

/-- `epsilon^b (Delta^(b-1)(X)) = 1` for every positive number of leaves. -/
theorem epsilon_iteratedDelta_X_eq_one (b : Nat) (_hb : 0 < b) :
    epsilonWords (iteratedDelta b .X) = 1 := by
  simp [epsilonWords, iteratedDelta]

/-- The canonical insertion after applying the counit on all new factors. -/
def canonicalInsertion {V : Type*} [AddCommGroup V] [Module ℚ V]
    (b : Nat) (basis : FrobeniusBasis) : V →ₗ[ℚ] V :=
  (epsilonWords (iteratedDelta b basis)) • LinearMap.id

/-- Pull a canonical row back through an explicit vertex equivalence. -/
def transportedRow {V C : Type*}
    [AddCommGroup V] [Module ℚ V] [AddCommGroup C] [Module ℚ C]
    (Q : V ≃ₗ[ℚ] C) (row : C →ₗ[ℚ] ℚ) : V →ₗ[ℚ] ℚ :=
  row.comp Q.toLinearMap

/-- Conjugate a canonical insertion by explicit source and target coordinates. -/
def conjugatedInsertion {Vs Vt C : Type*}
    [AddCommGroup Vs] [Module ℚ Vs]
    [AddCommGroup Vt] [Module ℚ Vt]
    [AddCommGroup C] [Module ℚ C]
    (Qs : Vs ≃ₗ[ℚ] C) (Qt : Vt ≃ₗ[ℚ] C)
    (b : Nat) (basis : FrobeniusBasis) : Vs →ₗ[ℚ] Vt :=
  Qt.symm.toLinearMap.comp
    ((canonicalInsertion (V := C) b basis).comp Qs.toLinearMap)

/-- The conjugated undotted row vanishes on the whole source. -/
theorem directQ_undotted_row_eq_zero {Vs Vt C : Type*}
    [AddCommGroup Vs] [Module ℚ Vs]
    [AddCommGroup Vt] [Module ℚ Vt]
    [AddCommGroup C] [Module ℚ C]
    (Qs : Vs ≃ₗ[ℚ] C) (Qt : Vt ≃ₗ[ℚ] C)
    (row : C →ₗ[ℚ] ℚ) (b : Nat) (hb : 0 < b) :
    (transportedRow Qt row).comp (conjugatedInsertion Qs Qt b .one) = 0 := by
  ext x
  simp [transportedRow, conjugatedInsertion, canonicalInsertion,
    epsilon_iteratedDelta_one_eq_zero b hb]

/-- The conjugated dotted row is the source row on the whole source. -/
theorem directQ_dotted_row_eq_source {Vs Vt C : Type*}
    [AddCommGroup Vs] [Module ℚ Vs]
    [AddCommGroup Vt] [Module ℚ Vt]
    [AddCommGroup C] [Module ℚ C]
    (Qs : Vs ≃ₗ[ℚ] C) (Qt : Vt ≃ₗ[ℚ] C)
    (row : C →ₗ[ℚ] ℚ) (b : Nat) (hb : 0 < b) :
    (transportedRow Qt row).comp (conjugatedInsertion Qs Qt b .X) =
      transportedRow Qs row := by
  ext x
  simp [transportedRow, conjugatedInsertion, canonicalInsertion,
    epsilon_iteratedDelta_X_eq_one b hb]

/-- Ratio of target to source physical-copy orbit sizes. -/
def physicalCopyOrbitRatio (source target : ℚ) : ℚ :=
  target / source

/-- Physical-copy orbit normalizations telescope along a finite two-edge path. -/
theorem physicalCopyOrbitRatio_telescope
    (source middle target : ℚ) (_hsource : source ≠ 0) (hmiddle : middle ≠ 0) :
    physicalCopyOrbitRatio source middle * physicalCopyOrbitRatio middle target =
      physicalCopyOrbitRatio source target := by
  simp only [physicalCopyOrbitRatio, div_eq_mul_inv]
  calc
    middle * source⁻¹ * (target * middle⁻¹) =
        (middle * middle⁻¹) * (target * source⁻¹) := by ac_rfl
    _ = target * source⁻¹ := by simp [hmiddle]

/-- Product of successive orbit ratios along an arbitrary finite path. -/
def physicalCopyPathRatio : ℚ → List ℚ → ℚ
  | _, [] => 1
  | source, next :: rest =>
      physicalCopyOrbitRatio source next * physicalCopyPathRatio next rest

/-- Last orbit size reached by a finite path, with the source for an empty path. -/
def physicalCopyPathEndpoint : ℚ → List ℚ → ℚ
  | source, [] => source
  | _, next :: rest => physicalCopyPathEndpoint next rest

/-- Physical-copy orbit ratios telescope along every finite state path. -/
theorem physicalCopyOrbitRatio_path_telescope
    (source : ℚ) (targets : List ℚ) (hsource : source ≠ 0)
    (htargets : ∀ target ∈ targets, target ≠ 0) :
    physicalCopyPathRatio source targets =
      physicalCopyOrbitRatio source (physicalCopyPathEndpoint source targets) := by
  induction targets generalizing source with
  | nil =>
      simp [physicalCopyPathRatio, physicalCopyPathEndpoint,
        physicalCopyOrbitRatio, hsource]
  | cons middle rest ih =>
      have hmiddle : middle ≠ 0 := htargets middle (by simp)
      have hrest : ∀ target ∈ rest, target ≠ 0 := by
        intro target htarget
        exact htargets target (by simp [htarget])
      rw [physicalCopyPathRatio, physicalCopyPathEndpoint]
      rw [ih middle hmiddle hrest]
      exact physicalCopyOrbitRatio_telescope source middle
        (physicalCopyPathEndpoint middle rest) hsource hmiddle

/-- The edge map supplied by source and target vertex potentials. -/
def vertexEdge {Vs Vt C : Type*}
    [AddCommGroup Vs] [Module ℚ Vs]
    [AddCommGroup Vt] [Module ℚ Vt]
    [AddCommGroup C] [Module ℚ C]
    (Qs : Vs ≃ₗ[ℚ] C) (Qt : Vt ≃ₗ[ℚ] C) : Vs →ₗ[ℚ] Vt :=
  Qt.symm.toLinearMap.comp Qs.toLinearMap

/-- Transport one canonical cubic operator to a vertex. -/
def transportedCubic {V C : Type*}
    [AddCommGroup V] [Module ℚ V]
    [AddCommGroup C] [Module ℚ C]
    (Q : V ≃ₗ[ℚ] C) (K : C →ₗ[ℚ] C) : V →ₗ[ℚ] V :=
  Q.symm.toLinearMap.comp (K.comp Q.toLinearMap)

/-- Vertex-potential conjugation gives cubic naturality on the whole source. -/
theorem vertexPotential_cubic_naturality {Vs Vt C : Type*}
    [AddCommGroup Vs] [Module ℚ Vs]
    [AddCommGroup Vt] [Module ℚ Vt]
    [AddCommGroup C] [Module ℚ C]
    (Qs : Vs ≃ₗ[ℚ] C) (Qt : Vt ≃ₗ[ℚ] C) (K : C →ₗ[ℚ] C) :
    (transportedCubic Qt K).comp (vertexEdge Qs Qt) =
      (vertexEdge Qs Qt).comp (transportedCubic Qs K) := by
  ext x
  simp [transportedCubic, vertexEdge]

/-- The product of vertex-coboundary edges around a triangle is the identity. -/
theorem vertexPotential_loop_flat {V0 V1 V2 C : Type*}
    [AddCommGroup V0] [Module ℚ V0]
    [AddCommGroup V1] [Module ℚ V1]
    [AddCommGroup V2] [Module ℚ V2]
    [AddCommGroup C] [Module ℚ C]
    (Q0 : V0 ≃ₗ[ℚ] C) (Q1 : V1 ≃ₗ[ℚ] C) (Q2 : V2 ≃ₗ[ℚ] C) :
    (vertexEdge Q2 Q0).comp
        ((vertexEdge Q1 Q2).comp (vertexEdge Q0 Q1)) = LinearMap.id := by
  ext x
  simp [vertexEdge]

/-- A concrete edge-local twist used only as a negative algebraic control. -/
def edgeLocalTwist : ℚ →ₗ[ℚ] ℚ := -LinearMap.id

theorem edgeLocalTwist_ne_id : edgeLocalTwist ≠ LinearMap.id := by
  intro h
  have h1 := congrArg (fun f : ℚ →ₗ[ℚ] ℚ => f 1) h
  have hne : (-1 : ℚ) ≠ 1 := by decide
  apply hne
  simpa [edgeLocalTwist] using h1

/--
Two identity edges and one local twist cannot arise from a common family of
vertex potentials.  This distinguishes an arbitrary edge decoration from a
globally flat vertex coboundary; it is not an actual geometric braid claim.
-/
theorem edgeLocalTwist_not_vertexCoboundary :
    ¬ ∃ Q0 Q1 Q2 : ℚ ≃ₗ[ℚ] ℚ,
      vertexEdge Q0 Q1 = LinearMap.id ∧
      vertexEdge Q1 Q2 = LinearMap.id ∧
      vertexEdge Q2 Q0 = edgeLocalTwist := by
  rintro ⟨Q0, Q1, Q2, h01, h12, h20⟩
  have hloop := vertexPotential_loop_flat Q0 Q1 Q2
  rw [h01, h12, h20] at hloop
  apply edgeLocalTwist_ne_id
  simpa using hloop

end Smooth4PC
