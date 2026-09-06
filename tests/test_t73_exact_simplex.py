import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/t73_exact_simplex.py"
VOLUME = ROOT / "geometry/t73_x_m1_outer_collar_v7_ribbon_volume_3017.json"
OBSTRUCTION = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_ribbon_volume_obstruction_3017.json"
)


class ExactSimplexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("simplex", SCRIPT)
        assert spec and spec.loader
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_saved_ribbon_obstruction_witness(self):
        volume = json.loads(VOLUME.read_text())
        obstruction = json.loads(OBSTRUCTION.read_text())
        record = volume["transition_volumes"][obstruction["transition_index"]]
        vertices = [
            tuple(Fraction(value) for value in vertex)
            for vertex in record["spacetime_vertices"]
        ]
        first, second = [
            tuple(vertices[index] for index in record["tetrahedra"][tetrahedron])
            for tetrahedron in obstruction["tetrahedron_indices"]
        ]
        witness = self.module.tetrahedron_intersection_witness(first, second)
        self.assertIsNotNone(witness)
        self.assertEqual(witness["affine_rank"], 4)
        self.assertEqual(
            tuple(witness["point"]),
            tuple(Fraction(value) for value in obstruction["intersection_point"]),
        )

    def test_time_translated_copy_is_disjoint(self):
        first = (
            (Fraction(0), Fraction(0), Fraction(0), Fraction(0)),
            (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
            (Fraction(0), Fraction(1), Fraction(0), Fraction(0)),
            (Fraction(0), Fraction(0), Fraction(1), Fraction(0)),
        )
        second = tuple((*vertex[:3], Fraction(2)) for vertex in first)
        self.assertFalse(self.module.tetrahedra_intersect(first, second))


if __name__ == "__main__":
    unittest.main()
