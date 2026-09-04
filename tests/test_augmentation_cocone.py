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

CONSUMER_PRELUDE = r"""
import Smooth4PC.AugmentationCocone

noncomputable section
namespace AugmentationConsumer

open Smooth4PC

abbrev Target (b : Nat) := TensorTarget ℚ b

def qSource : ℚ ≃ₗ[ℚ] ℚ := LinearEquiv.refl ℚ ℚ
def qTarget (b : Nat) : Target b ≃ₗ[ℚ] Target b := LinearEquiv.refl ℚ (Target b)
def testRow : ℚ →ₗ[ℚ] ℚ := LinearMap.id

example (b : Nat) (hb : 0 < b) :
    epsilonWords (iteratedDelta b .one) = 0 :=
  epsilon_iteratedDelta_one_eq_zero b hb

example (b : Nat) (hb : 0 < b) :
    epsilonWords (iteratedDelta b .X) = 1 :=
  epsilon_iteratedDelta_X_eq_one b hb

example (basis : FrobeniusBasis) : iteratedDelta 2 basis = delta basis :=
  iteratedDelta_two_eq_delta basis

example (b : Nat) (hb : 0 < b) :
    (actualTargetRow b (qTarget b) testRow).comp
        (conjugatedInsertion qSource b (qTarget b) .one) = 0 :=
  directQ_undotted_row_eq_zero qSource b (qTarget b) testRow hb

example (b : Nat) (hb : 0 < b) :
    (actualTargetRow b (qTarget b) testRow).comp
        (conjugatedInsertion qSource b (qTarget b) .X) =
      actualSourceRow qSource testRow :=
  directQ_dotted_row_eq_source qSource b (qTarget b) testRow hb

section CubicEdge

variable {Vs Vt Cs Ct : Type*}
variable [AddCommGroup Vs] [Module ℚ Vs]
variable [AddCommGroup Vt] [Module ℚ Vt]
variable [AddCommGroup Cs] [Module ℚ Cs]
variable [AddCommGroup Ct] [Module ℚ Ct]
variable (Qs : Vs ≃ₗ[ℚ] Cs) (Qt : Vt ≃ₗ[ℚ] Ct)
variable (D : Cs →ₗ[ℚ] Ct) (Ks : Cs →ₗ[ℚ] Cs) (Kt : Ct →ₗ[ℚ] Ct)

example (hK : Kt.comp D = D.comp Ks) :
    (transportedCubic Qt Kt).comp (conjugatedEdge Qs Qt D) =
      (conjugatedEdge Qs Qt D).comp (transportedCubic Qs Ks) :=
  vertexPotential_cubic_naturality Qs Qt D Ks Kt hK

end CubicEdge

end AugmentationConsumer
"""

AXIOM_THEOREMS = (
    "Smooth4PC.epsilon_iteratedDelta_one_eq_zero",
    "Smooth4PC.epsilon_iteratedDelta_X_eq_one",
    "Smooth4PC.iteratedDelta_two_eq_delta",
    "Smooth4PC.iteratedDelta_word_length",
    "Smooth4PC.directQ_undotted_row_eq_zero",
    "Smooth4PC.directQ_dotted_row_eq_source",
    "Smooth4PC.physicalCopyOrbitRatio_telescope",
    "Smooth4PC.physicalCopyOrbitRatio_path_telescope",
    "Smooth4PC.vertexPotential_cubic_naturality",
    "Smooth4PC.edgeLocalTwist_not_vertexCoboundary",
)

AXIOM_AUDIT = "\n".join(f"#print axioms {theorem}" for theorem in AXIOM_THEOREMS)


class AugmentationCoconeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[1]
        cls.module = cls.repo / "Smooth4PC" / "AugmentationCocone.lean"

    def lean_environment(
        self, use_fallback: bool, *, prepend: tuple[Path, ...] = ()
    ) -> dict[str, str]:
        env = os.environ.copy()
        env.pop("LEAN_PATH", None)
        if not use_fallback and not prepend:
            return env
        fallback_packages = self.repo / "deps" / "mathlib4" / ".lake" / "packages"
        mathlib_build = (
            self.repo / "deps" / "mathlib4" / ".lake" / "build" / "lib" / "lean"
        )
        fallback_paths: list[Path] = []
        if use_fallback and fallback_packages.is_dir():
            fallback_paths = sorted(
                package / ".lake" / "build" / "lib" / "lean"
                for package in fallback_packages.iterdir()
                if (package / ".lake" / "build" / "lib" / "lean").is_dir()
            )
        lean_paths = [*prepend]
        if use_fallback and mathlib_build.is_dir():
            lean_paths.append(mathlib_build)
        lean_paths.extend(fallback_paths)
        if lean_paths:
            env["LEAN_PATH"] = os.pathsep.join(str(path) for path in lean_paths)
        return env

    def run_lean(self, *args: str, use_fallback: bool,
                 prepend: tuple[Path, ...] = ()) -> subprocess.CompletedProcess[str]:
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

    def compile_import_consumer(
        self, consumer_source: str, *, module_source: str | None = None
    ) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str] | None]:
        with tempfile.TemporaryDirectory(
            prefix=".augmentation-cocone-", dir=self.repo
        ) as tmp:
            temporary = Path(tmp)
            olean_root = temporary / "olean"
            olean = olean_root / "Smooth4PC" / "AugmentationCocone.olean"
            olean.parent.mkdir(parents=True)
            if module_source is None:
                source = self.module
            else:
                source = temporary / "source" / "Smooth4PC" / "AugmentationCocone.lean"
                source.parent.mkdir(parents=True)
                source.write_text(module_source, encoding="utf-8")
            build = self.run_lean(
                "-o", str(olean), str(source), use_fallback=True
            )
            if build.returncode != 0:
                return build, None
            consumer = temporary / "AugmentationConsumer.lean"
            consumer.write_text(consumer_source, encoding="utf-8")
            check = self.run_lean(
                str(consumer), use_fallback=True, prepend=(olean_root,)
            )
            return build, check

    def test_raw_direct_compile_status_is_reported_honestly(self) -> None:
        self.assertTrue(PINNED_LAKE.is_file(), f"missing pinned Lake: {PINNED_LAKE}")
        raw = self.run_lean(str(self.module), use_fallback=False)
        output = raw.stdout + raw.stderr
        status = "PASS" if raw.returncode == 0 else "FAIL"
        first_line = next((line for line in output.splitlines() if line.strip()), "")
        print(f"RAW_DIRECT_COMPILE={status}; exit={raw.returncode}; {first_line}")
        if raw.returncode != 0:
            self.assertIn("unknown module prefix 'Aesop'", output)

    def test_module_compiles_with_repo_relative_dependency_fallback(self) -> None:
        result = self.run_lean(str(self.module), use_fallback=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_recursive_coproduct_and_precounit_target_are_structural(self) -> None:
        source = self.module.read_text(encoding="utf-8")
        self.assertIn("abbrev TensorWord := List FrobeniusBasis", source)
        self.assertRegex(
            source,
            r"(?s)def delta.*?\.one\s*=>\s*\[\[\.one, \.X\], \[\.X, \.one\]\].*?"
            r"\.X\s*=>\s*\[\[\.X, \.X\]\]",
        )
        split_block = source[source.index("def splitHead") : source.index("def iterateSplit")]
        self.assertIn("delta", split_block)
        iterate_block = source[
            source.index("def iterateSplit") : source.index("def iteratedDelta")
        ]
        self.assertIn("flatMap splitHead", iterate_block)
        iterated_block = source[
            source.index("def iteratedDelta") : source.index("theorem epsilonWords_splitHead")
        ]
        self.assertIn("iterateSplit", iterated_block)
        self.assertIn("iteratedDelta_two_eq_delta", source)

        self.assertIn(
            "abbrev FixedTensorWord (b : Nat) := {word : TensorWord // word.length = b}",
            source,
        )
        self.assertRegex(source, r"abbrev TensorTarget.*FixedTensorWord b →₀ C")
        self.assertIn("iteratedDelta_word_length", source)
        insertion_block = source[
            source.index("def canonicalInsertion") : source.index("def targetCounitRow")
        ]
        self.assertIn("Finsupp.lsingle", insertion_block)
        self.assertIn("FixedTensorWord", insertion_block)
        self.assertNotIn("epsilon", insertion_block)
        row_block = source[
            source.index("def targetCounitRow") : source.index("theorem targetRow_comp_insertion")
        ]
        self.assertIn("Finsupp.lsum", row_block)
        self.assertIn("epsilonTensor", row_block)

    def test_physical_orbits_use_copy_counts_occupancies_and_absent_case(self) -> None:
        source = self.module.read_text(encoding="utf-8")
        self.assertRegex(source, r"(?s)def orbitSize.*Nat\.choose")
        self.assertIn("def orbitPresent", source)
        self.assertIn("physicalCopyOrbitRatio_absent", source)
        self.assertIn("physicalCopyOrbitRatio_path_telescope", source)

    def test_exact_consumer_types_compile_and_axioms_are_foundational_only(self) -> None:
        build, result = self.compile_import_consumer(CONSUMER_PRELUDE + AXIOM_AUDIT)
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        self.assertIsNotNone(result)
        assert result is not None
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertNotIn("sorryAx", output)
        for theorem in AXIOM_THEOREMS:
            self.assertIn(f"'{theorem}'", output)
        allowed = {"propext", "Quot.sound", "Classical.choice"}
        for payload in re.findall(r"depends on axioms:\s*\[([^\]]*)\]", output):
            names = {name.strip() for name in payload.split(",") if name.strip()}
            self.assertLessEqual(names, allowed, f"unexpected axioms: {sorted(names)}")

    def test_name_only_true_direct_q_mutant_is_rejected(self) -> None:
        source = self.module.read_text(encoding="utf-8")
        marker = "theorem directQ_dotted_row_eq_source"
        start = source.index(marker)
        end = source.index("/-! ### Physical-copy orbit normalization -/", start)
        mutant_source = (
            source[:start]
            + "theorem directQ_dotted_row_eq_source : True := by\n  trivial\n\n"
            + source[end:]
        )
        self.assertIn(marker, mutant_source)
        build, result = self.compile_import_consumer(
            CONSUMER_PRELUDE, module_source=mutant_source
        )
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertNotEqual(result.returncode, 0, "name-only True mutant compiled")
        self.assertRegex(
            result.stdout + result.stderr,
            r"(?i)type mismatch|application type mismatch|function expected",
        )

    def test_unindexed_all_length_target_consumer_is_rejected(self) -> None:
        mutant = r"""
import Smooth4PC.AugmentationCocone

noncomputable section
namespace UnindexedTargetMutant
open Smooth4PC

abbrev AllLengthTarget := TensorWord →₀ ℚ
def qSource : ℚ ≃ₗ[ℚ] ℚ := LinearEquiv.refl ℚ ℚ
def qAll : AllLengthTarget ≃ₗ[ℚ] AllLengthTarget :=
  LinearEquiv.refl ℚ AllLengthTarget
def row : ℚ →ₗ[ℚ] ℚ := LinearMap.id

example (b : Nat) (hb : 0 < b) :
    (actualTargetRow b qAll row).comp
        (conjugatedInsertion qSource b qAll .X) =
      actualSourceRow qSource row :=
  directQ_dotted_row_eq_source qSource b qAll row hb

end UnindexedTargetMutant
"""
        build, result = self.compile_import_consumer(mutant)
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertNotEqual(result.returncode, 0, "unindexed target mutant compiled")
        self.assertRegex(
            result.stdout + result.stderr,
            r"(?i)type mismatch|application type mismatch|failed to synthesize",
        )

    def test_negative_edge_control_and_canonical_cubic_edge_are_exposed(self) -> None:
        source = self.module.read_text(encoding="utf-8")
        self.assertIn("(D : Cs →ₗ[ℚ] Ct)", source)
        self.assertIn("(hK : Kt.comp D = D.comp Ks)", source)
        self.assertIn("pureVertexCoboundary_triangle_flat", source)
        self.assertIn("edgeLocalTwist_not_vertexCoboundary", source)
        self.assertIn("does not assert the actual T73 geometric premises", source)

    def test_forbidden_proof_shortcuts_are_absent(self) -> None:
        source = self.module.read_text(encoding="utf-8")
        forbidden = (
            "native_decide",
            "ofReduceBool",
            "axiom",
            "opaque",
            "sorry",
            "admit",
        )
        for token in forbidden:
            self.assertNotRegex(source, rf"\b{re.escape(token)}\b")


if __name__ == "__main__":
    unittest.main()
