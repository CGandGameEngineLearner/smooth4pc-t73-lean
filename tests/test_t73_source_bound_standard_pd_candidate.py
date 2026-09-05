from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_source_bound_standard_pd_candidate.py"


class SourceBoundStandardPDCandidateTest(unittest.TestCase):
    def test_all_pd_rows_and_local_insertions(self):
        spec = importlib.util.spec_from_file_location("verify_standard_pd", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_SOURCE_BOUND_STANDARD_PD_COMBINATORICS_ONLY"
        )
        self.assertEqual(result["components"], 7)
        self.assertEqual(result["crossings"], 4748)
        self.assertEqual(result["framing_status"], "PASS_TARGET_ONLY")


if __name__ == "__main__":
    unittest.main()
