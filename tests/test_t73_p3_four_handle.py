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


class P3FourHandleTest(unittest.TestCase):
    def test_johnson_replacement_four_handle_picture(self) -> None:
        module = load("certify_t73_p3_four_handle")
        result = module.generate()
        self.assertEqual(result["schema"], "t73_p3_four_handle/v2")
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(
            result["E11_status"],
            "PASS_ACTUAL_THREE_HANDLE_MAP",
        )
        self.assertEqual(result["E12_status"], "PASS")
        self.assertEqual(result["E13_status"], "PARTIAL")
        self.assertEqual(len(result["cancellations"]), 3)
        self.assertTrue(all(item["cancels"] for item in result["cancellations"]))
        self.assertEqual(result["remaining_boundary"]["homeomorphism_type"], "S^3")
        self.assertTrue(result["remaining_boundary"]["contains_p0_ball"])
        self.assertEqual(result["four_handle"]["core"]["euler_characteristic"], 1)
        self.assertEqual(result["four_handle"]["core"]["boundary_euler_characteristic"], 0)
        self.assertTrue(result["four_handle"]["empty_link"])
        self.assertTrue(result["four_handle"]["core"]["empty_link"])
        self.assertTrue(result["four_handle"]["triangulated_W3"])
        self.assertFalse(result["closed_manifold"]["identified_with_Sigma_A_0"])
        self.assertFalse(result["mww_3_10"]["identifies_iterated_quotient_with_Sigma_A_0"])
        self.assertTrue(result["mww_3_10"]["identifies_iterated_quotient_with_X_J"])
        self.assertTrue(result["e12_s4"]["summand_zero"])
        self.assertTrue(result["e12_s4"]["about_standard_S4_not_candidate"])
        self.assertFalse(result["e12_s4"]["s4_reduction_data_inhabited"])
        self.assertEqual(result["e13_determinants"]["det_A"], 1)
        self.assertEqual(result["e13_determinants"]["det_A_minus_I"], 1)
        self.assertFalse(result["e13_determinants"]["identifies_X_J_with_Sigma_A_0"])
        self.assertTrue(result["checks"]["counterexample_not_claimed"])
        self.assertFalse(result["uniqueness_of_regular_neighborhoods_used"])
        spheres = load("certify_t73_s_standard_spheres").generate()
        self.assertEqual(result["s_spheres_sha256"], spheres["certificate_sha256"])
        self.assertEqual(result["remaining_boundary"]["p0_ball_bounds"], spheres["model_ball"]["bounds"])


if __name__ == "__main__":
    unittest.main()
