from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_fiber_reversal_template.py"
    spec = importlib.util.spec_from_file_location("fiber_reversal", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonFiberReversalTemplateTest(unittest.TestCase):
    def test_template_is_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_fiber_reversal_template.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(rebuilt["standard_fiber_reversal"], "PASS")
        self.assertEqual(rebuilt["actual_regular_neighbourhood_chart"], "OPEN")
        for side in rebuilt["sides"]:
            self.assertEqual(side["source_to_target_disk"], "PASS")
            self.assertEqual(side["disk_triangle_count"], 4)
            self.assertEqual(side["ambient_cell_count"], 56)
            self.assertEqual(side["jacobian_det_min"], "1")
            self.assertEqual(side["jacobian_det_max"], "1")
            self.assertTrue(side["outer_boundary_identity"])
            self.assertTrue(side["explicit_cellwise_inverse"])


if __name__ == "__main__":
    unittest.main()
