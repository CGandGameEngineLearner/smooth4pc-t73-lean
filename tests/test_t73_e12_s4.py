from __future__ import annotations

import importlib.util
import json
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


class E12S4ReductionTest(unittest.TestCase):
    def test_empty_khovanov_and_standard_s4_kill_degree_494(self) -> None:
        module = load("certify_t73_e12_s4")
        result = module.generate()
        self.assertEqual(result["schema"], "t73_e12_s4_reduction/v1")
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["E12_status"], "PASS")
        self.assertFalse(result["lean_s4_reduction_data_inhabited"])
        self.assertFalse(result["identified_with_X_J"])
        self.assertTrue(result["about_standard_S4_not_candidate"])
        kh = result["s4_reduction"]["evalB4"]["empty_khovanov"]
        self.assertEqual(kh["resolution_cube_vertices"], 1)
        self.assertEqual(kh["homology_rank_total"], 1)
        self.assertEqual(kh["rational_dimension_by_quantum_degree"]["0"], 1)
        self.assertEqual(kh["rational_dimension_by_quantum_degree"]["494"], 0)
        sphere = result["s4_reduction"]["attach4"]["geometric_model"]
        self.assertEqual(sphere["euler_characteristic"], 2)
        self.assertEqual(sphere["B4"]["euler_characteristic"], 1)
        self.assertEqual(sphere["name"], "S^4")
        self.assertFalse(sphere["identified_with_X_J"])
        self.assertTrue(result["checks"]["s4_degree_494_zero"])
        self.assertTrue(result["checks"]["p3_four_ball_bound"])
        p3 = json.loads((ROOT / "audit" / "t73_p3_four_handle.json").read_text(encoding="utf-8"))
        self.assertEqual(result["p3_certificate_sha256"], p3["certificate_sha256"])
        self.assertEqual(sphere["B4"]["vertices"], len(p3["four_handle"]["core"]["vertices"]))


if __name__ == "__main__":
    unittest.main()
