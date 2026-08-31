from __future__ import annotations

import re
import unittest
from pathlib import Path


class ArithmeticAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[1]
        cls.arithmetic = cls.repo / "Smooth4PC" / "Arithmetic.lean"
        cls.audit = cls.repo / "AuditArithmetic.lean"
        cls.fixture_dir = cls.repo / "tests" / "fixtures" / "arithmetic_mutants"

    def test_required_arithmetic_sources_exist(self) -> None:
        self.assertTrue(self.arithmetic.is_file(), "Smooth4PC/Arithmetic.lean is missing")
        self.assertTrue(self.audit.is_file(), "AuditArithmetic.lean is missing")

    def test_forbidden_proof_shortcuts_are_absent(self) -> None:
        forbidden = (
            "native_decide",
            "ofReduceBool",
            "axiom",
            "opaque",
            "sorry",
            "admit",
        )
        combined = self.arithmetic.read_text(encoding="utf-8") + self.audit.read_text(
            encoding="utf-8"
        )
        combined += "".join(
            path.read_text(encoding="utf-8")
            for path in sorted(self.fixture_dir.glob("*.lean"))
        )
        for token in forbidden:
            self.assertNotRegex(combined, rf"\b{re.escape(token)}\b")

    def test_det3_is_explicitly_row_major_and_has_zero_fallback(self) -> None:
        text = self.arithmetic.read_text(encoding="utf-8")
        self.assertIn("Row-major 3 x 3 determinant", text)
        self.assertIn("| [[a, b, c], [d, e, f], [g, h, i]] =>", text)
        self.assertIn("a * (e * i - f * h)", text)
        self.assertIn("- b * (d * i - f * g)", text)
        self.assertIn("+ c * (d * h - e * g)", text)
        self.assertRegex(text, r"(?m)^\s*\| _ => 0$")

    def test_all_required_theorems_exist(self) -> None:
        text = self.audit.read_text(encoding="utf-8")
        names = (
            "matrixA_rowMajor_entry_0_1",
            "det_matrixA_eq_one",
            "det_matrixAMinusI_eq_one",
            "det_sphereColumns_eq_one",
            "cubic_factor_times_epsilon_eq_h3",
            "oneHandleActualCapH3_ne_zero",
            "th1Sigma0_eq_zero",
            "th1Sigma1MinusId_eq_zero",
            "th2Sigma0_eq_zero",
            "th2Sigma1MinusId_eq_zero",
            "thxySigma0_eq_zero",
            "thxySigma1MinusId_eq_zero",
            "degree_subtraction_eq_494",
            "degree_494_ne_zero",
            "certificate_degree_eq",
        )
        for name in names:
            self.assertRegex(text, rf"(?m)^theorem {re.escape(name)}\b")

    def test_mutant_fixture_set_and_named_failure_theorems(self) -> None:
        expected = {
            "transpose_mutant.lean": "transposeMutant_rowMajorEntry_should_fail",
            "entry_mutant.lean": "entryMutant_det_should_fail",
            "det_implementation_mutant.lean": "detImplementationMutant_should_fail",
            "value_mutant.lean": "valueMutant_h3_should_fail",
            "degree_mutant.lean": "degreeMutant_494_should_fail",
        }
        actual = {path.name for path in self.fixture_dir.glob("*.lean")}
        self.assertEqual(actual, set(expected))
        for filename, theorem in expected.items():
            text = (self.fixture_dir / filename).read_text(encoding="utf-8")
            self.assertRegex(text, rf"(?m)^theorem {re.escape(theorem)}\b")
            self.assertNotIn("Task5", text)
            self.assertNotIn("sync mutant", text.lower())

    def test_mutants_change_the_intended_axis(self) -> None:
        transpose = (self.fixture_dir / "transpose_mutant.lean").read_text(
            encoding="utf-8"
        )
        entry = (self.fixture_dir / "entry_mutant.lean").read_text(encoding="utf-8")
        determinant = (
            self.fixture_dir / "det_implementation_mutant.lean"
        ).read_text(encoding="utf-8")
        value = (self.fixture_dir / "value_mutant.lean").read_text(encoding="utf-8")
        degree = (self.fixture_dir / "degree_mutant.lean").read_text(encoding="utf-8")
        self.assertIn("[[0, 0, 1], [269, 41, 0], [1240, 189, 32]]", transpose)
        self.assertIn("[[0, 269, 1241]", entry)
        self.assertIn("+ b * (d * i - f * g)", determinant)
        self.assertIn("-59071", value)
        self.assertIn("[0, 493]", degree)


if __name__ == "__main__":
    unittest.main()
