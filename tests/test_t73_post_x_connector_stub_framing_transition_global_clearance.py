import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "audit/t73_post_x_connector_stub_framing_transition_global_clearance.json"
CONSTRUCTION = ROOT / "audit/t73_post_x_connector_stub_framing_transitions_receipt.json"
VERIFIER = ROOT / "scripts/verify_t73_post_x_connector_stub_framing_transition_global_clearance.py"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


class ConnectorStubTransitionGlobalClearanceTest(unittest.TestCase):
    def test_full_receipt(self):
        receipt = json.loads(RECEIPT.read_text())
        construction = json.loads(CONSTRUCTION.read_text())
        unsigned = {key: value for key, value in receipt.items() if key != "sha256"}
        self.assertEqual(receipt["sha256"], canonical_sha256(unsigned))
        self.assertEqual(receipt["construction_receipt_sha256"], construction["sha256"])
        self.assertEqual(receipt["transition_cache_sha256"], construction["cache_sha256"])
        self.assertEqual(
            receipt["verifier_sha256"],
            hashlib.sha256(VERIFIER.read_bytes()).hexdigest().upper(),
        )
        result = receipt["full_result"]
        self.assertEqual(
            result["verdict"],
            "PASS_POST_X_CONNECTOR_STUB_FRAMING_TRANSITION_GLOBAL_CLEARANCE",
        )
        self.assertEqual(result["replaced_base_product_segments"], 3026)
        self.assertTrue(result["globally_embedded_corrected_product_ribbons"])


if __name__ == "__main__":
    unittest.main()
