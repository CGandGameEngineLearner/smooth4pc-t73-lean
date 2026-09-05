from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_band_local_movie.py"


class XBandLocalMovieTest(unittest.TestCase):
    @unittest.skipUnless(
        os.environ.get("T73_RUN_FULL_X_LOCAL") == "1",
        "full 1513-state verifier is covered by the hash-bound receipt",
    )
    def test_all_1513_local_framed_states(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_x_local_movie", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_ALL_1513_X_LOCAL_FRAMED_BAND_STATES"
        )
        self.assertEqual(result["bands"], 1513)
        self.assertEqual(result["remaining_x_passage_sources"], ["m_1:C_i"])
        self.assertEqual(result["global_hybrid_splices_verified"], 1)


if __name__ == "__main__":
    unittest.main()
