import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SCRIPT = SCRIPTS / "build_t73_x_m1_stub_ribbon_cross_band_verification_receipt.py"


class StubRibbonCrossBandVerificationTest(unittest.TestCase):
    def test_saved_full_verification_bindings(self):
        sys.path.insert(0, str(SCRIPTS))
        try:
            spec = importlib.util.spec_from_file_location("receipt", SCRIPT)
            assert spec and spec.loader
            receipt_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(receipt_module)
            receipt = receipt_module.check_files(
                __import__("json").loads(receipt_module.OUTPUT.read_text())
            )
        finally:
            sys.path.remove(str(SCRIPTS))
        self.assertEqual(
            receipt["result"]["verdict"],
            "PASS_X_M1_STUB_RIBBON_CROSS_BAND_CLEARANCE",
        )
        self.assertEqual(receipt["result"]["minimum_clearance_in_ribbon_widths"], "100000")
        self.assertEqual(receipt["status"], "PASS_FULL_EXACT_AND_ERROR_BOUNDED_VERIFICATION")


if __name__ == "__main__":
    unittest.main()
