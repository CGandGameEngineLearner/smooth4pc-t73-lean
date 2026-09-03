from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SpineStarHandlebodyTest(unittest.TestCase):
    def test_discrete_voronoi_pair_fills_and_s_maps_johnson(self) -> None:
        path = ROOT / "scripts" / "certify_t73_spine_star_handlebodies.py"
        spec = importlib.util.spec_from_file_location("stars", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate()
        self.assertEqual(result["star_L_B_tetrahedron_count"], 156)
        self.assertEqual(result["star_L_D_tetrahedron_count"], 156)
        self.assertTrue(result["stars_disjoint"])
        self.assertTrue(result["stars_contained_in_voronoi_cells"])
        self.assertEqual(result["handlebody_L_B_tetrahedron_count"], 192)
        self.assertEqual(result["handlebody_L_D_tetrahedron_count"], 192)
        self.assertEqual(result["euler_L_B"]["chi"], -2)
        self.assertEqual(result["euler_L_D"]["chi"], -2)
        self.assertEqual(result["interface_triangle_count"], 96)
        self.assertEqual(result["interface_surface_euler"]["chi"], -4)
        self.assertTrue(result["Q_interior_to_star_L_B"])
        self.assertTrue(result["protected_pl_cube_in_star_L_B"])
        self.assertTrue(result["fills_torus"])
        self.assertEqual(result["equatorial_tets_touching_both_stars"], 0)
        self.assertFalse(result["uniqueness_of_regular_neighborhoods_used"])
        self.assertEqual(result["s_maps_johnson_pair_onto_ar_pair"], "PASS")
        self.assertEqual(result["heegaard_handlebody_complex"], "PASS")
        self.assertEqual(result["ar_handlebody_as_certified_complex"], "PASS")
        self.assertEqual(result["euclidean_voronoi_surface_as_subcomplex"], "OPEN")
        self.assertEqual(result["mapping_torus_handlebody_identification"], "OPEN")
        self.assertEqual(result["p0a_status"], "PASS")
        self.assertEqual(result["star_complex_status"], "PASS")


if __name__ == "__main__":
    unittest.main()
