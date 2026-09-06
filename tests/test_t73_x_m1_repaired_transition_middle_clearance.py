import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SCRIPT = SCRIPTS / "verify_t73_x_m1_repaired_transition_middle_clearance.py"


class RepairedTransitionMiddleClearanceTest(unittest.TestCase):
    def test_exact_z_separation(self):
        sys.path.insert(0, str(SCRIPTS))
        try:
            spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
            assert spec and spec.loader
            verifier = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(verifier)
            result = verifier.verify()
        finally:
            sys.path.remove(str(SCRIPTS))
        self.assertEqual(result["verdict"], "PASS_X_M1_REPAIRED_TRANSITION_MIDDLE_CLEARANCE")
        self.assertEqual(result["transition_middle_endpoint_matches"], 3026)
        self.assertEqual(result["extra_intersections"], 0)


if __name__ == "__main__":
    unittest.main()
