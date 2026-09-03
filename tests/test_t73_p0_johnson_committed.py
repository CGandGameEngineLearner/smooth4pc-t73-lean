from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class P0JohnsonCommittedTest(unittest.TestCase):
    def test_committed_certificate_has_every_required_gate(self):
        certificate = json.loads((ROOT / "audit" / "t73_p0_johnson_certificate.json").read_text())
        self.assertEqual(certificate["verdict"], "PASS")
        self.assertEqual(
            certificate["P0_status"],
            "PROVED_FOR_EXPLICIT_JOHNSON_REPLACEMENT_PRESENTATION",
        )
        self.assertTrue(certificate["checks"]["embedded_framed_collar"])
        self.assertTrue(certificate["checks"]["ar_passage_binding"])
        self.assertTrue(certificate["checks"]["geometric_braid"])
        self.assertEqual(
            certificate["hashes"]["geometric_braid"],
            "7C2D2F792C2672221A76CAF08A71F560AF0CB7654B4D537C00FAD00B16EFA187",
        )
        self.assertEqual(certificate["historical_pd_claim"], "NONE")


if __name__ == "__main__":
    unittest.main()
