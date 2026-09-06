import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_band_global_r3_port_strips.py"


class XBandGlobalR3PortStripsTest(unittest.TestCase):
    def test_full_construction(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify(check_cache_sha=False)
        self.assertEqual(
            result["verdict"],
            "PASS_X_BAND_GLOBAL_R3_PORT_STRIPS_FULL_CONSTRUCTION",
        )
        self.assertEqual(result["fixed_shell_ports"], 6052)
        self.assertEqual(result["strip_triangles"], 15130)
        self.assertTrue(result["centerlines_globally_disjoint"])
        self.assertEqual(result["strip_global_clearance"], "OPEN")


if __name__ == "__main__":
    unittest.main()
