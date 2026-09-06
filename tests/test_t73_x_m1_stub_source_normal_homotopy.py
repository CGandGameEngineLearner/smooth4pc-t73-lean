import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_stub_source_normal_homotopy.py"


class StubSourceNormalHomotopyTest(unittest.TestCase):
    def test_uniform_positive_cone_homotopy(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(result["verdict"], "PASS_X_M1_STUB_SOURCE_NORMAL_HOMOTOPY")
        self.assertEqual(result["stub_segments"], 10582)
        self.assertEqual(result["relative_twist"], 0)
        self.assertTrue(result["uniform_nonvanishing_homotopy"])


if __name__ == "__main__":
    unittest.main()
