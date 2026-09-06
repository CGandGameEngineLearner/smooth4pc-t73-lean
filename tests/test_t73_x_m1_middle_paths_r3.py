import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts/verify_t73_x_m1_middle_paths_r3.py"
RECEIPT = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
FULL = ROOT / "audit/t73_x_m1_middle_paths_r3_verification.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


class XMiddlePathsR3Test(unittest.TestCase):
    def test_receipts_and_scope(self):
        receipt = json.loads(RECEIPT.read_text())
        full = json.loads(FULL.read_text())
        for value in (receipt, full):
            unsigned = {key: item for key, item in value.items() if key != "sha256"}
            self.assertEqual(value["sha256"], canonical_sha256(unsigned))
        self.assertEqual(full["construction_receipt_sha256"], receipt["sha256"])
        self.assertEqual(
            full["verifier_sha256"],
            hashlib.sha256(VERIFIER.read_bytes()).hexdigest().upper(),
        )
        result = full["full_result"]
        self.assertEqual(result["records_reconstructed"], 1513)
        self.assertEqual(result["core_segments_reconstructed"], 48416)
        self.assertEqual(result["orientation_step_counts"], {"1": 1511, "33": 2})
        self.assertTrue(result["pairwise_disjoint_middle_ribbons"])
        self.assertEqual(len(result["remaining_piece_types"]), 3)

        spec = importlib.util.spec_from_file_location("verifier", VERIFIER)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        _, _, _, checks = verifier.check_receipt()
        self.assertTrue(all(checks.values()))


if __name__ == "__main__":
    unittest.main()
