from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_verifier():
    path = ROOT / "scripts" / "verify_t73_actual_leftover_z_circles.py"
    spec = importlib.util.spec_from_file_location("leftover_verifier", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ActualLeftoverCirclesTest(unittest.TestCase):
    def test_leftover_circles_and_mutation(self):
        result = load_verifier().verify()
        self.assertEqual(result["ACTUAL_LEFTOVER_Z_CIRCLES"], "PASS")
        self.assertEqual(result["CIRCLES"], 227)
        self.assertEqual(result["MUTATION_RELATIVE_TWIST"], "FAIL")


if __name__ == "__main__":
    unittest.main()
