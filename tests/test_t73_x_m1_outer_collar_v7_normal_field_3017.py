import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_outer_collar_v7_normal_field_3017.py"


class OuterCollarV7NormalField3017Test(unittest.TestCase):
    def test_saved_normal_field(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["states_replayed"], 22)
        self.assertEqual(result["transitions_replayed"], 21)
        self.assertEqual(result["framing_transversality_checks"], 110)
        self.assertEqual(result["state_core_push_segment_checks"], 550)
        self.assertEqual(result["push_trace_triangles"], 210)
        self.assertEqual(result["push_trace_self_triangle_checks"], 504)
        self.assertEqual(result["core_push_trace_triangle_checks"], 2100)
        self.assertEqual(result["forbidden_internal_intersections"], 0)
        self.assertEqual(result["static_one_skeleton_clearance"], "OPEN")
        self.assertEqual(result["ribbon_world_volume"], "OPEN")


if __name__ == "__main__":
    unittest.main()
