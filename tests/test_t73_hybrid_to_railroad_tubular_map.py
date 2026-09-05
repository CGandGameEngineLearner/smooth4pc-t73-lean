from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_hybrid_to_railroad_tubular_map.py"


class HybridToRailroadTubularMapTest(unittest.TestCase):
    def test_five_framed_solid_torus_maps(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_tubes", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_HYBRID_TO_RAILROAD_FRAMED_TUBULAR_HOMEOMORPHISMS_ONLY",
        )
        self.assertEqual(result["components"], 5)
        self.assertEqual(result["relative_twists"], [0, 0, 0, 0, 0])
        self.assertEqual(result["complement_extension_status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
