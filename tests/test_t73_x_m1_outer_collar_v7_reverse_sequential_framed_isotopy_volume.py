import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts/build_t73_x_m1_outer_collar_v7_reverse_sequential_framed_isotopy_volume_verification.py"
)


class OuterCollarV7ReverseSequentialFramedVolumeTest(unittest.TestCase):
    def test_saved_reverse_volume_replay(self):
        spec = importlib.util.spec_from_file_location("receipt", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        result = receipt["full_result"]
        self.assertEqual(result["schedule_first_interface"], 3025)
        self.assertEqual(result["schedule_last_interface"], 0)
        self.assertEqual(result["triangular_prisms_reconstructed"], 121020)
        self.assertEqual(result["r4_tetrahedra"], 363060)
        self.assertEqual(result["r4_rank_checks"], 363060)
        self.assertTrue(result["moving_volume_interiors_pairwise_time_disjoint"])
        self.assertEqual(result["reverse_moving_static_volume_clearance"], "OPEN")


if __name__ == "__main__":
    unittest.main()
