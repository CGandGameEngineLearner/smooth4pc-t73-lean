import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_complete_global_r3_replacement_core_embedding_v3.py"


class CompleteGlobalR3ReplacementCoreEmbeddingV3Test(unittest.TestCase):
    def test_all_ten_subsystem_pairs(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_X_M1_COMPLETE_GLOBAL_R3_REPLACEMENT_CORE_EMBEDDING_V3",
        )
        self.assertEqual(result["core_segments"], 92284)
        self.assertEqual(result["subsystem_pairs_verified"], 10)
        self.assertTrue(result["complete_replacement_core_embedding"])
        self.assertEqual(result["complete_push_paths"], "OPEN")


if __name__ == "__main__":
    unittest.main()
