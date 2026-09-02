from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class GammaThreeMagnusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parents[1]
        script = repo / "scripts" / "verify_t73_gamma3_magnus.py"
        spec = importlib.util.spec_from_file_location("gamma3", script)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import Gamma3 verifier")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_exact_magnus_expansion_is_identity_through_degree_three(self) -> None:
        receipt = self.module.verify()
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertEqual(
            receipt["nonidentity_coefficients"],
            {"linear": 0, "quadratic": 0, "cubic": 0},
        )
        self.assertLessEqual(receipt["maximum_intermediate_absolute_coefficient"], 4)

    def test_deleted_letter_has_nontrivial_permutation(self) -> None:
        word = self.module.public_word()[:-1]
        permutation = list(range(self.module.DIMENSION))
        for letter in word:
            index = abs(letter) - 1
            permutation[index], permutation[index + 1] = (
                permutation[index + 1],
                permutation[index],
            )
        self.assertNotEqual(permutation, list(range(self.module.DIMENSION)))


if __name__ == "__main__":
    unittest.main()
