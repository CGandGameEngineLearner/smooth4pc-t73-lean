import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_homology_admissible_affine_framed_model.py"


class HomologyAdmissibleAffineFramedModelTest(unittest.TestCase):
    def test_exact_matrix_and_scope(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_HOMOLOGY_ADMISSIBLE_AFFINE_FRAMED_MODEL_ONLY",
        )
        self.assertEqual(result["smith_diagonal"], [1, 1, 1, 1, 0, 0, 0])
        self.assertEqual(result["boundary_h1"], "Z^3")
        self.assertEqual(result["actual_t73_relative_equivalence"], "OPEN")


if __name__ == "__main__":
    unittest.main()
