from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load():
    path = ROOT / "scripts" / "audit_t73_pd_spherogram_adapter.py"
    spec = importlib.util.spec_from_file_location("pd_adapter", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PDSpherogramAdapterTest(unittest.TestCase):
    def test_committed_report_matches_live_audit(self):
        module = load()
        data = json.loads(module.PD.read_text(encoding="utf-8"))
        stored = json.loads(module.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(stored, module.attempt_complete(data))

    def test_current_ledger_is_rejected(self) -> None:
        module = load()
        data = json.loads(module.PD.read_text(encoding="utf-8"))
        result = module.attempt_complete(data)
        self.assertEqual(result["verdict"], "OPEN")
        self.assertEqual(result["input_crossings"], 1958)
        self.assertGreater(result["repeated_segment_count"], 0)
        self.assertEqual(result["component_incidence"]["r_zx"], 0)
        self.assertEqual(result["spherogram_link"], "OPEN")

    def test_pd_arc_incidence_mutation(self) -> None:
        module = load()
        with self.assertRaisesRegex(ValueError, "exactly twice"):
            module.validate_standard_pd_code([[0, 1, 2, 3], [0, 1, 2, 4]])

    def test_valid_small_pd_incidence(self) -> None:
        module = load()
        module.validate_standard_pd_code([[0, 1, 0, 1]])


if __name__ == "__main__":
    unittest.main()
