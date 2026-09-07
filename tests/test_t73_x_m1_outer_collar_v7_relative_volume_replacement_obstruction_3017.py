import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts/verify_t73_x_m1_outer_collar_v7_relative_volume_replacement_obstruction_3017.py"
)


class RelativeVolumeReplacementObstruction3017Test(unittest.TestCase):
    def test_saved_replacement_obstruction(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["transition_index"], 11)
        self.assertEqual(result["moving_tetrahedron_index"], 26)
        self.assertEqual(result["replacement_rectangle_index"], 67225)
        self.assertEqual(result["replacement_band"], 1102)
        self.assertEqual(result["replacement_segment"], 4)
        self.assertEqual(result["shared_vertices"], 0)
        self.assertTrue(result["intersection_point_replayed"])
        self.assertEqual(
            result["retained_external_volume"],
            "PROBE_PASS_592_EXACT_CANDIDATES_NOT_RECEIPTED",
        )
        self.assertEqual(result["replacement_external_volume"], "CANDIDATE_REFUTED")


if __name__ == "__main__":
    unittest.main()
