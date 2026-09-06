import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_x_m1_outer_collar_ribbon_self_clearance.py"


class OuterCollarRibbonSelfObstructionTest(unittest.TestCase):
    def test_v1_exact_overlap_witness(self):
        spec = importlib.util.spec_from_file_location("obstruction", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        saved = json.loads(module.OUTPUT.read_text())
        self.assertEqual(
            saved["verdict"], "REFUTED_X_M1_OUTER_COLLAR_RIBBON_SELF_CLEARANCE"
        )
        self.assertEqual(saved["collision"]["first_interface"], 3024)
        self.assertEqual(saved["collision"]["second_interface"], 3023)
        self.assertTrue(saved["collision"]["witness_is_off_shared_inner_edge"])
        self.assertTrue(saved["collision"]["witness_in_both_second_triangles"])


if __name__ == "__main__":
    unittest.main()
