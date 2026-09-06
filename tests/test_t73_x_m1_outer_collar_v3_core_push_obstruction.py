import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_x_m1_outer_collar_v3_core_push_clearance.py"


class OuterCollarV3CorePushObstructionTest(unittest.TestCase):
    def test_saved_exact_mutual_collision(self):
        spec = importlib.util.spec_from_file_location("obstruction", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        saved = json.loads(module.OUTPUT.read_text())
        self.assertEqual(
            saved["verdict"], "REFUTED_X_M1_OUTER_COLLAR_V3_CORE_PUSH_CLEARANCE"
        )
        self.assertEqual(saved["collision"]["core_interface"], 3022)
        self.assertEqual(saved["collision"]["push_interface"], 3022)
        self.assertEqual(
            saved["collision"]["pair"], "core:last_exterior_ray/push:height_bridge"
        )
        self.assertNotEqual(saved["collision"]["witness"]["core_parameter"], "0")
        self.assertNotEqual(saved["collision"]["witness"]["push_parameter"], "0")


if __name__ == "__main__":
    unittest.main()
