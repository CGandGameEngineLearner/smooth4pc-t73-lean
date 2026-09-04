from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_t73_selected_source_exterior.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("source_clearance", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SourceClearanceMathTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = load_verifier()

    def test_exact_segment_distance_examples(self):
        F = Fraction
        crossing = ((F(0), F(0), F(0)), (F(2), F(0), F(0)))
        transverse = ((F(1), F(-1), F(0)), (F(1), F(1), F(0)))
        parallel = ((F(0), F(1), F(0)), (F(2), F(1), F(0)))
        endpoint = ((F(3), F(2), F(0)), (F(3), F(4), F(0)))
        self.assertEqual(
            self.verifier.segment_distance_squared(crossing, transverse), F(0)
        )
        self.assertEqual(
            self.verifier.segment_distance_squared(crossing, parallel), F(1)
        )
        self.assertEqual(
            self.verifier.segment_distance_squared(crossing, endpoint), F(5)
        )

    def test_saved_clearance_exceeds_construction_and_ribbon_bounds(self):
        source = json.loads(
            (ROOT / "geometry/t73_selected_source_exterior.json").read_text(
                encoding="utf-8"
            )
        )
        clearance = source["ribbon_clearance"]
        minimum = Fraction(clearance["minimum_centre_segment_distance_squared"])
        width = Fraction(clearance["maximum_vertex_l1_push_width"])
        self.assertGreater(minimum, Fraction(1, 1000) ** 2)
        self.assertGreater(minimum, (2 * width) ** 2)
        self.assertEqual(
            sum(
                len(interval["ruled_ribbon_triangles"])
                for interval in source["exterior_intervals"]
            ),
            2520,
        )


if __name__ == "__main__":
    unittest.main()
