from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_ball_shrinks.py"
    spec = importlib.util.spec_from_file_location("ball_shrinks", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonBallShrinkTest(unittest.TestCase):
    def test_radial_shrinks_are_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_ball_shrinks.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(rebuilt["fixed_boundary_radial_shrinks"], "PASS")
        self.assertEqual(rebuilt["ball_exchange_status"], "OPEN")
        for template in rebuilt["templates"]:
            self.assertEqual(len(template["components"]), 6)
            self.assertTrue(template["all_outer_boundaries_fixed"])
            self.assertTrue(template["all_jacobians_positive"])


if __name__ == "__main__":
    unittest.main()
