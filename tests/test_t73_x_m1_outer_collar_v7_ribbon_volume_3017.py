import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_outer_collar_v7_ribbon_volume_3017.py"


class OuterCollarV7RibbonVolume3017Test(unittest.TestCase):
    def test_saved_local_ribbon_volume(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["states_replayed"], 22)
        self.assertEqual(result["state_ribbon_triangles"], 220)
        self.assertEqual(result["state_nonincident_triangle_checks"], 528)
        self.assertEqual(result["transitions_replayed"], 21)
        self.assertEqual(result["r4_tetrahedra"], 630)
        self.assertEqual(result["boundary_triangles"], 924)
        self.assertEqual(result["endpoint_boundary_triangles"], 84)
        self.assertEqual(result["internal_face_pairs"], 798)
        self.assertEqual(result["r4_volume_self_clearance"], "OPEN")
        self.assertEqual(result["static_ribbon_volume_clearance"], "OPEN")


if __name__ == "__main__":
    unittest.main()
