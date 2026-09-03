from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class E13IdentificationTest(unittest.TestCase):
    def test_cs_object_is_computed_and_identified_by_close(self) -> None:
        module = load("certify_t73_e13_identification")
        result = module.generate()
        self.assertEqual(result["schema"], "t73_e13_identification/v2")
        self.assertEqual(result["verdict"], "IDENTIFIED_CS_HANDLE_PICTURE")
        self.assertEqual(result["E13_status"], "PASS")
        self.assertTrue(result["checks"]["identified_with_Sigma_A_0"])
        self.assertTrue(result["checks"]["cs_object_computed"])
        self.assertFalse(result["checks"]["uniqueness_of_regular_neighborhoods_used"])
        self.assertFalse(result["checks"]["isotopy_extension_used_to_identify_x_j"])
        self.assertFalse(result["checks"]["lean_cs_topology_data_inhabited"])
        self.assertEqual(result["checks"]["missing_map_count"], 1)

        cs = result["standard_cs_object"]
        self.assertEqual(cs["name"], "Sigma_A^0")
        self.assertTrue(cs["homotopy_sphere_by_iwaki"])
        self.assertTrue(cs["identified_with_X_J"])
        self.assertFalse(cs["mapping_torus"]["triangulated_4_complex"])
        self.assertEqual(cs["mapping_torus"]["section_circle"]["framing"], "untwisted product framing epsilon=0")
        self.assertEqual(len(cs["cover_cores"]), 3)
        self.assertEqual(cs["cover_cores"][0]["vector"], [0, 0, 1])
        self.assertEqual(cs["cover_cores"][1]["vector"], [269, 41, 0])
        self.assertEqual(cs["cover_cores"][2]["vector"], [1240, 189, 32])
        self.assertEqual(cs["surviving_2_handles"]["handle_counts_after_two_cancellations"]["h1"], 2)
        self.assertEqual(result["x_j"]["s_one_handle_count"], 3)
        self.assertTrue(result["x_j"]["identified_with_Sigma_A_0"])
        self.assertFalse(result["x_j"]["p3_certificate_claims_identification"])

        present = result["present_maps"]
        self.assertTrue(present["linear_monodromy_is_A"])
        self.assertTrue(present["johnson_m2_word_equals_compact_cs_m2"])
        self.assertTrue(present["iwaki_2_1_applies_to_this_cs_object"])
        missing_ids = {item["id"] for item in result["missing_maps"]}
        self.assertEqual(missing_ids, {"lean_cs_topology_data"})
        resolved_ids = {item["id"] for item in result["resolved_maps"]}
        self.assertIn("embedded_cs_2_handles_equal_p0_strands", resolved_ids)
        self.assertIn("kirby_movie_cover_cores_to_x_j", resolved_ids)
        self.assertIn("lk_m2_ryz_from_reduced_pd", resolved_ids)
        close = load("certify_t73_e13_close").generate()
        close.pop("_pd", None)
        self.assertEqual(result["e13_close_sha256"], close["certificate_sha256"])


if __name__ == "__main__":
    unittest.main()
