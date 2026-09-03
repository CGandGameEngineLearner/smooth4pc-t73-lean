from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class SphereSlideLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parents[1]
        script = repo / "scripts" / "generate_t73_sphere_slide_ledger.py"
        spec = importlib.util.spec_from_file_location("sphere_slides", script)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import sphere slide generator")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_nielsen_program_reconstructs_sphere_matrix(self) -> None:
        ledger = self.module.generate_ledger()
        self.assertEqual(ledger["determinant"], 1)
        self.assertGreater(ledger["operation_count"], 0)
        check = self.module.identity(3)
        for operation in ledger["construction_from_standard_basis"]:
            self.module.apply(check, operation)
        self.assertEqual(check, self.module.SPHERE_COLUMNS)

    def test_mutated_matrix_is_not_the_registered_program_target(self) -> None:
        ledger = self.module.generate_ledger()
        mutated = [row[:] for row in self.module.SPHERE_COLUMNS]
        mutated[0][0] += 1
        check = self.module.identity(3)
        for operation in ledger["construction_from_standard_basis"]:
            self.module.apply(check, operation)
        self.assertNotEqual(check, mutated)


if __name__ == "__main__":
    unittest.main()
