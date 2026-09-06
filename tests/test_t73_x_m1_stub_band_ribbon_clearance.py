import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_x_m1_stub_band_ribbon_clearance_verification.py"


class StubBandRibbonClearanceTest(unittest.TestCase):
    def test_saved_full_gmp_receipt(self):
        spec = importlib.util.spec_from_file_location("receipt", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        result = receipt["full_result"]
        self.assertEqual(result["exact_rectangle_checks"], 2_656_225)
        self.assertEqual(
            result["shared_vertex_triangle_incidences"]
            + result["adjacent_rectangle_triangle_incidences"],
            19_673,
        )
        self.assertEqual(result["intersections"], 0)


if __name__ == "__main__":
    unittest.main()
