from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class JohnsonARBridgeTest(unittest.TestCase):
    def test_affine_bridge_maps_both_spines_and_axes(self):
        path = ROOT / "scripts" / "certify_t73_johnson_ar_bridge.py"
        spec = importlib.util.spec_from_file_location("bridge", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate()
        self.assertEqual(result["K1_vertex_image"], ["-1/2"] * 3)
        self.assertEqual(result["K2_vertex_image"], ["1/2"] * 3)
        self.assertTrue(result["orientation_preserving"])
        self.assertEqual(result["spine_one_complex_map"], "PASS")
        self.assertEqual(result["ambient_simplicial_map"], "PASS")
        self.assertEqual(result["johnson_tetrahedron_count"], 48)
        self.assertEqual(len(result["johnson_spine_edges_scaled"]), 12)
        self.assertEqual(result["ar_handlebody_as_certified_complex"], "PASS")
        self.assertEqual(result["spine_star_complex_status"], "PASS")
        self.assertEqual(result["spine_star_L_B_tetrahedra"], 156)
        self.assertEqual(result["handlebody_L_B_tetrahedra"], 192)
        self.assertTrue(result["spine_stars_fill_torus"])
        self.assertEqual(result["equatorial_tets_unsplit"], 0)
        self.assertEqual(result["s_maps_johnson_pair_onto_ar_pair"], "PASS")
        self.assertEqual(result["heegaard_handlebody_complex"], "PASS")
        self.assertFalse(result["uniqueness_of_regular_neighborhoods_used"])
        self.assertEqual(result["p0a_status"], "PASS")
        self.assertEqual(result["bridge_status"], "PASS")


if __name__ == "__main__":
    unittest.main()
