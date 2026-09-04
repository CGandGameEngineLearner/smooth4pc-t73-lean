from __future__ import annotations

import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_outer_curve_collar.py"
    spec = importlib.util.spec_from_file_location("outer_collar", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonOuterCurveCollarTest(unittest.TestCase):
    def test_outer_collar_is_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_outer_curve_collar.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(rebuilt["all_outer_curve_collars"], "PASS")
        self.assertEqual(rebuilt["outer_paired_support_boundary_extension"], "PASS")
        self.assertEqual(rebuilt["curve_move_count"], 90)
        self.assertEqual(rebuilt["expanded_ambient_cell_count"], 362880)
        self.assertEqual(rebuilt["final_restore_assembly"], "OPEN")
        for movie in rebuilt["movies"]:
            expected = 5 if movie["power"] < 0 else 40
            self.assertEqual(movie["curve_move_count"], expected)
            self.assertEqual(movie["transition_region_triangles"], expected)
            self.assertEqual(movie["outer_curve_collar"], "PASS")
            self.assertTrue(movie["all_intermediate_curves_simple"])
            self.assertTrue(movie["final_curve_equals_target"])
            self.assertTrue(movie["all_actual_charts_positive"])
            self.assertTrue(movie["all_actual_chart_inverses_explicit"])
            self.assertTrue(movie["all_carriers_miss_protected_ball"])
            self.assertGreater(
                Fraction(movie["protected_ball_bbox_clearance_min"]),
                Fraction(1, 196104),
            )
            self.assertGreater(Fraction(movie["chart_determinant_min"]), 0)
            self.assertEqual(movie["conjugated_jacobian_det_min"], "1/3")
            self.assertEqual(movie["conjugated_jacobian_det_max"], "3")


if __name__ == "__main__":
    unittest.main()
