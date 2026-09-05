from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_t73_selected_source_partition_z0.py"
OUTPUT = ROOT / "geometry" / "t73_selected_source_partition_z0.json"


def load():
    spec = importlib.util.spec_from_file_location("t73_z0_partition", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Z0PartitionTest(unittest.TestCase):
    def test_saved_partition_is_an_exact_rebuild(self):
        module = load()
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), module.build())

    def test_fragments_and_interface_have_the_declared_halfspace(self):
        data = json.loads(OUTPUT.read_text(encoding="utf-8"))
        covered = set()
        for side, sign in (("z_nonpositive", -1), ("z_nonnegative", 1)):
            for item in data["blocks"][side]:
                covered.add((item["route_index"], item["triangle_index"]))
                for triangle in item["triangles"]:
                    for vertex in triangle:
                        z = Fraction(vertex[2])
                        self.assertLessEqual(z, 0) if sign < 0 else self.assertGreaterEqual(z, 0)
        self.assertEqual(len(covered), data["original_triangle_count"])
        for item in data["interface_segments"]:
            self.assertEqual(len(item["segment"]), 2)
            self.assertTrue(all(Fraction(vertex[2]) == 0 for vertex in item["segment"]))


if __name__ == "__main__":
    unittest.main()
