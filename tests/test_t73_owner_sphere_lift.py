from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class OwnerSphereLiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parents[1]
        script = repo / "scripts" / "generate_t73_owner_sphere_lift.py"
        spec = importlib.util.spec_from_file_location("owner_lift", script)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import owner sphere lift generator")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_boundary_minor_and_unique_owner_lifts(self) -> None:
        ledger = self.module.generate_ledger()
        self.assertEqual(ledger["m2_m3_minor_determinant"], -1)
        self.assertEqual(len(ledger["owner_lifts"]), 3)
        for lift in ledger["owner_lifts"]:
            self.assertEqual(lift[:2], [0, 0])
            self.assertEqual(
                self.module.multiply(ledger["cellular_boundary_d2"], lift),
                [0, 0],
            )

    def test_m2_mutation_breaks_cycle_condition(self) -> None:
        ledger = self.module.generate_ledger()
        mutated = ledger["owner_lifts"][0][:]
        mutated[0] = 1
        self.assertNotEqual(
            self.module.multiply(ledger["cellular_boundary_d2"], mutated),
            [0, 0],
        )


if __name__ == "__main__":
    unittest.main()
