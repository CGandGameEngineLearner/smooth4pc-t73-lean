import Smooth4PC.T73Finite

namespace Smooth4PC.T73

/-!
This module gives a purely combinatorial semantics for finite positive split
movies.  A node splits one new Frobenius factor into two new factors; there are
no negative nodes and no operation on the old factor.  Nothing in this file
identifies a tree or one of its maps with an actual T73 surface.
-/

/-- An ordered finite tree of positive new--new splits. -/
inductive PositiveNewNewSplitTree where
  | leaf
  | split (left right : PositiveNewNewSplitTree)
  deriving DecidableEq, Repr

namespace PositiveNewNewSplitTree

/-- Number of new material factors at the output of the split tree. -/
def leafCount : PositiveNewNewSplitTree → Nat
  | .leaf => 1
  | .split left right => left.leafCount + right.leafCount

theorem leafCount_pos (tree : PositiveNewNewSplitTree) : 0 < tree.leafCount := by
  induction tree with
  | leaf => simp [leafCount]
  | split left right hleft hright =>
      simp only [leafCount]
      omega

end PositiveNewNewSplitTree

/-- The two ordered new outputs of one positive split, including both summands
of `Delta(1)`. -/
def positiveSplitPairs : FrobeniusBasis → List (FrobeniusBasis × FrobeniusBasis)
  | .one => [(.one, .X), (.X, .one)]
  | .X => [(.X, .X)]

/-- Concatenate every left output word with every right output word. -/
def combineTensorWords (left right : List TensorWord) : List TensorWord :=
  left.flatMap fun leftWord => right.map fun rightWord => leftWord ++ rightWord

/-- All ordered output words of a positive split tree on one input label. -/
def splitTreeWords : PositiveNewNewSplitTree → FrobeniusBasis → List TensorWord
  | .leaf, basis => [[basis]]
  | .split left right, basis =>
      (positiveSplitPairs basis).flatMap fun pair =>
        combineTensorWords (splitTreeWords left pair.1) (splitTreeWords right pair.2)

theorem mem_combineTensorWords {left right : List TensorWord} {word : TensorWord}
    (hword : word ∈ combineTensorWords left right) :
    ∃ leftWord ∈ left, ∃ rightWord ∈ right, word = leftWord ++ rightWord := by
  simp only [combineTensorWords, List.mem_flatMap, List.mem_map] at hword
  rcases hword with ⟨leftWord, hleft, rightWord, hright, hword⟩
  exact ⟨leftWord, hleft, rightWord, hright, hword.symm⟩

/-- Every output summand has one tensor factor for each leaf of the tree. -/
theorem splitTreeWords_word_length (tree : PositiveNewNewSplitTree)
    (basis : FrobeniusBasis) {word : TensorWord}
    (hword : word ∈ splitTreeWords tree basis) :
    word.length = tree.leafCount := by
  induction tree generalizing basis word with
  | leaf =>
      simp [splitTreeWords] at hword
      subst word
      rfl
  | split left right hleft hright =>
      simp only [splitTreeWords, List.mem_flatMap] at hword
      rcases hword with ⟨pair, _, hpair⟩
      rcases mem_combineTensorWords hpair with
        ⟨leftWord, hleftWord, rightWord, hrightWord, rfl⟩
      rw [List.length_append, hleft pair.1 hleftWord, hright pair.2 hrightWord]
      rfl

@[simp] theorem epsilonTensor_append (left right : TensorWord) :
    epsilonTensor (left ++ right) = epsilonTensor left * epsilonTensor right := by
  simp [epsilonTensor, List.map_append, List.prod_append]

@[simp] theorem epsilonWords_append (left right : List TensorWord) :
    epsilonWords (left ++ right) = epsilonWords left + epsilonWords right := by
  simp [epsilonWords, List.map_append, List.sum_append]

theorem epsilonWords_map_append_left (leftWord : TensorWord)
    (right : List TensorWord) :
    epsilonWords (right.map fun rightWord => leftWord ++ rightWord) =
      epsilonTensor leftWord * epsilonWords right := by
  induction right with
  | nil => simp [epsilonWords]
  | cons rightWord right ih =>
      change epsilonTensor (leftWord ++ rightWord) +
          epsilonWords (right.map fun next => leftWord ++ next) =
        epsilonTensor leftWord *
          (epsilonTensor rightWord + epsilonWords right)
      rw [epsilonTensor_append, ih, mul_add]

