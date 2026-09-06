import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_repaired_global_r3_middle_transition_cores.py"


class RepairedGlobalR3MiddleTransitionCoresTest(unittest.TestCase):
    def test_escape_germs_and_routes(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify(check_cache_sha=False)
        self.assertEqual(
            result["verdict"],
            "PASS_X_M1_REPAIRED_GLOBAL_R3_MIDDLE_TRANSITION_CORES_FULL",
        )
        self.assertEqual(result["shell_escape_germs"], 3026)
        self.assertEqual(result["core_segments"], 18156)
        self.assertEqual(result["stub_cross_clearance"], "OPEN_RUST_EXACT_REPLAY")


if __name__ == "__main__":
    unittest.main()
