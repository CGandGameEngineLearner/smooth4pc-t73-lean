from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class SphereReynoldsOrbitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parents[1]
        script = repo / "scripts" / "verify_t73_sphere_reynolds_orbits.py"
        spec = importlib.util.spec_from_file_location("sphere_orbits", script)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import sphere Reynolds verifier")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_registered_sphere_copy_orbits(self) -> None:
        ledger = self.module.verify()
        self.assertEqual(ledger["base_detector_selection_orbit"], 1)
        self.assertEqual(ledger["orbit_sizes"], [1312, 190, 42])
        for row in ledger["sphere_orbits"]:
            self.assertEqual(row["m2_selection_orbit"], 1)

    def test_wrong_orientation_allocation_changes_orbit(self) -> None:
        ledger = self.module.verify()
        counts = ledger["sphere_orbits"][0]["target_copy_counts"]
        mutated = {owner: dict(value) for owner, value in counts.items()}
        mutated["r_xy"]["negative"] -= 1
        mutated["r_xy"]["positive"] += 1
        self.assertNotEqual(
            self.module.detector_selection_count(mutated),
            ledger["sphere_orbits"][0]["detector_selection_orbit"],
        )


if __name__ == "__main__":
    unittest.main()
