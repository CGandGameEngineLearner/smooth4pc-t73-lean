from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_t73_canonical_arm_restore.py"


class CanonicalArmRestoreGateTest(unittest.TestCase):
    def test_current_assembly_fails_closed(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT)], cwd=ROOT, text=True, capture_output=True
        )
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["verdict"], "OPEN")
        self.assertIn("not a canonical ArmRestore map witness", payload["reason"])

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


if __name__ == "__main__":
    unittest.main()

