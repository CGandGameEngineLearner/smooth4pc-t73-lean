from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class IAFramingSearchTest(unittest.TestCase):
    def test_depth_two_search_is_reproducible(self) -> None:
        path = ROOT / "scripts" / "search_t73_ia_framing.py"
        spec = importlib.util.spec_from_file_location("ia_search", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate(max_depth=2, max_states=20000)
        self.assertEqual(result["verdict"], "NO_ZERO_WITHIN_SEARCH")
        self.assertEqual(result["best_candidates"][0]["absolute_net_coefficient"], 40)
        self.assertFalse(result["search_truncated"])

    def test_depth_three_separates_basepoint_only_and_detector_changed(self) -> None:
        path = ROOT / "scripts" / "search_t73_ia_framing.py"
        spec = importlib.util.spec_from_file_location("ia_search_depth3", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate(max_depth=3, max_states=200000)
        self.assertEqual(result["detector_changed_candidates"], 1097)
        self.assertEqual(result["best_detector_changed_candidates"][0]["absolute_net_coefficient"], 42)


if __name__ == "__main__":
    unittest.main()
