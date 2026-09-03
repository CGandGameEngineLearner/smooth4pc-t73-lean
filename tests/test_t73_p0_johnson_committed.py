from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class P0JohnsonCommittedTest(unittest.TestCase):
    def test_committed_certificate_has_every_required_gate(self):
        certificate = json.loads((ROOT / "audit" / "t73_p0_johnson_certificate.json").read_text())
        self.assertEqual(certificate["verdict"], "PASS")
        self.assertTrue(certificate["checks"])
        self.assertTrue(all(certificate["checks"].values()))
        self.assertEqual(certificate["historical_pd_claim"], "NONE")


if __name__ == "__main__":
    unittest.main()
