import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts/build_t73_x_m1_outer_collar_v7_reverse_dynamic_core_candidate_matrix.py"
)


class OuterCollarV7ReverseDynamicCoreMatrixTest(unittest.TestCase):
    def test_saved_complete_candidate_matrix(self):
        spec = importlib.util.spec_from_file_location("matrix", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.check_saved(json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["active_phase_one_core_triangle_count"], 30260)
        self.assertEqual(result["source_vertical_core_triangle_count"], 6052)
        self.assertEqual(result["final_vertical_core_triangle_count"], 36312)
        self.assertEqual(result["source_candidate_count"], 18403145)
        self.assertEqual(result["final_candidate_count"], 26507429)
        self.assertEqual(result["total_candidate_count"], 44910574)
        self.assertEqual(result["nonempty_semantic_type_pair_count"], 14)
        self.assertEqual(result["classification"], "CANDIDATE_MATRIX_ONLY")


if __name__ == "__main__":
    unittest.main()
