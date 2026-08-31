from __future__ import annotations

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


PINNED_LAKE = Path(
    r"C:\Users\LENOVO\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe"
)

CONSUMER = r"""
import Smooth4PC.HattoriBalancedInput

namespace HattoriBalancedInputConsumer
open Smooth4PC

universe u v w

example (g : BalancedHattoriGeometry.{u, v, w}) (T T' : g.Obj) :
    g.Coeff T T' ≃
      (g.Hom (g.B T) (g.B T') × (Fin 227 → FrobeniusLabel)) :=
  g.H T T'

example : allX = (fun _ : Fin 227 => FrobeniusLabel.X) := rfl

example (g : BalancedHattoriGeometry.{u, v, w}) (U : g.Obj) :
    g.H (chosenT g U) (chosenT g U) (vT g U) = diagonalTarget g U :=
  vT_binding g U

example (g : BalancedHattoriGeometry.{u, v, w}) (U : g.Obj) :
    selectedInput g U = vT g U :=
  selectedInput_eq_vT g U

example : cupVector = basisVector 0 - basisVector 5 := rfl
example : Fin 88 → ℚ := cupVector
example : positiveSource = EndpointSource.M1_88 := positiveSource_is_M1_88

example : relativeNu baseState = 0 := relativeNu_base
example : relativeNu cupState = 0 := relativeNu_cup
example (s : PhysicalState) : relativeNu (dottedX s) = relativeNu s :=
  relativeNu_dottedX s
example (s : PhysicalState) : relativeNu (undottedOne s) = relativeNu s + 1 :=
  relativeNu_undottedOne s
example (s : PhysicalState) (h : 1 ≤ relativeNu s) : headRow s = 0 :=
  headRow_zero_of_relativeNu_ge_one s h
example (s : PhysicalState) (h : 1 ≤ relativeNu s) : relativeHeadRow s = 0 :=
  relativeHeadRow_zero_of_relativeNu_ge_one s h

example : (183 : ℤ) + 315 - 4 = 494 := degree_ledger_eq_494
example : (-8 : ℤ) * 7384 = -59072 := cubic_arithmetic_eq_neg59072
example : (-59072 : ℤ) ≠ 0 := neg59072_ne_zero
example : cubicValue = (-59072 : ℤ) := cubicValue_eq_neg59072

end HattoriBalancedInputConsumer
"""

