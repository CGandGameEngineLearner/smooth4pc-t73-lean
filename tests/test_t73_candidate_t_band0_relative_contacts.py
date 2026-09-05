from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_candidate_t_band0_relative_contacts.py"


class CandidateTBand0RelativeContactsTest(unittest.TestCase):
    def test_all_source_target_contacts_lie_on_attachment_edges(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_t_band0_contacts", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.verify()["verdict"], "PASS_CANDIDATE_BAND0_RELATIVE_CONTACTS_ONLY")


if __name__ == "__main__":
    unittest.main()
