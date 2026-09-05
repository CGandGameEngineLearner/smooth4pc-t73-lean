from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_actual_kirby_core_embedding.py"


class ActualKirbyCoreEmbeddingTest(unittest.TestCase):
    def test_two_dotted_and_five_framed_cores_are_embedded(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_kirby_core", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_SOURCE_BOUND_KIRBY_CORE_STRUCTURAL_CONSTRUCTION_ONLY",
        )
        self.assertEqual(result["framed_components"], 5)
        self.assertEqual(result["dotted_components"], 2)
        self.assertEqual(result["framing_status"], "OPEN")
        self.assertEqual(
            result["full_pairwise_embedding_status"],
            "OPEN_PENDING_GENERIC_PD_EXPORT",
        )


if __name__ == "__main__":
    unittest.main()
