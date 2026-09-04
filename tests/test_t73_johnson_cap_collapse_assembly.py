from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_cap_collapse_assembly.py"
    spec = importlib.util.spec_from_file_location("cap_assembly", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonCapCollapseAssemblyTest(unittest.TestCase):
    def test_assembly_is_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_cap_collapse_assembly.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(rebuilt["all_fiber_transports"], "PASS")
        self.assertEqual(rebuilt["paired_saddle_fiber_transport"], "PASS")
        self.assertEqual(rebuilt["paired_saddle_ambient_cells"], "OPEN")
        self.assertEqual(rebuilt["johnson_restore_ambient_cells"], "OPEN")
        self.assertEqual(rebuilt["expanded_ambient_cell_count"], 330882192)
        for movie in rebuilt["movies"]:
            self.assertEqual(movie["fiber_transport"], "PASS")
            self.assertEqual(movie["paired_saddle_fiber_cells"], "PASS")
            self.assertEqual(movie["paired_saddle_ambient_cells"], "OPEN")
            self.assertEqual(movie["jacobian_det_min"], "1/3")
            self.assertEqual(movie["jacobian_det_max"], "3")
            for cap_name in ("source_cap_collapse", "target_cap_collapse"):
                cap = movie[cap_name]
                self.assertEqual(cap["cap_collapse_chart"], "PASS")
                self.assertTrue(cap["all_charts_positive"])
                self.assertTrue(cap["all_chart_inverses_explicit"])


if __name__ == "__main__":
    unittest.main()
