import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_SCRIPT = (
    ROOT / "scripts/build_t73_x_m1_framed_outer_interface_collars_v7_verification.py"
)
MATRIX_SCRIPT = (
    ROOT / "scripts/build_t73_x_m1_outer_collar_v7_one_skeleton_candidate_matrices.py"
)
ONE_SKELETON_SCRIPT = (
    ROOT / "scripts/build_t73_x_m1_outer_collar_v7_one_skeleton_clearance.py"
)
RIBBON_MATRIX_SCRIPT = (
    ROOT / "scripts/build_t73_x_m1_outer_collar_v7_ribbon_candidate_matrix.py"
)
RIBBON_SCRIPT = ROOT / "scripts/build_t73_x_m1_outer_collar_v7_ribbon_clearance.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OuterCollarV7GlobalClearanceTest(unittest.TestCase):
    def test_local_receipt(self):
        module = load(LOCAL_SCRIPT, "v7_local")
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        self.assertEqual(receipt["full_result"]["changed_collars"], 2)
        self.assertEqual(
            receipt["full_result"]["historical_collision_exact_rechecks"], 2
        )

    def test_one_skeleton(self):
        matrix_module = load(MATRIX_SCRIPT, "v7_matrices")
        matrix = matrix_module.build()
        self.assertEqual(matrix, json.loads(matrix_module.OUTPUT.read_text()))
        self.assertEqual(matrix["core_candidate_count"], 14_249_037)
        self.assertEqual(matrix["push_candidate_count"], 14_249_037)
        self.assertEqual(matrix["directed_core_push_candidate_count"], 28_516_170)
        clearance_module = load(ONE_SKELETON_SCRIPT, "v7_one_skeleton")
        clearance = clearance_module.build()
        self.assertEqual(clearance, json.loads(clearance_module.OUTPUT.read_text()))
        self.assertTrue(clearance["globally_embedded_one_skeleton"])
        self.assertEqual(clearance["intersection_count"], 0)

    def test_ribbon_clearance(self):
        matrix_module = load(RIBBON_MATRIX_SCRIPT, "v7_ribbon_matrix")
        matrix = matrix_module.build()
        self.assertEqual(matrix, json.loads(matrix_module.OUTPUT.read_text()))
        self.assertEqual(matrix["nonincident_candidate_count"], 14_233_903)
        clearance_module = load(RIBBON_SCRIPT, "v7_ribbon")
        clearance = clearance_module.build()
        self.assertEqual(clearance, json.loads(clearance_module.OUTPUT.read_text()))
        self.assertEqual(clearance["covered_nonincident_type_pair_count"], 8)
        self.assertEqual(clearance["global_functional_interval_overlap_count"], 9_098)
        self.assertEqual(clearance["exact_triangle_pair_check_count"], 48)
        self.assertEqual(clearance["intersection_count"], 0)
        self.assertTrue(clearance["global_ribbon_clearance"])


if __name__ == "__main__":
    unittest.main()
