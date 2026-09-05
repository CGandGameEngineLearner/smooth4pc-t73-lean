from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_t_hcs_collar_ejection_map.py"


class THcsCollarEjectionMapTest(unittest.TestCase):
    def test_finite_collar_map_is_orientation_preserving(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_t_hcs_collar", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_T_HCS_COLLAR_EJECTION_CELL_MAP")
        self.assertEqual(result["tetrahedra"], 24)
        self.assertEqual(result["scope"], "COLLAR_EJECTION_ONLY_HANDLE_PAIR_DELETION_OPEN")


if __name__ == "__main__":
    unittest.main()
