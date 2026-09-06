import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_negative_global_r3_middle_transition_cores_v3.py"


class NegativeGlobalR3MiddleTransitionCoresV3Test(unittest.TestCase):
    def test_negative_height_routes(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify(check_cache_sha=False)
        self.assertEqual(
            result["verdict"],
            "PASS_X_M1_NEGATIVE_GLOBAL_R3_MIDDLE_TRANSITION_CORES_V3_FULL",
        )
        self.assertEqual(result["core_segments"], 18156)
        self.assertEqual(result["band_cross_clearance"], "OPEN_EXACT_SHELL_ESCAPE_AND_SKEW_SEGMENTS")
        self.assertEqual(result["push_transitions"], "OPEN")


if __name__ == "__main__":
    unittest.main()
