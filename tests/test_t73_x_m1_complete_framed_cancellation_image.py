from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_complete_framed_cancellation_image.py"
class XM1CompleteFramedCancellationImageTest(unittest.TestCase):
    def test_complete_atlas_cycles(self):
        spec = importlib.util.spec_from_file_location("verify_complete_x", SCRIPT); assert spec and spec.loader
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); result = module.verify()
        self.assertEqual(result["verdict"], "PASS_COMPLETE_X_M1_FRAMED_CANCELLATION_IMAGE_IN_ATLAS")
        self.assertEqual(result["target_core_segments"], 81812)
        self.assertEqual(result["single_affine_s3_chart_status"], "OPEN")
if __name__ == "__main__": unittest.main()
