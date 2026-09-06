import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_global_r3_middle_transition_cores.py"


class GlobalR3MiddleTransitionCoresTest(unittest.TestCase):
    def test_all_transition_cores(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify(check_cache_sha=False)
        self.assertEqual(
            result["verdict"],
            "PASS_X_M1_GLOBAL_R3_MIDDLE_TRANSITION_CORES_FULL",
        )
        self.assertEqual(result["transitions"], 3026)
        self.assertEqual(result["core_segments"], 15130)
        self.assertTrue(result["centerlines_globally_disjoint"])
        self.assertEqual(result["cross_system_clearance"], "OPEN")


if __name__ == "__main__":
    unittest.main()
