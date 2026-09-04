from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "scripts" / "analyze_t73_johnson_restore_overlay.py"
    spec = importlib.util.spec_from_file_location("restore_overlay", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonRestoreOverlayTest(unittest.TestCase):
    def test_overlay_is_recomputed_and_fiber_cutoff_rejected(self) -> None:
        stored = json.loads(
            (ROOT / "geometry" / "t73_johnson_restore_overlay.json").read_text(
                encoding="utf-8"
            )
        )
        rebuilt = load_script().generate()
        self.assertEqual(stored, rebuilt)
        self.assertEqual(rebuilt["fiber_preserving_restore_status"], "REJECTED")
        self.assertEqual(rebuilt["johnson_restore_status"], "OPEN")
        for template in rebuilt["templates"]:
            multiplier = 2 if template["power"] > 0 else 1
            self.assertEqual(template["overlay_piece_count"], 384 * multiplier)
            self.assertEqual(
                template["overlay_tetrahedron_count"], 1536 if multiplier == 1 else 3584
            )
            self.assertEqual(
                template["endpoint_classification"]["mandatory_active"], 96 * multiplier
            )
            self.assertEqual(
                template["endpoint_classification"]["mandatory_inactive"], 96 * multiplier
            )
            self.assertEqual(
                template["endpoint_classification"]["flexible"], 192 * multiplier
            )
            self.assertEqual(template["mismatch_vertex_transport_failures"], 0)
            self.assertGreater(template["cube_owner_mismatches"], 0)
            self.assertGreater(template["tetrahedron_owner_mismatches"], 0)


if __name__ == "__main__":
    unittest.main()
