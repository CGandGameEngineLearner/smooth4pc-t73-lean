from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_octahedral_halfturn.py"
    spec = importlib.util.spec_from_file_location("octahedral_halfturn", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonOctahedralHalfturnTest(unittest.TestCase):
    def test_halfturn_cells_are_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_octahedral_halfturn.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(rebuilt["ambient_halfturn_template"], "PASS")
        self.assertTrue(rebuilt["all_cells_positive"])
        self.assertTrue(rebuilt["all_outer_boundaries_fixed"])
        self.assertEqual(rebuilt["sweep_placement_status"], "OPEN")
        for side in rebuilt["sides"]:
            self.assertEqual(side["cell_count"], 56)
            self.assertEqual(side["jacobian_det_min"], "1")
            self.assertEqual(side["jacobian_det_max"], "1")
            self.assertTrue(side["explicit_cellwise_inverse"])


if __name__ == "__main__":
    unittest.main()
