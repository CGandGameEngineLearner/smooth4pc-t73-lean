from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_verifier():
    path = ROOT / "scripts" / "verify_t73_actual_cut_tangle.py"
    spec = importlib.util.spec_from_file_location("actual_cut_verifier", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ActualCutTangleTest(unittest.TestCase):
    def test_geometry_cut_and_mutation(self):
        result = load_verifier().verify()
        self.assertEqual(result["ACTUAL_CUT_TANGLE"], "PASS")
        self.assertEqual(result["PASSAGES"], 44)
        self.assertEqual(result["LEFTOVER_Z_CIRCLES"], 227)
        self.assertEqual(result["OWNER_COUNTS"], {"r_xy": 2, "m_2": 42})
        self.assertEqual(result["MUTATION_DUPLICATE_PASSAGE"], "FAIL")
        self.assertEqual(result["FROZEN_B44_SOURCE_DEPENDENCY"], "ABSENT")


if __name__ == "__main__":
    unittest.main()
