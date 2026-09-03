from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SRelativeMovesTest(unittest.TestCase):
    def test_committed_certificate_replays(self) -> None:
        path = ROOT / "scripts" / "certify_t73_s_relative_moves.py"
        spec = importlib.util.spec_from_file_location("s_relative", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        generated = module.generate()
        self.assertEqual(generated["verdict"], "OPEN")
        self.assertFalse(generated["checks"]["detector_fixed"])
        self.assertEqual(generated["relative_geometry"]["spotted_ball_boundary_count"], 7)
        self.assertEqual(generated["relative_geometry"]["maximum_spotted_ball_tubings"], 5)
        self.assertEqual(
            generated["mww_hemisphere_table"]["coequalizer_difference"],
            {"1": 0, "X": 0},
        )
        self.assertFalse(
            generated["candidate_binding"]["actual_standard_sphere_endpoint_foam_computed"]
        )


if __name__ == "__main__":
    unittest.main()
