import Smooth4PC.T73Finite

namespace Smooth4PC.T73

/-- The integral rank-three lattice used by the Cappell--Shaneson monodromy. -/
abbrev CSLattice := Fin 3 → Int

/-- The explicit action of `A-I` on the lattice, in the frozen row convention. -/
def aMinusIMap : CSLattice →ₗ[Int] CSLattice where
  toFun v i :=
    match i.1 with
    | 0 => -v 0 + 269 * v 1 + 1240 * v 2
    | 1 => 40 * v 1 + 189 * v 2
    | 2 => v 0 + 31 * v 2
    | _ => 0
  map_add' left right := by
    ext i
    fin_cases i <;> simp <;> ring
  map_smul' scalar v := by
    ext i
    fin_cases i <;> simp <;> ring

/-- An integer inverse of `A-I`, computed from its adjugate. -/
def aMinusIInverse : CSLattice →ₗ[Int] CSLattice where
  toFun v i :=
    match i.1 with
    | 0 => 1240 * v 0 - 8339 * v 1 + 1241 * v 2
    | 1 => 189 * v 0 - 1271 * v 1 + 189 * v 2
    | 2 => -40 * v 0 + 269 * v 1 - 40 * v 2
    | _ => 0
  map_add' left right := by
    ext i
    fin_cases i <;> simp <;> ring
  map_smul' scalar v := by
    ext i
    fin_cases i <;> simp <;> ring

theorem aMinusIInverse_left (v : CSLattice) :
    aMinusIInverse (aMinusIMap v) = v := by
  ext i
  fin_cases i <;> simp [aMinusIInverse, aMinusIMap] <;> ring

theorem aMinusIInverse_right (v : CSLattice) :
    aMinusIMap (aMinusIInverse v) = v := by
  ext i
  fin_cases i <;> simp [aMinusIInverse, aMinusIMap] <;> ring

/-- `A-I` is an integral linear equivalence, not merely invertible over `ℚ`. -/
def aMinusIEquiv : CSLattice ≃ₗ[Int] CSLattice where
  toLinearMap := aMinusIMap
  invFun := aMinusIInverse
  left_inv := aMinusIInverse_left
  right_inv := aMinusIInverse_right

theorem aMinusIMap_surjective : Function.Surjective aMinusIMap :=
  aMinusIEquiv.surjective

theorem aMinusIMap_range_eq_top : LinearMap.range aMinusIMap = ⊤ :=
  LinearMap.range_eq_top.mpr aMinusIMap_surjective

/-- The integral coinvariant lattice `coker(A-I)` is zero. -/
theorem aMinusICokernel_eq_zero
    (x : CSLattice ⧸ LinearMap.range aMinusIMap) : x = 0 := by
  refine Submodule.Quotient.induction_on _ x ?_
  intro v
  rw [Submodule.Quotient.mk_eq_zero]
  rw [aMinusIMap_range_eq_top]
  trivial

/-- The action of `(A⁻¹)ᵀ-I` on `H₂(T³;ℤ)` in the dual basis. -/
def hTwoMinusIMap : CSLattice →ₗ[Int] CSLattice where
  toFun v i :=
    match i.1 with
    | 0 => 1311 * v 0 + 189 * v 1 - 41 * v 2
    | 1 => -8608 * v 0 - 1241 * v 1 + 269 * v 2
    | 2 => v 0 - v 2
    | _ => 0
  map_add' left right := by
    ext i
    fin_cases i <;> simp <;> ring
  map_smul' scalar v := by
    ext i
    fin_cases i <;> simp <;> ring

/-- An integral inverse of `(A⁻¹)ᵀ-I`; its determinant is `-1`. -/
def hTwoMinusIInverse : CSLattice →ₗ[Int] CSLattice where
  toFun v i :=
    match i.1 with
    | 0 => -1241 * v 0 - 189 * v 1 + 40 * v 2
    | 1 => 8339 * v 0 + 1270 * v 1 - 269 * v 2
    | 2 => -1241 * v 0 - 189 * v 1 + 39 * v 2
    | _ => 0
  map_add' left right := by
    ext i
    fin_cases i <;> simp <;> ring
  map_smul' scalar v := by
    ext i
    fin_cases i <;> simp <;> ring

theorem hTwoMinusIInverse_left (v : CSLattice) :
    hTwoMinusIInverse (hTwoMinusIMap v) = v := by
  ext i
  fin_cases i <;> simp [hTwoMinusIInverse, hTwoMinusIMap] <;> ring

theorem hTwoMinusIInverse_right (v : CSLattice) :
    hTwoMinusIMap (hTwoMinusIInverse v) = v := by
  ext i
  fin_cases i <;> simp [hTwoMinusIInverse, hTwoMinusIMap] <;> ring

def hTwoMinusIEquiv : CSLattice ≃ₗ[Int] CSLattice where
  toLinearMap := hTwoMinusIMap
  invFun := hTwoMinusIInverse
  left_inv := hTwoMinusIInverse_left
  right_inv := hTwoMinusIInverse_right

theorem hTwoMinusIMap_surjective : Function.Surjective hTwoMinusIMap :=
  hTwoMinusIEquiv.surjective

theorem hTwoMinusIMap_range_eq_top : LinearMap.range hTwoMinusIMap = ⊤ :=
  LinearMap.range_eq_top.mpr hTwoMinusIMap_surjective

theorem hTwoMinusICokernel_eq_zero
    (x : CSLattice ⧸ LinearMap.range hTwoMinusIMap) : x = 0 := by
  refine Submodule.Quotient.induction_on _ x ?_
  intro v
  rw [Submodule.Quotient.mk_eq_zero]
  rw [hTwoMinusIMap_range_eq_top]
  trivial

theorem t73CSLinearObstructionsVanish :
    Function.Bijective aMinusIMap ∧ Function.Bijective hTwoMinusIMap :=
  ⟨aMinusIEquiv.bijective, hTwoMinusIEquiv.bijective⟩

end Smooth4PC.T73
