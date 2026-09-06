import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_standard_pair_boundary_s3.py"


class StandardPairBoundaryS3Test(unittest.TestCase):
    def test_shelling_certificate(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_STANDARD_X_M1_HANDLE_PAIR_BOUNDARY_S3_SHELLING",
        )
        self.assertEqual(result["boundary_tetrahedra"], 26)
        self.assertEqual(result["complement_ball_tetrahedra"], 25)
        self.assertEqual(result["recognized_boundary_type"], "S3")


if __name__ == "__main__":
    unittest.main()
