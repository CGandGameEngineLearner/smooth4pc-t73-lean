from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "audit/t73_m1_parallel_annulus_tubular_clearance_receipt.json"
FRAME = ROOT / "geometry/t73_m1_parallel_annulus_tubular_frame.json"


class M1TubularClearanceReceiptTest(unittest.TestCase):
    def test_full_clearance_receipt(self):
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8")); frame = json.loads(FRAME.read_text(encoding="utf-8"))
        verifier = ROOT / receipt["verifier_path"]
        self.assertEqual(receipt["tubular_frame_sha256"], frame["sha256"])
        self.assertEqual(receipt["verifier_sha256"], hashlib.sha256(verifier.read_bytes()).hexdigest().upper())
        self.assertEqual(receipt["verdict"], "PASS_M1_PARALLEL_ANNULUS_NONINCIDENT_TETRAHEDRON_CLEARANCE")
        self.assertEqual(receipt["full_verifier_result"]["exact_convex_feasibility_checks"], 573)
        self.assertTrue(receipt["full_verifier_result"]["embedded_tubular_neighborhood"])


if __name__ == "__main__": unittest.main()
