from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_t_band_attachment_intervals.py"


class TBandAttachmentIntervalTest(unittest.TestCase):
    def test_intervals_lie_on_actual_source_and_target_lines(self):
        spec = importlib.util.spec_from_file_location("verify_t_intervals", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.verify()["verdict"], "PASS_T_INTERVAL_ACTUAL_EDGE_BINDING_CANDIDATE_WIDTH")


if __name__ == "__main__":
    unittest.main()
