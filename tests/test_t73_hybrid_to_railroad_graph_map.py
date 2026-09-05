from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_hybrid_to_railroad_graph_map.py"


class HybridToRailroadGraphMapTest(unittest.TestCase):
    def test_framed_graph_cells_map_bijectively(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_graph_map", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_HYBRID_TO_RAILROAD_FRAMED_GRAPH_ISOMORPHISM_ONLY",
        )
        self.assertEqual(result["vertices"], 1780)
        self.assertEqual(result["edges"], 1780)
        self.assertEqual(result["ambient_isotopy_status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
