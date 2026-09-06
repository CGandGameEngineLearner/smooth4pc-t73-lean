import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts/verify_t73_dual_zero_framing_twist_global_clearance.py"
RECEIPT = ROOT / "audit/t73_dual_zero_framing_twist_global_clearance.json"
DATA = ROOT / "geometry/t73_dual_zero_framing_twist_ribbons.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


class DualZeroFramingTwistGlobalClearanceTest(unittest.TestCase):
    def test_full_receipt_and_independent_replay(self):
        receipt = json.loads(RECEIPT.read_text())
        data = json.loads(DATA.read_text())
        unsigned = {key: value for key, value in receipt.items() if key != "sha256"}
        self.assertEqual(receipt["sha256"], canonical_sha256(unsigned))
        self.assertEqual(receipt["twist_ribbon_payload_sha256"], data["sha256"])
        self.assertEqual(
            receipt["verifier_sha256"],
            hashlib.sha256(VERIFIER.read_bytes()).hexdigest().upper(),
        )
        spec = importlib.util.spec_from_file_location("clearance_verifier", VERIFIER)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        replay = verifier.verify()
        self.assertEqual(replay, receipt["full_result"])
        self.assertEqual(
            replay["verdict"],
            "PASS_DUAL_ZERO_FRAMING_TWIST_GLOBAL_CLEARANCE",
        )
        self.assertTrue(replay["embedded_and_disjoint_from_retained_model"])


if __name__ == "__main__":
    unittest.main()
