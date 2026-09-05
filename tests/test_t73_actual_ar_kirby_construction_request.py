from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_actual_ar_kirby_construction_request.py"
OUTPUT = ROOT / "geometry/t73_actual_ar_kirby_construction_request.json"


def load():
    spec = importlib.util.spec_from_file_location("t73_ar_kirby_request", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ActualArKirbyConstructionRequestTest(unittest.TestCase):
    def test_saved_request_is_live_and_open(self):
        data = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(data, load().build())
        self.assertEqual(data["completion_status"], "OPEN")
        self.assertEqual(data["required_band_geometry"]["t_band_count"], 6)
        self.assertEqual(data["required_band_geometry"]["x_band_count"], 1513)
        self.assertEqual(len(data["required_post_cancellation_components"]), 7)


if __name__ == "__main__":
    unittest.main()
