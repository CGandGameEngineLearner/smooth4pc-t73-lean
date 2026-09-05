from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_post_x_framed_replacement_cells.py"


class PostXFramedReplacementCellReceiptTest(unittest.TestCase):
    def test_receipt_and_source_bindings(self):
        spec = importlib.util.spec_from_file_location("verify_post_x_framed", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        receipt, checks = module.check_receipt()
        self.assertTrue(all(checks.values()))
        self.assertEqual(receipt["framed_replacement_cell_count"], 1513)
        self.assertEqual(receipt["explicit_push_path_vertices"], 68085)
        self.assertEqual(receipt["replacement_core_segments_per_cell"], 40)


if __name__ == "__main__":
    unittest.main()
