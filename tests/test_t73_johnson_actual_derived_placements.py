from __future__ import annotations

import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_actual_derived_placements.py"
    spec = importlib.util.spec_from_file_location("actual_placements", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonActualDerivedPlacementTest(unittest.TestCase):
    def test_actual_placements_are_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_actual_derived_placements.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(rebuilt["placement_count"], 2604)
        self.assertEqual(rebuilt["expanded_ambient_cell_count"], 14929152)
        self.assertEqual(rebuilt["actual_collapse_pair_placement"], "PASS")
        self.assertEqual(rebuilt["paired_saddle_side_chart_cells"], "PASS")
        self.assertEqual(rebuilt["paired_saddle_fiber_transport"], "OPEN")
        self.assertEqual(rebuilt["paired_saddle_ambient_cells"], "OPEN")
        self.assertTrue(rebuilt["all_actual_charts_orientation_preserving"])
        self.assertTrue(rebuilt["all_actual_chart_inverses_explicit"])
        self.assertTrue(rebuilt["all_actual_conjugated_cells_positive"])
        self.assertEqual(rebuilt["mutation_chart_orientation"], "FAIL")
        self.assertLess(Fraction(rebuilt["mutant_chart_determinant"]), 0)
        for movie in rebuilt["movies"]:
            for state in movie["states"]:
                for side in state["sides"]:
                    self.assertEqual(side["actual_jacobian_det_min"], "1/3")
                    self.assertEqual(side["actual_jacobian_det_max"], "3")
                    self.assertTrue(side["all_charts_orientation_preserving"])
                    self.assertTrue(side["all_chart_inverses_explicit"])
                    self.assertTrue(side["all_conjugated_cells_positive"])
                    self.assertGreater(
                        Fraction(side["protected_ball_bbox_clearance_min"]),
                        Fraction(1, 196104),
                    )


if __name__ == "__main__":
    unittest.main()
