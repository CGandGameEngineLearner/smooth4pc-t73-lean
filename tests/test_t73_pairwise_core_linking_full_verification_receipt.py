from __future__ import annotations
import hashlib,json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"audit/t73_pairwise_core_linking_full_verification.json"
class PairwiseCoreFullReceiptTest(unittest.TestCase):
 def test_full_receipt(self):
  d=json.loads(DATA.read_text());v=ROOT/d["verifier_path"];self.assertEqual(d["verifier_sha256"],hashlib.sha256(v.read_bytes()).hexdigest().upper());self.assertEqual(d["verdict"],"PASS_ALL_TEN_PAIRWISE_CORE_LINKINGS_FULL");self.assertEqual(d["total_crossings"],5371724);self.assertTrue(all(x["exact_crossings_recomputed"]==x["crossings"] and x["database_sha_checked"] for x in d["full_results"].values()))
if __name__=="__main__":unittest.main()
