from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_band_hybrid_movie.py"


class XBandHybridMovieTest(unittest.TestCase):
    def test_all_hybrid_piece_word_states(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_x_hybrid_movie", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_ALL_1513_X_HYBRID_PIECE_WORD_STATES"
        )
        self.assertEqual(result["transitions"], 1513)
        self.assertEqual(result["chart_gluing_checks"], 6052)
        self.assertEqual(result["inverse_state_checks"], 1513)


if __name__ == "__main__":
    unittest.main()
