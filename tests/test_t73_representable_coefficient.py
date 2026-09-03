from __future__ import annotations

import re
import os
import shutil
import subprocess
from pathlib import Path
import unittest


THEOREMS = (
    "Smooth4PC.LinearHomAutofunctor.symm_comp_map_left",
    "Smooth4PC.LinearHomAutofunctor.symm_comp_map_right",
    "Smooth4PC.LinearHomAutofunctor.rawMap_to_from",
    "Smooth4PC.LinearHomAutofunctor.rawMap_from_to",
    "Smooth4PC.LinearHomAutofunctor.coefficientHH0Equiv_apply_mk",
)


class RepresentableCoefficientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[1]
        cls.module = cls.repo / "Smooth4PC" / "RepresentableCoefficient.lean"
        cls.audit = cls.repo / "T73RepresentableAudit.lean"

    def test_no_hidden_project_declarations(self) -> None:
        source = self.module.read_text(encoding="utf-8")
        for token in ("sorry", "admit", "axiom", "opaque", "unsafe", "extern"):
            self.assertNotRegex(source, rf"\b{token}\b")

    def test_expected_quotient_equivalence_is_present(self) -> None:
        source = self.module.read_text(encoding="utf-8")
        self.assertIn("def coefficientHH0Equiv", source)
        self.assertIn("B.toRegular.cyclicRelation_le_comap", source)
        self.assertIn("B.fromRegular.cyclicRelation_le_comap", source)
        self.assertIn("rawMap_to_from", source)
        self.assertIn("rawMap_from_to", source)

    @unittest.skipUnless(
        os.name != "nt" and shutil.which("lake"),
        "run the Lean audit in the documented WSL environment",
    )
    def test_axiom_audit_compiles(self) -> None:
        result = subprocess.run(
            ["lake", "lean", str(self.audit)],
            cwd=self.repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertNotIn("sorryAx", output)
        reports = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", output)
        self.assertEqual({name for name, _ in reports}, set(THEOREMS))
        allowed = {"propext", "Classical.choice", "Quot.sound"}
        for _, payload in reports:
            names = {name.strip() for name in payload.split(",") if name.strip()}
            self.assertLessEqual(names, allowed)


if __name__ == "__main__":
    unittest.main()
