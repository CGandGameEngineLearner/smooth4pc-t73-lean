from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_actual_railroad_core_coordinates.py"


class ActualRailroadCoreCoordinatesTest(unittest.TestCase):
    def test_exact_generic_five_component_coordinates(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_railroad_coords", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_SOURCE_BOUND_RAILROAD_CORE_COORDINATES_CANDIDATE",
        )
        self.assertEqual(result["crossings"], 1168)
        self.assertEqual(result["surviving_passage_events"], 1779)
        self.assertEqual(result["actual_isotopy_to_hybrid_state"], "OPEN")


if __name__ == "__main__":
    unittest.main()
