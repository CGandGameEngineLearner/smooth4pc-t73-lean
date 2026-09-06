import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_band_global_r3_push_disks.py"


class XBandGlobalR3PushDisksTest(unittest.TestCase):
    def test_full_local_product(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify(check_cache_sha=False)
        self.assertEqual(
            result["verdict"],
            "PASS_X_BAND_GLOBAL_R3_PUSH_DISKS_FULL_LOCAL_PRODUCT",
        )
        self.assertEqual(result["surface_product_tetrahedra"], 45390)
        self.assertEqual(result["lane_framing_ribbon_triangles"], 30260)
        self.assertEqual(result["global_push_disk_clearance"], "OPEN")


if __name__ == "__main__":
    unittest.main()
