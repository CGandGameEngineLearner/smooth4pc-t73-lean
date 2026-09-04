from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_verifier():
    path = ROOT / "scripts" / "verify_t73_three_handle_surface_transport.py"
    spec = importlib.util.spec_from_file_location("surface_transport_verifier", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ThreeHandleSurfaceTransportTest(unittest.TestCase):
    def test_surface_transport_and_mutation(self):
        result = load_verifier().verify()
        self.assertEqual(result["ACTUAL_THREE_HANDLE_SURFACE_TRANSPORT"], "PASS")
        self.assertEqual(result["SURFACES"], 3)
        self.assertEqual(result["CORE_DISK_COUNTS"], [12578, 1824, 409])
        self.assertEqual(result["T_BANDS_PER_SURFACE"], 6)
        self.assertEqual(result["X_BANDS_PER_SURFACE"], 1513)
        self.assertEqual(result["MUTATION_MISSING_X_BAND"], "FAIL")


if __name__ == "__main__":
    unittest.main()
