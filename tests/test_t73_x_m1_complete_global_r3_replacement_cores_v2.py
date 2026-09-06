import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_complete_global_r3_replacement_cores_v2.py"


class CompleteGlobalR3ReplacementCoresV2Test(unittest.TestCase):
    def test_repaired_full_reconstruction(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify(check_cache_sha=False)
        self.assertEqual(
            result["verdict"],
            "PASS_X_M1_COMPLETE_GLOBAL_R3_REPLACEMENT_CORES_V2_FULL",
        )
        self.assertEqual(result["core_segments_reconstructed"], 92284)
        self.assertTrue(result["old_exact_collision_repaired"])
        self.assertEqual(result["complete_push_paths"], "OPEN")


if __name__ == "__main__":
    unittest.main()
