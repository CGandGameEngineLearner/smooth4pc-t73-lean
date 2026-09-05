from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "audit/t73_m1_parallel_annulus_ambient_ejection_receipt.json"
DATA = ROOT / "geometry/t73_m1_parallel_annulus_ambient_ejection.json"


class M1AmbientEjectionReceiptTest(unittest.TestCase):
    def test_full_support_clearance_receipt(self):
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8")); data = json.loads(DATA.read_text(encoding="utf-8")); verifier = ROOT / receipt["verifier_path"]
        self.assertEqual(receipt["ambient_ejection_sha256"], data["sha256"])
        self.assertEqual(receipt["verifier_sha256"], hashlib.sha256(verifier.read_bytes()).hexdigest().upper())
        self.assertEqual(receipt["verdict"], "PASS_M1_PARALLEL_ANNULUS_AMBIENT_EJECTION_SUPPORT_CLEARANCE")
        self.assertEqual(receipt["full_verifier_result"]["exact_convex_feasibility_checks"], 2100)
        self.assertTrue(receipt["full_verifier_result"]["compactly_supported_ambient_homeomorphism"])


if __name__ == "__main__": unittest.main()
