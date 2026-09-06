import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_stub_r3_embeddedness_transfer.py"


class StubR3EmbeddednessTransferTest(unittest.TestCase):
    def test_inductive_transfer(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(result["verdict"], "PASS_X_M1_STUB_R3_EMBEDDEDNESS_TRANSFER")
        self.assertEqual(result["source_stub_segments"], 6052)
        self.assertEqual(result["r3_stub_pieces"], 10582)
        self.assertTrue(result["r3_stub_pairwise_embeddedness"])


if __name__ == "__main__":
    unittest.main()
