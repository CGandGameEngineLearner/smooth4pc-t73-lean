from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_source_pd_post_x_coverage.py"


class SourcePDPostXCoverageTest(unittest.TestCase):
    def test_missing_replacement_paths_are_not_hidden(self):
        spec = importlib.util.spec_from_file_location("verify_pd_coverage", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_SOURCE_PD_POST_X_COVERAGE_GAP_AUDIT")
        self.assertEqual(result["omitted_core_segments"], 60520)
        self.assertEqual(result["repair_status"], "OPEN_PROJECT_FULL_REPLACEMENT_PATHS")


if __name__ == "__main__":
    unittest.main()
