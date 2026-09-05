from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_collar_ejection_map.py"


class XM1CollarEjectionMapTest(unittest.TestCase):
    def test_remaining_cores_have_a_finite_cubical_ejection_map(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_x_m1_collar", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_X_M1_CORE_COLLAR_EJECTION_MAP")
        self.assertEqual(result["tetrahedra"], 36)
        self.assertEqual(result["remaining_core_segments_in_domain"], 12104)
        self.assertEqual(
            result["framed_neighborhood_status"], "OPEN_SEPARATE_CHECK_REQUIRED"
        )


if __name__ == "__main__":
    unittest.main()
