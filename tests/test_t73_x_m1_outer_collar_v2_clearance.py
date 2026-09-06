import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_SCRIPT = (
    ROOT / "scripts/build_t73_x_m1_outer_collar_v2_core_push_clearance_verification.py"
)
RIBBON_SCRIPT = ROOT / "scripts/build_t73_x_m1_outer_collar_v2_ribbon_self_clearance.py"


class OuterCollarV2ClearanceTest(unittest.TestCase):
    def test_saved_core_push_pass(self):
        spec = importlib.util.spec_from_file_location("core_receipt", CORE_SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        self.assertEqual(
            receipt["full_result"]["pair_results"]["core/push"]["exact_segment_checks"],
            5_191_079,
        )
        self.assertTrue(receipt["full_result"]["global_core_push_clearance"])

    def test_saved_ribbon_refutation(self):
        spec = importlib.util.spec_from_file_location(
            "ribbon_obstruction", RIBBON_SCRIPT
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        saved = json.loads(module.OUTPUT.read_text())
        self.assertEqual(
            saved["verdict"], "REFUTED_X_M1_OUTER_COLLAR_V2_RIBBON_SELF_CLEARANCE"
        )
        self.assertEqual(saved["collision"]["first_rectangle"], 6051)
        self.assertEqual(saved["collision"]["second_rectangle"], 5411)
        witness = saved["collision"]["witness"]
        self.assertNotEqual(witness["edge_parameter"], "0")
        self.assertNotEqual(witness["edge_parameter"], "1")


if __name__ == "__main__":
    unittest.main()
