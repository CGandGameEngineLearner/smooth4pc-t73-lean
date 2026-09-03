from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load():
    path = ROOT / "scripts" / "audit_t73_premises.py"
    spec = importlib.util.spec_from_file_location("audit_t73_premises", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PremiseAuditTest(unittest.TestCase):
    def test_committed_audit_regenerates(self) -> None:
        module = load()
        committed = __import__("json").loads(module.COMMITTED.read_text())
        self.assertEqual(committed, module.generate())

    def test_load_bearing_geometry_is_open(self) -> None:
        audit = load().generate()
        self.assertEqual(audit["items"]["P0"]["state"], "PASS")
        self.assertTrue(audit["items"]["P0"]["proved"])
        self.assertEqual(audit["items"]["P0"]["p0a_status"], "PASS")
        self.assertEqual(audit["items"]["P0"]["p0b_status"], "PASS")
        self.assertEqual(audit["items"]["P0"]["p0c_status"], "PASS")
        for key in ("C", "S"):
            self.assertEqual(audit["items"][key]["state"], "OPEN")
            self.assertFalse(audit["items"][key]["proved"])
            self.assertFalse(audit["items"][key]["falsified"])
        self.assertFalse(audit["counterexample_claim_proved"])
        self.assertEqual(audit["overall"], "OPEN")
        self.assertNotIn("ALL_LOAD_BEARING_ITEMS_DISCHARGED", str(audit))


if __name__ == "__main__":
    unittest.main()
