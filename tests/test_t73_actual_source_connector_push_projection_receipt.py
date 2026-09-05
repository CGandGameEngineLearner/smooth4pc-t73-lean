from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_actual_source_connector_push_projection.py"


class ActualSourceConnectorPushReceiptTest(unittest.TestCase):
    def test_receipt_is_bound_and_fail_closed(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_connector_push", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        receipt, checks = module.check_receipt()
        self.assertTrue(all(checks.values()))
        self.assertEqual(receipt["crossing_count"], 2528401)
        self.assertEqual(receipt["component_summaries"]["m_2"]["parity"], "odd")
        self.assertIn("only", receipt["verdict"].lower())


if __name__ == "__main__":
    unittest.main()
