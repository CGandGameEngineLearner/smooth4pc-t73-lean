import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SCRIPT = SCRIPTS / "verify_t73_x_m1_stub_core_push_clearance.py"


class StubCorePushClearanceTest(unittest.TestCase):
    def test_direction_class_hash_clearance(self):
        sys.path.insert(0, str(SCRIPTS))
        try:
            spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
            assert spec and spec.loader
            verifier = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(verifier)
            result = verifier.verify()
        finally:
            sys.path.remove(str(SCRIPTS))
        self.assertEqual(result["verdict"], "PASS_X_M1_STUB_CORE_PUSH_CLEARANCE")
        self.assertEqual(result["direction_pairs"], 16)
        self.assertEqual(result["exact_segment_checks"], 1582)
        self.assertEqual(result["intersections"], 0)
        self.assertEqual(result["stub_ribbon_clearance"], "OPEN")


if __name__ == "__main__":
    unittest.main()
