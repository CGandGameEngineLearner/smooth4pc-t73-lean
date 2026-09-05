from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_ejection_overlap_transitions.py"


class XM1OverlapTransitionsReceiptTest(unittest.TestCase):
    def test_receipt(self):
        spec = importlib.util.spec_from_file_location("verify_overlap", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        receipt, checks = module.check_receipt(); self.assertTrue(all(checks.values()))
        self.assertEqual(receipt["interface_count"], 3026)
        self.assertEqual(receipt["total_mapping_cylinder_tetrahedra"], 18156)


if __name__ == "__main__": unittest.main()
