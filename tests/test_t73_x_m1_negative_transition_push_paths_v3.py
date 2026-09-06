import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_x_m1_negative_transition_push_paths_v3_verification.py"


class NegativeTransitionPushPathsV3Test(unittest.TestCase):
    def test_saved_full_verification(self):
        spec = importlib.util.spec_from_file_location("verification", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        result = receipt["full_result"]
        self.assertEqual(result["transitions"], 3026)
        self.assertEqual(result["ribbon_triangles"], 36312)
        self.assertEqual(result["endpoint_push_port_matches"], 6052)
        self.assertEqual(result["relative_twist_sum"], 0)
        self.assertEqual(result["global_clearance"], "OPEN")


if __name__ == "__main__":
    unittest.main()