/-- Counit evaluation factors over the two independent branches. -/
theorem epsilonWords_combineTensorWords (left right : List TensorWord) :
    epsilonWords (combineTensorWords left right) =
      epsilonWords left * epsilonWords right := by
  induction left with
  | nil => simp [combineTensorWords, epsilonWords]
  | cons leftWord left ih =>
      rw [show combineTensorWords (leftWord :: left) right =
        right.map (fun next => leftWord ++ next) ++
          combineTensorWords left right by rfl]
      rw [epsilonWords_append]
      change epsilonWords (right.map fun next => leftWord ++ next) +
          epsilonWords (combineTensorWords left right) =
        (epsilonTensor leftWord + epsilonWords left) * epsilonWords right
      rw [epsilonWords_map_append_left, ih, add_mul]

/-- Every positive new--new split tree has the same total counit as its root. -/
theorem epsilonWords_splitTreeWords (tree : PositiveNewNewSplitTree)
    (basis : FrobeniusBasis) :
    epsilonWords (splitTreeWords tree basis) = epsilon basis := by
  induction tree generalizing basis with
  | leaf => simp [splitTreeWords, epsilonWords, epsilonTensor]
  | split left right hleft hright =>
      cases basis <;>
        simp [splitTreeWords, positiveSplitPairs, epsilonWords_combineTensorWords,
          hleft, hright, epsilon]

theorem epsilonWords_splitTreeWords_one_eq_zero
    (tree : PositiveNewNewSplitTree) :
    epsilonWords (splitTreeWords tree .one) = 0 := by
  simpa [epsilon] using epsilonWords_splitTreeWords tree .one

theorem epsilonWords_splitTreeWords_X_eq_one
    (tree : PositiveNewNewSplitTree) :
    epsilonWords (splitTreeWords tree .X) = 1 := by
  simpa [epsilon] using epsilonWords_splitTreeWords tree .X

noncomputable section

/-- Output words packaged with their tree-determined leaf count. -/
def fixedSplitTreeWords (tree : PositiveNewNewSplitTree) (basis : FrobeniusBasis) :
    List (FixedTensorWord tree.leafCount) :=
  (splitTreeWords tree basis).attach.map fun word =>
    ⟨word.1, splitTreeWords_word_length tree basis word.2⟩

theorem fixedEpsilonWords_fixedSplitTreeWords
    (tree : PositiveNewNewSplitTree) (basis : FrobeniusBasis) :
    fixedEpsilonWords (fixedSplitTreeWords tree basis) =
      epsilonWords (splitTreeWords tree basis) := by
  simp [fixedEpsilonWords, fixedSplitTreeWords, epsilonWords]

/-- Whole-source insertion for a positive split tree.  Each old-factor value is
copied unchanged into every output word, so old-factor identity is built into
the map rather than postulated as a scalar check. -/
def splitTreeInsertion {C : Type*} [AddCommGroup C] [Module ℚ C]
    (tree : PositiveNewNewSplitTree) (basis : FrobeniusBasis) :
    C →ₗ[ℚ] TensorTarget C tree.leafCount := by
  classical
  exact ((fixedSplitTreeWords tree basis).map
    (fun word : FixedTensorWord tree.leafCount => Finsupp.lsingle word)).sum

theorem targetRow_comp_splitTreeInsertion
    {C : Type*} [AddCommGroup C] [Module ℚ C]
    (tree : PositiveNewNewSplitTree) (row : C →ₗ[ℚ] ℚ)
    (basis : FrobeniusBasis) :
    (targetCounitRow tree.leafCount row).comp
        (splitTreeInsertion tree basis) =
      (epsilonWords (splitTreeWords tree basis)) • row := by
  rw [show splitTreeInsertion tree basis =
      ((fixedSplitTreeWords tree basis).map
        fun word : FixedTensorWord tree.leafCount => Finsupp.lsingle word).sum by rfl]
  rw [targetRow_comp_fixedWords, fixedEpsilonWords_fixedSplitTreeWords]

