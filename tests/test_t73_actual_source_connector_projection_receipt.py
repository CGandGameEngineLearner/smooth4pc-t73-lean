from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_actual_source_connector_projection_receipt.py"


class ActualSourceConnectorProjectionReceiptTest(unittest.TestCase):
    def test_compact_receipt_binds_full_cached_projection(self):
        spec = importlib.util.spec_from_file_location("source_projection_receipt", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.check_receipt(check_full=False)
        self.assertEqual(
            result["verdict"], "PASS_SOURCE_CONNECTOR_PROJECTION_RECEIPT"
        )
        self.assertEqual(result["full_crossings"], 1758060)


if __name__ == "__main__":
    unittest.main()
