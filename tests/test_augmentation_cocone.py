from __future__ import annotations

import os
import re
import subprocess
import unittest
from pathlib import Path


PINNED_LAKE = Path(
    r"C:\Users\LENOVO\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe"
)


class AugmentationCoconeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[1]
        cls.module = cls.repo / "Smooth4PC" / "AugmentationCocone.lean"

    def compile_module(self) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        local_aesop = (
            self.repo
            / ".lake"
            / "packages"
            / "aesop"
            / ".lake"
            / "build"
            / "lib"
            / "lean"
            / "Aesop.olean"
        )
        fallback_packages = (
            self.repo / "deps" / "mathlib4" / ".lake" / "packages"
        )
        if not local_aesop.is_file() and fallback_packages.is_dir():
            fallback_paths = sorted(
                package / ".lake" / "build" / "lib" / "lean"
                for package in fallback_packages.iterdir()
                if (package / ".lake" / "build" / "lib" / "lean").is_dir()
            )
            inherited = env.get("LEAN_PATH")
            env["LEAN_PATH"] = os.pathsep.join(
                [*(str(path) for path in fallback_paths), *([inherited] if inherited else [])]
            )
        return subprocess.run(
            [str(PINNED_LAKE), "env", "lean", str(self.module)],
            cwd=self.repo,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_module_compiles_with_pinned_lean_4_32_1(self) -> None:
        self.assertTrue(PINNED_LAKE.is_file(), f"missing pinned Lake: {PINNED_LAKE}")
        result = self.compile_module()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_module_exposes_the_finite_cocone_theorems(self) -> None:
        source = self.module.read_text(encoding="utf-8")
        required = (
            "epsilon_iteratedDelta_one_eq_zero",
            "epsilon_iteratedDelta_X_eq_one",
            "directQ_undotted_row_eq_zero",
            "directQ_dotted_row_eq_source",
            "physicalCopyOrbitRatio_telescope",
            "physicalCopyOrbitRatio_path_telescope",
            "vertexPotential_cubic_naturality",
            "vertexPotential_loop_flat",
            "edgeLocalTwist_not_vertexCoboundary",
        )
        for theorem in required:
            self.assertRegex(source, rf"(?m)^theorem {re.escape(theorem)}\b")

    def test_module_uses_tensor_words_and_keeps_geometry_external(self) -> None:
        source = self.module.read_text(encoding="utf-8")
        self.assertIn("inductive FrobeniusBasis", source)
        self.assertIn("abbrev TensorWord", source)
        self.assertIn("def delta", source)
        self.assertIn("def epsilon", source)
        self.assertIn("∏ i, epsilon (word i)", source)
        self.assertNotIn("X^227", source)
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
