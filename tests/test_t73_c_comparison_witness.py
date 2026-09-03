from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_t73_c_comparison_witness.py"
WITNESS = ROOT / "audit" / "t73_c_comparison_witness.json"


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_t73_c_comparison_witness", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CComparisonWitnessTest(unittest.TestCase):
    def test_committed_witness_regenerates(self) -> None:
        load_generator().verify_committed(WITNESS)

    def test_all_endpoint_sign_conventions_are_nonzero(self) -> None:
        table = load_generator().generate_witness()["endpoint_coordinates"][
            "sign_robust_cubic_values"
        ]
        self.assertEqual(len(table), 4)
        self.assertTrue(all(value != 0 for value in table.values()))
        self.assertEqual(table["cup5_-1_cap2_-1"], -59072)

    def test_pairing_mutant_is_rejected(self) -> None:
        generator = load_generator()
        compact = generator.load_script("generate_t73_compact_kirby_ledger")
        word = compact.after_x_cancellation(1)
        y_index = next(i for i, letter in enumerate(word) if letter.lower() == "y")
        word[(y_index + 1) % len(word)] = "y"
        with self.assertRaises(AssertionError):
            generator.pair_y_to_next_z("mutant", word)


if __name__ == "__main__":
    unittest.main()
