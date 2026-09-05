from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_foot_to_dotted_disk_tracks.py"


class FootToDottedDiskTracksTest(unittest.TestCase):
    def test_all_marked_points_move_without_collision(self):
        spec = importlib.util.spec_from_file_location("verify_disk_tracks", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_EXPLICIT_REFLECTION_PAIRED_MARKED_DISK_TRACKS",
        )
        self.assertEqual(result["moves"], 1785)
        self.assertEqual(result["reflection_checks"], 1785)


if __name__ == "__main__":
    unittest.main()
