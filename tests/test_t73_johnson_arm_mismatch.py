from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "analyze_t73_johnson_arm_mismatch.py"
    spec = importlib.util.spec_from_file_location("arm_mismatch", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonArmMismatchTest(unittest.TestCase):
    def test_exact_decomposition_is_live(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_arm_mismatch.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(rebuilt["template_count"], 12)
        self.assertTrue(rebuilt["all_mismatch_pieces_disjoint_from_origin_star"])
        self.assertTrue(rebuilt["all_mismatch_components_are_collapsible_balls"])
        self.assertIn("OPEN", rebuilt["johnson_restore_status"])
        for template in rebuilt["templates"]:
            self.assertGreater(template["piece_count"], 0)
            self.assertEqual(template["origin_star_piece_count"], 0)
            self.assertEqual(template["restore_status"], "OPEN")
            self.assertEqual(len(template["components"]), 6)
            self.assertTrue(
                all(component["boundary_is_sphere"] for component in template["components"])
            )
            self.assertTrue(template["all_components_are_collapsible_balls"])
            self.assertTrue(
                all(component["support_ball_status"] == "PASS" for component in template["components"])
            )


if __name__ == "__main__":
    unittest.main()
