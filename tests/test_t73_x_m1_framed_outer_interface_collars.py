import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_x_m1_framed_outer_interface_collars_verification.py"


class FramedOuterInterfaceCollarsTest(unittest.TestCase):
    def test_saved_local_candidate_verification(self):
        spec = importlib.util.spec_from_file_location("receipt", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        result = receipt["full_result"]
        self.assertEqual(result["collars_reconstructed"], 3026)
        self.assertEqual(result["ribbon_triangles_reconstructed"], 6052)
        self.assertEqual(result["classification"], "CANDIDATE_UNVERIFIED")
        self.assertEqual(result["global_clearance"], "OPEN")


if __name__ == "__main__":
    unittest.main()
