import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_regina_boundary_recognition.json"
BUILDER = ROOT / "scripts/build_t73_x_m1_regina_boundary_recognition.py"
VERIFIER = ROOT / "scripts/verify_t73_x_m1_regina_boundary_recognition.py"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


class ReginaBoundaryRecognitionTest(unittest.TestCase):
    def test_saved_full_recognition(self):
        data = json.loads(DATA.read_text())
        unsigned = {key: value for key, value in data.items() if key != "sha256"}
        self.assertEqual(data["sha256"], canonical_sha256(unsigned))
        self.assertEqual(data["regina_version"], "7.4")
        self.assertEqual(data["support_prime_summands"][0]["iso_sig"], "cMcabbjaj")
        self.assertTrue(data["support_prime_isomorphic_to_reference_s2xs1"])
        self.assertEqual(data["standard_boundary"]["simplified_iso_sig"], "bkaagj")
        self.assertTrue(data["standard_boundary"]["is_sphere"])
        self.assertTrue(BUILDER.is_file() and VERIFIER.is_file())


if __name__ == "__main__":
    unittest.main()
