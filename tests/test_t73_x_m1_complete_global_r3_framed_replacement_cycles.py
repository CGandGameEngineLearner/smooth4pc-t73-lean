import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts/build_t73_x_m1_complete_global_r3_framed_replacement_cycles_verification.py"
)


class CompleteGlobalR3FramedReplacementCyclesTest(unittest.TestCase):
    def test_saved_full_verification(self):
        spec = importlib.util.spec_from_file_location("receipt", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        result = receipt["full_result"]
        self.assertEqual(result["core_push_segments_each"], 92284)
        self.assertEqual(result["ribbon_triangles_reconstructed"], 184568)
        self.assertEqual(result["subsystem_pair_clearance_count"], 10)
        self.assertTrue(result["globally_embedded_complete_framing"])


if __name__ == "__main__":
    unittest.main()
