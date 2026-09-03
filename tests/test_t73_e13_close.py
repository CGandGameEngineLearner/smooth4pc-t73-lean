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


class E13CloseTest(unittest.TestCase):
    def test_constructed_handle_picture_identifies(self) -> None:
        module = load("certify_t73_e13_close")
        result = module.generate()
        pd = result.pop("_pd")
        self.assertEqual(result["schema"], "t73_e13_close/v1")
        self.assertEqual(result["verdict"], "IDENTIFIED_CS_HANDLE_PICTURE")
        self.assertEqual(result["E13_status"], "PASS")
        self.assertTrue(result["checks"]["identified_with_Sigma_A_0"])
        self.assertTrue(result["checks"]["psi_supports_constructed"])
        self.assertTrue(result["checks"]["railroad_pd_constructed"])
        self.assertTrue(result["checks"]["linking_from_pd"])
        self.assertFalse(result["checks"]["lean_cs_topology_data_inhabited"])
        self.assertFalse(result["checks"]["uniqueness_of_regular_neighborhoods_used"])
        self.assertFalse(result["checks"]["isotopy_extension_used_to_identify_x_j"])
        self.assertTrue(result["checks"]["counterexample_not_claimed"])
        self.assertEqual(result["psi"]["move_count"], 93)
        self.assertTrue(result["psi"]["all_supports_miss_protected_ball"])
        self.assertEqual(result["attaching_link"]["linking_m2_ryz"], 0)
        self.assertEqual(pd["schema"], "t73_reduced_link_pd/v1")
        self.assertEqual(set(pd["components"]), {"m_2", "m_3", "r_xy", "r_yz", "r_zx"})
        linking = load("extract_t73_ryz_linking").compute(pd)
        self.assertEqual(linking["linking_m2_ryz"], 0)
        self.assertEqual(len(result["selected_y_channels"]["wickets"]), 44)
        self.assertEqual(result["selected_y_channels"]["owners"], {"r_xy": 2, "m_2": 42})
        self.assertEqual(len(result["pipeline"]), 10)
        self.assertTrue(all(stage["status"] == "PASS" for stage in result["pipeline"]))
        open_ids = [item["id"] for item in result["resolved_maps"] if item["status"] == "OPEN"]
        self.assertEqual(open_ids, ["lean_cs_topology_data"])


if __name__ == "__main__":
    unittest.main()
