from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


_WINDOWS_PINNED_LAKE = Path(
    r"C:\Users\LENOVO\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe"
)
PINNED_LAKE = (
    _WINDOWS_PINNED_LAKE
    if _WINDOWS_PINNED_LAKE.is_file()
    else Path(shutil.which("lake") or _WINDOWS_PINNED_LAKE)
)

CONSUMER = r"""
import Smooth4PC.HattoriBalancedInput

namespace HattoriBalancedInputConsumer
open Smooth4PC

universe u

example (g : BalancedHattoriGeometry.{u}) (T T' : g.Obj) :
    g.Coeff T T' ≃ₗ[ℚ]
      TensorProduct ℚ (g.Hom (g.B T) (g.B T'))
        ((Fin 227 → FrobeniusLabel) →₀ ℚ) :=
  g.H T T'

example : TensorBasis227 = (Fin 227 → FrobeniusLabel) := rfl
example : Tensor227 = (TensorBasis227 →₀ ℚ) := rfl
example : xTensor227 = Finsupp.single allX 1 := rfl

example (g : BalancedHattoriGeometry.{u}) (U : g.Obj) :
    g.H (chosenT g U) (chosenT g U) (inverseImageVT g U) =
      diagonalTarget g U :=
  inverseImageVT_binding g U

example (g : BalancedHattoriGeometry.{u}) (U : g.Obj)
    (actual : ActualDiagonalInput g U) :
    g.IsCycle (selectedInput actual) :=
  selectedInput_isCycle actual

example (g : BalancedHattoriGeometry.{u}) (U : g.Obj)
    (actual : ActualDiagonalInput g U) :
    g.H (chosenT g U) (chosenT g U) (selectedInput actual) =
      diagonalTarget g U :=
  selectedInput_binding actual

example : cupVector = basisVector 2 - basisVector 87 := rfl
example : Fin 88 → ℚ := cupVector
example : positiveSource = EndpointSource.M1_88 := positiveSource_is_M1_88

example (b : DefectBasis) : totalDefectBasis b = 1 + relativeNuBasis b := rfl
example (r : M1_88 →ₗ[ℚ] ℚ) :
    (defectHeadRow r).comp dottedMap = defectHeadRow r :=
  defectHeadRow_comp_dotted r
example (r : M1_88 →ₗ[ℚ] ℚ) :
    (defectHeadRow r).comp undottedMap = 0 :=
  defectHeadRow_comp_undotted r
example (p : PhysicalCopyPermutation) (b : DefectBasis) :
    relativeNuBasis (permuteBasis p b) = relativeNuBasis b :=
  physicalCopyPermutation_preserves_relativeNu p b

example : (183 : ℤ) + 315 - 4 = 494 := degree_ledger_eq_494
example : (-8 : ℤ) * (-328) = 2624 := cubic_arithmetic_eq_2624
example : (2624 : ℤ) ≠ 0 := cubic2624_ne_zero
example : cubicValue = (2624 : ℤ) := cubicValue_eq_2624

end HattoriBalancedInputConsumer
"""

AXIOM_THEOREMS = (
    "Smooth4PC.B_chosenT_eq_U",
    "Smooth4PC.inverseImageVT_binding",
    "Smooth4PC.selectedInput_isCycle",
    "Smooth4PC.selectedInput_binding",
    "Smooth4PC.basisPush_single",
    "Smooth4PC.defectHeadRow_comp_dotted",
    "Smooth4PC.defectHeadRow_comp_undotted",
    "Smooth4PC.physicalCopyPermutation_preserves_relativeNu",
    "Smooth4PC.degree_ledger_eq_494",
    "Smooth4PC.cubic_arithmetic_eq_2624",
    "Smooth4PC.cubic2624_ne_zero",
    "Smooth4PC.cubicValue_eq_2624",
)


class HattoriBalancedInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[1]
        cls.module = cls.repo / "Smooth4PC" / "HattoriBalancedInput.lean"

    def lean_environment(
        self, use_fallback: bool, *, prepend: tuple[Path, ...] = ()
    ) -> dict[str, str]:
        env = os.environ.copy()
        env.pop("LEAN_PATH", None)
        paths: list[Path] = [*prepend]
        fallback = self.repo / "deps" / "mathlib4" / ".lake"
        if use_fallback:
            mathlib = fallback / "build" / "lib" / "lean"
            if mathlib.is_dir():
                paths.append(mathlib)
            packages = fallback / "packages"
            if packages.is_dir():
                paths.extend(
                    package / ".lake" / "build" / "lib" / "lean"
                    for package in sorted(packages.iterdir())
                    if (package / ".lake" / "build" / "lib" / "lean").is_dir()
                )
        if paths:
            env["LEAN_PATH"] = os.pathsep.join(str(path) for path in paths)
        return env

    def run_lean(
        self, *args: str, use_fallback: bool, prepend: tuple[Path, ...] = ()
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(PINNED_LAKE), "env", "lean", *args],
            cwd=self.repo,
            env=self.lean_environment(use_fallback, prepend=prepend),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def compile_consumer(
        self, consumer: str, *, module_source: str | None = None
    ) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str] | None]:
        with tempfile.TemporaryDirectory(prefix=".hattori-input-", dir=self.repo) as tmp:
            root = Path(tmp)
            olean_root = root / "olean"
            olean = olean_root / "Smooth4PC" / "HattoriBalancedInput.olean"
            olean.parent.mkdir(parents=True)
            source = self.module
            if module_source is not None:
                source = root / "source" / "Smooth4PC" / "HattoriBalancedInput.lean"
                source.parent.mkdir(parents=True)
                source.write_text(module_source, encoding="utf-8")
            build = self.run_lean("-o", str(olean), str(source), use_fallback=True)
            if build.returncode != 0:
                return build, None
            path = root / "Consumer.lean"
            path.write_text(consumer, encoding="utf-8")
            check = self.run_lean(str(path), use_fallback=True, prepend=(olean_root,))
            return build, check

    def test_raw_direct_compile_status_is_reported_honestly(self) -> None:
        self.assertTrue(PINNED_LAKE.is_file())
        raw = self.run_lean(str(self.module), use_fallback=False)
        output = raw.stdout + raw.stderr
        status = "PASS" if raw.returncode == 0 else "FAIL"
        first = next((line for line in output.splitlines() if line.strip()), "")
        print(f"RAW_DIRECT_COMPILE={status}; exit={raw.returncode}; {first}")
        if raw.returncode != 0:
            self.assertRegex(output, r"unknown module prefix '(?:Aesop|ImportGraph)'")

    def test_module_compiles_with_repo_relative_dependency_fallback(self) -> None:
        result = self.run_lean(str(self.module), use_fallback=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_exact_consumer_types_and_foundational_axioms(self) -> None:
        audit = "\n".join(f"#print axioms {name}" for name in AXIOM_THEOREMS)
        build, check = self.compile_consumer(CONSUMER + audit)
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        self.assertIsNotNone(check)
        assert check is not None
        output = check.stdout + check.stderr
        self.assertEqual(check.returncode, 0, output)
        self.assertNotIn("sorryAx", output)
        for theorem in AXIOM_THEOREMS:
            self.assertIn(f"'{theorem}'", output)
        allowed = {"propext", "Quot.sound", "Classical.choice"}
        for payload in re.findall(r"depends on axioms:\s*\[([^\]]*)\]", output):
            names = {name.strip() for name in payload.split(",") if name.strip()}
            self.assertLessEqual(names, allowed, f"unexpected axioms: {sorted(names)}")

    def test_semantic_mutants_compile_but_fail_exact_consumer(self) -> None:
        source = self.module.read_text(encoding="utf-8")
        one_sided = source.replace(
            "  idHom : ∀ T, Hom T T\n",
            "  idHom : ∀ T, Hom T T\n  mate : ∀ T, Hom T (B T)\n",
        ).replace(
            "TensorProduct ℚ (Hom (B T) (B T')) Tensor227",
            "TensorProduct ℚ (Hom T (B T')) Tensor227",
        ).replace(
            "TensorProduct ℚ (g.Hom (g.B T) (g.B T')) Tensor227",
            "TensorProduct ℚ (g.Hom T (g.B T')) Tensor227",
        ).replace(
            "g.Hom (g.B (chosenT g U)) (g.B (chosenT g U))",
            "g.Hom (chosenT g U) (g.B (chosenT g U))",
        ).replace(
            "g.idHom _ ⊗ₜ[ℚ] xTensor227",
            "g.mate _ ⊗ₜ[ℚ] xTensor227",
        )
        unindexed = source.replace(
            "abbrev TensorBasis227 := Fin 227 → FrobeniusLabel",
            "abbrev TensorBasis227 := FrobeniusLabel",
        ).replace(
            "def allX : TensorBasis227 := fun _ => .X",
            "def allX : TensorBasis227 := .X",
        )
        xi_input = source.replace(
            "  actualVT : g.Coeff (chosenT g U) (chosenT g U)\n",
            "  actualVT : g.Coeff (chosenT g U) (chosenT g U)\n"
            "  xi : g.Coeff (chosenT g U) (chosenT g U)\n",
        ).replace(
            "def selectedInput {g : BalancedHattoriGeometry} {U : g.Obj}\n"
            "    (actual : ActualDiagonalInput g U) := actual.actualVT",
            "def selectedInput {g : BalancedHattoriGeometry} {U : g.Obj}\n"
            "    (actual : ActualDiagonalInput g U) := actual.xi",
        ).replace(
            "selectedInput actual = actual.actualVT := rfl",
            "selectedInput actual = actual.xi := rfl",
        ).replace(
            "g.IsCycle (selectedInput actual) := actual.cycle",
            "g.IsCycle (selectedInput actual) := actual.xiCycle",
        ).replace(
            "  xi : g.Coeff (chosenT g U) (chosenT g U)\n",
            "  xi : g.Coeff (chosenT g U) (chosenT g U)\n"
            "  xiCycle : g.IsCycle xi\n",
        ).replace(
            "g.H (chosenT g U) (chosenT g U) (selectedInput actual) =\n"
            "      diagonalTarget g U := actual.binding",
            "g.H (chosenT g U) (chosenT g U) (selectedInput actual) =\n"
            "      g.H (chosenT g U) (chosenT g U) actual.xi := rfl",
        )
        m0 = source.replace(
            "abbrev M1_88 := Fin 88 → ℚ\n\n"
            "def basisVector (i : Fin 88) : M1_88 :=",
            "abbrev M0_88 := Fin 87 → ℚ\n"
            "abbrev M1_88 := M0_88\n\n"
            "def basisVector (i : Fin 87) : M1_88 :=",
        ).replace("endpoint : Fin 88", "endpoint : Fin 87").replace(
            "Equiv.Perm (Fin 88)", "Equiv.Perm (Fin 87)"
        )
        retired = source.replace(
            "def cubicValue : ℤ := 2624", "def cubicValue : ℤ := -28864"
        ).replace(
            "theorem cubicValue_eq_2624 : cubicValue = (2624 : ℤ) := by",
            "theorem cubicValue_eq_2624 : cubicValue = (-28864 : ℤ) := by",
        )
        mutants = {
            "one_sided_hom": one_sided,
            "unindexed_x_label": unindexed,
            "xi_input": xi_input,
            "m0_source": m0,
            "retired_scalar": retired,
        }
        for name, mutant in mutants.items():
            with self.subTest(mutant=name):
                self.assertNotEqual(mutant, source, f"{name} mutation did not apply")
                build, check = self.compile_consumer(CONSUMER, module_source=mutant)
                self.assertEqual(
                    build.returncode, 0,
                    f"{name} must compile standalone:\n{build.stdout}{build.stderr}",
                )
                self.assertIsNotNone(check)
                assert check is not None
                self.assertNotEqual(check.returncode, 0, f"{name} passed consumer")

    def test_interface_is_narrow_and_shortcuts_absent(self) -> None:
        source = self.module.read_text(encoding="utf-8")
        self.assertIn("TensorProduct ℚ", source)
        self.assertIn("TensorBasis227 →₀ ℚ", source)
        self.assertIn("idHom _ ⊗ₜ[ℚ] xTensor227", source)
        self.assertIn("structure BalancedHattoriCompatibility", source)
        self.assertIn("structure ActualDiagonalInput", source)
        self.assertNotIn("X ^ 227", source)
        self.assertNotIn("X^227", source)
        for token in ("native_decide", "axiom", "opaque", "sorry", "admit"):
            self.assertNotRegex(source, rf"\b{re.escape(token)}\b")
        for forbidden in ("Diffeomorphic", "NotStandard", "counterexample"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
