from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_x_band_local_movie_receipt.py"


class XBandLocalMovieReceiptTest(unittest.TestCase):
    def test_hash_bound_full_verification_receipt(self):
        spec = importlib.util.spec_from_file_location("x_local_receipt", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.check_receipt()
        self.assertEqual(result["verdict"], "PASS_X_LOCAL_MOVIE_RECEIPT")
        self.assertEqual(
            result["full_verifier_verdict"],
            "PASS_ALL_1513_X_LOCAL_FRAMED_BAND_STATES",
        )


if __name__ == "__main__":
    unittest.main()
