from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_verifier():
    path = ROOT / "scripts" / "verify_t73_johnson_spine_binding.py"
    spec = importlib.util.spec_from_file_location("spine_binding_verifier", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonSpineBindingTest(unittest.TestCase):
    def test_binding_and_mutations(self) -> None:
        result = load_verifier().verify()
        self.assertEqual(result["T73_JOHNSON_SPINE_BINDING"], "PASS")
        self.assertEqual(result["FACTORS"], 93)
        self.assertEqual(result["LEAF_BINDINGS"], 1772)
        self.assertEqual(result["CONNECTOR_BINDINGS"], 1775)
        self.assertEqual(result["CURVE_TRANSPORT"], "PASS")
        self.assertEqual(result["GENERAL_POINT_EVALUATOR"], "OPEN")
        self.assertEqual(result["MUTATION_FACTOR_SIDE"], "FAIL")
        self.assertEqual(result["MUTATION_LEAF_ORIENTATION"], "FAIL")
        self.assertEqual(result["MUTATION_CONNECTOR_COUNT"], "FAIL")


if __name__ == "__main__":
    unittest.main()
