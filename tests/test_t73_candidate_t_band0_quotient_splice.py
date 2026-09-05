from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_candidate_t_band0_quotient_splice.py"


def load():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("verify_t_band0_quotient", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CandidateTBand0QuotientSpliceTest(unittest.TestCase):
    def test_saved_splice_is_quotient_embedded(self):
        result = load().verify()
        self.assertEqual(result["verdict"], "PASS_CANDIDATE_QUOTIENT_EMBEDDEDNESS_ONLY")
        self.assertGreater(result["exact_deck_checks"], 0)

    def test_seam_is_explicit_in_saved_data(self):
        module = load()
        data = json.loads(module.SPLICE.read_text(encoding="utf-8"))
        self.assertEqual(len(data["mapping_torus_seam_segment_indices"]), 1)


if __name__ == "__main__":
    unittest.main()
