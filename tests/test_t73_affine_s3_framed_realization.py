from __future__ import annotations
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"geometry/t73_affine_s3_framed_realization.json"
class AffineFramedConstructionTest(unittest.TestCase):
 def test_constructed_scope(self):
  d=json.loads(DATA.read_text());self.assertEqual(d["completion_status"],"CANONICAL_AFFINE_S3_CORE_AND_PUSH_CYCLES_CONSTRUCTED");self.assertEqual(d["core_segment_count"],23109);self.assertEqual(d["push_segment_count"],23109);self.assertEqual(d["framed_embedding_verification_status"],"OPEN_EXACT_CORE_PUSH_DISJOINTNESS")
if __name__=="__main__":unittest.main()
