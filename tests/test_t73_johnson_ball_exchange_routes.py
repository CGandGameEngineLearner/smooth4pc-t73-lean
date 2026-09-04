from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "build_t73_johnson_ball_exchange_routes.py"
    spec = importlib.util.spec_from_file_location("exchange_routes", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonBallExchangeRouteTest(unittest.TestCase):
    def test_routes_are_recomputed(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_ball_exchange_routes.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertTrue(rebuilt["all_routes_disjoint"])
        self.assertIn("OPEN", rebuilt["ball_exchange_status"])
        for template in rebuilt["templates"]:
            self.assertEqual(template["route_count"], 6)
            self.assertEqual(template["disjoint_exchange_routes"], "PASS")
            self.assertEqual(template["translation_cell_status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
