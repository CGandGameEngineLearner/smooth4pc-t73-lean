from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_t_hcs_handle_pair_deletion.py"


class THcsHandlePairDeletionTest(unittest.TestCase):
    def test_standard_pair_and_actual_cell_binding(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_t_hcs_deletion", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_T_HCS_HANDLE_PAIR_DELETION_AND_POST_LINK_STATE"
        )
        self.assertEqual(result["union_betti"], [1, 0, 0, 0, 0])
        self.assertEqual(result["boundary_betti"], [1, 0, 0, 1])
        self.assertEqual(result["actual_belt_intersections"], 1)


if __name__ == "__main__":
    unittest.main()
