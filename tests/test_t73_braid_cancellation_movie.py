from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class BraidCancellationMovieTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parents[1]
        script = repo / "scripts" / "verify_t73_braid_cancellation_movie.py"
        spec = importlib.util.spec_from_file_location("braid_movie", script)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import braid cancellation verifier")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_braid_and_cable_cancel_with_zero_relative_framing(self) -> None:
        ledger = self.module.verify()
        self.assertEqual(ledger["B44"]["cancellation_pairs"], 11340)
        self.assertEqual(ledger["B88"]["cancellation_pairs"], 45360)
        self.assertEqual(ledger["framing"]["total_relative_change"], 0)
        self.assertEqual(ledger["simultaneous_transport"]["P"], "identity")

    def test_unmatched_tail_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "did not freely cancel"):
            self.module.cancellation_ledger([1, 2, -1])


if __name__ == "__main__":
    unittest.main()
