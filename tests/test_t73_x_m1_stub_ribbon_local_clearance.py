import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SCRIPT = SCRIPTS / "build_t73_x_m1_stub_ribbon_local_clearance.py"


class StubRibbonLocalClearanceTest(unittest.TestCase):
    def test_all_within_band_ribbons(self):
        sys.path.insert(0, str(SCRIPTS))
        try:
            spec = importlib.util.spec_from_file_location("audit", SCRIPT)
            assert spec and spec.loader
            audit = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(audit)
            result = audit.build()
        finally:
            sys.path.remove(str(SCRIPTS))
        self.assertEqual(result["verdict"], "PASS_X_M1_STUB_RIBBON_LOCAL_CLEARANCE")
        self.assertEqual(result["within_band_ribbon_exact_triangle_checks"], 0)
        self.assertEqual(result["within_band_ribbon_segment_exact_checks"], 0)
        self.assertTrue(result["within_band_stub_ribbon_embedding"])
        self.assertEqual(
            result["cross_band_ribbon_clearance_status"],
            "OPEN_PROJECT_TO_DISPLACEMENT_QUOTIENT",
        )


if __name__ == "__main__":
    unittest.main()
