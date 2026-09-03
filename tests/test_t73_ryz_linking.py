from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load():
    path = ROOT / "scripts" / "extract_t73_ryz_linking.py"
    spec = importlib.util.spec_from_file_location("extract_t73_ryz_linking", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture(signs):
    return {
        "schema": "t73_reduced_link_pd/v1",
        "components": ["m_2", "r_yz"],
        "crossings": [
            {"over_owner": "m_2", "under_owner": "r_yz", "sign": sign}
            for sign in signs
        ],
        "normal_field_transport": {"status": "PASS"},
    }


class RyzLinkingTest(unittest.TestCase):
    def test_positive_hopf_ledger_has_linking_one(self) -> None:
        self.assertEqual(load().compute(fixture([1, 1]))["linking_m2_ryz"], 1)

    def test_opposite_crossings_have_linking_zero(self) -> None:
        self.assertEqual(load().compute(fixture([1, -1]))["linking_m2_ryz"], 0)

    def test_odd_mixed_crossing_sum_is_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            load().compute(fixture([1]))

    def test_word_ledger_does_not_determine_linking(self) -> None:
        path = ROOT / "scripts" / "falsify_t73_linking_from_words.py"
        spec = importlib.util.spec_from_file_location("falsify_t73_linking_from_words", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate()
        self.assertFalse(result["word_ledger_determines_linking"])
        self.assertEqual(result["zero_linking_control"]["linking_m2_ryz"], 0)
        self.assertEqual(result["unit_linking_control"]["linking_m2_ryz"], 1)


if __name__ == "__main__":
    unittest.main()
