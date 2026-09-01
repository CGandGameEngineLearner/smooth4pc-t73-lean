from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


AXIOM_THEOREMS = (
    "Smooth4PC.T73.detA_eq_one",
    "Smooth4PC.T73.detAMinusI_eq_one",
    "Smooth4PC.T73.sphereDet_eq_one",
    "Smooth4PC.T73.computedCubic_eq_neg59072",
    "Smooth4PC.T73.computedCubic_ne_zero",
    "Smooth4PC.T73.computedDegree_eq_494",
    "Smooth4PC.T73.computedDegree_ne_zero",
    "Smooth4PC.T73.undottedRow_eq_zero",
    "Smooth4PC.T73.dottedRow_eq_source",
    "Smooth4PC.T73.epsilonWords_splitTreeWords",
    "Smooth4PC.T73.splitTree_wholeSource_undotted_eq_zero",
    "Smooth4PC.T73.splitTree_wholeSource_dotted_eq_source",
    "Smooth4PC.T73.splitTree_directQ_undotted_row_eq_zero",
    "Smooth4PC.T73.splitTree_directQ_dotted_row_eq_source",
    "Smooth4PC.T73.SphereChart.ell_comp_undotted_eq_zero",
    "Smooth4PC.T73.SphereChart.ell_comp_dottedMinusId_eq_zero",
    "Smooth4PC.T73.sphereRelation_le_ker",
    "Smooth4PC.T73.descendedSphereRow_comp_quotient",
    "Smooth4PC.T73.sphereClass_ne_zero",
    "Smooth4PC.DiagonalShadow.cyclicRelation_le_ker",
    "Smooth4PC.DiagonalShadow.descendedRow_comp_quotient",
    "Smooth4PC.CoefficientBimoduleMorphism.cyclicRelation_le_comap",
    "Smooth4PC.ShadowMorphism.descendedRow_naturality",
    "Smooth4PC.T73.aMinusIInverse_left",
    "Smooth4PC.T73.aMinusIInverse_right",
    "Smooth4PC.T73.aMinusICokernel_eq_zero",
    "Smooth4PC.T73.hTwoMinusIInverse_left",
    "Smooth4PC.T73.hTwoMinusIInverse_right",
    "Smooth4PC.T73.hTwoMinusICokernel_eq_zero",
    "Smooth4PC.T73.t73CSLinearObstructionsVanish",
    "Smooth4PC.T73.t73IsHomotopySphere_of_topology",
    "Smooth4PC.T73.s4DegreeZero_of_reduction",
    "Smooth4PC.T73.conditionalNotStandard",
    "Smooth4PC.T73.conditionalIsHomotopySphere",
    "Smooth4PC.T73.conditionalCounterexample",
    "Smooth4PC.T73.conditionalCounterexample_of_topology",
)
FOUNDATIONAL_AXIOMS = {"propext", "Quot.sound", "Classical.choice"}
SPHERE_CONSUMER = r"""
import Smooth4PC.T73Finite

namespace T73SphereConsumer

open Smooth4PC.T73

example : sphereColumns 0 1 = -189 := by
  norm_num [sphereColumns]

example : sphereColumns 1 0 = 8608 := by
  norm_num [sphereColumns]

end T73SphereConsumer
"""


def resolve_lake() -> Path:
    configured = os.environ.get("T73_LAKE")
    if configured:
        candidate = Path(configured).expanduser()
        if candidate.is_file():
            return candidate
        raise FileNotFoundError(f"T73_LAKE does not name a file: {candidate}")

    on_path = shutil.which("lake")
    if on_path:
        return Path(on_path)

    toolchain_bin = (
        Path.home()
        / ".elan"
        / "toolchains"
        / "leanprover--lean4---v4.32.1"
        / "bin"
    )
    for name in ("lake.exe", "lake"):
        candidate = toolchain_bin / name
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("lake was not found via T73_LAKE, PATH, or ~/.elan")