AXIOM_THEOREMS = (
    "Smooth4PC.B_chosenT_eq_U",
    "Smooth4PC.vT_binding",
    "Smooth4PC.selectedInput_eq_vT",
    "Smooth4PC.relativeNu_eq_addedDefect",
    "Smooth4PC.relativeNu_base",
    "Smooth4PC.relativeNu_cup",
    "Smooth4PC.relativeNu_dottedX",
    "Smooth4PC.relativeNu_undottedOne",
    "Smooth4PC.headRow_zero_of_relativeNu_ge_one",
    "Smooth4PC.relativeHeadRow_zero_of_relativeNu_ge_one",
    "Smooth4PC.degree_ledger_eq_494",
    "Smooth4PC.cubic_arithmetic_eq_neg59072",
    "Smooth4PC.neg59072_ne_zero",
    "Smooth4PC.cubicValue_eq_neg59072",
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
        fallback_root = self.repo / "deps" / "mathlib4" / ".lake"
        fallback_paths: list[Path] = [*prepend]
        if use_fallback:
            mathlib_build = fallback_root / "build" / "lib" / "lean"
            if mathlib_build.is_dir():
                fallback_paths.append(mathlib_build)
            packages = fallback_root / "packages"
            if packages.is_dir():
                fallback_paths.extend(
                    package / ".lake" / "build" / "lib" / "lean"
                    for package in sorted(packages.iterdir())
                    if (package / ".lake" / "build" / "lib" / "lean").is_dir()
                )
        if fallback_paths:
            env["LEAN_PATH"] = os.pathsep.join(str(path) for path in fallback_paths)
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
            consumer_path = root / "Consumer.lean"
            consumer_path.write_text(consumer, encoding="utf-8")
            check = self.run_lean(
                str(consumer_path), use_fallback=True, prepend=(olean_root,)
            )
            return build, check

    def test_raw_direct_compile_status_is_reported_honestly(self) -> None:
        self.assertTrue(PINNED_LAKE.is_file(), f"missing pinned Lake: {PINNED_LAKE}")
        raw = self.run_lean(str(self.module), use_fallback=False)
        output = raw.stdout + raw.stderr
        status = "PASS" if raw.returncode == 0 else "FAIL"
        first = next((line for line in output.splitlines() if line.strip()), "")
        print(f"RAW_DIRECT_COMPILE={status}; exit={raw.returncode}; {first}")
        if raw.returncode != 0:
            self.assertRegex(
                output,
                r"unknown module prefix '(?:Aesop|ImportGraph)'",
                "raw compile failed for a reason other than the pre-existing dependency gap",
            )

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
            "  idHom : ∀ T, Hom T T\n"
            "  mate : ∀ T, Hom T (B T)\n",
        ).replace(
            "Hom (B T) (B T') × SeparateXLabels",
            "Hom T (B T') × SeparateXLabels",
        ).replace(
            "g.Hom (g.B (chosenT g U)) (g.B (chosenT g U)) × SeparateXLabels :=\n"
            "  (g.idHom _, allX)",
            "g.Hom (chosenT g U) (g.B (chosenT g U)) × SeparateXLabels :=\n"
            "  (g.mate _, allX)",
        )
        mutants = {
            "one_sided_hom": one_sided,
            "unindexed_x_label": source.replace(
                "abbrev SeparateXLabels := Fin 227 → FrobeniusLabel\n\n"
                "def allX : SeparateXLabels := fun _ => .X",
                "abbrev SeparateXLabels := FrobeniusLabel\n\n"
                "def allX : SeparateXLabels := .X",
            ),
            "xi_input": source.replace(
                "def selectedInput (g : BalancedHattoriGeometry) (U : g.Obj) := vT g U\n\n"
                "theorem selectedInput_eq_vT (g : BalancedHattoriGeometry) (U : g.Obj) :\n"
                "    selectedInput g U = vT g U := rfl",
                "def selectedInput (g : BalancedHattoriGeometry) (U : g.Obj)\n"
                "    (xi : g.Coeff (chosenT g U) (chosenT g U)) := xi\n\n"
                "theorem selectedInput_eq_vT (g : BalancedHattoriGeometry) (U : g.Obj)\n"
                "    (xi : g.Coeff (chosenT g U) (chosenT g U)) :\n"
                "    selectedInput g U xi = xi := rfl",
            ),
            "m0_source": source.replace(
                "abbrev M1_88 := Fin 88 → ℚ\n\n"
                "def basisVector (i : Fin 88) : M1_88 :=",
                "abbrev M0_88 := Fin 87 → ℚ\n"
                "abbrev M1_88 := M0_88\n\n"
                "def basisVector (i : Fin 87) : M1_88 :=",
            ),
            "retired_scalar": source.replace(
                "def cubicValue : ℤ := -59072",
                "def cubicValue : ℤ := -28864",
            ).replace(
                "theorem cubicValue_eq_neg59072 : cubicValue = (-59072 : ℤ) := by",
                "theorem cubicValue_eq_neg59072 : cubicValue = (-28864 : ℤ) := by",
            ),
        }
        for name, mutant in mutants.items():
            with self.subTest(mutant=name):
                self.assertNotEqual(mutant, source, f"{name} mutation did not apply")
                build, check = self.compile_consumer(CONSUMER, module_source=mutant)
                self.assertEqual(
                    build.returncode,
                    0,
                    f"{name} mutant should be a valid standalone module:\n"
                    + build.stdout
                    + build.stderr,
                )
                self.assertIsNotNone(check)
                assert check is not None
                self.assertNotEqual(
                    check.returncode,
                    0,
                    f"{name} mutant passed the exact semantic consumer",
                )

    def test_interface_is_narrow_and_shortcuts_absent(self) -> None:
        source = self.module.read_text(encoding="utf-8")
        self.assertIn("Fin 227 → FrobeniusLabel", source)
        self.assertIn("Hom (B T) (B T')", source)
        self.assertNotIn("X ^ 227", source)
        self.assertNotIn("X^227", source)
        for token in ("native_decide", "axiom", "opaque", "sorry", "admit"):
            self.assertNotRegex(source, rf"\b{re.escape(token)}\b")
        for forbidden_conclusion in (
            "Diffeomorphic",
            "NotStandard",
            "counterexample",
            "final quotient",
        ):
            self.assertNotIn(forbidden_conclusion, source)


if __name__ == "__main__":
    unittest.main()
