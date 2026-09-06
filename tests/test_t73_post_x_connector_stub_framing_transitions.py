import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_post_x_connector_stub_framing_transitions.py"


class PostXConnectorStubFramingTransitionsTest(unittest.TestCase):
    def test_all_local_transition_ribbons(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify(check_cache_sha=False)
        self.assertEqual(
            result["verdict"],
            "PASS_POST_X_CONNECTOR_STUB_FRAMING_TRANSITIONS_FULL_LOCAL",
        )
        self.assertEqual(result["transitions"], 3026)
        self.assertEqual(result["endpoint_normal_matches"], 6052)
        self.assertEqual(result["relative_twist_sum"], 0)
        self.assertEqual(result["global_clearance"], "OPEN")


if __name__ == "__main__":
    unittest.main()
