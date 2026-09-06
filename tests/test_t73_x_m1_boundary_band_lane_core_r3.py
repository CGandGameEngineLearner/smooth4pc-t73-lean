import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_boundary_band_lane_core_r3.py"


class BoundaryBandLaneCoreR3Test(unittest.TestCase):
    def test_complete_boundary_lane(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_X_M1_BOUNDARY_BAND_LANE_CORE_R3_FULL",
        )
        self.assertEqual(result["mapped_boundary_pieces"], 7)
        self.assertEqual(result["interior_pieces"], 15151)
        self.assertEqual(result["complete_lane"], "band0/positive_band_lane")
        self.assertEqual(result["mapped_push"], "OPEN")


if __name__ == "__main__":
    unittest.main()
