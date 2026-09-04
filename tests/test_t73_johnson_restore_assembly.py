from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_restore_assembly.py"
    spec = importlib.util.spec_from_file_location("restore_assembly", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonRestoreAssemblyTest(unittest.TestCase):
    def test_restore_is_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_restore_assembly.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(rebuilt["johnson_arm_restore"], "PASS")
        self.assertEqual(rebuilt["paired_saddle_ambient_cells"], "PASS")
        self.assertEqual(rebuilt["heegaard_preserving_unit_generators"], "PASS")
        self.assertTrue(rebuilt["all_movies_map_both_owners_setwise"])
        self.assertTrue(rebuilt["all_movies_fix_protected_ball"])
        self.assertTrue(rebuilt["all_restores_isotopic_to_identity"])
        self.assertTrue(rebuilt["all_inverses_explicit"])
        self.assertEqual(rebuilt["mutation_side_bit"], "FAIL")
        full = rebuilt["full_93_factor_assembly"]
        self.assertEqual(full["status"], "PASS")
        self.assertEqual(full["factor_count"], 93)
        self.assertEqual(full["product_on_H1"], full["matrix_A"])
        self.assertTrue(full["psi_star_equals_A"])
        self.assertTrue(full["all_factors_map_both_owners_setwise"])
        self.assertTrue(full["all_factors_fix_protected_ball"])
        self.assertTrue(full["all_factor_inverses_explicit"])
        self.assertEqual(full["expanded_ambient_cell_count"], 8113517822)


if __name__ == "__main__":
    unittest.main()
