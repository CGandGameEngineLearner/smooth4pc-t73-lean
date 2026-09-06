import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts/build_t73_x_m1_outer_collar_v7_replacement_ribbon_candidate_matrix.py"
)


class OuterCollarV7ReplacementRibbonMatrixTest(unittest.TestCase):
    def test_complete_cross_matrix_and_target_stars(self):
        spec = importlib.util.spec_from_file_location("matrix", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.build()
        self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["collar_rectangle_count"], 18156)
        self.assertEqual(result["replacement_rectangle_count"], 92284)
        self.assertEqual(result["expanded_3d_aabb_pair_count"], 19_224_171)
        self.assertEqual(result["intended_target_framing_edge_adjacency_count"], 3026)
        self.assertEqual(
            result["target_framing_edge_star_relation_counts"],
            {"TRANSVERSE_PLANES": 3026},
        )
        self.assertEqual(result["nonincident_candidate_count"], 19_221_145)
        self.assertEqual(
            result["aabb_and_functional_interval_candidate_count"], 4_809_221
        )
        self.assertEqual(
            result["clearance_status"],
            "OPEN_APPLY_EXACT_FUNCTIONAL_INTERVAL_BOUNDS_AND_TRIANGLE_CHECKS",
        )


if __name__ == "__main__":
    unittest.main()
