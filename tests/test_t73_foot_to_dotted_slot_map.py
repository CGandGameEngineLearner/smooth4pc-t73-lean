from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_foot_to_dotted_slot_map.py"


class FootToDottedSlotMapTest(unittest.TestCase):
    def test_surviving_marked_points_have_unique_dotted_slots(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_dotted_slots", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_FOOT_MARKED_ORDER_AND_DOTTED_SLOT_ASSIGNMENT_ONLY",
        )
        self.assertEqual(result["surviving_marked_points"], 1779)
        self.assertEqual(result["explicit_disk_tracks"], "OPEN")


if __name__ == "__main__":
    unittest.main()