/-- Whole-source undotted equation for every finite positive new--new split
tree with identity on the old factor. -/
theorem splitTree_wholeSource_undotted_eq_zero
    {C : Type*} [AddCommGroup C] [Module ℚ C]
    (tree : PositiveNewNewSplitTree) (row : C →ₗ[ℚ] ℚ) :
    (targetCounitRow tree.leafCount row).comp
        (splitTreeInsertion tree .one) = 0 := by
  rw [targetRow_comp_splitTreeInsertion,
    epsilonWords_splitTreeWords_one_eq_zero]
  simp

/-- Whole-source dotted equation for every finite positive new--new split tree
with identity on the old factor. -/
theorem splitTree_wholeSource_dotted_eq_source
    {C : Type*} [AddCommGroup C] [Module ℚ C]
    (tree : PositiveNewNewSplitTree) (row : C →ₗ[ℚ] ℚ) :
    (targetCounitRow tree.leafCount row).comp
        (splitTreeInsertion tree .X) = row := by
  rw [targetRow_comp_splitTreeInsertion,
    epsilonWords_splitTreeWords_X_eq_one]
  simp

/-- Conjugate a positive split-tree insertion through independent source and
target coordinates. -/
def conjugatedSplitTreeInsertion {Vs Vt C : Type*}
    [AddCommGroup Vs] [Module ℚ Vs]
    [AddCommGroup Vt] [Module ℚ Vt]
    [AddCommGroup C] [Module ℚ C]
    (Qs : Vs ≃ₗ[ℚ] C) (tree : PositiveNewNewSplitTree)
    (Qt : Vt ≃ₗ[ℚ] TensorTarget C tree.leafCount)
    (basis : FrobeniusBasis) : Vs →ₗ[ℚ] Vt :=
  Qt.symm.toLinearMap.comp
    ((splitTreeInsertion tree basis).comp Qs.toLinearMap)

/-- Coordinate-conjugated form of the arbitrary-tree undotted equation. -/
theorem splitTree_directQ_undotted_row_eq_zero {Vs Vt C : Type*}
    [AddCommGroup Vs] [Module ℚ Vs]
    [AddCommGroup Vt] [Module ℚ Vt]
    [AddCommGroup C] [Module ℚ C]
    (Qs : Vs ≃ₗ[ℚ] C) (tree : PositiveNewNewSplitTree)
    (Qt : Vt ≃ₗ[ℚ] TensorTarget C tree.leafCount)
    (row : C →ₗ[ℚ] ℚ) :
    (actualTargetRow tree.leafCount Qt row).comp
        (conjugatedSplitTreeInsertion Qs tree Qt .one) = 0 := by
  ext value
  have hvalue := LinearMap.congr_fun
    (splitTree_wholeSource_undotted_eq_zero tree row) (Qs value)
  simpa [actualTargetRow, conjugatedSplitTreeInsertion] using hvalue

/-- Coordinate-conjugated form of the arbitrary-tree dotted equation. -/
theorem splitTree_directQ_dotted_row_eq_source {Vs Vt C : Type*}
    [AddCommGroup Vs] [Module ℚ Vs]
    [AddCommGroup Vt] [Module ℚ Vt]
    [AddCommGroup C] [Module ℚ C]
    (Qs : Vs ≃ₗ[ℚ] C) (tree : PositiveNewNewSplitTree)
    (Qt : Vt ≃ₗ[ℚ] TensorTarget C tree.leafCount)
    (row : C →ₗ[ℚ] ℚ) :
    (actualTargetRow tree.leafCount Qt row).comp
        (conjugatedSplitTreeInsertion Qs tree Qt .X) =
      actualSourceRow Qs row := by
  ext value
  have hvalue := LinearMap.congr_fun
    (splitTree_wholeSource_dotted_eq_source tree row) (Qs value)
  simpa [actualTargetRow, actualSourceRow, conjugatedSplitTreeInsertion] using hvalue

end

end Smooth4PC.T73
