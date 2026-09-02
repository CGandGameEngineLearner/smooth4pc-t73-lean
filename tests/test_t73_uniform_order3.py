from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class UniformOrderThreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parents[1]
        script = repo / "scripts" / "verify_t73_uniform_order3.py"
        spec = importlib.util.spec_from_file_location("uniform_order3", script)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import uniform order-three verifier")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_every_endpoint_basis_vector_starts_in_order_three(self) -> None:
        receipt = self.module.verify()
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertEqual(receipt["matrix_entries_checked"], 7744)
        self.assertEqual(receipt["orders_0_1_2_nonzero_entries"], 0)
        self.assertGreater(receipt["cubic_nonzero_entries"], 0)

    def test_deleted_artin_letter_is_rejected(self) -> None:
        recompute = self.module.load_recompute()
        word = self.module.full_word(recompute)
        failures = self.module.low_order_failures(recompute, word[:-1], stop_after=1)
        self.assertEqual(len(failures), 1)


if __name__ == "__main__":
    unittest.main()
