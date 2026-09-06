import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_stub_r3_push_paths.py"


class StubR3PushPathsTest(unittest.TestCase):
    def test_full_local_paths_and_band_ports(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify(check_cache_sha=False)
        self.assertEqual(result["verdict"], "PASS_X_M1_STUB_R3_PUSH_PATHS_FULL_LOCAL")
        self.assertEqual(result["stub_push_paths"], 6052)
        self.assertEqual(result["ribbon_triangles"], 21164)
        self.assertEqual(result["band_push_port_matches"], 6052)
        self.assertEqual(result["global_stub_push_clearance"], "OPEN")


if __name__ == "__main__":
    unittest.main()
