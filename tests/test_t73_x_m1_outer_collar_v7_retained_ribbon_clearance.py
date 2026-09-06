import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_SCRIPT = (
    ROOT / "scripts/build_t73_x_m1_outer_collar_v7_retained_ribbon_candidate_matrix.py"
)
RECEIPT_SCRIPT = (
    ROOT
    / "scripts/build_t73_x_m1_outer_collar_v7_retained_ribbon_clearance_verification.py"
)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OuterCollarV7RetainedRibbonClearanceTest(unittest.TestCase):
    def test_retained_inventory_and_matrix(self):
        module = load(MATRIX_SCRIPT, "matrix")
        result = module.build()
        self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["removed_terminal_segment_count"], 3026)
        self.assertEqual(result["retained_rectangle_count"], 4630)
        self.assertEqual(result["source_framing_edge_adjacency_count"], 3018)
        self.assertEqual(
            result["source_framing_edge_star_relation_counts"],
            {"TRANSVERSE_PLANES": 3018},
        )
        self.assertEqual(result["nonincident_candidate_count"], 1_651_086)
        self.assertEqual(result["aabb_and_functional_interval_candidate_count"], 825896)

    def test_saved_full_exact_clearance(self):
        module = load(RECEIPT_SCRIPT, "receipt")
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        result = receipt["full_result"]
        self.assertEqual(result["aabb_and_float_outward_f_candidates"], 825896)
        self.assertEqual(result["exact_skew_axis_rejects"], 825896)
        self.assertEqual(result["intersection_count"], 0)
        self.assertTrue(result["global_retained_cross_clearance"])


if __name__ == "__main__":
    unittest.main()
