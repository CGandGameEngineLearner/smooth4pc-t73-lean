from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load():
    path = ROOT / "scripts" / "audit_t73_rxy_pivotal_currying.py"
    spec = importlib.util.spec_from_file_location("rxy_currying", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RxyCurryingTest(unittest.TestCase):
    def test_eight_connectors(self):
        module = load()
        data = json.loads(module.SOURCE.read_text(encoding="utf-8"))
        result = module.classify(data)
        self.assertEqual(len(result["records"]), 8)
        self.assertEqual(
            result["matching_class_counts"],
            {"same_variance": 4, "opposite_variance": 4},
        )
        self.assertEqual(result["normalized_pivotal_degree"], 0)
        self.assertFalse(result["can_restore_494"])

    def test_missing_connector_is_rejected(self):
        module = load()
        data = json.loads(module.SOURCE.read_text(encoding="utf-8"))
        data["exterior_intervals"] = [
            interval for interval in data["exterior_intervals"]
            if interval["interval_id"] != "r_xy:positive:interval:3"
        ]
        with self.assertRaisesRegex(AssertionError, "exactly eight"):
            module.classify(data)


if __name__ == "__main__":
    unittest.main()
