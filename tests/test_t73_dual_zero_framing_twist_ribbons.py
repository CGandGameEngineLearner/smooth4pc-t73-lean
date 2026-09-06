import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_dual_zero_framing_twist_ribbons.py"


class DualZeroFramingTwistRibbonsTest(unittest.TestCase):
    def test_local_pl_twists_and_exact_self_linkings(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_DUAL_ZERO_FRAMING_LOCAL_PL_TWIST_RIBBONS",
        )
        self.assertEqual(result["integer_self_linkings"], {
            "r_xy": 0,
            "r_yz": 0,
            "r_zx": 0,
        })
        self.assertEqual(result["ribbon_triangles"], 40)
        self.assertEqual(result["global_clearance"], "OPEN")


if __name__ == "__main__":
    unittest.main()
