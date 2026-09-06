import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_repaired_stub_cross_clearance.py"


class RepairedStubCrossClearanceTest(unittest.TestCase):
    def test_exact_rust_receipt(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(result["verdict"], "PASS_X_M1_REPAIRED_STUB_CROSS_CLEARANCE")
        self.assertTrue(result["old_collision_repaired"])
        self.assertEqual(result["escape_extra_intersections"], 0)
        self.assertEqual(result["skew_modular_survivors"], 0)


if __name__ == "__main__":
    unittest.main()
