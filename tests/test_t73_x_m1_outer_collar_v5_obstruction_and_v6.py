import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V5_OBSTRUCTION = ROOT / "audit/t73_x_m1_outer_collar_v5_ribbon_clearance.json"
V6_SCRIPT = (
    ROOT / "scripts/build_t73_x_m1_framed_outer_interface_collars_v6_verification.py"
)


class OuterCollarV5ObstructionAndV6Test(unittest.TestCase):
    def test_v5_exact_nonincident_obstruction(self):
        saved = json.loads(V5_OBSTRUCTION.read_text())
        self.assertEqual(
            saved["verdict"], "REFUTED_X_M1_OUTER_COLLAR_V5_RIBBON_CLEARANCE"
        )
        collision = saved["collision"]
        self.assertEqual(collision["first"], [3024, 1, 0])
        self.assertEqual(collision["second"], [3023, 2, 0])
        self.assertNotEqual(collision["witness"]["edge_parameter"], "0")

    def test_v6_saved_full_local_replay(self):
        spec = importlib.util.spec_from_file_location("v6_receipt", V6_SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        result = receipt["full_result"]
        self.assertEqual(result["changed_after_dual_collars"], 4)
        self.assertEqual(result["unchanged_collars"], 3022)
        self.assertEqual(result["local_ribbon_star_checks"], 15134)
        self.assertEqual(result["former_v5_collision_exact_rechecks"], 1)
        self.assertEqual(result["classification"], "CANDIDATE_UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
