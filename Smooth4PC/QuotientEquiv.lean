import Mathlib.LinearAlgebra.Quotient.Basic

namespace Smooth4PC

noncomputable section

variable {A B : Type*}
  [AddCommGroup A] [Module ℚ A]
  [AddCommGroup B] [Module ℚ B]

/-- A pair of inverse maps modulo specified relation submodules induces a
linear equivalence of the two quotients. -/
def quotientLinearEquiv
    (R : Submodule ℚ A) (S : Submodule ℚ B)
    (f : A →ₗ[ℚ] B) (g : B →ₗ[ℚ] A)
    (hf : R ≤ S.comap f) (hg : S ≤ R.comap g)
    (hgf : ∀ a : A, g (f a) - a ∈ R)
    (hfg : ∀ b : B, f (g b) - b ∈ S) :
    (A ⧸ R) ≃ₗ[ℚ] (B ⧸ S) := by
  let forward : (A ⧸ R) →ₗ[ℚ] (B ⧸ S) := R.mapQ S f hf
  let backward : (B ⧸ S) →ₗ[ℚ] (A ⧸ R) := S.mapQ R g hg
  apply LinearEquiv.ofLinear forward backward
  · apply LinearMap.ext
    rintro ⟨b⟩
    change (Submodule.Quotient.mk (f (g b)) : B ⧸ S) =
      Submodule.Quotient.mk b
    exact (Submodule.Quotient.eq S).2 (hfg b)
  · apply LinearMap.ext
    rintro ⟨a⟩
    change (Submodule.Quotient.mk (g (f a)) : A ⧸ R) =
      Submodule.Quotient.mk a
    exact (Submodule.Quotient.eq R).2 (hgf a)

@[simp] theorem quotientLinearEquiv_apply_mk
    (R : Submodule ℚ A) (S : Submodule ℚ B)
    (f : A →ₗ[ℚ] B) (g : B →ₗ[ℚ] A)
    (hf : R ≤ S.comap f) (hg : S ≤ R.comap g)
    (hgf : ∀ a : A, g (f a) - a ∈ R)
    (hfg : ∀ b : B, f (g b) - b ∈ S) (a : A) :
    quotientLinearEquiv R S f g hf hg hgf hfg
        (Submodule.Quotient.mk a : A ⧸ R) =
      (Submodule.Quotient.mk (f a) : B ⧸ S) := by
  rfl

@[simp] theorem quotientLinearEquiv_symm_apply_mk
    (R : Submodule ℚ A) (S : Submodule ℚ B)
    (f : A →ₗ[ℚ] B) (g : B →ₗ[ℚ] A)
    (hf : R ≤ S.comap f) (hg : S ≤ R.comap g)
    (hgf : ∀ a : A, g (f a) - a ∈ R)
    (hfg : ∀ b : B, f (g b) - b ∈ S) (b : B) :
    (quotientLinearEquiv R S f g hf hg hgf hfg).symm
        (Submodule.Quotient.mk b : B ⧸ S) =
      (Submodule.Quotient.mk (g b) : A ⧸ R) := by
  rfl

end


end Smooth4PC
