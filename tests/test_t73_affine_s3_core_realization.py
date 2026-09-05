from __future__ import annotations
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"geometry/t73_affine_s3_core_realization.json";RECEIPT=ROOT/"audit/t73_affine_s3_core_realization_verification.json"
class AffineS3CoreTest(unittest.TestCase):
 def test_core_embedding(self):
  d=json.loads(DATA.read_text());r=json.loads(RECEIPT.read_text());self.assertEqual(r["affine_core_sha256"],d["sha256"]);self.assertEqual(r["verdict"],"PASS_CANONICAL_AFFINE_S3_CORE_EMBEDDING");self.assertEqual(r["full_verifier_result"]["framed_core_segments"],23109);self.assertEqual(r["full_verifier_result"]["framed_push_status"],"OPEN_CONSTRUCT_AFFINE_PUSH_CORRIDORS")
if __name__=="__main__":unittest.main()
