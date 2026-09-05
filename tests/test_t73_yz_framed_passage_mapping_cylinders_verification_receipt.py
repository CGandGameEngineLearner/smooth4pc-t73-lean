from __future__ import annotations
import hashlib,json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"audit/t73_yz_framed_passage_mapping_cylinders_verification.json";CON=ROOT/"audit/t73_yz_framed_passage_mapping_cylinders_receipt.json"
class YZCylinderFullReceiptTest(unittest.TestCase):
 def test_full_receipt(self):
  d=json.loads(DATA.read_text());c=json.loads(CON.read_text());v=ROOT/d["verifier_path"];self.assertEqual(d["construction_receipt_sha256"],c["sha256"]);self.assertEqual(d["verifier_sha256"],hashlib.sha256(v.read_bytes()).hexdigest().upper());self.assertEqual(d["verdict"],"PASS_ALL_YZ_FRAMED_PASSAGE_MAPPING_CYLINDERS_FULL");self.assertTrue(d["full_verifier_result"]["continuous_dotted_conversion_in_atlas"])
if __name__=="__main__":unittest.main()
