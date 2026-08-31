import Mathlib.Algebra.Module.LinearMap.Basic
import Mathlib.Algebra.Module.Equiv.Basic
import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Data.Rat.BigOperators
import Mathlib.LinearAlgebra.Finsupp.LSum

namespace Smooth4PC

/-!
This module proves only the finite augmentation and conjugation algebra used by
the candidate argument.  It does not assert the actual T73 geometric premises
that would identify concrete sphere or psi movies with these abstract maps.
-/

/-- The basis `(1, X)` of the rank-two Frobenius module. -/
inductive FrobeniusBasis where
  | one
  | X
  deriving DecidableEq, Repr

/-- An ordered tensor word in the basis `(1, X)`. -/
abbrev TensorWord := List FrobeniusBasis

/-- The Frobenius counit on basis elements. -/
def epsilon : FrobeniusBasis → ℚ
  | .one => 0
  | .X => 1

/-- Apply the counit to every tensor factor and multiply the results. -/
def epsilonTensor (word : TensorWord) : ℚ :=
  (word.map epsilon).prod

/-- Extend tensor-word counit evaluation linearly over a finite support list. -/
def epsilonWords (words : List TensorWord) : ℚ :=
  (words.map epsilonTensor).sum

/-- The genuine rank-two coproduct on basis elements. -/
def delta : FrobeniusBasis → List TensorWord
  | .one => [[.one, .X], [.X, .one]]
  | .X => [[.X, .X]]

/-- Split the first tensor factor by `delta`; the empty tensor is left fixed. -/
def splitHead : TensorWord → List TensorWord
  | [] => [[]]
  | basis :: tail => (delta basis).map (fun head => head ++ tail)

/-- Recursively apply `splitHead` to every summand. -/
def iterateSplit : Nat → List TensorWord → List TensorWord
  | 0, words => words
  | steps + 1, words => iterateSplit steps (words.flatMap splitHead)

/-- The `(b-1)`-fold recursive coproduct, with `b=0` deliberately unsupported. -/
def iteratedDelta : Nat → FrobeniusBasis → List TensorWord
  | 0, _ => []
  | b + 1, basis => iterateSplit b [[basis]]

/-- The first recursive split is definitionally the declared binary coproduct. -/
@[simp] theorem iteratedDelta_two_eq_delta (basis : FrobeniusBasis) :
    iteratedDelta 2 basis = delta basis := by
  cases basis <;> rfl

/-- Splitting a nonempty word increases its tensor length by exactly one. -/
theorem splitHead_word_length {word output : TensorWord} (hword : word ≠ [])
    (houtput : output ∈ splitHead word) : output.length = word.length + 1 := by
  cases word with
  | nil => exact (hword rfl).elim
  | cons head tail =>
      cases head <;> simp [splitHead, delta] at houtput <;>
        rcases houtput with rfl | rfl <;> simp

/-- Repeated splitting raises a common positive word length by the step count. -/
theorem iterateSplit_word_length (steps base : Nat) (words : List TensorWord)
    (hbase : ∀ word ∈ words, word.length = base) (hpositive : 0 < base) :
    ∀ word ∈ iterateSplit steps words, word.length = base + steps := by
  induction steps generalizing base words with
  | zero => simpa [iterateSplit] using hbase
  | succ steps ih =>
      intro word hword
      have hnext :
          ∀ next ∈ words.flatMap splitHead, next.length = base + 1 := by
        intro next hnextMem
        simp only [List.mem_flatMap] at hnextMem
        rcases hnextMem with ⟨prior, hprior, hnextPrior⟩
        have hpriorLength := hbase prior hprior
        have hpriorNe : prior ≠ [] := by
          intro hEmpty
          subst prior
          simp at hpriorLength
          omega
        rw [splitHead_word_length hpriorNe hnextPrior, hpriorLength]
      have hrec := ih (base + 1) (words.flatMap splitHead) hnext (by omega)
        word (by simpa [iterateSplit] using hword)
      omega

/-- Every recursive coproduct summand has exactly the requested leaf count. -/
theorem iteratedDelta_word_length (b : Nat) (basis : FrobeniusBasis)
    {word : TensorWord} (hword : word ∈ iteratedDelta b basis) :
    word.length = b := by
  cases b with
  | zero => simp [iteratedDelta] at hword
  | succ steps =>
      have hlength := iterateSplit_word_length steps 1 [[basis]] (by simp) (by omega)
        word (by simpa [iteratedDelta] using hword)
      omega

