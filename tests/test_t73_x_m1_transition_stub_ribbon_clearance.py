import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_x_m1_transition_stub_ribbon_clearance_verification.py"


class TransitionStubRibbonClearanceTest(unittest.TestCase):
    def test_saved_gmp_receipt(self):
        spec = importlib.util.spec_from_file_location("receipt", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        self.assertEqual(receipt["full_result"]["exact_rectangle_checks"], 2_287_656)
        self.assertEqual(receipt["full_result"]["intersections"], 0)


if __name__ == "__main__":
    unittest.main()