class T73FiniteFormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[1]
        cls.finite = cls.repo / "Smooth4PC" / "T73Finite.lean"
        cls.external = cls.repo / "Smooth4PC" / "T73External.lean"
        cls.conditional = cls.repo / "Smooth4PC" / "T73Conditional.lean"
        cls.sphere_quotient = cls.repo / "Smooth4PC" / "T73SphereQuotient.lean"
        cls.split_movie = cls.repo / "Smooth4PC" / "T73SplitMovie.lean"
        cls.coefficient_trace = cls.repo / "Smooth4PC" / "CoefficientTrace.lean"
        cls.cs_algebra = cls.repo / "Smooth4PC" / "T73CSAlgebra.lean"
        cls.cs_topology = cls.repo / "Smooth4PC" / "T73CSTopology.lean"
        cls.s4_control = cls.repo / "Smooth4PC" / "T73S4Control.lean"
        cls.audit = cls.repo / "T73Audit.lean"
        cls.lake = resolve_lake()

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
        args = [str(self.lake), "env", "lean"]
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

    def assert_axiom_reports(self, output: str) -> None:
        reports = re.findall(
            r"(?m)^'([^']+)' depends on axioms:\s*\[([^\]]*)\]$", output
        )
        self.assertEqual(len(reports), len(AXIOM_THEOREMS), "missing axiom report")
        self.assertEqual({name for name, _ in reports}, set(AXIOM_THEOREMS))
        for _, payload in reports:
            names = {name.strip() for name in payload.split(",") if name.strip()}
            self.assertLessEqual(
                names, FOUNDATIONAL_AXIOMS, f"unexpected axioms: {sorted(names)}"
            )

    def test_axiom_report_gate_rejects_a_synthetically_removed_line(self) -> None:
        complete = "\n".join(
            f"'{name}' depends on axioms: [propext]" for name in AXIOM_THEOREMS
        )
        missing = complete.replace(complete.splitlines()[0] + "\n", "", 1)
        with self.assertRaisesRegex(AssertionError, "missing axiom report"):
            self.assert_axiom_reports(missing)

    def test_finite_module_exists_and_builds(self) -> None:
        self.assertTrue(self.finite.is_file(), "missing Smooth4PC/T73Finite.lean")
        self.assertTrue(
            self.external.is_file(), "missing Smooth4PC/T73External.lean"
        )
        self.assertTrue(
            self.conditional.is_file(), "missing Smooth4PC/T73Conditional.lean"
        )
        self.assertTrue(
            self.sphere_quotient.is_file(),
            "missing Smooth4PC/T73SphereQuotient.lean",
        )
        self.assertTrue(
            self.split_movie.is_file(), "missing Smooth4PC/T73SplitMovie.lean"
        )
        for path in (
            self.coefficient_trace,
            self.cs_algebra,
            self.cs_topology,
            self.s4_control,
        ):
            self.assertTrue(path.is_file(), f"missing {path.name}")
        self.assertTrue(self.audit.is_file(), "missing T73Audit.lean")

        finite_source = self.finite.read_text(encoding="utf-8")
        external_source = self.external.read_text(encoding="utf-8")
        conditional_source = self.conditional.read_text(encoding="utf-8")
        sphere_quotient_source = self.sphere_quotient.read_text(encoding="utf-8")
        split_movie_source = self.split_movie.read_text(encoding="utf-8")
        coefficient_trace_source = self.coefficient_trace.read_text(encoding="utf-8")
        cs_algebra_source = self.cs_algebra.read_text(encoding="utf-8")
        cs_topology_source = self.cs_topology.read_text(encoding="utf-8")
        s4_control_source = self.s4_control.read_text(encoding="utf-8")
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
                finite_source
                + external_source
                + conditional_source
                + sphere_quotient_source
                + split_movie_source
                + coefficient_trace_source
                + cs_algebra_source
                + cs_topology_source
                + s4_control_source
                + audit_source,
                rf"\b{re.escape(token)}\b",
                f"forbidden Lean token: {token}",
            )

        self.assertIn("(geom : ExternalGeometry u)", conditional_source)
        self.assertIn("(cs : CSExternalGeometry u)", conditional_source)
        self.assertNotRegex(conditional_source, r"\btheorem\s+notStandard\b")
        self.assertNotRegex(conditional_source, r"\btheorem\s+counterexample\b")

        self.assertIn("substitutionLinear ^ 3 * cubicBase", finite_source)
        self.assertIn(
            "degreeMinus44 + degreePlus227 + degreePlus315 + degreeMinus4",
            finite_source,
        )
        self.assertIn("matrixA row column - identityEntry row column", finite_source)
        self.assertIn("a * (e * i - f * h)", finite_source)

        scratch_value = os.environ.get("T73_TMP")
        scratch = Path(scratch_value).expanduser() if scratch_value else None
        with tempfile.TemporaryDirectory(prefix="finite-build-", dir=scratch) as tmp:
            olean_root = Path(tmp) / "olean"
            augmentation = self.repo / "Smooth4PC" / "AugmentationCocone.lean"
            augmentation_olean = (
                olean_root / "Smooth4PC" / "AugmentationCocone.olean"
            )
            certificate_data = self.repo / "Smooth4PC" / "CertificateData.lean"
            certificate_data_olean = (
                olean_root / "Smooth4PC" / "CertificateData.olean"
            )
            arithmetic = self.repo / "Smooth4PC" / "Arithmetic.lean"
            arithmetic_olean = olean_root / "Smooth4PC" / "Arithmetic.olean"
            interfaces = self.repo / "Smooth4PC" / "Interfaces.lean"
            interfaces_olean = olean_root / "Smooth4PC" / "Interfaces.olean"
            coefficient_trace_olean = (
                olean_root / "Smooth4PC" / "CoefficientTrace.olean"
            )
            finite_olean = olean_root / "Smooth4PC" / "T73Finite.olean"
            cs_algebra_olean = olean_root / "Smooth4PC" / "T73CSAlgebra.olean"
            cs_topology_olean = olean_root / "Smooth4PC" / "T73CSTopology.olean"
            s4_control_olean = olean_root / "Smooth4PC" / "T73S4Control.olean"
            sphere_quotient_olean = (
                olean_root / "Smooth4PC" / "T73SphereQuotient.olean"
            )
            split_movie_olean = olean_root / "Smooth4PC" / "T73SplitMovie.olean"
            external_olean = olean_root / "Smooth4PC" / "T73External.olean"
            conditional_olean = olean_root / "Smooth4PC" / "T73Conditional.olean"
            for source, target in (
                (augmentation, augmentation_olean),
                (certificate_data, certificate_data_olean),
                (arithmetic, arithmetic_olean),
                (interfaces, interfaces_olean),
                (self.coefficient_trace, coefficient_trace_olean),
                (self.finite, finite_olean),
                (self.external, external_olean),
                (self.cs_algebra, cs_algebra_olean),
                (self.cs_topology, cs_topology_olean),
                (self.s4_control, s4_control_olean),
                (self.split_movie, split_movie_olean),
                (self.sphere_quotient, sphere_quotient_olean),
                (self.conditional, conditional_olean),
            ):
                build = self.run_lean(source, olean_root, target)
                self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            consumer = Path(tmp) / "T73SphereConsumer.lean"
            consumer.write_text(SPHERE_CONSUMER, encoding="utf-8")
            sphere_check = self.run_lean(consumer, olean_root)
            self.assertEqual(
                sphere_check.returncode,
                0,
                sphere_check.stdout + sphere_check.stderr,
            )
            audit = self.run_lean(self.audit, olean_root)
            output = audit.stdout + audit.stderr
            self.assertEqual(audit.returncode, 0, output)
        self.assertIn("T73_TYPE|Smooth4PC.T73.computedCubic", output)
        self.assertIn("T73_BODY|Smooth4PC.T73.matrixAMinusI", output)
        self.assertIn(
            "T73_TYPE|Smooth4PC.T73.conditionalNotStandard", output
        )
        self.assertNotIn("sorryAx", output)
        self.assertNotIn("Lean.ofReduceBool", output)
        self.assert_axiom_reports(output)


if __name__ == "__main__":
    unittest.main()
