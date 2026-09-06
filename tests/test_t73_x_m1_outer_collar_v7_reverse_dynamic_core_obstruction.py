import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "scripts/verify_t73_x_m1_outer_collar_v7_reverse_dynamic_core_obstruction.py"
)


class OuterCollarV7ReverseDynamicCoreObstructionTest(unittest.TestCase):
    def test_saved_reverse_dynamic_obstruction(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["active_interface"], 2)
        self.assertEqual(result["source_interface"], 0)
        self.assertEqual(result["intersection_dimension"], 1)
        self.assertEqual(result["intersection_segment_endpoints_checked"], 2)
        self.assertTrue(result["intersection_midpoint_checked"])
        self.assertTrue(result["static_source_segments_disjoint"])
        self.assertEqual(result["forward_order"], "REFUTED")
        self.assertEqual(result["reverse_order"], "REFUTED")
        self.assertEqual(result["sequential_reordering_only"], "REFUTED")


if __name__ == "__main__":
    unittest.main()
