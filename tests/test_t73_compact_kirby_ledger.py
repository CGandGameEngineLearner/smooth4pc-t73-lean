from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class CompactKirbyLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parents[1]
        script = repo / "scripts" / "generate_t73_compact_kirby_ledger.py"
        spec = importlib.util.spec_from_file_location("compact_kirby", script)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import compact Kirby generator")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_registered_reduced_words(self) -> None:
        ledger = self.module.generate_ledger()
        components = ledger["surviving_components"]
        self.assertEqual(components["m_2"]["length"], 311)
        self.assertEqual(components["m_2"]["exponent_sums"]["y"], 40)
        self.assertEqual(components["m_2"]["exponent_sums"]["z"], 269)
        self.assertEqual(components["m_3"]["length"], 1460)
        self.assertEqual(components["m_3"]["exponent_sums"]["y"], 189)
        self.assertEqual(components["m_3"]["exponent_sums"]["z"], 1271)

    def test_rzx_is_a_split_product_bigon_word(self) -> None:
        ledger = self.module.generate_ledger()
        self.assertEqual(
            ledger["surviving_components"]["r_zx_split_unknot"]["word"], []
        )


if __name__ == "__main__":
    unittest.main()
