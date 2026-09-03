from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class CompactPointPushTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[1]
        script = cls.repo / "scripts" / "verify_t73_compact_point_push.py"
        spec = importlib.util.spec_from_file_location("compact_point_push", script)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import compact point-push verifier")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.input = cls.repo / "data" / "T73_DELTA3_PUBLIC_INPUT.json"

    def test_compact_schema_regenerates_every_public_row(self) -> None:
        receipt = self.module.verify(self.input)
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertEqual(receipt["factor_count"], 252)
        self.assertEqual(receipt["pure_factor_count"], 252)
        self.assertEqual(receipt["B44_permutation"], "identity")
        self.assertEqual(receipt["B44_writhe"], 0)
        self.assertEqual(receipt["B44_positive_letters"], 5670)
        self.assertEqual(receipt["B44_negative_letters"], 5670)
        self.assertEqual(receipt["sweeps"], 6)
        self.assertEqual(receipt["factors_per_sweep"], 42)

    def test_mutated_coordinate_is_rejected(self) -> None:
        rows = self.module.generate_rows()
        rows[0][1] += 1
        self.assertNotEqual(
            self.module.canonical_sha(rows),
            self.module.verify(self.input)["crossing_rows_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
