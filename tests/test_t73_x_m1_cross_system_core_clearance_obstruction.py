import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_cross_system_core_clearance_obstruction.py"


class CrossSystemCoreClearanceObstructionTest(unittest.TestCase):
    def test_rust_exact_collision_is_fail_closed(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_EXACT_CROSS_SYSTEM_COLLISION_OBSTRUCTION",
        )
        self.assertEqual(result["stub_band_extra_intersections"], 0)
        self.assertGreaterEqual(result["stub_transition_extra_intersections_at_least"], 1)
        self.assertFalse(result["complete_replacement_core_embedding"])


if __name__ == "__main__":
    unittest.main()
