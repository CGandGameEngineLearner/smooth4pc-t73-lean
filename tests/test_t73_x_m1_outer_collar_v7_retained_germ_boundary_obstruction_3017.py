import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts/verify_t73_x_m1_outer_collar_v7_retained_germ_boundary_obstruction_3017.py"
)


class OuterCollarV7RetainedGermBoundaryObstruction3017Test(unittest.TestCase):
    def test_saved_retained_germ_boundary_obstruction(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["retained_rectangle_index"], 4071)
        self.assertEqual(result["matching_states"], 11)
        self.assertEqual(result["mismatching_states"], 11)
        self.assertEqual(result["mismatching_state_indices"], list(range(6, 17)))
        self.assertTrue(result["fixed_core_germ_vertex"])
        self.assertFalse(result["fixed_push_germ_vertex"])
        self.assertEqual(result["normal_field_internal"], "RETAINED")
        self.assertEqual(result["literal_retained_framing_boundary"], "REFUTED")


if __name__ == "__main__":
    unittest.main()
