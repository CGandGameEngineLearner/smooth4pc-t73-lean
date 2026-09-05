from __future__ import annotations
import hashlib,json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"audit/t73_affine_s3_core_realization_verification.json";CORE=ROOT/"geometry/t73_affine_s3_core_realization.json"
class AffineCoreReceiptTest(unittest.TestCase):
 def test_receipt(self):
  d=json.loads(DATA.read_text());c=json.loads(CORE.read_text());v=ROOT/d["verifier_path"];self.assertEqual(d["affine_core_sha256"],c["sha256"]);self.assertEqual(d["verifier_sha256"],hashlib.sha256(v.read_bytes()).hexdigest().upper());self.assertEqual(d["verdict"],"PASS_CANONICAL_AFFINE_S3_CORE_EMBEDDING");self.assertEqual(d["full_verifier_result"]["waypoint_endpoint_incidence_checks"],25318728)
if __name__=="__main__":unittest.main()
