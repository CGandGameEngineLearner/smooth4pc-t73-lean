from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_verifier():
    path = ROOT / "scripts" / "verify_t73_actual_product_rectangles.py"
    spec = importlib.util.spec_from_file_location("actual_rectangles_verifier", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ActualProductRectanglesTest(unittest.TestCase):
    def test_rectangles_and_mutation(self):
        result = load_verifier().verify()
        self.assertEqual(result["ACTUAL_PRODUCT_RECTANGLES"], "PASS")
        self.assertEqual(result["RECTANGLES"], 44)
        self.assertEqual(result["MUTATION_Z_SOURCE"], "FAIL")


if __name__ == "__main__":
    unittest.main()
