import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_x_m1_transition_ribbon_global_clearance.py"


class TransitionRibbonGlobalClearanceTest(unittest.TestCase):
    def test_complete_transition_subsystem(self):
        spec = importlib.util.spec_from_file_location("global_clearance", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.build()
        self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["transition_transition_constant_rectangle_checks"], 5_865_390)
        self.assertEqual(result["transition_stub_rectangle_checks"], 2_287_656)
        self.assertEqual(result["middle_port_segment_triangle_checks"], 193_664)
        self.assertEqual(result["middle_port_permitted_triangle_incidences"], 6_052)
        self.assertEqual(result["intersection_count"], 0)
        self.assertTrue(result["global_transition_ribbon_clearance"])


if __name__ == "__main__":
    unittest.main()
