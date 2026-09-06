from __future__ import annotations
import hashlib,json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"audit/t73_product_self_linking_full_verification.json"
class ProductSelfLinkingFullReceiptTest(unittest.TestCase):
 def test_full_receipt(self):
  d=json.loads(DATA.read_text());v=ROOT/d["verifier_path"];self.assertEqual(d["verifier_sha256"],hashlib.sha256(v.read_bytes()).hexdigest().upper());self.assertEqual(d["verdict"],"PASS_ALL_FIVE_PRODUCT_SELF_LINKINGS_FULL");self.assertEqual(sum(x["exact_crossings_recomputed"] for x in d["full_results"].values()),25776472);self.assertTrue(all(x["database_sha_checked"] for x in d["full_results"].values()))
if __name__=="__main__":unittest.main()
