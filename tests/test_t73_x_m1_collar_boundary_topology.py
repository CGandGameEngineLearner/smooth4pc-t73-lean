import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_collar_boundary_topology.py"


class XM1CollarBoundaryTopologyTest(unittest.TestCase):
    def test_support_boundary_is_not_ambient_boundary(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_X_M1_COLLAR_SUPPORT_BOUNDARY_TOPOLOGY_AUDIT",
        )
        self.assertEqual(result["betti_numbers_over_Q"], [1, 1, 1, 1])
        self.assertEqual(result["interior_lane_core_point_occurrences"], 24252)
        self.assertFalse(result["product_support_is_ambient_boundary"])


if __name__ == "__main__":
    unittest.main()
