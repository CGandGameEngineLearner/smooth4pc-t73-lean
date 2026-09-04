from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_verifier():
    path = ROOT / "scripts" / "verify_t73_johnson_spine_embedding.py"
    spec = importlib.util.spec_from_file_location("spine_verifier", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JohnsonSpineEmbeddingTest(unittest.TestCase):
    def test_embedding_and_mutations(self) -> None:
        result = load_verifier().verify()
        self.assertEqual(result["ACTUAL_SPINE_EMBEDDING"], "PASS")
        self.assertEqual(result["HANDLE_ARCS"], 1772)
        self.assertEqual(result["CENTRAL_CONNECTORS"], 1775)
        self.assertEqual(result["RETRACTION_WORDS"], "PASS")
        self.assertEqual(result["ABELIANIZATION_IS_A"], "PASS")
        self.assertEqual(result["MUTATION_LANE_DUPLICATE"], "FAIL")
        self.assertEqual(result["MUTATION_CONNECTOR_HEIGHT"], "FAIL")
        self.assertEqual(result["MUTATION_ORIENTATION"], "FAIL")
        self.assertEqual(result["MUTATION_SIDE_BIT"], "FAIL")
        self.assertEqual(result["AMBIENT_RESTORE_SPINE_BINDING"], "OPEN")
        self.assertEqual(result["ACTUAL_CURVE_EVALUATOR"], "OPEN")


if __name__ == "__main__":
    unittest.main()
