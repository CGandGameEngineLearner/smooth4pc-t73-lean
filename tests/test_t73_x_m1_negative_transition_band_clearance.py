import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_negative_transition_band_clearance.py"


class NegativeTransitionBandClearanceTest(unittest.TestCase):
    def test_exact_separation(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_X_M1_NEGATIVE_TRANSITION_BAND_CORE_CLEARANCE",
        )
        self.assertEqual(result["conservative_xy_candidates"], 0)
        self.assertEqual(result["extra_intersections"], 0)


if __name__ == "__main__":
    unittest.main()
