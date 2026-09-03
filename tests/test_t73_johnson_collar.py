from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class JohnsonCollarTest(unittest.TestCase):
    def test_exact_johnson_word_gives_44_framed_lanes(self):
        path = ROOT / "scripts" / "generate_t73_johnson_ribbon_collar.py"
        spec = importlib.util.spec_from_file_location("johnson_collar", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate()
        self.assertEqual(len(result["wickets"]), 44)
        self.assertEqual(result["owner_counts"], {"r_xy": 2, "m_2": 42})
        self.assertEqual(result["negative_wickets"], [2, 44])
        self.assertTrue(result["pairwise_disjointness_status"].startswith("PASS"))
        self.assertTrue(result["ar_passage_binding_status"].startswith("PASS"))


if __name__ == "__main__":
    unittest.main()
