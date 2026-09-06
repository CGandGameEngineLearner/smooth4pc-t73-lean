import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_kirby_homology_admissible_correction.py"


class KirbyHomologyAdmissibleCorrectionTest(unittest.TestCase):
    def test_unique_diagonal_correction(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_UNIQUE_HOMOLOGY_ADMISSIBLE_DIAGONAL_CORRECTION",
        )
        self.assertEqual(result["required_framing_corrections"], {
            "r_xy": 1,
            "r_yz": 1,
            "r_zx": 3,
        })
        self.assertEqual(result["smith_diagonal"], [1, 1, 1, 1, 0, 0, 0])
        self.assertEqual(result["geometric_realization"], "OPEN")


if __name__ == "__main__":
    unittest.main()
