from __future__ import annotations

import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_paired_saddle_support.py"
    spec = importlib.util.spec_from_file_location("paired_saddle_support", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonPairedSaddleSupportTest(unittest.TestCase):
    def test_supports_are_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_paired_saddle_support.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(rebuilt["paired_saddle_support"], "PASS")
        self.assertEqual(rebuilt["paired_saddle_ambient_cells"], "OPEN")
        for movie in rebuilt["movies"]:
            self.assertEqual(movie["paired_saddle_support"], "PASS")
            self.assertTrue(movie["support_collapses_to_point"])
            self.assertEqual(movie["support_boundary"]["topology"], "sphere")
            self.assertEqual(movie["source_patch"]["total_genus"], 0)
            self.assertEqual(movie["target_patch"]["total_genus"], 0)
            self.assertTrue(movie["boundary_curves_equal"])
            self.assertTrue(movie["outer_boundary_membership_agrees"])
            self.assertGreater(
                Fraction(movie["protected_ball_bbox_clearance"]),
                Fraction(1, 196104),
            )


if __name__ == "__main__":
    unittest.main()
