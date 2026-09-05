from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_handle_pair_deletion.py"


class XM1HandlePairDeletionTest(unittest.TestCase):
    def test_actual_cubical_pair_deletes_to_five_components(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_x_m1_deletion", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_X_M1_HANDLE_PAIR_DELETION_AND_FIVE_COMPONENT_STATE",
        )
        self.assertEqual(result["post_cancel_components"], 5)
        self.assertEqual(result["remaining_one_handles"], ["y", "z"])


if __name__ == "__main__":
    unittest.main()
