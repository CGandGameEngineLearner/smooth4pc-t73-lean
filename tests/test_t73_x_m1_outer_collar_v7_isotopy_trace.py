import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_x_m1_outer_collar_v7_isotopy_trace_verification.py"


class OuterCollarV7IsotopyTraceTest(unittest.TestCase):
    def test_saved_full_local_trace_replay(self):
        spec = importlib.util.spec_from_file_location("receipt", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        result = receipt["full_result"]
        self.assertEqual(result["traces_reconstructed"], 3026)
        self.assertEqual(result["edge_noncollapse_checks"], 15130)
        self.assertEqual(result["core_trace_triangles"], 30260)
        self.assertEqual(result["push_trace_triangles"], 30260)
        self.assertEqual(result["phase_two_push_trace_triangles"], 6052)
        self.assertEqual(result["spacetime_global_embeddedness"], "OPEN")
        self.assertEqual(result["ambient_support"], "OPEN")


if __name__ == "__main__":
    unittest.main()
