from __future__ import annotations
import hashlib,json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"audit/t73_affine_s3_framed_realization_verification.json";FRAMED=ROOT/"geometry/t73_affine_s3_framed_realization.json"
class AffineFramedReceiptTest(unittest.TestCase):
 def test_receipt(self):
  d=json.loads(DATA.read_text());f=json.loads(FRAMED.read_text());v=ROOT/d["verifier_path"];self.assertEqual(d["affine_framed_realization_sha256"],f["sha256"]);self.assertEqual(d["verifier_sha256"],hashlib.sha256(v.read_bytes()).hexdigest().upper());self.assertEqual(d["verdict"],"PASS_CANONICAL_AFFINE_S3_FRAMED_LINK_EMBEDDING");self.assertEqual(d["full_verifier_result"]["push_waypoint_endpoint_incidence_checks"],50637456)
if __name__=="__main__":unittest.main()
