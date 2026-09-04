from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_relative_side_collapses.py"
    spec = importlib.util.spec_from_file_location("side_collapses", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonRelativeSideCollapseTest(unittest.TestCase):
    def test_relative_collapses_are_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_relative_side_collapses.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(rebuilt["side_ball_count"], 16)
        self.assertTrue(rebuilt["all_side_balls_collapse_relative_to_disk"])
        self.assertEqual(rebuilt["derived_star_chart_cells"], "OPEN")
        for movie in rebuilt["movies"]:
            self.assertTrue(movie["all_four_side_collapses"])
            for state in movie["states"]:
                self.assertTrue(state["both_sides_collapse_to_disk"])
                for side in state["sides"]:
                    collapse = side["collapse"]
                    self.assertEqual(collapse["relative_collapse_status"], "PASS")
                    self.assertEqual(
                        collapse["remaining_simplex_counts"],
                        collapse["protected_simplex_counts"],
                    )
                    self.assertEqual(
                        collapse["remaining_equals_protected_disk_by_dimension"],
                        [True, True, True, True],
                    )


if __name__ == "__main__":
    unittest.main()
