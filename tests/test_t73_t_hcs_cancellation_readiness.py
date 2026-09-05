from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_t_hcs_cancellation_readiness.py"


class THcsCancellationReadinessTest(unittest.TestCase):
    def test_original_framing_gap_is_resolved_before_cancellation_map(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("t_hcs_readiness", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.build()
        self.assertEqual(result["verdict"], "READY_FOR_EXPLICIT_T_HCS_CANCELLATION_MAP")
        self.assertEqual(result["total_framing_segments_entering_t_ball"], 4)
        self.assertEqual(result["exteriorized_framing_segments_entering_t_ball"], 0)
        self.assertEqual(
            result["components"]["m_2"]["framing_push_off"][
                "segments_below_open_t_ball_boundary"
            ],
            0,
        )


if __name__ == "__main__":
    unittest.main()
