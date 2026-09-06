import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts/build_t73_x_m1_outer_collar_v7_sequential_isotopy_trace_verification.py"
)


class OuterCollarV7SequentialIsotopyTraceTest(unittest.TestCase):
    def test_saved_full_local_trace_replay(self):
        spec = importlib.util.spec_from_file_location("receipt", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        result = receipt["full_result"]
        self.assertEqual(result["traces_reconstructed"], 3026)
        self.assertEqual(result["complete_core_world_sheet_triangles"], 90770)
        self.assertEqual(result["complete_push_world_sheet_triangles"], 121020)
        self.assertEqual(result["r4_triangle_rank_checks"], 211790)
        self.assertEqual(result["boundary_matches"], 15130)
        self.assertTrue(result["moving_sheet_interiors_pairwise_time_disjoint"])
        self.assertEqual(result["moving_static_clearance"], "OPEN")
        self.assertEqual(result["ambient_support"], "OPEN")


if __name__ == "__main__":
    unittest.main()
