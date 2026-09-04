from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_verifier():
    path = ROOT / "scripts" / "verify_t73_actual_geometric_braid.py"
    spec = importlib.util.spec_from_file_location("actual_braid_verifier", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ActualGeometricBraidTest(unittest.TestCase):
    def test_actual_braid_and_chart_mutation(self):
        result = load_verifier().verify()
        self.assertEqual(result["ACTUAL_GEOMETRIC_BRAID"], "PASS")
        self.assertEqual(result["STRANDS"], 44)
        self.assertEqual(result["CROSSINGS"], 11340)
        self.assertEqual(result["ENDPOINT_RETURN"], "PASS")
        self.assertEqual(result["NORMAL_RETURN"], "PASS")
        self.assertEqual(result["MUTATION_CHART_COLLISION"], "FAIL")
        self.assertEqual(result["FROZEN_COMPARISON_ORDER"], "AFTER_GEOMETRY_RECOVERY")


if __name__ == "__main__":
    unittest.main()
