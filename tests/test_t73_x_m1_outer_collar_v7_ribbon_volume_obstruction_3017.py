import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "scripts/verify_t73_x_m1_outer_collar_v7_ribbon_volume_obstruction_3017.py"
)


class OuterCollarV7RibbonVolumeObstruction3017Test(unittest.TestCase):
    def test_saved_ribbon_volume_obstruction(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["transition_index"], 7)
        self.assertEqual(result["tetrahedron_indices"], [15, 22])
        self.assertEqual(result["shared_vertices"], 0)
        self.assertTrue(result["intersection_point_replayed"])
        self.assertEqual(result["normal_field"], "RETAINED")
        self.assertEqual(result["framed_one_skeleton"], "RETAINED")
        self.assertEqual(result["ribbon_volume"], "CANDIDATE_REFUTED")


if __name__ == "__main__":
    unittest.main()
