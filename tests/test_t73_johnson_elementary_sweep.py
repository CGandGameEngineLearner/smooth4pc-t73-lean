from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_elementary_sweep.py"
    spec = importlib.util.spec_from_file_location("elementary_sweep", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonElementarySweepTest(unittest.TestCase):
    def test_sweeps_are_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_elementary_sweep.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertTrue(rebuilt["all_movies_reach_target"])
        self.assertEqual(rebuilt["ambient_pl_cell_status"], "OPEN")
        self.assertEqual(len(rebuilt["movies"]), 4)
        for movie in rebuilt["movies"]:
            self.assertTrue(movie["reaches_target_handlebody"])
            self.assertEqual(movie["remaining_after_grouped_moves"], 0)
            self.assertEqual(movie["paired_saddle"]["status"], "PASS")
            self.assertEqual(movie["paired_saddle"]["add_attachment"], "two_disks")
            self.assertEqual(movie["paired_saddle"]["remove_attachment"], "annulus")
            self.assertTrue(
                movie["paired_saddle"]["reaches_target_after_simultaneous_toggle"]
            )
            self.assertEqual(
                movie["paired_saddle"]["final_manifold_invariants"]["boundary_euler"],
                -4,
            )
            self.assertEqual(
                movie["paired_saddle"]["final_manifold_invariants"]["side_face_components"],
                [1, 1],
            )


if __name__ == "__main__":
    unittest.main()
