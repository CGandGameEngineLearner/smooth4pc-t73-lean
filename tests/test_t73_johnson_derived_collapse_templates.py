from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_derived_collapse_templates.py"
    spec = importlib.util.spec_from_file_location("derived_collapses", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonDerivedCollapseTemplateTest(unittest.TestCase):
    def test_templates_are_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_derived_collapse_templates.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertTrue(rebuilt["all_derived_stars_are_ball_disk_moves"])
        self.assertEqual(rebuilt["ambient_cell_maps"], "OPEN")
        expected = {1: (96, 36, 60, 6), 2: (216, 156, 60, 30), 3: (576, 396, 180, 12)}
        for template in rebuilt["templates"]:
            dimension = template["collapse_dimension"]
            before, after, difference, boundary_edges = expected[dimension]
            self.assertEqual(template["before_star_tetrahedra"], before)
            self.assertEqual(template["after_star_tetrahedra"], after)
            self.assertEqual(template["difference_tetrahedra"], difference)
            self.assertEqual(template["before_boundary"]["topology"], "sphere")
            self.assertEqual(template["after_boundary"]["topology"], "sphere")
            self.assertEqual(template["before_patch"]["topology"], "disk")
            self.assertEqual(template["after_patch"]["topology"], "disk")
            self.assertEqual(template["before_patch"]["boundary_edge_count"], boundary_edges)
            self.assertEqual(template["after_patch"]["boundary_edge_count"], boundary_edges)
            self.assertTrue(template["before_collapse"]["collapses_to_point"])
            self.assertTrue(template["after_collapse"]["collapses_to_point"])
            self.assertTrue(template["geometric_tetrahedra_nondegenerate"])


if __name__ == "__main__":
    unittest.main()
