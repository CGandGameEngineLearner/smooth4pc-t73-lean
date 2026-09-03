from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("gap"), "GAP is not installed")
class CompactFreeBasisTest(unittest.TestCase):
    def test_gap_decides_compact_spine_basis(self) -> None:
        path = ROOT / "scripts" / "check_t73_compact_free_basis.py"
        spec = importlib.util.spec_from_file_location("check_basis", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.run(timeout=300)
        self.assertEqual(result["compact"]["word_lengths"], [1, 310, 1461])
        self.assertEqual(result["compact_verdict"], "FAIL_NOT_FREE_BASIS")
        self.assertEqual(result["control_verdict"], "PASS_FREE_BASIS")


if __name__ == "__main__":
    unittest.main()
