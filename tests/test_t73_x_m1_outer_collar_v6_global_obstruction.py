import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_SCRIPT = (
    ROOT / "scripts/build_t73_x_m1_outer_collar_v6_one_skeleton_candidate_matrices.py"
)
ONE_SKELETON_SCRIPT = (
    ROOT / "scripts/build_t73_x_m1_outer_collar_v6_one_skeleton_clearance.py"
)
RIBBON_MATRIX_SCRIPT = (
    ROOT / "scripts/build_t73_x_m1_outer_collar_v6_ribbon_candidate_matrix.py"
)
RIBBON_OBSTRUCTION = ROOT / "audit/t73_x_m1_outer_collar_v6_ribbon_clearance.json"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OuterCollarV6GlobalObstructionTest(unittest.TestCase):
    def test_one_skeleton_matrices_and_clearance(self):
        matrix_module = load(MATRIX_SCRIPT, "v6_matrices")
        matrix = matrix_module.build()
        self.assertEqual(matrix, json.loads(matrix_module.OUTPUT.read_text()))
        self.assertEqual(matrix["core_candidate_count"], 14_249_056)
        self.assertEqual(matrix["push_candidate_count"], 14_249_056)
        self.assertEqual(matrix["directed_core_push_candidate_count"], 28_516_206)
        clearance_module = load(ONE_SKELETON_SCRIPT, "v6_clearance")
        clearance = clearance_module.build()
        self.assertEqual(clearance, json.loads(clearance_module.OUTPUT.read_text()))
        self.assertTrue(clearance["globally_embedded_one_skeleton"])
        self.assertEqual(clearance["intersection_count"], 0)

    def test_ribbon_matrix_and_exact_obstruction(self):
        matrix_module = load(RIBBON_MATRIX_SCRIPT, "v6_ribbon_matrix")
        matrix = matrix_module.build()
        self.assertEqual(matrix, json.loads(matrix_module.OUTPUT.read_text()))
        self.assertEqual(matrix["nonincident_candidate_count"], 14_233_922)
        obstruction = json.loads(RIBBON_OBSTRUCTION.read_text())
        self.assertEqual(
            obstruction["verdict"], "REFUTED_X_M1_OUTER_COLLAR_V6_RIBBON_CLEARANCE"
        )
        self.assertEqual(obstruction["collision"]["first"], [3020, 1, 0])
        self.assertEqual(obstruction["collision"]["second"], [3019, 2, 0])
        self.assertNotEqual(obstruction["collision"]["witness"]["edge_parameter"], "0")


if __name__ == "__main__":
    unittest.main()
