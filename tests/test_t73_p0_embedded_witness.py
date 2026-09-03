from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_checker():
    path = ROOT / "scripts" / "check_t73_p0_embedded_witness.py"
    spec = importlib.util.spec_from_file_location("check_t73_p0_embedded_witness", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class P0EmbeddedWitnessTest(unittest.TestCase):
    def test_compact_word_ledger_is_rejected(self) -> None:
        checker = load_checker()
        schema = json.loads(checker.SCHEMA_PATH.read_text(encoding="utf-8"))
        compact = checker.ROOT / "scripts" / "generate_t73_compact_kirby_ledger.py"
        spec = importlib.util.spec_from_file_location("compact_kirby", compact)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with self.assertRaises(AssertionError):
            checker.validate(module.generate_ledger(), schema)

    def test_empty_pass_receipts_are_rejected(self) -> None:
        checker = load_checker()
        schema = json.loads(checker.SCHEMA_PATH.read_text(encoding="utf-8"))
        candidate = {"schema": "t73_p0_embedded_framed_link_witness/v1"}
        for field in schema["required_top_level_fields"]:
            candidate[field] = {}
        candidate["independent_checks"] = []
        with self.assertRaises(AssertionError):
            checker.validate(candidate, schema)


if __name__ == "__main__":
    unittest.main()
