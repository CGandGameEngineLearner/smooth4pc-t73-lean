from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DualMeridianIASearchTest(unittest.TestCase):
    def test_depth_two_search_and_inner_control(self) -> None:
        path = ROOT / "scripts" / "search_t73_dual_meridian_ia.py"
        spec = importlib.util.spec_from_file_location("dual_search", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate(max_depth=2, max_states=20000)
        self.assertTrue(result["inner_positive_control"]["sufficient_extension_pass"])
        self.assertEqual(result["verdict"], "NONE_WITHIN_SEARCH")
        self.assertFalse(result["search_truncated"])


if __name__ == "__main__":
    unittest.main()
