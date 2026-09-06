import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSTRUCTION_VERIFIER = ROOT / "scripts/verify_t73_x_band_global_r3_port_strips.py"
CLEARANCE_VERIFIER = ROOT / "scripts/verify_t73_x_band_global_r3_port_strip_clearance.py"
RECEIPT = ROOT / "audit/t73_x_band_global_r3_port_strip_clearance.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


class XBandGlobalR3PortStripClearanceTest(unittest.TestCase):
    def test_construction_and_clearance_receipt(self):
        spec = importlib.util.spec_from_file_location("construction", CONSTRUCTION_VERIFIER)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        construction = verifier.verify(check_cache_sha=False)
        self.assertTrue(construction["centerlines_globally_disjoint"])

        receipt = json.loads(RECEIPT.read_text())
        unsigned = {key: value for key, value in receipt.items() if key != "sha256"}
        self.assertEqual(receipt["sha256"], canonical_sha256(unsigned))
        self.assertEqual(
            receipt["verifier_sha256"],
            hashlib.sha256(CLEARANCE_VERIFIER.read_bytes()).hexdigest().upper(),
        )
        result = receipt["full_result"]
        self.assertEqual(result["within_band_exact_triangle_checks"], 13622)
        self.assertTrue(result["globally_embedded_port_fixed_band_strips"])
        self.assertEqual(result["push_framing"], "OPEN")


if __name__ == "__main__":
    unittest.main()