@[simp] theorem epsilonWords_splitHead (word : TensorWord) :
    epsilonWords (splitHead word) = epsilonTensor word := by
  cases word with
  | nil => simp [epsilonWords, splitHead, epsilonTensor]
  | cons basis tail =>
      cases basis <;> simp [epsilonWords, splitHead, delta, epsilonTensor, epsilon]

@[simp] theorem epsilonWords_flatMap_splitHead (words : List TensorWord) :
    epsilonWords (words.flatMap splitHead) = epsilonWords words := by
  induction words with
  | nil => simp [epsilonWords]
  | cons word words ih =>
      rw [epsilonWords] at ih ⊢
      rw [List.flatMap_cons, List.map_append, List.sum_append]
      rw [show (List.map epsilonTensor (splitHead word)).sum = epsilonTensor word by
        simpa [epsilonWords] using epsilonWords_splitHead word]
      rw [ih]
      simp [epsilonWords]

@[simp] theorem epsilonWords_iterateSplit (steps : Nat) (words : List TensorWord) :
    epsilonWords (iterateSplit steps words) = epsilonWords words := by
  induction steps generalizing words with
  | zero => rfl
  | succ steps ih => simp [iterateSplit, ih]

/-- `epsilon^b (Delta^(b-1)(1)) = 0` for every positive `b`. -/
theorem epsilon_iteratedDelta_one_eq_zero (b : Nat) (hb : 0 < b) :
    epsilonWords (iteratedDelta b .one) = 0 := by
  cases b with
  | zero => omega
  | succ steps =>
      rw [iteratedDelta, epsilonWords_iterateSplit]
      simp [epsilonWords, epsilonTensor, epsilon]

/-- `epsilon^b (Delta^(b-1)(X)) = 1` for every positive `b`. -/
theorem epsilon_iteratedDelta_X_eq_one (b : Nat) (hb : 0 < b) :
    epsilonWords (iteratedDelta b .X) = 1 := by
  cases b with
  | zero => omega
  | succ steps =>
      rw [iteratedDelta, epsilonWords_iterateSplit]
      simp [epsilonWords, epsilonTensor, epsilon]

