import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "scripts/build_t73_x_m1_outer_collar_v7_isotopy_trace_v2_verification.py"
)


class OuterCollarV7ComprehensiveIsotopyTraceTest(unittest.TestCase):
    def test_saved_full_local_trace_replay(self):
        spec = importlib.util.spec_from_file_location("receipt", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        result = receipt["full_result"]
        self.assertEqual(result["traces_reconstructed"], 3026)
        self.assertEqual(result["complete_core_trace_triangles"], 60520)
        self.assertEqual(result["complete_push_trace_triangles"], 60520)
        self.assertEqual(result["r4_triangle_rank_checks"], 121040)
        self.assertEqual(result["phase_boundary_core_push_matches"], 6052)
        self.assertEqual(result["spacetime_global_embeddedness"], "OPEN")
        self.assertEqual(result["ambient_support"], "OPEN")


if __name__ == "__main__":
    unittest.main()
