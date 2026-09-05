from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_ejection_overlap_transition_gap.json"


class XM1EjectionOverlapGapTest(unittest.TestCase):
    def test_gap_is_fail_closed(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertEqual(data["core_overlap_transition_count"], 3026)
        self.assertEqual(data["push_overlap_transition_count"], 3026)
        self.assertFalse(data["extended_chart_transition_present"])
        self.assertFalse(data["complete_core_image_gluing"])


if __name__ == "__main__": unittest.main()