/-- A tensor word carrying a kernel-checked proof of its exact leaf count. -/
abbrev FixedTensorWord (b : Nat) := {word : TensorWord // word.length = b}

/-- The pre-counit direct sum over tensor words of one fixed leaf count. -/
abbrev TensorTarget (C : Type*) [Zero C] (b : Nat) := FixedTensorWord b →₀ C

/-- Package every recursive coproduct summand with its exact-length proof. -/
def fixedIteratedDelta (b : Nat) (basis : FrobeniusBasis) :
    List (FixedTensorWord b) :=
  (iteratedDelta b basis).attach.map fun word =>
    ⟨word.1, iteratedDelta_word_length b basis word.2⟩

/-- Counit evaluation of a finite list of fixed-length tensor words. -/
def fixedEpsilonWords {b : Nat} (words : List (FixedTensorWord b)) : ℚ :=
  (words.map fun word => epsilonTensor word.1).sum

theorem fixedEpsilonWords_fixedIteratedDelta (b : Nat) (basis : FrobeniusBasis) :
    fixedEpsilonWords (fixedIteratedDelta b basis) =
      epsilonWords (iteratedDelta b basis) := by
  simp [fixedEpsilonWords, fixedIteratedDelta, epsilonWords]

noncomputable section

/-
The raw insertion map.  It inserts one copy of `value` at every fixed-length
tensor word in the recursive coproduct support; no counit is evaluated here.
-/
def canonicalInsertion {C : Type*} [AddCommGroup C] [Module ℚ C]
    (b : Nat) (basis : FrobeniusBasis) : C →ₗ[ℚ] TensorTarget C b := by
  classical
  exact ((fixedIteratedDelta b basis).map
    (fun word : FixedTensorWord b => Finsupp.lsingle word)).sum

/-- The target augmentation row, evaluated only after the raw insertion. -/
def targetCounitRow {C : Type*} [AddCommGroup C] [Module ℚ C]
    (b : Nat) (row : C →ₗ[ℚ] ℚ) : TensorTarget C b →ₗ[ℚ] ℚ := by
  classical
  exact (Finsupp.lsum ℚ) (fun word => (epsilonTensor word.1) • row)

theorem targetRow_comp_fixedWords {C : Type*} [AddCommGroup C] [Module ℚ C]
    (row : C →ₗ[ℚ] ℚ) (b : Nat) (words : List (FixedTensorWord b)) :
    (targetCounitRow b row).comp
        ((words.map fun word => Finsupp.lsingle word).sum) =
      (fixedEpsilonWords words) • row := by
  classical
  induction words with
  | nil =>
      ext value
      simp [targetCounitRow, fixedEpsilonWords]
  | cons word words ih =>
      ext value
      have ihValue := LinearMap.congr_fun ih value
      change targetCounitRow b row
          (Finsupp.single word value +
            ((words.map fun next => Finsupp.lsingle next).sum value)) =
        ((fixedEpsilonWords (word :: words)) • row) value
      rw [(targetCounitRow b row).map_add]
      have hsingle :
          targetCounitRow b row (Finsupp.single word value) =
            epsilonTensor word.1 * row value := by
        simp [targetCounitRow]
      rw [hsingle]
      change _ + (targetCounitRow b row).comp
          ((words.map fun next => Finsupp.lsingle next).sum) value = _
      rw [ihValue]
      simp [fixedEpsilonWords, add_mul]

/-- Evaluation of a raw insertion is the recursive tensor-word counit sum. -/
theorem targetRow_comp_insertion {C : Type*} [AddCommGroup C] [Module ℚ C]
    (row : C →ₗ[ℚ] ℚ) (b : Nat) (basis : FrobeniusBasis) :
    (targetCounitRow b row).comp (canonicalInsertion b basis) =
      (epsilonWords (iteratedDelta b basis)) • row := by
  rw [show canonicalInsertion b basis =
      ((fixedIteratedDelta b basis).map
        fun word : FixedTensorWord b => Finsupp.lsingle word).sum by rfl]
  rw [targetRow_comp_fixedWords, fixedEpsilonWords_fixedIteratedDelta]

/-- The raw undotted insertion is killed by the target row on the whole source. -/
theorem targetRow_undotted_eq_zero {C : Type*} [AddCommGroup C] [Module ℚ C]
    (row : C →ₗ[ℚ] ℚ) (b : Nat) (hb : 0 < b) :
    (targetCounitRow b row).comp (canonicalInsertion b .one) = 0 := by
  rw [targetRow_comp_insertion, epsilon_iteratedDelta_one_eq_zero b hb]
  simp

/-- The raw dotted insertion pulls the target row back to the source row. -/
theorem targetRow_dotted_eq_source {C : Type*} [AddCommGroup C] [Module ℚ C]
    (row : C →ₗ[ℚ] ℚ) (b : Nat) (hb : 0 < b) :
    (targetCounitRow b row).comp (canonicalInsertion b .X) = row := by
  rw [targetRow_comp_insertion, epsilon_iteratedDelta_X_eq_one b hb]
  simp

/-- Pull the canonical source row back through explicit source coordinates. -/
def actualSourceRow {Vs C : Type*}
    [AddCommGroup Vs] [Module ℚ Vs] [AddCommGroup C] [Module ℚ C]
    (Qs : Vs ≃ₗ[ℚ] C) (row : C →ₗ[ℚ] ℚ) : Vs →ₗ[ℚ] ℚ :=
  row.comp Qs.toLinearMap

/-- Pull the fixed-leaf pre-counit row back through explicit target coordinates. -/
def actualTargetRow {Vt C : Type*}
    [AddCommGroup Vt] [Module ℚ Vt] [AddCommGroup C] [Module ℚ C]
    (b : Nat) (Qt : Vt ≃ₗ[ℚ] TensorTarget C b)
    (row : C →ₗ[ℚ] ℚ) : Vt →ₗ[ℚ] ℚ :=
  (targetCounitRow b row).comp Qt.toLinearMap

/-- Conjugate the raw fixed-leaf insertion through source and target coordinates. -/
def conjugatedInsertion {Vs Vt C : Type*}
    [AddCommGroup Vs] [Module ℚ Vs]
    [AddCommGroup Vt] [Module ℚ Vt]
    [AddCommGroup C] [Module ℚ C]
    (Qs : Vs ≃ₗ[ℚ] C) (b : Nat) (Qt : Vt ≃ₗ[ℚ] TensorTarget C b)
    (basis : FrobeniusBasis) : Vs →ₗ[ℚ] Vt :=
  Qt.symm.toLinearMap.comp
    ((canonicalInsertion b basis).comp Qs.toLinearMap)

/-- The conjugated undotted cocone equation holds on the entire actual source. -/
theorem directQ_undotted_row_eq_zero {Vs Vt C : Type*}
    [AddCommGroup Vs] [Module ℚ Vs]
    [AddCommGroup Vt] [Module ℚ Vt]
    [AddCommGroup C] [Module ℚ C]
    (Qs : Vs ≃ₗ[ℚ] C) (b : Nat) (Qt : Vt ≃ₗ[ℚ] TensorTarget C b)
    (row : C →ₗ[ℚ] ℚ) (hb : 0 < b) :
    (actualTargetRow b Qt row).comp
        (conjugatedInsertion Qs b Qt .one) = 0 := by
  ext value
  have hvalue := LinearMap.congr_fun (targetRow_undotted_eq_zero row b hb) (Qs value)
  simpa [actualTargetRow, conjugatedInsertion] using hvalue

/-- The conjugated dotted cocone equation holds on the entire actual source. -/
theorem directQ_dotted_row_eq_source {Vs Vt C : Type*}
    [AddCommGroup Vs] [Module ℚ Vs]
    [AddCommGroup Vt] [Module ℚ Vt]
    [AddCommGroup C] [Module ℚ C]
    (Qs : Vs ≃ₗ[ℚ] C) (b : Nat) (Qt : Vt ≃ₗ[ℚ] TensorTarget C b)
    (row : C →ₗ[ℚ] ℚ) (hb : 0 < b) :
    (actualTargetRow b Qt row).comp
        (conjugatedInsertion Qs b Qt .X) = actualSourceRow Qs row := by
  ext value
  have hvalue := LinearMap.congr_fun (targetRow_dotted_eq_source row b hb) (Qs value)
  simpa [actualTargetRow, actualSourceRow, conjugatedInsertion] using hvalue

/-! ### Physical-copy orbit normalization -/

/-- Product of ownerwise binomial orbit sizes from copy counts and occupancies. -/
def orbitSize : List Nat → List Nat → Nat
  | [], [] => 1
  | copies :: copyTail, occupied :: occupiedTail =>
      Nat.choose copies occupied * orbitSize copyTail occupiedTail
  | _, _ => 0

/-- An orbit is present exactly when its binomial-product size is nonzero. -/
def orbitPresent (copyCounts occupancy : List Nat) : Prop :=
  orbitSize copyCounts occupancy ≠ 0

/-- Ratio of target and source orbit sizes, with absent orbits mapped to zero. -/
def physicalCopyOrbitRatio
    (sourceCopies targetCopies occupancy : List Nat) : ℚ :=
  by
    classical
    exact
      if orbitPresent sourceCopies occupancy ∧ orbitPresent targetCopies occupancy then
        (orbitSize targetCopies occupancy : ℚ) /
          (orbitSize sourceCopies occupancy : ℚ)
      else
        0

/-- Any absent source or target orbit has zero normalization by definition. -/
theorem physicalCopyOrbitRatio_absent
    (sourceCopies targetCopies occupancy : List Nat)
    (hAbsent : ¬ orbitPresent sourceCopies occupancy ∨
      ¬ orbitPresent targetCopies occupancy) :
    physicalCopyOrbitRatio sourceCopies targetCopies occupancy = 0 := by
  rcases hAbsent with hSource | hTarget
  · simp [physicalCopyOrbitRatio, hSource]
  · simp [physicalCopyOrbitRatio, hTarget]

/-- Present physical-copy orbit ratios telescope across two consecutive edges. -/
theorem physicalCopyOrbitRatio_telescope
    (sourceCopies middleCopies targetCopies occupancy : List Nat)
    (hSource : orbitPresent sourceCopies occupancy)
    (hMiddle : orbitPresent middleCopies occupancy)
    (hTarget : orbitPresent targetCopies occupancy) :
    physicalCopyOrbitRatio sourceCopies middleCopies occupancy *
        physicalCopyOrbitRatio middleCopies targetCopies occupancy =
      physicalCopyOrbitRatio sourceCopies targetCopies occupancy := by
  have hMiddleRat : (orbitSize middleCopies occupancy : ℚ) ≠ 0 :=
    Nat.cast_ne_zero.mpr hMiddle
  simp only [physicalCopyOrbitRatio, hSource, hMiddle, hTarget, and_self, if_true,
    div_eq_mul_inv]
  calc
    (orbitSize middleCopies occupancy : ℚ) *
          (orbitSize sourceCopies occupancy : ℚ)⁻¹ *
        ((orbitSize targetCopies occupancy : ℚ) *
          (orbitSize middleCopies occupancy : ℚ)⁻¹) =
      ((orbitSize middleCopies occupancy : ℚ) *
          (orbitSize middleCopies occupancy : ℚ)⁻¹) *
        ((orbitSize targetCopies occupancy : ℚ) *
          (orbitSize sourceCopies occupancy : ℚ)⁻¹) := by ac_rfl
    _ = (orbitSize targetCopies occupancy : ℚ) *
        (orbitSize sourceCopies occupancy : ℚ)⁻¹ := by simp [hMiddleRat]

/-- Product of orbit ratios along a finite sequence of physical-copy states. -/
def physicalCopyPathRatio (occupancy : List Nat) :
    List Nat → List (List Nat) → ℚ
  | _, [] => 1
  | source, next :: rest =>
      physicalCopyOrbitRatio source next occupancy *
        physicalCopyPathRatio occupancy next rest

/-- Last physical-copy state reached by a path, or its source for an empty path. -/
def physicalCopyPathEndpoint : List Nat → List (List Nat) → List Nat
  | source, [] => source
  | _, next :: rest => physicalCopyPathEndpoint next rest

/-- The endpoint of a nonempty state path is one of its listed target states. -/
theorem physicalCopyPathEndpoint_mem :
    ∀ (source : List Nat) (targets : List (List Nat)),
      targets ≠ [] → physicalCopyPathEndpoint source targets ∈ targets
  | _, [], hTargets => (hTargets rfl).elim
  | _, [target], _ => by simp [physicalCopyPathEndpoint]
  | _, target :: next :: rest, _ => by
      apply List.mem_cons_of_mem
      exact physicalCopyPathEndpoint_mem target (next :: rest) (by simp)

/-- Present states have a present endpoint along any finite state path. -/
theorem physicalCopyPathEndpoint_present
    (occupancy source : List Nat) (targets : List (List Nat))
    (hSource : orbitPresent source occupancy)
    (hTargets : ∀ target ∈ targets, orbitPresent target occupancy) :
    orbitPresent (physicalCopyPathEndpoint source targets) occupancy := by
  cases targets with
  | nil => simpa [physicalCopyPathEndpoint] using hSource
  | cons target rest =>
      apply hTargets
      exact physicalCopyPathEndpoint_mem source (target :: rest) (by simp)

/-- Present orbit ratios telescope along every finite physical-copy state path. -/
theorem physicalCopyOrbitRatio_path_telescope
    (occupancy source : List Nat) (targets : List (List Nat))
    (hSource : orbitPresent source occupancy)
    (hTargets : ∀ target ∈ targets, orbitPresent target occupancy) :
    physicalCopyPathRatio occupancy source targets =
      physicalCopyOrbitRatio source
        (physicalCopyPathEndpoint source targets) occupancy := by
  induction targets generalizing source with
  | nil =>
      have hSourceRat : (orbitSize source occupancy : ℚ) ≠ 0 :=
        Nat.cast_ne_zero.mpr hSource
      simp [physicalCopyPathRatio, physicalCopyPathEndpoint,
        physicalCopyOrbitRatio, hSource, hSourceRat]
  | cons middle rest ih =>
      have hMiddle : orbitPresent middle occupancy := hTargets middle (by simp)
      have hRest : ∀ target ∈ rest, orbitPresent target occupancy := by
        intro target hTarget
        exact hTargets target (by simp [hTarget])
      rw [physicalCopyPathRatio, physicalCopyPathEndpoint]
      rw [ih middle hMiddle hRest]
      exact physicalCopyOrbitRatio_telescope source middle
        (physicalCopyPathEndpoint middle rest) occupancy hSource hMiddle
        (physicalCopyPathEndpoint_present occupancy middle rest hMiddle hRest)

/-! ### Cubic conjugation and flatness -/

/-- Transport an endomorphism from canonical coordinates to an actual vertex. -/
def transportedCubic {V C : Type*}
    [AddCommGroup V] [Module ℚ V]
    [AddCommGroup C] [Module ℚ C]
    (Q : V ≃ₗ[ℚ] C) (K : C →ₗ[ℚ] C) : V →ₗ[ℚ] V :=
  Q.symm.toLinearMap.comp (K.comp Q.toLinearMap)

/-- Conjugate a typed canonical edge through independent vertex coordinates. -/
def conjugatedEdge {Vs Vt Cs Ct : Type*}
    [AddCommGroup Vs] [Module ℚ Vs]
    [AddCommGroup Vt] [Module ℚ Vt]
    [AddCommGroup Cs] [Module ℚ Cs]
    [AddCommGroup Ct] [Module ℚ Ct]
    (Qs : Vs ≃ₗ[ℚ] Cs) (Qt : Vt ≃ₗ[ℚ] Ct)
    (D : Cs →ₗ[ℚ] Ct) : Vs →ₗ[ℚ] Vt :=
  Qt.symm.toLinearMap.comp (D.comp Qs.toLinearMap)

/-- Canonical cubic naturality transports through the two vertex equivalences. -/
theorem vertexPotential_cubic_naturality {Vs Vt Cs Ct : Type*}
    [AddCommGroup Vs] [Module ℚ Vs]
    [AddCommGroup Vt] [Module ℚ Vt]
    [AddCommGroup Cs] [Module ℚ Cs]
    [AddCommGroup Ct] [Module ℚ Ct]
    (Qs : Vs ≃ₗ[ℚ] Cs) (Qt : Vt ≃ₗ[ℚ] Ct)
    (D : Cs →ₗ[ℚ] Ct) (Ks : Cs →ₗ[ℚ] Cs) (Kt : Ct →ₗ[ℚ] Ct)
    (hK : Kt.comp D = D.comp Ks) :
    (transportedCubic Qt Kt).comp (conjugatedEdge Qs Qt D) =
      (conjugatedEdge Qs Qt D).comp (transportedCubic Qs Ks) := by
  ext value
  have hValue := LinearMap.congr_fun hK (Qs value)
  simpa [transportedCubic, conjugatedEdge] using hValue

/-- A pure coordinate coboundary edge, with no canonical edge factor. -/
def pureVertexEdge {Vs Vt C : Type*}
    [AddCommGroup Vs] [Module ℚ Vs]
    [AddCommGroup Vt] [Module ℚ Vt]
    [AddCommGroup C] [Module ℚ C]
    (Qs : Vs ≃ₗ[ℚ] C) (Qt : Vt ≃ₗ[ℚ] C) : Vs →ₗ[ℚ] Vt :=
  Qt.symm.toLinearMap.comp Qs.toLinearMap

/-- Pure vertex-coboundary edges have identity holonomy around a triangle. -/
theorem pureVertexCoboundary_triangle_flat {V0 V1 V2 C : Type*}
    [AddCommGroup V0] [Module ℚ V0]
    [AddCommGroup V1] [Module ℚ V1]
    [AddCommGroup V2] [Module ℚ V2]
    [AddCommGroup C] [Module ℚ C]
    (Q0 : V0 ≃ₗ[ℚ] C) (Q1 : V1 ≃ₗ[ℚ] C) (Q2 : V2 ≃ₗ[ℚ] C) :
    (pureVertexEdge Q2 Q0).comp
        ((pureVertexEdge Q1 Q2).comp (pureVertexEdge Q0 Q1)) = LinearMap.id := by
  ext value
  simp [pureVertexEdge]

/-- A concrete local twist used only as a negative algebraic control. -/
def edgeLocalTwist : ℚ →ₗ[ℚ] ℚ := -LinearMap.id

theorem edgeLocalTwist_ne_id : edgeLocalTwist ≠ LinearMap.id := by
  intro h
  have h1 := congrArg (fun map : ℚ →ₗ[ℚ] ℚ => map 1) h
  have hne : (-1 : ℚ) ≠ 1 := by decide
  apply hne
  simpa [edgeLocalTwist] using h1

/--
Two identity edges and one local twist cannot arise from a common family of
pure vertex potentials.  This is not an actual geometric braid claim.
-/
theorem edgeLocalTwist_not_vertexCoboundary :
    ¬ ∃ Q0 Q1 Q2 : ℚ ≃ₗ[ℚ] ℚ,
      pureVertexEdge Q0 Q1 = LinearMap.id ∧
      pureVertexEdge Q1 Q2 = LinearMap.id ∧
      pureVertexEdge Q2 Q0 = edgeLocalTwist := by
  rintro ⟨Q0, Q1, Q2, h01, h12, h20⟩
  have hloop := pureVertexCoboundary_triangle_flat Q0 Q1 Q2
  rw [h01, h12, h20] at hloop
  apply edgeLocalTwist_ne_id
  simpa using hloop

end

end Smooth4PC
