from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_t_band_sequential_movie.py"


class TBandSequentialMovieTest(unittest.TestCase):
    def test_all_six_framed_slides_replay_in_current_link_order(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_t_movie", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_SIX_T_BAND_SEQUENTIAL_FRAMED_KIRBY_SLIDES"
        )
        self.assertEqual(result["states"], 7)
        self.assertEqual(result["transitions"], 6)


if __name__ == "__main__":
    unittest.main()
