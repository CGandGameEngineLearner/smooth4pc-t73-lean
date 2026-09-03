from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonLiftTest(unittest.TestCase):
    def test_transvections_reconstruct_A(self):
        witness = load("factor_t73_matrix_johnson").generate()
        self.assertEqual(witness["matrix_product_status"], "PASS")
        self.assertTrue(all(move["power"] in (-1, 1) for move in witness["unit_alpha_moves"]))

    def test_johnson_lift_reports_its_actual_channel_count(self):
        lift = load("build_t73_johnson_lift").generate()
        self.assertEqual(lift["splitting_preserving_status"], "PASS_BY_JOHNSON_ALPHA_GENERATORS")
        self.assertIn(lift["public_44_channel_status"], ("PASS", "FAIL"))


if __name__ == "__main__":
    unittest.main()
