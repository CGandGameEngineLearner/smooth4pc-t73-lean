import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_band_global_r3_lane_push_clearance.json"
VERIFIER = ROOT / "scripts/verify_t73_x_band_global_r3_lane_push_clearance.py"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


class XBandGlobalR3LanePushClearanceTest(unittest.TestCase):
    def test_full_clearance_receipt(self):
        data = json.loads(DATA.read_text())
        unsigned = {key: value for key, value in data.items() if key != "sha256"}
        self.assertEqual(data["sha256"], canonical_sha256(unsigned))
        self.assertEqual(
            data["verifier_sha256"],
            hashlib.sha256(VERIFIER.read_bytes()).hexdigest().upper(),
        )
        result = data["full_result"]
        self.assertEqual(
            result["verdict"],
            "PASS_X_BAND_GLOBAL_R3_LANE_PUSH_AND_RIBBON_CLEARANCE",
        )
        self.assertEqual(result["lane_core_push_exact_segment_checks"], 19673)
        self.assertEqual(result["within_lane_ribbon_exact_triangle_checks"], 27245)
        self.assertEqual(result["ribbon_segment_exact_checks"], 87033)
        self.assertTrue(result["globally_embedded_band_lane_push_paths_and_ribbons"])
        self.assertEqual(result["endpoint_push_gluing"], "OPEN")


if __name__ == "__main__":
    unittest.main()
