from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class CompactHattoriBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[1]
        script = cls.repo / "scripts" / "verify_t73_compact_hattori_binding.py"
        spec = importlib.util.spec_from_file_location("compact_hattori", script)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import compact Hattori verifier")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_compact_cable_counts_and_braids(self) -> None:
        ledger = self.module.verify()
        self.assertEqual(ledger["cut_parameters"], {"p_y": 44, "p_z": 271})
        self.assertEqual(ledger["oriented_y_endpoints"], 88)
        self.assertEqual(ledger["z_z_circle_factors"], 227)
        self.assertEqual(ledger["B44"]["length"], 11340)
        self.assertEqual(ledger["B88"]["length"], 45360)
        self.assertEqual(
            ledger["required_simultaneous_transport"]["status"],
            "DISCHARGED_BY_PUBLIC_REPLACEMENT_COORDINATES",
        )

    def test_count_mutation_is_detectable(self) -> None:
        ledger = self.module.verify()
        mutated = dict(ledger["cut_parameters"])
        mutated["p_z"] -= 1
        self.assertNotEqual(mutated["p_z"] - mutated["p_y"], 227)


if __name__ == "__main__":
    unittest.main()
