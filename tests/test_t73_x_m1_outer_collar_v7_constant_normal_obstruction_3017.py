import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "scripts/verify_t73_x_m1_outer_collar_v7_constant_normal_obstruction_3017.py"
)


class OuterCollarV7ConstantNormalObstruction3017Test(unittest.TestCase):
    def test_saved_constant_normal_obstruction(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["states_replayed"], 22)
        self.assertEqual(result["state_core_push_segment_checks"], 550)
        self.assertEqual(result["push_state_self_segment_checks"], 132)
        self.assertEqual(result["push_diagonal_masks_replayed"], 32)
        self.assertEqual(result["invalid_push_diagonal_masks"], 32)
        self.assertEqual(
            result["canonical_collision"],
            {"push_diagonal_mask": 0, "core_triangle": 0, "push_triangle": 2},
        )


if __name__ == "__main__":
    unittest.main()
