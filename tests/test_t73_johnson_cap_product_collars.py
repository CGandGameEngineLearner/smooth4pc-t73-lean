from __future__ import annotations

import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_cap_product_collars.py"
    spec = importlib.util.spec_from_file_location("cap_collars", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonCapProductCollarTest(unittest.TestCase):
    def test_collars_are_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_cap_product_collars.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(rebuilt["all_cap_product_collars"], "PASS")
        self.assertEqual(rebuilt["all_orientation_mutations"], "FAIL")
        self.assertEqual(rebuilt["cap_collapse_chart_assembly"], "OPEN")
        for movie in rebuilt["movies"]:
            self.assertEqual(movie["cap_product_collar"], "PASS")
            self.assertEqual(movie["mutation_cap_orientation"], "FAIL")
            self.assertEqual(movie["cell_count"], 36)
            self.assertEqual(movie["cap_triangle_count"], 12)
            self.assertTrue(movie["explicit_cellwise_inverse"])
            self.assertGreater(Fraction(movie["jacobian_det_min"]), 0)
            self.assertLess(Fraction(movie["rejected_jacobian_det_max"]), 0)
            expected_orientation = "preserving" if movie["power"] < 0 else "reversing"
            self.assertEqual(movie["selected_cap_orientation"], expected_orientation)


if __name__ == "__main__":
    unittest.main()
