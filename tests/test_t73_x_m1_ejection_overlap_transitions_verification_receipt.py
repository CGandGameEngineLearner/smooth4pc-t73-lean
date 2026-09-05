from __future__ import annotations
import hashlib, json
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_verification.json"
CONSTRUCTION = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_receipt.json"
class XM1OverlapVerificationReceiptTest(unittest.TestCase):
    def test_full_receipt(self):
        data = json.loads(DATA.read_text(encoding="utf-8")); construction = json.loads(CONSTRUCTION.read_text(encoding="utf-8")); verifier = ROOT / data["verifier_path"]
        self.assertEqual(data["construction_receipt_sha256"], construction["sha256"])
        self.assertEqual(data["verifier_sha256"], hashlib.sha256(verifier.read_bytes()).hexdigest().upper())
        self.assertEqual(data["verdict"], "PASS_X_M1_FRAMED_OVERLAP_TRANSITIONS_FULL")
        self.assertEqual(data["full_verifier_result"]["core_boundary_matches"], 3026)
        self.assertTrue(data["full_verifier_result"]["charted_cycle_continuity"])
if __name__ == "__main__": unittest.main()
