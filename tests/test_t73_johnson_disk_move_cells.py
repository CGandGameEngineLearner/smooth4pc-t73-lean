from __future__ import annotations

import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_disk_move_cells.py"
    spec = importlib.util.spec_from_file_location("disk_move_cells", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonDiskMoveCellTest(unittest.TestCase):
    def test_actual_cells_are_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_disk_move_cells.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(rebuilt["disk_move_ambient_cells"], "PASS")
        self.assertEqual(rebuilt["paired_saddle_ambient_cells"], "OPEN")
        self.assertTrue(rebuilt["all_disk_move_cells_positive"])
        self.assertEqual(sum(movie["cell_count"] for movie in rebuilt["movies"]), 122864)
        for movie in rebuilt["movies"]:
            self.assertEqual(movie["jacobian_det_min"], "1/3")
            self.assertEqual(movie["jacobian_det_max"], "3")
            self.assertTrue(movie["all_outer_boundaries_fixed"])
            self.assertTrue(movie["all_supports_miss_protected_ball"])
            self.assertGreater(
                Fraction(movie["protected_ball_bbox_clearance_min"]),
                Fraction(1, 196104),
            )


if __name__ == "__main__":
    unittest.main()
