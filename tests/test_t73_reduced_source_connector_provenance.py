from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_reduced_source_connector_provenance.py"


class ReducedSourceConnectorProvenanceTest(unittest.TestCase):
    def test_every_reduced_edge_has_actual_source_cells(self):
        spec = importlib.util.spec_from_file_location("verify_connectors", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_ALL_REDUCED_EDGES_ACTUAL_CONNECTOR_PROVENANCE",
        )
        self.assertEqual(result["reduced_edges"], 1780)
        self.assertEqual(result["raw_connector_cells"], 1785)


if __name__ == "__main__":
    unittest.main()
