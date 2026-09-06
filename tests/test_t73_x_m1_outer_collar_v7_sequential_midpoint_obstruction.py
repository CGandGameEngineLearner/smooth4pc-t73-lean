import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "scripts/verify_t73_x_m1_outer_collar_v7_sequential_midpoint_obstruction.py"
)


class OuterCollarV7SequentialMidpointObstructionTest(unittest.TestCase):
    def test_saved_midpoint_obstruction(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["active_interface"], 2)
        self.assertEqual(result["obstacle_interface"], 0)
        self.assertEqual(result["global_time"], "9/12104")
        self.assertEqual(result["collision_triangle_pairs"], 3)
        self.assertEqual(result["saved_witnesses_replayed"], 3)
        self.assertEqual(result["sequential_time_schedule"], "RETAINED")
        self.assertEqual(result["linear_spatial_interpolation"], "REFUTED")


if __name__ == "__main__":
    unittest.main()
