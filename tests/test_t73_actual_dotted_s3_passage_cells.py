from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_actual_dotted_s3_passage_cells.py"


class ActualDottedS3PassageCellsTest(unittest.TestCase):
    def test_all_local_hopf_passages(self):
        spec = importlib.util.spec_from_file_location("verify_dotted_s3", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_ACTUAL_DISJOINT_FRAMED_DOTTED_S3_PASSAGE_CELLS")
        self.assertEqual(result["passages"], 1785)
        self.assertEqual(result["dotted_crossings"], 3570)


if __name__ == "__main__":
    unittest.main()
