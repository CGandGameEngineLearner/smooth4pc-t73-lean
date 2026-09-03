from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonSixSweepTest(unittest.TestCase):
    def test_ar_side_six_sweeps_equal_public_word(self):
        result = load("derive_t73_johnson_six_sweeps").generate()
        self.assertEqual(result["factor_count"], 252)
        self.assertEqual(result["B44_length"], 11340)
        self.assertTrue(result["relative_endpoint_word_equal"])
        self.assertEqual(result["verdict"], "PASS")

    def test_return_passage_orientation_mutant_changes_word(self):
        collar = load("generate_t73_johnson_ribbon_collar").generate()
        mutant = copy.deepcopy(collar)
        mutant["wickets"][43]["orientation"] = 1
        result = load("derive_t73_johnson_six_sweeps").generate(mutant)
        self.assertFalse(result["relative_endpoint_word_equal"])


if __name__ == "__main__":
    unittest.main()
