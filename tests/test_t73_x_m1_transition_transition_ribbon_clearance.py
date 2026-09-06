import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_x_m1_transition_transition_ribbon_clearance_verification.py"


class TransitionTransitionRibbonClearanceTest(unittest.TestCase):
    def test_saved_full_gmp_verification(self):
        spec = importlib.util.spec_from_file_location("receipt", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        self.assertEqual(receipt["full_result"]["constant_rectangle_checks"], 5_865_390)
        self.assertEqual(receipt["full_result"]["variable_triangle_checks"], 88)
        self.assertEqual(receipt["full_result"]["intersections"], 0)
        self.assertEqual(receipt["status"], "PASS_FULL_GMP_EXACT_VERIFICATION")


if __name__ == "__main__":
    unittest.main()
