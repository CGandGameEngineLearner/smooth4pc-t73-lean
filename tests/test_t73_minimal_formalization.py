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


class T73FiniteFormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[1]
        cls.finite = cls.repo / "Smooth4PC" / "T73Finite.lean"
        cls.audit = cls.repo / "T73Audit.lean"

    def lean_environment(self, olean_root: Path) -> dict[str, str]:
        env = os.environ.copy()
        env.pop("LEAN_PATH", None)
        mathlib = self.repo / "deps" / "mathlib4"
        paths = [olean_root, mathlib / ".lake" / "build" / "lib" / "lean"]
        packages = mathlib / ".lake" / "packages"
        paths.extend(
            package / ".lake" / "build" / "lib" / "lean"
            for package in sorted(packages.iterdir())
            if (package / ".lake" / "build" / "lib" / "lean").is_dir()
        )
        env["LEAN_PATH"] = os.pathsep.join(str(path) for path in paths)
        return env

    def run_lean(
        self, source: Path, olean_root: Path, output: Path | None = None
    ) -> subprocess.CompletedProcess[str]:
        args = [str(PINNED_LAKE), "env", "lean"]
        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)
            args.extend(["-o", str(output)])
        args.append(str(source))
        return subprocess.run(
            args,
            cwd=self.repo,
            env=self.lean_environment(olean_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def test_finite_module_exists_and_builds(self) -> None:
        self.assertTrue(self.finite.is_file(), "missing Smooth4PC/T73Finite.lean")
        self.assertTrue(self.audit.is_file(), "missing T73Audit.lean")

        finite_source = self.finite.read_text(encoding="utf-8")
        audit_source = self.audit.read_text(encoding="utf-8")
        for token in (
            "sorry",
            "admit",
            "axiom",
            "constant",
            "opaque",
            "unsafe",
            "extern",
            "implemented_by",
            "run_tac",
        ):
            self.assertNotRegex(
                finite_source + audit_source,
                rf"\b{re.escape(token)}\b",
                f"forbidden Lean token: {token}",
            )

        self.assertIn("substitutionLinear ^ 3 * cubicBase", finite_source)
        self.assertIn(
            "degreeMinus44 + degreePlus227 + degreePlus315 + degreeMinus4",
            finite_source,
        )
        self.assertIn("matrixA row column - identityEntry row column", finite_source)
        self.assertIn("a * (e * i - f * h)", finite_source)

        scratch = Path(r"D:\tmp\t73_minimal_lean")
        with tempfile.TemporaryDirectory(prefix="finite-build-", dir=scratch) as tmp:
            olean_root = Path(tmp) / "olean"
            augmentation = self.repo / "Smooth4PC" / "AugmentationCocone.lean"
            augmentation_olean = (
                olean_root / "Smooth4PC" / "AugmentationCocone.olean"
            )
            finite_olean = olean_root / "Smooth4PC" / "T73Finite.olean"
            for source, target in (
                (augmentation, augmentation_olean),
                (self.finite, finite_olean),
            ):
                build = self.run_lean(source, olean_root, target)
                self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            audit = self.run_lean(self.audit, olean_root)
            output = audit.stdout + audit.stderr
            self.assertEqual(audit.returncode, 0, output)
        self.assertIn("T73_TYPE|Smooth4PC.T73.computedCubic", output)
        self.assertIn("T73_BODY|Smooth4PC.T73.matrixAMinusI", output)
        self.assertNotIn("sorryAx", output)
        self.assertNotIn("Lean.ofReduceBool", output)
        allowed = {"propext", "Quot.sound", "Classical.choice"}
        for payload in re.findall(r"depends on axioms:\s*\[([^\]]*)\]", output):
            names = {name.strip() for name in payload.split(",") if name.strip()}
            self.assertLessEqual(names, allowed, f"unexpected axioms: {sorted(names)}")


if __name__ == "__main__":
    unittest.main()
