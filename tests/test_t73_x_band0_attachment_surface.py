from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_band0_attachment_surface.py"


class XBandZeroAttachmentSurfaceTest(unittest.TestCase):
    def test_actual_attachments_and_candidate_disk(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_x_band0", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_X_BAND0_ACTUAL_ATTACHMENTS_CANDIDATE_FRAMING_INTERIOR",
        )
        self.assertEqual(result["post_cancel_source_deck"], [269, 40, 0])
        self.assertEqual(result["target_parallel_coefficient"], 20)


if __name__ == "__main__":
    unittest.main()
