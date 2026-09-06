from __future__ import annotations
import hashlib,json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"audit/t73_affine_s3_product_ribbon_global_clearance.json";CON=ROOT/"audit/t73_affine_s3_product_framed_realization_receipt.json"
class ProductRibbonClearanceTest(unittest.TestCase):
 def test_full_clearance_receipt(self):
  d=json.loads(DATA.read_text());c=json.loads(CON.read_text());v=ROOT/d["verifier_path"];self.assertEqual(d["construction_receipt_sha256"],c["sha256"]);self.assertEqual(d["product_framed_payload_sha256"],c["payload_sha256"]);self.assertEqual(d["verifier_sha256"],hashlib.sha256(v.read_bytes()).hexdigest().upper());self.assertEqual(d["verdict"],"PASS_AFFINE_S3_PRODUCT_CORRIDOR_RIBBON_GLOBAL_CLEARANCE");self.assertTrue(d["embedded_corridor_product_ribbons"]);self.assertEqual(d["triangle_result"]["exact_triangle_triangle_checks"],1779);self.assertEqual(d["segment_result"]["exact_segment_triangle_checks"],3560)
if __name__=="__main__":unittest.main()
