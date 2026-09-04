from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_negative_cap_normalization.py"
    spec = importlib.util.spec_from_file_location("cap_normalization", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonNegativeCapNormalizationTest(unittest.TestCase):
    def test_normalization_is_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_negative_cap_normalization.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(
            rebuilt["all_source_disks_normalize_to_remove_caps"], "PASS"
        )
        self.assertEqual(rebuilt["normalization_chart_count"], 4)
        self.assertEqual(rebuilt["expanded_ambient_cell_count"], 16128)
        self.assertEqual(rebuilt["paired_saddle_final_assembly"], "OPEN")
        for movie in rebuilt["movies"]:
            expected = 2 if movie["power"] < 0 else 0
            self.assertEqual(movie["actual_chart_count"], expected)
            self.assertEqual(movie["relative_collapse"]["step_count"], expected)
            self.assertEqual(movie["source_disk_to_remove_cap"], "PASS")
            self.assertTrue(movie["all_actual_charts_positive"])
            self.assertTrue(movie["all_actual_chart_inverses_explicit"])


if __name__ == "__main__":
    unittest.main()
