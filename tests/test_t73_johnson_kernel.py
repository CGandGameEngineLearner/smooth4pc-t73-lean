from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class JohnsonKernelSearchTest(unittest.TestCase):
    def test_depth_two_search_is_reproducible(self):
        path = ROOT / "scripts" / "search_t73_johnson_kernel.py"
        spec = importlib.util.spec_from_file_location("johnson_kernel", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate(max_depth=2, max_states=50000)
        self.assertEqual(result["kernel_generator_count"], 96)
        self.assertEqual(result["states_visited"], 8377)
        self.assertFalse(result["search_truncated"])
        self.assertEqual(result["verdict"], "NONE_WITHIN_SEARCH")


if __name__ == "__main__":
    unittest.main()
