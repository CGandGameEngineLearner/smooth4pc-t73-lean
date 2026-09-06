import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts/verify_t73_x_m1_support_generator_sphere_cut.py"
DATA = ROOT / "geometry/t73_x_m1_support_generator_sphere_cut.json"
REGINA = ROOT / "audit/t73_x_m1_support_generator_sphere_cut_regina_verification.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


class SupportGeneratorSphereCutTest(unittest.TestCase):
    def test_cut_and_regina_receipt(self):
        spec = importlib.util.spec_from_file_location("verifier", VERIFIER)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(result["verdict"], "PASS_X_M1_SUPPORT_GENERATOR_SPHERE_CUT")
        self.assertEqual(result["cut_boundary_spheres"], 2)

        data = json.loads(DATA.read_text())
        regina = json.loads(REGINA.read_text())
        unsigned = {key: value for key, value in regina.items() if key != "sha256"}
        self.assertEqual(regina["sha256"], canonical_sha256(unsigned))
        self.assertEqual(regina["support_generator_sphere_cut_sha256"], data["sha256"])
        self.assertTrue(regina["cut"]["has_two_sphere_boundary_components"])
        self.assertTrue(regina["capped"]["is_sphere"])
        self.assertEqual(regina["capped"]["simplified_iso_sig"], "bkaagj")
        self.assertEqual(regina["cut_recognized_type"], "S2 x I")


if __name__ == "__main__":
    unittest.main()
