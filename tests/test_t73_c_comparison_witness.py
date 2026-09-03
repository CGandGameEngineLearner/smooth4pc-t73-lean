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
        coords = load_generator().generate_witness()["endpoint_coordinates"]
        self.assertEqual(coords["public_normalization"]["delta3"], 2624)
        self.assertTrue(coords["mixed_index_variants_are_not_the_frozen_cubic"])
        witness = load_generator().generate_witness()
        self.assertEqual(witness["C_status"], "PASS")
        self.assertEqual(witness["C1_status"], "PASS")
        self.assertEqual(witness["C2_status"], "PASS")

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
