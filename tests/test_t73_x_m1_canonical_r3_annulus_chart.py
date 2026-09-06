import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_canonical_r3_annulus_chart.py"


class CanonicalR3AnnulusChartTest(unittest.TestCase):
    def test_exact_solid_torus(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(result["verdict"], "PASS_X_M1_CANONICAL_R3_SOLID_TORUS_CHART")
        self.assertEqual(result["tetrahedra"], 408)
        self.assertEqual(result["boundary_euler_characteristic"], 0)


if __name__ == "__main__":
    unittest.main()
