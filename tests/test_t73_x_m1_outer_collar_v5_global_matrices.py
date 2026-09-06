import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = {
    "matrices": ROOT
    / "scripts/build_t73_x_m1_outer_collar_v5_one_skeleton_candidate_matrices.py",
    "core": ROOT / "scripts/build_t73_x_m1_outer_collar_v5_core_clearance.py",
    "push": ROOT / "scripts/build_t73_x_m1_outer_collar_v5_push_clearance.py",
    "mutual": ROOT / "scripts/build_t73_x_m1_outer_collar_v5_core_push_clearance.py",
    "ribbon": ROOT
    / "scripts/build_t73_x_m1_outer_collar_v5_ribbon_candidate_matrix.py",
}


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS[name])
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OuterCollarV5GlobalMatricesTest(unittest.TestCase):
    def test_one_skeleton_matrices(self):
        module = load("matrices")
        result = module.build()
        self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["core_candidate_count"], 14_249_042)
        self.assertEqual(result["push_candidate_count"], 14_249_042)
        self.assertEqual(result["directed_core_push_candidate_count"], 28_516_174)

    def test_all_one_skeleton_clearance(self):
        expected = {
            "core": (6_048, "global_core_clearance"),
            "push": (75_610, "global_push_clearance"),
            "mutual": (90_784, "global_core_push_clearance"),
        }
        for name, (checks, field) in expected.items():
            with self.subTest(name=name):
                module = load(name)
                result = module.build()
                self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
                self.assertEqual(result["exact_segment_check_count"], checks)
                self.assertEqual(result["intersection_count"], 0)
                self.assertTrue(result[field])

    def test_ribbon_matrix_and_local_stars(self):
        module = load("ribbon")
        result = module.build()
        self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["rectangle_count"], 18_156)
        self.assertEqual(result["ribbon_triangle_count"], 36_312)
        self.assertEqual(result["local_star_count"], 15_134)
        self.assertEqual(result["nonincident_candidate_count"], 14_233_908)
        self.assertEqual(result["nonempty_nonincident_type_pair_count"], 8)
        self.assertEqual(
            result["clearance_status"], "OPEN_APPLY_EXACT_RULED_RECTANGLE_SEPARATION"
        )


if __name__ == "__main__":
    unittest.main()
