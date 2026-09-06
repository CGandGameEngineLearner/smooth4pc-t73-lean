import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
FULL = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_verification.json"
VERIFIER = ROOT / "scripts/verify_t73_x_m1_splice_stub_cores_r3.py"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


class SpliceStubCoresR3Test(unittest.TestCase):
    def test_full_receipt(self):
        data = json.loads(DATA.read_text())
        full = json.loads(FULL.read_text())
        for value in (data, full):
            unsigned = {key: item for key, item in value.items() if key != "sha256"}
            self.assertEqual(value["sha256"], canonical_sha256(unsigned))
        self.assertEqual(full["construction_receipt_sha256"], data["sha256"])
        self.assertEqual(
            full["verifier_sha256"],
            hashlib.sha256(VERIFIER.read_bytes()).hexdigest().upper(),
        )
        result = full["full_result"]
        self.assertEqual(result["core_pieces_reconstructed"], 10582)
        self.assertEqual(result["continuity_checks"], 4530)
        self.assertTrue(result["cache_sha_checked"])
        self.assertEqual(result["mapped_push"], "OPEN")


if __name__ == "__main__":
    unittest.main()
