from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_derived_collapse_cells.py"
    spec = importlib.util.spec_from_file_location("derived_cells", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonDerivedCollapseCellTest(unittest.TestCase):
    def test_cells_are_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_derived_collapse_cells.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(rebuilt["all_standard_derived_collapse_cells"], "PASS")
        self.assertEqual(rebuilt["actual_collapse_pair_placement"], "OPEN")
        self.assertEqual(
            sum(
                side["ambient_cell_count"]
                for dimension in rebuilt["dimensions"]
                for side in dimension["sides"]
            ),
            34944,
        )
        for dimension in rebuilt["dimensions"]:
            self.assertEqual(dimension["derived_collapse_ambient_cells"], "PASS")
            expected_moves = 168 if dimension["collapse_dimension"] == 3 else 72
            for side in dimension["sides"]:
                self.assertEqual(side["move_count"], expected_moves)
                self.assertEqual(side["jacobian_det_min"], "1/3")
                self.assertEqual(side["jacobian_det_max"], "3")
                self.assertTrue(side["all_intermediate_interfaces_are_disks"])
                self.assertTrue(side["all_cells_positive"])
                self.assertTrue(side["explicit_cellwise_inverses"])
                self.assertEqual(side["initial_interface"]["topology"], "disk")
                self.assertEqual(side["final_interface"]["topology"], "disk")


if __name__ == "__main__":
    unittest.main()
