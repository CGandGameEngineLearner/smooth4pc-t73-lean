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
        module.main if False else None
        import json

        committed = json.loads(module.COMMITTED.read_text())
        self.assertEqual(committed, module.generate())

    def test_open_is_not_falsified(self) -> None:
        audit = load().generate()
        for key in ("C", "S"):
            self.assertEqual(audit["items"][key]["state"], "OPEN")
            self.assertFalse(audit["items"][key]["proved"])
            self.assertFalse(audit["items"][key]["falsified"])
        self.assertTrue(audit["items"]["P3_E12"]["proved"])
        self.assertEqual(audit["items"]["P0"]["state"], "OPEN")
        self.assertFalse(audit["items"]["P0"]["proved"])
        self.assertFalse(audit["counterexample_claim_proved"])


if __name__ == "__main__":
    unittest.main()
