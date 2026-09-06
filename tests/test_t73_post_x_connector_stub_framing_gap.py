import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SCRIPT = SCRIPTS / "verify_t73_post_x_connector_stub_framing_gap.py"


class PostXConnectorStubFramingGapTest(unittest.TestCase):
    def test_all_literal_push_interfaces_fail_closed(self):
        sys.path.insert(0, str(SCRIPTS))
        try:
            spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
            assert spec and spec.loader
            verifier = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(verifier)
            result = verifier.verify()
        finally:
            sys.path.remove(str(SCRIPTS))
        self.assertEqual(result["verdict"], "PASS_POST_X_CONNECTOR_STUB_FRAMING_GAP")
        self.assertEqual(result["core_endpoint_matches"], 3026)
        self.assertEqual(result["missing_normal_homotopies"], 3026)
        self.assertFalse(result["actual_complete_push_cycles"])


if __name__ == "__main__":
    unittest.main()
