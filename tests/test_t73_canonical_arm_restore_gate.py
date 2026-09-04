from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_t73_canonical_arm_restore.py"
RESTORE = ROOT / "geometry" / "t73_johnson_restore_assembly.json"
SUPPORT = ROOT / "geometry" / "t73_johnson_paired_saddle_support.json"
CAP = ROOT / "geometry" / "t73_johnson_cap_collapse_assembly.json"
OUTER = ROOT / "geometry" / "t73_johnson_outer_curve_collar.json"


class CanonicalArmRestoreGateTest(unittest.TestCase):
    def test_current_assembly_fails_closed(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT)], cwd=ROOT, text=True, capture_output=True
        )
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["verdict"], "OPEN")
        self.assertIn("promotes upstream OPEN to PASS", payload["reason"])
        self.assertIn("simplicial self-map of the complete paired-support boundary sphere", payload["reason"])

    def test_semantic_booleans_are_not_a_witness(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--allow-open"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["verdict"], "OPEN")

    def test_current_artifacts_expose_the_open_promotion(self) -> None:
        restore = json.loads(RESTORE.read_text(encoding="utf-8"))
        support = json.loads(SUPPORT.read_text(encoding="utf-8"))
        cap = json.loads(CAP.read_text(encoding="utf-8"))
        outer = json.loads(OUTER.read_text(encoding="utf-8"))
        self.assertEqual(support["paired_saddle_ambient_cells"], "OPEN")
        self.assertEqual(cap["paired_saddle_ambient_cells"], "OPEN")
        self.assertEqual(cap["johnson_restore_ambient_cells"], "OPEN")
        self.assertEqual(outer["final_restore_assembly"], "OPEN")
        self.assertEqual(restore["paired_saddle_ambient_cells"], "PASS")
        self.assertEqual(restore["johnson_arm_restore"], "PASS")

    @unittest.expectedFailure
    def test_legacy_assembler_must_not_promote_open_geometry(self) -> None:
        """Desired fail-closed invariant; expected to fail on the legacy assembler."""

        path = ROOT / "scripts" / "build_t73_johnson_restore_assembly.py"
        spec = importlib.util.spec_from_file_location("restore_assembler", path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader if spec else None)
        module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        result = module.generate()
        self.assertEqual(
            result["paired_saddle_ambient_cells"],
            "OPEN",
            "assembler must remain OPEN until boundary_halfturn_cells and "
            "ambient_pl_cells are exact coordinate maps",
        )


if __name__ == "__main__":
    unittest.main()
